import requests
import os
import time
import snowflake.connector
from snowflake_connection import get_snowflake_connection
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("POLYGON_API_KEY")
url = f"https://api.massive.com/v3/reference/tickers"


def fetch_all_tickers(api_key, sleep_seconds=2):
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

    except KeyboardInterrupt:
        print("process interrupted by user")
        raise

    return sorted(set(tickers))


def insert_to_snowflake(tickers):
    conn = get_snowflake_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("truncate table tickers_direct")
        insert_query = "INSERT INTO tickers_direct   (ticker) VALUES (%s)"
        data_to_insert = [(ticker,) for ticker in tickers]
        cursor.executemany(insert_query, data_to_insert)
        conn.commit()

        print(f"Inserted {len(tickers)} tickers into Snowflake.")

    finally:
        cursor.close()
        conn.close()


def run_direct_pipeline():
    result = {}

    total_start = time.time()

    # ===== API Time =======
    api_start = time.time()
    tickers = fetch_all_tickers(API_KEY)
    api_end = time.time()

    # ======= insert time =======
    insert_start = time.time()
    insert_to_snowflake(tickers)
    insert_end = time.time()

    total_end = time.time()

    result["rows"] = len(tickers)
    result["api_time"] = api_end - api_start
    result["insert_time"] = insert_end - insert_start
    result["total_time"] = total_end - total_start

    return result


if __name__ == "__main__":
    result = run_direct_pipeline()
    print(result)
