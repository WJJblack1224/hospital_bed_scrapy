import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd

def align_format(df,empty_column=True):
  df["總床數"] = df["總床數"].astype(int)
  df["佔床數"] = df["佔床數"].astype(int)
  if empty_column:
    df["空床數"] = df["總床數"] - df["佔床數"]
  else:
    df["空床數"] = df["空床數"].astype(int)
  df["佔床率"] = round(df["佔床數"]/df["總床數"],4)
  df['佔床率'] = df['佔床率'].apply(lambda x: '{:.2%}'.format(x))
  return df

def ChimeiScraper(number):
    url = "https://www.chimei.org.tw/%E4%BD%94%E5%BA%8A%E7%8E%87%E6%9F%A5%E8%A9%A2/%E4%BD%94%E5%BA%8A%E7%8E%87%E6%9F%A5%E8%A9%A2.aspx?ihospital=10&ffloor="
    form_data = {'RBL院區': str(number), 'Btn查詢': '查詢'}
    response = requests.post(url, data=form_data)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find("table", {"id": "DG1"})
        data = []
        rows = table.find_all("tr")
        for row in rows[1:]:
            cells = row.find_all("td")
            row_data = [cell.get_text(strip=True) for cell in cells]
            data.append(row_data)
        df = pd.DataFrame(data, columns=["病床類別", "總床數", "佔床數", "空床數", "佔床率"])
        df = align_format(df,False)
        return df
    else:
        print(f'請求失敗 (奇美醫院, 區域 {number}):', response.status_code)
        return None
    
def KuoScraper():
    url = "https://www.kgh.com.tw/InstantMessage/BedInfoAPI"
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find("table")
        data = []
        rows = table.find_all("tr")
        for row in rows[1:]:
            cells = row.find_all("td")
            row_data = [cell.get_text(strip=True) for cell in cells]
            data.append(row_data)
        df = pd.DataFrame(data, columns=["病床類別", "總床數", "佔床數", "空床數", "佔床率"])
        df = df.iloc[1:, :].reset_index(drop=True)
        df = align_format(df,True)
        return df
    else:
        print('請求失敗 (郭綜合醫院):', response.status_code)

def AnnanScraper():
    url = "https://www.tmanh.org.tw/Announce/CurrentBedAvailability"
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find("table")
        data = []
        rows = table.find_all("tr")
        for row in rows[1:]:
            cells = row.find_all("td")
            row_data = [cell.get_text(strip=True) for cell in cells]
            data.append(row_data)
        df = pd.DataFrame(data, columns=["病床類別", "總床數", "佔床數", "空床數"])
        df = df.iloc[1:, :].reset_index(drop=True)
        df = df.iloc[:9,:]
        df = align_format(df,False)
        return df
    else:
        print('請求失敗 (安南醫院):', response.status_code)

def TainanScraper():
    url = "https://www.tmh.org.tw/tmh2016/ImpBD.aspx?Kind=2"
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find("table", {"id": "ctl00_ContentPlaceHolder1_GV_Bed"})
        data = []
        rows = table.find_all("tr")
        for row in rows[1:]:
            cells = row.find_all("td")
            row_data = [cell.get_text(strip=True) for cell in cells]
            data.append(row_data)
        df = pd.DataFrame(data, columns=["病床類別", "總床數", "佔床數", "空床數", "佔床率"])
        df = align_format(df,False)
        return df
    else:
        print('請求失敗 (台南醫院):', response.status_code)

def NCKUHScraper():
  url = "https://web.hosp.ncku.edu.tw/nckm/Bedstatus/BedStatus.aspx"
  response = requests.get(url)
  if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find("table", {"id": "GV_EmgInsure"})
    data = []
    rows = table.find_all("tr")
    for row in rows[1:]:
      cells = row.find_all("td")
      row_data = [cell.get_text(strip=True) for cell in cells]
      data.append(row_data)
    df = pd.DataFrame(data, columns=["病床類別", "總床數", "佔床數", "空床數"])
    df = align_format(df,True)
    return df
  else:
    print('請求失敗 (成大醫院):', response.status_code)

def driver_operate(driver,url):
    driver.get(url)
    driver.implicitly_wait(10)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find('table')
    df = pd.read_html(str(table))[0]
    return df

def clean_df(df,rows_to_drop):
    df = df.drop(rows_to_drop)
    df.iloc[0] = df.iloc[0].shift(-1).fillna(method='ffill')
    df = df.iloc[:, :-1]
    df.reset_index(drop=True, inplace=True)
    df = df[1:]
    df = df.drop(df.columns[-1], axis=1)
    df.columns = ["病床類別", "總床數", "佔床數", "空床數", "佔床率"]
    return df
    

def SinlauScraper(area):
    chrome_options = Options()
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36"
    chrome_options.add_argument(f'user-agent={user_agent}')
    driver = webdriver.Chrome(options=chrome_options)
    driver.maximize_window()
    try:
        if area == "Tainan":
            url = "http://59.125.233.216/sinlau/pgm/imbed/IMBED1.asp"
            df = driver_operate(driver, url)
            rows_to_drop = [0, 1, 3, 7, 9, 17, 18]
        elif area == "Madou":
            url = "http://59.125.233.216/sinlau/pgm/imbed/IMBED1.asp?SLArea=SL201"
            df = driver_operate(driver, url)
            rows_to_drop = [0, 1, 3, 7, 12, 13]
        else:
            return None
    finally:
        driver.quit()
    df = clean_df(df,rows_to_drop)
    df = align_format(df,False)
    return df

