import os
from multiprocessing import Pool
from sqlalchemy import create_engine
from flask import Flask, jsonify, request
import HospitalScrapy 
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 建立 Flask 應用程式
app = Flask(__name__)

# 建立資料庫連接
def connect_to_db():
    db_type = os.getenv("DB_TYPE")
    db_username = os.getenv("DB_USERNAME")
    db_password = os.getenv("DB_PASSWORD")
    db_host = os.getenv("DB_HOST")
    db_name = os.getenv("DB_NAME")
    
    if db_type == "mysql":
        connection_string = f'mysql+pymysql://{db_username}:{db_password}@{db_host}/{db_name}'
    elif db_type == "postgresql":
        connection_string = f'postgresql+psycopg2://{db_username}:{db_password}@{db_host}/{db_name}'
    else:
        raise ValueError("不支援的資料庫類型，請選擇 'mysql' 或 'postgresql'")
    
    engine = create_engine(connection_string)
    return engine

# 將 DataFrame 儲存到資料庫
def save_to_db(df, table_name):
    engine = connect_to_db()
    df.to_sql(table_name, con=engine, if_exists='replace', index=False)

# 爬取所有醫院資料並儲存到資料庫
def scrape_and_save():
    hospital_scrapers = [
        ("ChimeiScraper", 10, "chimei_main"),
        ("ChimeiScraper", 13, "chimei_liuying"),
        ("ChimeiScraper", 14, "chimei_jiali"),
        ("KuoScraper", None, "kuo"),
        ("AnnanScraper", None, "annan"),
        ("TainanScraper", None, "tainan"),
        ("NCKUHScraper", None, "nckuh"),
        ("SinlauScraper", "Tainan", "sinlau_tainan"),
        ("SinlauScraper", "Madou", "sinlau_madou")
    ]
    
    with Pool(processes=6) as pool:
        results = pool.starmap(scrape_hospital_and_save, [(scraper[0], scraper[1], scraper[2]) for scraper in hospital_scrapers])
    
    return "所有資料已成功儲存到資料庫"

# 爬取每家醫院資料並儲存
def scrape_hospital_and_save(scraper_name, param, table_name):
    engine = connect_to_db()
    if scraper_name == "ChimeiScraper":
        df = HospitalScrapy.ChimeiScraper(param)
    elif scraper_name == "KuoScraper":
        df = HospitalScrapy.KuoScraper()
    elif scraper_name == "AnnanScraper":
        df = HospitalScrapy.AnnanScraper()
    elif scraper_name == "TainanScraper":
        df = HospitalScrapy.TainanScraper()
    elif scraper_name == "NCKUHScraper":
        df = HospitalScrapy.NCKUHScraper()
    elif scraper_name == "SinlauScraper":
        df = HospitalScrapy.SinlauScraper(param)
    
    if df is not None:
        save_to_db(df, table_name)

# 建立 HTTP 端點來觸發爬蟲
@app.route("/", methods=["GET"])
def start_crawler():
    try:
        message = scrape_and_save()
        return jsonify({"status": "success", "message": message}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
