import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):

    OPENAI_API_KEY: str
    METADATA_EXTRACTION_MODEL: str
    SPEECH_TO_TEXT_MODEL: str
    MODEL_TEMPERATURE: float = 0.0

    class Config:
        env_file = ".env"


settings = Settings()

