from pydantic import SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Backend configuration, read from environment variables or backend/.env."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    groq_api_key: SecretStr | None = None
    frontend_origin: str = "http://localhost:5173"

    @field_validator("groq_api_key", mode="before")
    @classmethod
    def blank_key_is_unset(cls, value):
        # An empty or whitespace-only key counts as "not configured".
        if value is None:
            return None
        raw = value.get_secret_value() if isinstance(value, SecretStr) else str(value)
        return raw.strip() or None

    @field_validator("frontend_origin")
    @classmethod
    def origin_must_not_be_wildcard(cls, value: str) -> str:
        value = value.strip()
        if value == "*":
            raise ValueError("FRONTEND_ORIGIN must be a specific origin, not '*'")
        if not value:
            raise ValueError("FRONTEND_ORIGIN must not be empty")
        return value.rstrip("/")

    @property
    def groq_configured(self) -> bool:
        return self.groq_api_key is not None
