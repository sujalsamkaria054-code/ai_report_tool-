from dataclasses import dataclass


@dataclass
class Settings:
    app_name: str = "AI Report Tool"
    debug: bool = True
    api_prefix: str = ""
    host: str = "0.0.0.0"
    port: int = 8000


settings = Settings()
