import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Config:
    BASE_DIR = Path(__file__).resolve().parent.parent
    MODEL_DIR = BASE_DIR / "models"
    LIB_DIR = BASE_DIR / "libs"

    AUDIO_SAMPLE_RATE = 44100
    AUDIO_CHUNK_SIZE = 2048

    VOKATURI_DLL_PATH = LIB_DIR / "OpenVokaturi-4-0-win64.dll"
    VOSK_MODEL_PATH = MODEL_DIR / "vosk/es"

    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL = "gpt-4-turbo"
    OPENAI_TEMPERATURE = 0.7

    API_HOST = "0.0.0.0"
    API_PORT = 5000
    API_DEBUG = True

    @classmethod
    def validate(cls):
        errors = []
        if not cls.VOKATURI_DLL_PATH.exists():
            errors.append("DLL Vokaturi no encontrada.")
        if not cls.VOSK_MODEL_PATH.exists():
            errors.append("Modelo Vosk no encontrado.")
        if not cls.OPENAI_API_KEY:
            errors.append("OPENAI_API_KEY no configurada.")

        if errors:
            raise EnvironmentError("\n".join(errors))

settings = Config()
settings.validate()
