from openai import OpenAI
import asyncio
from app.core.config import settings

# Initialize OpenAI client using API key from configuration
client = OpenAI(api_key=settings.OPENAI_API_KEY)


class TranscriptionError(Exception):
    """Custom exception raised when audio transcription fails"""
    pass


async def transcribe_api(file_path: str) -> str:
    """
    Transcribe an audio file using OpenAI Whisper model.

    Features:
    - Retries transcription up to 3 times
    - Uses exponential backoff for retry delays
    - Runs blocking OpenAI API call in a thread to avoid blocking asyncio loop
    """
    max_retries = 3

    for attempt in range(max_retries):
        try:
            # Run blocking OpenAI transcription call inside a thread
            response = await asyncio.to_thread(_call_openai_transcribe, file_path)

            # Validate response contains transcription text
            if not getattr(response, "text", None):
                raise TranscriptionError("Empty transcription returned")

            return response.text

        except FileNotFoundError as e:
            # Handle case where the audio file path does not exist
            if attempt == max_retries - 1:
                raise TranscriptionError("Audio file not found") from e

            # Exponential backoff before retrying
            await asyncio.sleep(2 ** attempt)

        except PermissionError as e:
            # Handle file permission issues
            if attempt == max_retries - 1:
                raise TranscriptionError("No permission to read audio file") from e

            await asyncio.sleep(2 ** attempt)

        except Exception as e:
            # Catch all other transcription errors (network, API, etc.)
            if attempt == max_retries - 1:
                raise TranscriptionError("Audio transcription failed") from e

            await asyncio.sleep(2 ** attempt)


def _call_openai_transcribe(file_path: str):
    """
    Calls OpenAI transcription API.

    This function is intentionally synchronous because it is executed
    inside a thread using asyncio.to_thread().
    """
    with open(file_path, "rb") as audio_file:
        return client.audio.transcriptions.create(
            model=settings.SPEECH_TO_TEXT_MODEL,  # OpenAI speech-to-text model
            file=audio_file,
            prompt="Translate the speech to English",  # Ensures output is in English
        )