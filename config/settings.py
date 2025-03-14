# config/settings.py
import os
from pathlib import Path
from dotenv import load_dotenv
from typing import Dict, Any

# Cargar variables de entorno desde .env
load_dotenv()

class Config:
    """Configuración base para todos los entornos"""
    
    # Directorios principales
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    MODEL_DIR: Path = BASE_DIR / "models"
    LIB_DIR: Path = BASE_DIR / "libs"
    
    # Configuración de audio
    AUDIO_SAMPLE_RATE: int = 16000
    AUDIO_CHUNK_SIZE: int = 2048
    MAX_AUDIO_DURATION: int = 300  # segundos
    
    # Configuración de Vokaturi
    VOKATURI_DLL_PATH: Path = LIB_DIR / "OpenVokaturi-4-0-win64.dll"
    
    # Configuración de Vosk
    VOSK_MODEL_PATH: Path = MODEL_DIR / "vosk" / "es"
    
    # OpenAI
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = "gpt-4-turbo"
    OPENAI_TEMPERATURE: float = 0.7
    
    # Configuración de la API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 5000
    API_DEBUG: bool = False
    API_MAX_CONTENT_LENGTH: int = 16 * 1024 * 1024  # 16MB
    
    # Configuración de logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    @classmethod
    def validate(cls):
        """Validar configuraciones esenciales"""
        errors = []
        
        if not cls.VOKATURI_DLL_PATH.exists():
            errors.append(f"Vokaturi DLL no encontrada en {cls.VOKATURI_DLL_PATH}")
            
        if not cls.VOSK_MODEL_PATH.exists():
            errors.append(f"Modelo Vosk no encontrado en {cls.VOSK_MODEL_PATH}")
            
        if not cls.OPENAI_API_KEY:
            errors.append("OPENAI_API_KEY no configurada")
            
        if errors:
            raise EnvironmentError("\n".join(errors))
    
    @classmethod
    def as_dict(cls) -> Dict[str, Any]:
        """Devolver configuración como diccionario"""
        return {
            key: value 
            for key, value in cls.__dict__.items()
            if not key.startswith("__") and not callable(value)
        }

class DevelopmentConfig(Config):
    """Configuración para entorno de desarrollo"""
    API_DEBUG: bool = True
    LOG_LEVEL: str = "DEBUG"

class ProductionConfig(Config):
    """Configuración para entorno de producción"""
    API_DEBUG: bool = False
    LOG_LEVEL: str = "WARNING"

class TestingConfig(Config):
    """Configuración para pruebas"""
    API_DEBUG: bool = True
    TESTING: bool = True
    OPENAI_MODEL: str = "gpt-3.5-turbo"

def get_settings(env: str = None) -> Config:
    """Factory para obtener configuración según entorno"""
    env = env or os.getenv("APP_ENV", "development")
    
    configs = {
        "development": DevelopmentConfig,
        "production": ProductionConfig,
        "testing": TestingConfig
    }
    
    if env not in configs:
        raise ValueError(f"Entorno {env} no válido. Opciones: {', '.join(configs.keys())}")
    
    config = configs[env]
    config.validate()
    
    return config

# Configuración activa
settings = get_settings()