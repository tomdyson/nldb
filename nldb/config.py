import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env")

DATABASE = os.getenv("DATABASE", "nldb.db")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
UVICORN_HOST = os.getenv("UVICORN_HOST", "0.0.0.0")
UVICORN_PORT = int(os.getenv("UVICORN_PORT", 8080))