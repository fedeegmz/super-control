from pydantic import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Super Control"
    jwt_secretkey: str

    class Config:
        env_file = ".env"

settings = Settings()