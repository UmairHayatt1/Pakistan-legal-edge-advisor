import os
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

class AppSettings(BaseModel):
    app_name: str = "Pakistan Legal Compliance Agent"
    version: str = "1.0.0"
    env: str = os.getenv("APP_ENV", "development")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Base Paths
    base_dir: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir: str = os.path.join(base_dir, "data")
    vectordb_dir: str = os.path.join(base_dir, "vectordb", "chroma")
    
    # LLM & Embedding Configurations
    llm_model: str = os.getenv("LLM_MODEL", "llama-3.1-8b-instant")
    GROQ_MODEL: str = os.getenv("LLM_MODEL", "llama-3.1-8b-instant")
    embedding_model: str = os.getenv("EMBEDDING_MODEL_NAME", "BAAI/bge-small-en-v1.5")
    
    chunk_size: int = int(os.getenv("CHUNK_SIZE", "800"))
    chunk_overlap: int = int(os.getenv("CHUNK_OVERLAP", "150"))
    top_k: int = 8

settings = AppSettings()