from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    sqlalchemy_database_url: str = 'postgresql+psycopg2://user:password@localhost:5432/postgres'
    secret_key_jwt: str = "secret_key"
    algorithm: str = "HS256"
    mail_username: str = "example@meta.ua"
    mail_password: str = "secretPassword"
    mail_from: str = "example@meta.ua"
    mail_port: int = 465
    mail_server: str = "smtp.meta.ua"
    redis_host: str = 'localhost'
    redis_port: int = 6379
    #redis_password: str = '567234'
    cloudinary_name: str = "do8ipactb"
    cloudinary_api_key: int = 715755664291385
    cloudinary_api_secret: str = "secret"

    class Config:
        extra = 'allow'
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
