from fastapi import FastAPI, UploadFile, File, Query
import shutil
from app.services.speech_factory import transcribe
from app.services.metadata_service import extract_metadata
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # React app URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/process-audio")
async def process_audio(
    file: UploadFile = File(...),
    mode: str = Query("local", enum=["local", "api"])
):

    file_path = f"temp_{file.filename}"

    with open(file_path, "wb") as buffer:# write binary mode ,audio files are binary data (not text)
        shutil.copyfileobj(file.file, buffer)

    transcript = transcribe(file_path, mode)
    metadata = extract_metadata(transcript)

    return {
         "transcript": transcript,
        "metadata": metadata
    }


