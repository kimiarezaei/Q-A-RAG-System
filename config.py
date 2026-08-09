from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
     
    # API Keys
    model_config = SettingsConfigDict(env_file=".env")
    anthropic_api_key: str
    hf_token: str | None = None

    # document processing
    chunk_size: int = 1000
    chunk_overlap: int = 200

    # LLM
    model_name: str = "claude-sonnet-4-6"
    temperature: float = 0.0
    max_tokens: int = 500

    # RAG
    rag_temperature: float = 0.0
    rag_max_tokens: int = 500

    # Vector_store
    embedding_model_name: str = "all-MiniLM-L6-v2"
    indexing_batch_size  : int = 100  
    similarity_threshold : float = 0.75
    retrieval_top_k : int = 3

    # Cache
    vector_store_version: str = "v1"
    

    @computed_field
    @property
    def chroma_path(self) -> str:
        return f"chromadb_{self.vector_store_version}"

    @computed_field
    @property
    def log_file(self) -> str:
        return "logs/app.log"

    


settings = Settings()