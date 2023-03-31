import os
from timeit import default_timer as timer
from typing import Union

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from nldb.core import get_prompt_template, text_to_sql, execute_sql

UVICORN_HOST = os.environ.get("UVICORN_HOST", "0.0.0.0")
UVICORN_PORT = int(os.environ.get("UVICORN_PORT", 8080))


# FastAPI app
app = FastAPI()


@app.on_event("startup")
def template_loader():
    global prompt_template
    prompt_template = get_prompt_template()


@app.get("/api/ask")
def ask(q: Union[str, None] = None):
    start = timer()
    (sql_statement, tokens) = text_to_sql(prompt_template, q)
    generation_time = timer() - start
    if generation_time < 0.0001:
        tokens = 0  # cached results don't count towards tokens
    start = timer()
    result = execute_sql(sql_statement)
    execution_time = timer() - start
    return {
        "response": {
            "answer": result,
            "sql": sql_statement,
            "duration": [generation_time, execution_time],  # in seconds
            "tokens": tokens,
            "cost": tokens / 1000 * 0.002,  # gpt-3.5 is $0.002 per 1000 tokens,
        }
    }


def serve():
    app.mount("/", StaticFiles(directory="./", html=True), name="static")
    uvicorn.run(app, host=UVICORN_HOST, port=UVICORN_PORT)
