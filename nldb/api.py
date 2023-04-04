import os
from typing import Union

import uvicorn
from fastapi import FastAPI
from fastapi.responses import FileResponse

from nldb.core import get_prompt_template, text_to_sql, sql_to_answer

UVICORN_HOST = os.environ.get("UVICORN_HOST", "0.0.0.0")
UVICORN_PORT = int(os.environ.get("UVICORN_PORT", 8080))

app = FastAPI()


@app.on_event("startup")
def template_loader():
    global prompt_template
    prompt_template = get_prompt_template()


@app.get("/api/ask")
async def ask(q: Union[str, None] = None):
    (sql_statement, tokens_1, time_1) = text_to_sql(prompt_template, q)
    (results, answer, tokens_2, sql_time, time_2) = sql_to_answer(
        sql_statement, prompt_template, q
    )
    tokens = tokens_1 + tokens_2
    return {
        "response": {
            "answer": answer,
            "results": results,
            "sql": sql_statement,
            "timings": [time_1, sql_time, time_2],  # in seconds
            "tokens": tokens,
            "cost": (tokens_1 + tokens_2)
            / 1000
            * 0.002,  # gpt-3.5 is $0.002 per 1000 tokens,
        }
    }


@app.get("/")
async def read_index():
    return FileResponse("index.html")


def serve():
    uvicorn.run(app, host=UVICORN_HOST, port=UVICORN_PORT)
