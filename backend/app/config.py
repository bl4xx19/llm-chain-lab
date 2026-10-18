from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    llm_base_url: str = "https://api.groq.com/openai/v1"
    llm_api_key: str = ""
    llm_model: str = "openai/gpt-oss-20b"
    llm_temperature: float = 0.0
    llm_min_interval_seconds: float = 0.0
    llm_max_retries: int | None = None

    database_url: str = "postgresql+psycopg://labuser:labpass@db:5432/llm_chain_lab"

    class Config:
        env_file = ".env"


settings = Settings()
