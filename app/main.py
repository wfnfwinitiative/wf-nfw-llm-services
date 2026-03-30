from fastapi import FastAPI, UploadFile, File, Query, HTTPException
import os
import aiofiles
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
        #  Async save file
        async with aiofiles.open(file_path, "wb") as buffer:
            content = await file.read()
            await buffer.write(content)

        # Async transcription
        transcript = await transcribe(file_path, mode)

        if not transcript:
            raise HTTPException(status_code=422, detail="Empty transcript")

        #  Async metadata extraction
        try:
            metadata = await extract_metadata(transcript)
        except MetadataExtractionError:
            metadata = {"items": []}

        return {
            "transcript": transcript,
            "metadata": metadata
        }

    except TranscriptionError as e:
        raise HTTPException(status_code=502, detail=str(e))

    except Exception:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        if os.path.exists(file_path):
            os.remove(file_path)
