from openai import OpenAI
from app.config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)


class TranscriptionError(Exception):
    """Raised when audio transcription fails"""
    pass


def transcribe_api(file_path: str) -> str:
    try:
        with open(file_path, "rb") as audio_file:
            response = client.audio.transcriptions.create(
                model="gpt-4o-transcribe",
                file=audio_file,
                prompt="Translate the speech to English"
            )

        if not getattr(response, "text", None):
            raise TranscriptionError("Empty transcription returned")

        return response.text

    except FileNotFoundError as e:
        raise TranscriptionError("Audio file not found") from e

    except PermissionError as e:
        raise TranscriptionError("No permission to read audio file") from e

    except Exception as e:
        raise TranscriptionError("Audio transcription failed") from e