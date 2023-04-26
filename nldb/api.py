import os
from typing import Union

import uvicorn
from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel

from nldb.core import NLDB

UVICORN_HOST = os.environ.get("UVICORN_HOST", "0.0.0.0")
UVICORN_PORT = int(os.environ.get("UVICORN_PORT", 8080))

app = FastAPI()


@app.on_event("startup")
def load_prompt_template():
    """Load the prompt template on startup."""
    global prompt_template
    prompt_template = NLDB().prompt_template


@app.get("/api/ask")
async def ask(q: Union[str, None] = None):
    """Process a text query and return the SQL statement, results, and explanation."""
    nldb = NLDB(prompt_template)
    sql_statement = nldb.text_to_sql(q)
    results, plain_text_results, answer = nldb.sql_to_answer(sql_statement)
    return {
        "response": {
            "sql": sql_statement,
            "results": results,
            "plain_text_results": plain_text_results,
            "answer": answer,
            "timings": nldb.timings,  # in seconds
            "tokens": nldb.tokens,
            "cost": nldb.tokens / 1000 * 0.002,  # gpt-3.5 is $0.002 per 1000 tokens,
        }
    }


class ChartRequest(BaseModel):
    question: str
    results: str


@app.post("/api/chart")
async def chart(request_data: ChartRequest):
    """Process a question and results,
    executes returned code and returns filename of chart"""
    nldb = NLDB()
    filename, code = nldb.results_to_chart(request_data.question, request_data.results)
    print(filename)
    print(code)
    exec(code)
    return {"response": {"chart": filename}}


@app.get("/charts/{filename}")
async def serve_chart(filename: str):
    """Serve charts from ./charts"""
    return FileResponse(f"charts/{filename}")


@app.get("/")
async def serve_index():
    """Serve index.html"""
    return FileResponse("index.html")


def serve():
    uvicorn.run("nldb.api:app", host=UVICORN_HOST, port=UVICORN_PORT, workers=2)
