from app.services.speech_api import transcribe_api

async def transcribe(file_path: str, mode: str) -> str:
    if mode == "api":
        return await transcribe_api(file_path)   