import os
from dotenv import load_dotenv

# 環境変数をロード
load_dotenv()

class Config:
    DATABASE_URL = os.getenv("DATABASE_URL")

    if DATABASE_URL:
        # PostgreSQL の場合、`postgres://` を `postgresql://` に修正
        SQLALCHEMY_DATABASE_URI = DATABASE_URL.replace("postgres://", "postgresql://")
    else:
        raise ValueError("DATABASE_URL が設定されていません！")

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key_here")
