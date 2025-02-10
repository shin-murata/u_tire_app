import sqlite3

DB_PATH = "database/u_tire_app.db"  # データベースのパスを適宜変更

def reset_inventory():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 外部キー制約を一時的に無効化
    cursor.execute("PRAGMA foreign_keys = OFF;")

    # 在庫データ関連テーブルを削除
    cursor.execute("DELETE FROM input_page;")
    cursor.execute("DELETE FROM dispatch_history;")
    cursor.execute("DELETE FROM edit_page;")
    cursor.execute("DELETE FROM alert_page;")
    cursor.execute("DELETE FROM history_page;")

    # IDカウンターをリセット
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='input_page';")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='dispatch_history';")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='edit_page';")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='alert_page';")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='history_page';")

    # 外部キー制約を再び有効化
    cursor.execute("PRAGMA foreign_keys = ON;")

    # ここでコミット（トランザクションを終了）
    conn.commit()
    conn.close()

    # 別の接続を開いてVACUUMを実行（トランザクション外で）
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("VACUUM;")
    conn.commit()
    conn.close()

    print("在庫データをリセットしました。")

if __name__ == "__main__":
    reset_inventory()
