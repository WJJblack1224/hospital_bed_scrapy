import os
from flask import Flask, jsonify, request
import psycopg2
from dotenv import load_dotenv

app = Flask(__name__)

#載入環境變數
load_dotenv()

# 使用 PostgreSQL 資料庫連線
def connect_db():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USERNAME"),
        password=os.getenv("DB_PASSWORD")
    )

@app.route("/", methods=["GET"])
def fetch_data():
    try:
        conn = connect_db()
        cursor = conn.cursor()

        # 指定要抓取的資料表
        tables = ["chimei_main", "chimei_liuying", "chimei_jiali","kuo",
                  "annan","tainan","nckuh","sinlau_tainan","sinlau_madou"]
        data = {}

        for table in tables:
            cursor.execute(f"SELECT * FROM {table}")
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            data[table] = [dict(zip(columns, row)) for row in rows]

        cursor.close()
        conn.close()

        # 將資料轉成 JSON 格式返回
        return jsonify(data), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
