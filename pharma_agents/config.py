# config.py

from dataclasses import dataclass

@dataclass
class Settings:
    # Base URL where your FastAPI mock API is running
    # Example: http://localhost:8000
    api_base_url: str = "http://localhost:8000"


settings = Settings()