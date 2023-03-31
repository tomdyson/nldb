import os
import sqlite3
from functools import lru_cache
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
def text_to_sql(prompt_template: str, question: str) -> Tuple[str, int]:
    # uses GPT-3.5 to convert a question into a SQL statement
    prompt_messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": prompt_template % question},
    ]

    resp = ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=prompt_messages,
        temperature=0,
    )

    sql = resp["choices"][0]["message"]["content"].strip()
    tokens = resp["usage"]["total_tokens"]

    return (sql, tokens)


def execute_sql(query):
    # open the database in read-only mode
    connection = sqlite3.connect(f"file:{DATABASE}?mode=ro", uri=True)
    cursor = connection.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    # make the column names more readable
    columns = [description[0].replace("_", " ") for description in cursor.description]
    return tabulate(result, headers=columns, tablefmt="html")
    # return tabulate(result, headers=columns)
