import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    database_url: str = ""
    cors_origins: tuple[str, ...] = (
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    )

    @classmethod
    def from_environment(cls) -> "Settings":
        # Existing environment variables take precedence over backend/.env.
        load_dotenv(Path(__file__).resolve().parents[1] / ".env", override=False)
        origins = os.getenv("CORS_ORIGINS")
        return cls(
            database_url=os.getenv("DATABASE_URL", "").strip(),
            cors_origins=(
                tuple(origin.strip() for origin in origins.split(",") if origin.strip())
                if origins is not None
                else cls().cors_origins
            ),
        )
