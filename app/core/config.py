import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "Career Compass AI")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./career_compass.db")
    JWT_SECRET: str = os.getenv("JWT_SECRET", "supersecretjwtkeyforcareercompassai12345!")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "120"))

settings = Settings()
