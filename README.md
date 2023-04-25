# nldb

Natural Language Databasing. Talk to your data in English, via CLI, API or a simple web interface.

## Installation

```bash
pip install nldb
```

An OpenAI API key should be available as the `OPENAI_API_KEY` environment variable, e.g. using `export OPENAI_API_KEY=sk-etc`.

## Preparing your database
NLDB can talk to SQLite and DuckDB databases. Call yours `nldb.db` or specify the name with a `DATABASE` environment variable.

You may need to simplify, denormalise and anonymise your database for NLDB to work well. Your columns should have names whose meaning is obvious. While NLDB can join across tables, combining your data into a single table will reduce your prompt size and improve the accuracy of NLDB's query generation.

## Initialise NLDB

```bash
nldb init
```

This creates three files: `prompt.txt`, `index.html` and `Dockerfile`. 

## Edit your prompt

Edit `prompt.txt`, following the example and instructions in the generated file. You can test the effectiveness of your prompt by pasting it into ChatGPT, replacing `%s` with some example questions.

## Ask questions from the command line

```bash
nldb "What were the most watched videos by Japanese users in 2022?"
```

## Start the web server

```bash
nldb serve
```

## Adjust

Edit `prompt.txt` to refine the quality of the generated queries, restarting the server to see changes. Edit `index.html` or replace it with your own front-end.

## Deploy

Generate instructions for Fly.io and Google Cloud Run

```bash
nldb deploy
```
