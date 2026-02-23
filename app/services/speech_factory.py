from app.services.speech_local import transcribe_local
from app.services.speech_api import transcribe_api

def transcribe(file_path: str, mode: str) -> str:
    if mode == "api":
        return transcribe_api(file_path)
