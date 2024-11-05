import os
from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2
from dotenv import load_dotenv

app = Flask(__name__)
CORS(app)

# 載入環境變數
load_dotenv()

# 使用 PostgreSQL 資料庫連線
def connect_db():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USERNAME"),
        password=os.getenv("DB_PASSWORD")
    )

# 抓取所有表的資料
@app.route("/", methods=["GET"])
def fetch_data():
    try:
        conn = connect_db()
        cursor = conn.cursor()

        tables = ["chimei_main", "chimei_liuying", "chimei_jiali", "kuo",
                  "annan", "tainan", "nckuh", "sinlau_tainan", "sinlau_madou"]
        data = {}

        for table in tables:
            cursor.execute(f"SELECT * FROM {table}")
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            data[table] = [dict(zip(columns, row)) for row in rows]

        cursor.close()
        conn.close()

        return jsonify(data), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 抓取單一表的資料
@app.route("/<table_name>", methods=["GET"])
def fetch_single_table_data(table_name):
    try:
        tables = ["chimei_main", "chimei_liuying", "chimei_jiali", "kuo",
                  "annan", "tainan", "nckuh", "sinlau_tainan", "sinlau_madou"]
        
        if table_name not in tables:
            return jsonify({"error": "Table not found"}), 404

        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        data = [dict(zip(columns, row)) for row in rows]

        cursor.close()
        conn.close()

        return jsonify(data), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
