import requests 
import os
import time
import snowflake.connector
from snowflake.connector import get_snowflake_connection

load_dotenv()
API_KEY = os.getenv("POLYGON_API_KEY")
url = f'https://api.massive.com/v3/reference/tickers'

def fetc_all_tickers(api_key, sleep_seconds=2):
    params = {
        "market": "stocks",
        "active": "true",
        "order": "asc",
        "limit": 100,
        "sort": "ticker",
        "apiKey": api_key,
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()

    tickers = []
    for item in data["results"]:
        tickers.append(item["ticker"])

    try:
        while "next_url" in data:
            time.sleep(sleep_seconds)
            print("requesting next page", data["next_url"])
            response = requests.get(data["next_url"], params={"apiKey": api_key})
            if response.status_code == 429:
                print("Rate limit kena, tidur 60 detik...")
                time.sleep(60)
                continue
            response.raise_for_status()
            data = response.json()

            for item in data["results"]:
                tickers.append(item["ticker"])

        return sorted(set(tickers))
    
def insert_to_snowflake(tickers):
    conn = get_snowflake_connection()
    cursor = conn.cursor()

    try:
        insert_query = "INSERT INTO tickers (ticker) VALUES (%s)"
        data_to_insert = [(ticker,) for ticker in tickers]
        cursor.executemany(insert_query, data_to_insert)
        conn.commit()

        print(f"Inserted {len(tickers)} tickers into Snowflake.")
    
    finally:
        cursor.close()
        conn.close()

def run_pipeline():
    print("starting pipeline...")
    start_time = time.time()
    tickers = fetc_all_tickers(API_KEY)
    insert_to_snowflake(tickers)
    end_time = time.time()
    print(f"pipeline completed in {end_time - start_time:.2f} seconds")
          
if __name__ == "__main__":
    run_pipeline()
  