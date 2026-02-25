from fastapi import FastAPI, UploadFile, File, Query, HTTPException
import shutil
import os
from app.services.speech_api import TranscriptionError
from app.services.speech_factory import transcribe
from app.services.metadata_service import extract_metadata, MetadataExtractionError
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/process-audio")
async def process_audio(
    file: UploadFile = File(...),
    mode: str = Query("api", enum=["local", "api"])
):
    file_path = f"temp_{file.filename}"

    try:
        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Transcription
        transcript = transcribe(file_path, mode)

        if not transcript:
            raise HTTPException(status_code=422, detail="Empty transcript")

        # Metadata extraction
        try:
            metadata = extract_metadata(transcript)
        except MetadataExtractionError:
            metadata = {"items": []}  # graceful fallback

        return {
            "transcript": transcript,
            "metadata": metadata
        }

    except TranscriptionError as e:
        raise HTTPException(status_code=502, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=500, detail="Audio processing failed")

    finally:
        # Cleanup temp file
        if os.path.exists(file_path):
            os.remove(file_path)