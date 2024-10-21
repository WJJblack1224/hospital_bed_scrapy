import os
from multiprocessing import Pool
from sqlalchemy import create_engine
import HospitalScrapy 

# 建立資料庫連接
def connect_to_db():
    db_username = os.getenv("DB_USERNAME")
    db_password = os.getenv("DB_PASSWORD")
    db_host = os.getenv("DB_HOST")
    db_name = os.getenv("DB_NAME")
    
    # 使用 sqlalchemy 建立資料庫連接
    connection_string = f'mysql+pymysql://{db_username}:{db_password}@{db_host}/{db_name}'
    engine = create_engine(connection_string)
    
    return engine

# 將 DataFrame 儲存到資料庫
def save_to_db(df, table_name):
    # 每次儲存時都建立一個新的資料庫連接
    engine = connect_to_db()
    df.to_sql(table_name, con=engine, if_exists='replace', index=False)

# 爬取所有醫院資料並儲存到資料庫
def scrape_and_save():
    # 建立各醫院爬取的任務
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
    
    # 利用多處理進行並行爬取與儲存
    with Pool(processes=6) as pool:
        results = pool.starmap(scrape_hospital_and_save, [(scraper[0], scraper[1], scraper[2]) for scraper in hospital_scrapers])
    
    print("所有資料已成功儲存到資料庫")

# 爬取每家醫院資料並儲存
def scrape_hospital_and_save(scraper_name, param, table_name):
    # 每個進程內部建立資料庫連接
    engine = connect_to_db()
    
    # 根據不同的爬取器名稱選擇對應的爬取器
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
    
    # 檢查資料框是否有資料
    if df is not None:
        save_to_db(df, table_name)

if __name__ == "__main__":
    # 爬取並儲存資料
    scrape_and_save()
