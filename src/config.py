from dotenv import load_dotenv
import os

load_dotenv()  # reads .env into environment variables

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GEN_MODEL = os.getenv("GEN_MODEL", "gpt-4o-mini")