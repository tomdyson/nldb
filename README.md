# nldb

Natural Language Databasing. Talk to your data in English, via CLI, API or a simple web interface.

## Installation

```bash
pip install nldb
```

An OpenAI API key should be available as the `OPENAI_API_KEY` environment variable, e.g. using `export OPENAI_API_KEY=sk-etc` or adding it to your project `.env` file.

## Preparing your database
NLDB can talk to SQLite and DuckDB databases. Call yours `nldb.db` or specify the name with a `DATABASE` environment variable.

You may need to simplify and denormalise your database for NLDB to work well. Your columns should have names whose meaning is obvious. While NLDB can join across tables, combining your data into a single table will reduce your prompt size and improve the accuracy of NLDB's query generation.

## Initialise NLDB

```bash
nldb init
```

This creates three files: `index.html`, `Dockerfile` and `prompt.txt`. You can ignore the first two for now.

## Edit your prompt

Edit `prompt.txt`, following the example and instructions in the generated file. You can test the effectiveness of your prompt by pasting it into ChatGPT, replacing `%s` with some example questions.

## Ask questions from the command line

```bash
nldb "What were the most watched videos by Japanese users in 2022?"
```

## Start the API server

```bash
nldb serve
```

This starts an API server, on port 8080, with a single endpoint at `/api/ask`. This expects a GET request with a `q` parameter for the natural language query. It returns a JSON object containing the SQL statement, the result of executing the statement, a plain English answer and some timing and cost information.

There is a simple web interface to the API at `/`. If you don't want this, just delete `index.html`.

## Adjust

Edit `prompt.txt` to refine the quality of the generated queries, restarting the server to see changes. Edit `index.html` or replace it with your own front-end.

## Deploy

Generate instructions for Fly.io and Google Cloud Run

```bash
nldb deploy
```
