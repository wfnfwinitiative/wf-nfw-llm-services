import os
from pathlib import Path
from dotenv import load_dotenv

# Explicitly load .env from project root (parent of app/)
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path, override=True)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
