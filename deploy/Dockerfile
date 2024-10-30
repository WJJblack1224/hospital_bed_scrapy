FROM python:3.11

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

# 安裝Chromium和Chromedriver依賴
RUN apt-get update && \
    apt-get install -y chromium chromium-driver && \
    apt-get install -y libnss3 libgconf-2-4 libxss1 libappindicator3-1 fonts-liberation && \
    rm -rf /var/lib/apt/lists/*

# 設定環境變數讓Selenium可以找到Chromedriver
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_BIN=/usr/bin/chromedriver

# 設定PORT環境變數，Cloud Run預設使用8080埠
ENV PORT=8080

# 啟動應用程式
CMD ["python", "main.py"]
