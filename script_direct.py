import requests
import os
import time
import snowflake.connector
from snowflake_connection import get_snowflake_connection
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("POLYGON_API_KEY")
BASE_URL = "https://api.massive.com/v3/reference/tickers"

# 🔥 BATAS UNTUK BENCHMARK
MAX_TICKERS = 200


# ===== Safe request dengan retry + timeout =====
def safe_request(url, params=None, sleep_seconds=60, max_retries=5):
    retries = 0
    while retries < max_retries:
        try:
            response = requests.get(url, params=params, timeout=30)

            if response.status_code == 429:
                print(f"Rate limit kena, tidur {sleep_seconds} detik...")
                time.sleep(sleep_seconds)
                retries += 1
                continue

            response.raise_for_status()
            return response.json()

        except requests.exceptions.Timeout:
            print("Request timeout, retrying...")
            retries += 1
            time.sleep(5)

        except requests.exceptions.RequestException as e:
            print(f"HTTP error: {e}")
            raise

    raise Exception("Max retries reached")


# ===== Fetch tickers (DIBATASI 200) =====
def fetch_all_tickers(api_key, sleep_seconds=2):
    params = {
        "market": "stocks",
        "active": "true",
        "order": "asc",
        "limit": 100,
        "sort": "ticker",
        "apiKey": api_key,
    }

    tickers = []

    data = safe_request(BASE_URL, params=params)

    for item in data.get("results", []):
        tickers.append(item["ticker"])

        # 🔥 STOP kalau sudah 200
        if len(tickers) >= MAX_TICKERS:
            print(f"Reached MAX_TICKERS ({MAX_TICKERS})")
            return sorted(set(tickers[:MAX_TICKERS]))

    try:
        while "next_url" in data and data["next_url"]:
            time.sleep(sleep_seconds)
            print("Requesting next page:", data["next_url"])

            data = safe_request(data["next_url"], params={"apiKey": api_key})

            for item in data.get("results", []):
                tickers.append(item["ticker"])

                # 🔥 STOP kalau sudah 200
                if len(tickers) >= MAX_TICKERS:
                    print(f"Reached MAX_TICKERS ({MAX_TICKERS})")
                    return sorted(set(tickers[:MAX_TICKERS]))

    except KeyboardInterrupt:
        print("Process interrupted by user")
        raise

    return sorted(set(tickers))


# ===== Insert ke Snowflake =====
def insert_to_snowflake(tickers):
    conn = get_snowflake_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("TRUNCATE TABLE tickers_direct")
        print(f"Inserting {len(tickers)} tickers...")

        insert_query = "INSERT INTO tickers_direct (ticker) VALUES (%s)"
        data_to_insert = [(t,) for t in tickers]

        cursor.executemany(insert_query, data_to_insert)
        conn.commit()
        print("Insert selesai.")

    except Exception as e:
        print("Error inserting data:", e)
        conn.rollback()
        raise

    finally:
        cursor.close()
        conn.close()


# ===== Main pipeline =====
def run_direct_pipeline():
    result = {}
    total_start = time.time()

    # ===== API =====
    try:
        api_start = time.time()
        tickers = fetch_all_tickers(API_KEY)
        api_end = time.time()
    except Exception as e:
        print("Error fetching tickers:", e)
        tickers = []
        api_end = time.time()

    # ===== INSERT =====
    try:
        insert_start = time.time()
        if tickers:
            insert_to_snowflake(tickers)
        insert_end = time.time()
    except Exception as e:
        print("Error inserting to Snowflake:", e)
        insert_end = time.time()

    total_end = time.time()

    # ===== Return dict =====
    result["rows"] = len(tickers)
    result["api_time_sec"] = round(api_end - api_start, 2)
    result["insert_time_sec"] = round(insert_end - insert_start, 2)
    result["total_time_sec"] = round(total_end - total_start, 2)

    return result