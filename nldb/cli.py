import inspect
import os
import shutil

import typer

from nldb.api import serve
from nldb.config import get_settings
from nldb.core import NLDB

settings = get_settings()


def preflight_checks():
    # check that the prompt.txt file exists
    failures = 0
    if not os.path.exists("prompt.txt"):
        typer.echo("prompt.txt file not found")
        typer.echo("Run `nldb init` to create a new prompt.txt file")
        failures += 1
    if not os.path.exists(settings.database):
        typer.echo(f"Database file not found: {settings.database}")
        failures += 1
    if not settings.openai_api_key:
        typer.echo("OPENAI_API_KEY environment variable not set")
        failures += 1
    if failures > 0:
        raise typer.Exit(code=1)


def init():
    # create a starter Dockerfile, index.html and prompt.py
    package_dir = os.path.dirname(os.path.realpath(__file__))
    for file in ["Dockerfile", "index.html", "prompt.txt"]:
        dest = os.path.join(os.getcwd(), file)
        if os.path.exists(dest):
            typer.echo(f"{file} already exists here")
        else:
            shutil.copyfile(os.path.join(package_dir, "templates", file), dest)
            typer.echo(f"Created {file} at {dest}")
    # make a 'charts' directory if it doesn't exist
    charts_dir = os.path.join(os.getcwd(), "charts")
    if not os.path.exists(charts_dir):
        os.mkdir(charts_dir)
        typer.echo(f"Created directory at {charts_dir}")


def deploy_instructions():
    typer.echo("Printing deployment instructions")
    openai_api_key = settings.OPENAI_API_KEY or "your OpenAI API key"
    instructions = inspect.cleandoc(
        f"""
        # For fly.io:
        fly launch # answer no to Postgres, Redis and deploying now
        fly secrets set OPENAI_API_KEY={openai_api_key}
        fly deploy

        # For Google Cloud Run:
        gcloud run deploy --source . --set-env-vars="OPENAI_API_KEY={openai_api_key}"
        """
    )
    print(instructions)


def answer(query):
    nldb = NLDB()
    sql_statement = nldb.text_to_sql(query)
    print(f"\n{sql_statement.strip()}")
    answer = nldb.sql_to_answer(sql_statement)[2]
    print(f"\n{answer}\n")


def main(action: str | None = typer.Argument(None)):
    if not action or action == "serve":
        preflight_checks()
        serve()
    elif action == "init":
        init()
    elif action == "deploy":
        preflight_checks()
        deploy_instructions()
    else:
        answer(action)


# script entrypoint for flit
def cli_wrapper():
    typer.run(main)


if __name__ == "__main__":
    typer.run(main)
