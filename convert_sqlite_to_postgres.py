import re

# SQLiteのダンプファイルを読み込む
with open("sqlite_dump.sql", "r", encoding="utf-8") as f:
    sql = f.read()

# `PRAGMA foreign_keys=OFF;` を削除
sql = re.sub(r'PRAGMA foreign_keys=OFF;', '', sql)

# `sqlite_sequence` に関連するすべての行を削除
sql = re.sub(r'DELETE FROM sqlite_sequence;', '', sql)
sql = re.sub(r'INSERT INTO sqlite_sequence .*?;', '', sql)

# AUTOINCREMENTをSERIALに変換
sql = re.sub(r'INTEGER PRIMARY KEY AUTOINCREMENT', 'SERIAL PRIMARY KEY', sql)

# is_dispatched のみ BOOLEAN に変換
# is_dispatched は12番目のカラムにあるため、カラムの位置を特定して変換
def replace_boolean(match):
    values = match.group(1).split(',')
    # is_dispatched の値をチェック（前後の空白を削除）
    if values[11].strip() == "0":
        values[11] = "FALSE"
    elif values[11].strip() == "1":
        values[11] = "TRUE"
    return f"INSERT INTO input_page VALUES({','.join(values)});"

sql = re.sub(r'INSERT INTO input_page VALUES\((.*?)\);', replace_boolean, sql)

# password_hash の VARCHAR(150) → TEXT に変換
sql = sql.replace('password_hash VARCHAR(150) NOT NULL', 'password_hash TEXT NOT NULL')

# `DATETIME` を `TIMESTAMP` に変換
sql = re.sub(r'\bDATETIME\b', 'TIMESTAMP', sql)

# マイクロ秒の削除（YYYY-MM-DD HH:MM:SS.ssssss -> YYYY-MM-DD HH:MM:SS）
sql = re.sub(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\.\d{6}", r"\1", sql)

# `user` テーブル名の修正（予約語と衝突しないように）
sql = re.sub(r'\bCREATE TABLE user\b', 'CREATE TABLE users', sql)
sql = re.sub(r'\bINSERT INTO user\b', 'INSERT INTO users', sql)
sql = re.sub(r'\bFOREIGN KEY\s*\(\s*user_id\s*\)\s*REFERENCES\s*user\b', r'FOREIGN KEY (user_id) REFERENCES users', sql)

# 変換後のSQLを保存
with open("postgresql_dump.sql", "w", encoding="utf-8") as f:
    f.write(sql)

print("変換が完了しました！ `postgresql_dump.sql` を使用してください。")
