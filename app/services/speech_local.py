import whisper

_model = None  # global cache


def get_model():
    global _model

    if _model is None:
        print("Loading Whisper model...")
        _model = whisper.load_model("base")  # downloads if not present

    return _model


def transcribe_local(file_path: str) -> str:
    model = get_model()
    result = model.transcribe(file_path, task="translate")
    return result["text"]
