import os

class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///grocerystore.db"
    JWT_SECRET_KEY = "anthggpjis"
    UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")
    CELERY_BROKER_URL = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND = "redis://localhost:6379/2"