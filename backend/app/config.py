"""Configuration management using Pydantic settings."""
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database configuration
    db_host: str = Field(default="postgres", env="DB_HOST")
    db_port: int = Field(default=5432, env="DB_PORT")
    db_name: str = Field(default="olive_monitoring", env="DB_NAME")
    db_user: str = Field(default="olive_user", env="DB_USER")
    db_password: str = Field(default="", env="DB_PASSWORD")

    # Copernicus Data Space credentials
    copernicus_username: str = Field(default="", env="COPERNICUS_USERNAME")
    copernicus_password: str = Field(default="", env="COPERNICUS_PASSWORD")

    # Paths
    data_dir: str = Field(default="/app/data", env="DATA_DIR")

    # Alert email configuration (optional)
    smtp_host: str = Field(default="smtp.gmail.com", env="SMTP_HOST")
    smtp_port: int = Field(default=587, env="SMTP_PORT")
    smtp_username: str = Field(default="", env="SMTP_USERNAME")
    smtp_password: str = Field(default="", env="SMTP_PASSWORD")
    alert_email: str = Field(default="", env="ALERT_EMAIL")

    class Config:
        env_file = ".env"
        case_sensitive = False

    @property
    def database_url(self) -> str:
        """Construct PostgreSQL connection URL."""
        return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"


# Global settings instance
settings = Settings()
