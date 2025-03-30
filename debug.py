# routes/debug.py

from flask import Blueprint
from models import db, DispatchHistory
from datetime import datetime

debug_bp = Blueprint("debug", __name__)

@debug_bp.route("/check_dispatch_date")
def check_dispatch_date():
    records = db.session.query(DispatchHistory).all()
    result_lines = []

    for record in records:
        date_val = record.dispatch_date
        date_type = repr(type(date_val))  # ← ここをreprでラップ！
        print(f"[DEBUG] ID: {record.id}, 値: {date_val}, 型: {date_type}")  # ← ログにも出力
        result_lines.append(f"ID: {record.id}, 値: {date_val}, 型: {date_type}")

    return "<br>".join(result_lines)
