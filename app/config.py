import os
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import Optional

# Load environment variables from .env file
load_dotenv()

class Settings(BaseModel):
    """Application settings."""
    github_token: str = ""  # Empty token for anonymous access
    github_repository: str = os.getenv("GITHUB_REPOSITORY", "ololo-tratata/cursor-rules")
    rules_cache_ttl: int = int(os.getenv("RULES_CACHE_TTL", "3600"))  # 1 hour in seconds
    rules_local_path: str = os.getenv("RULES_LOCAL_PATH", "./rules")
    api_host: str = os.getenv("API_HOST", "0.0.0.0")
    api_port: int = int(os.getenv("API_PORT", "8000"))
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

# Create settings instance
settings = Settings()

# No need to warn about missing token as we're using anonymous access
# if not settings.github_token:
#     print("Warning: GITHUB_TOKEN not set. GitHub API calls may be rate limited.") 