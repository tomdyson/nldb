import os
import sqlite3
import duckdb
from functools import lru_cache
from timeit import default_timer as timer
from typing import Tuple

from openai import ChatCompletion
from tabulate import tabulate

DATABASE = os.environ.get("DATABASE", "nldb.db")


class ttimer:
    """A tiny timer context manager"""

    def __enter__(self):
        self.start_time = timer()
        return self

    def __exit__(self, type, value, traceback):
        self.time = timer() - self.start_time


def is_sqlite3_db(filename):
    try:
        con = sqlite3.connect(filename)
        cursor = con.cursor()
        cursor.execute("PRAGMA integrity_check")
        result = cursor.fetchone()
        cursor.close()
        con.close()
        return result == ("ok",)
    except sqlite3.Error:
        return False


class NLDB:
    def __init__(self, prompt_template: str = None) -> None:
        self.prompt_template = prompt_template or self.get_prompt_template()
        self.tokens = 0
        self.timings = []
        self.question = ""
        self.db_type = "sqlite3" if is_sqlite3_db(DATABASE) else "duckdb"

    def get_prompt_template(self) -> str:
        # returns the prompt template as a string, with comments removed
        lines = open("prompt.txt").read().split("\n")
        uncommented_lines = [line for line in lines if not line.strip().startswith("#")]
        return "\n".join(uncommented_lines).strip()

    @lru_cache
    def text_to_sql(self, question: str) -> str:
        # uses GPT-3.5 to convert a question into a SQL statement
        self.question = question
        prompt_messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": self.prompt_template % question},
        ]
        with ttimer() as gpt_timer:
            resp = ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=prompt_messages,
                temperature=0,
            )
        self.timings.append(gpt_timer.time)
        self.tokens += resp["usage"]["total_tokens"]

        return resp["choices"][0]["message"]["content"].strip()

    def execute_sql(self, query: str) -> Tuple[list, list]:
        # executes the SQL statement, returning a list of columns and a list of rows
        # open the database in read-only mode
        if self.db_type == "sqlite3":
            connection = sqlite3.connect(f"file:{DATABASE}?mode=ro", uri=True)
        elif self.db_type == "duckdb":
            connection = duckdb.connect(DATABASE, read_only=True)
        cursor = connection.cursor()
        cursor.execute(query)
        result = cursor.fetchall()
        columns = [column[0] for column in list(cursor.description)]
        cursor.close()
        connection.close()
        return (columns, result)

    @lru_cache
    def sql_to_answer(self, sql: str) -> Tuple[str, str]:
        # executes the SQL statement and asks GPT to explain them
        prompt_template = self.prompt_template
        question = self.question

        # execute the SQL statement
        with ttimer() as sql_timer:
            (columns, raw_results) = self.execute_sql(sql)
        self.timings.append(sql_timer.time)

        # format the results
        plain_text_results = tabulate(raw_results, headers=columns)
        clean_columns = [column[0].replace("_", " ") for column in columns]
        html_results = tabulate(raw_results, headers=clean_columns, tablefmt="html")

        prompt_messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt_template % question},
            {"role": "assistant", "content": sql},
            {
                "role": "system",
                "content": "The SQL statement returned the following results:\n\n"
                + plain_text_results,
            },
            {
                "role": "system",
                "content": f"Using these results, answer the question: {question}",
            },
            {
                "role": "system",
                "content": "Don't say what the query was, just answer the question.",
            },
        ]

        with ttimer() as gpt_timer:
            resp = ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=prompt_messages,
                temperature=0,
            )
        self.timings.append(gpt_timer.time)

        answer = resp["choices"][0]["message"]["content"].strip()
        self.tokens += resp["usage"]["total_tokens"]
        return (html_results, plain_text_results, answer)
