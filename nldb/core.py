import os
import sqlite3
from functools import lru_cache
from timeit import default_timer as timer
from typing import Tuple

from openai import ChatCompletion
from tabulate import tabulate

DATABASE = os.environ.get("DATABASE", "nldb.db")


def get_prompt_template() -> str:
    # returns the prompt template as a string, with comments removed
    lines = open("prompt.txt").read().split("\n")
    uncommented_lines = [line for line in lines if not line.strip().startswith("#")]
    return "\n".join(uncommented_lines).strip()


@lru_cache
def text_to_sql(prompt_template: str, question: str) -> Tuple[str, int, float]:
    # uses GPT-3.5 to convert a question into a SQL statement
    prompt_messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": prompt_template % question},
    ]

    start = timer()
    resp = ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=prompt_messages,
        temperature=0,
    )
    gpt_time = timer() - start

    sql = resp["choices"][0]["message"]["content"].strip()
    tokens = resp["usage"]["total_tokens"]

    return (sql, tokens, gpt_time)


@lru_cache
def sql_to_answer(
    sql: str, prompt_template: str, question: str
) -> Tuple[str, str, int, float, float]:
    start = timer()
    (columns, raw_results) = execute_sql(sql)
    execution_time = timer() - start
    formatted_results = tabulate(raw_results, headers=list(columns))
    clean_columns = [column[0].replace("_", " ") for column in columns]
    html_results = tabulate(raw_results, headers=clean_columns, tablefmt="html")

    sql_results_message = (
        "I executed the SQL statement and got the following results:\n\n"
        + formatted_results
    )

    prompt_messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": prompt_template % question},
        {"role": "assistant", "content": sql},
        {"role": "system", "content": sql_results_message},
        {
            "role": "system",
            "content": f"Using these results, answer the question: {question}",
        },
        {
            "role": "system",
            "content": "Don't say what the query was, just answer the question.",
        },
    ]

    gpt_start = timer()
    resp = ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=prompt_messages,
        temperature=0,
    )
    gpt_time = timer() - gpt_start

    answer = resp["choices"][0]["message"]["content"].strip()
    tokens = resp["usage"]["total_tokens"]
    return (html_results, answer, tokens, execution_time, gpt_time)


def execute_sql(query):
    # open the database in read-only mode
    connection = sqlite3.connect(f"file:{DATABASE}?mode=ro", uri=True)
    cursor = connection.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    columns = list(cursor.description)
    return (columns, result)
