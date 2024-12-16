import sqlite3

conn = sqlite3.connect('database/u_tire_app.db')  # データベースファイル名を指定
cursor = conn.cursor()

# テーブル一覧を表示
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("Tables:", tables)

# 各テーブルのスキーマ情報を表示
for table in tables:
    table_name = table[0]
    print(f"\nSchema for {table_name}:")
    cursor.execute(f"PRAGMA table_info({table_name});")
    schema = cursor.fetchall()
    for column in schema:
        print(column)

conn.close()
