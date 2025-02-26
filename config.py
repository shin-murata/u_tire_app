import os
from dotenv import load_dotenv

# 環境変数をロード
load_dotenv()

class Config:
    # Render の PostgreSQL URL を環境変数から取得
    DATABASE_URL = os.getenv("postgresql://u_tire_app_user:RNQRkAKWbg3eBheet2fDfUOW2avVlj9t@dpg-cutev07noe9s73997blg-a.singapore-postgres.render.com/u_tire_app")

    # DATABASE_URL が設定されていなければ、SQLite をデフォルトにする
    if DATABASE_URL:
        # PostgreSQL の場合、SQLAlchemy は `postgres://` ではなく `postgresql://` を要求するため修正
        SQLALCHEMY_DATABASE_URI = DATABASE_URL.replace("postgres://", "postgresql://")
    else:
        SQLALCHEMY_DATABASE_URI = "sqlite:///database/u_tire_app.db"  # ローカル開発用

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key_here")
