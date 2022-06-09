from pydantic import BaseModel, BaseSettings

# in this file we define all the environment variables
# that will be used in the application

class Settings(BaseSettings):
    database_hostname: str
    database_port: str
    database_password: str
    database_name: str
    database_username: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int


    class Config:
        env_file = ".env"       # this tell the class to read all values from file .env


settings = Settings()
