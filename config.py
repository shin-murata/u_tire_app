import os
from dotenv import load_dotenv

class Config:
    # 環境変数をロード
    load_dotenv()

    # DATABASE_URL を環境変数から取得（Render の PostgreSQL のURL）
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///database/u_tire_app.db")
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key_here")
