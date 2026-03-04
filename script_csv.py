import requests
import os
import time
import csv
import snowflake.connector
from snowflake_connection import get_snowflake_connection
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("POLYGON_API_KEY")
BASE_URL = "https://api.massive.com/v3/reference/tickers"

# 🔥 BATAS UNTUK BENCHMARK
MAX_TICKERS = 200
CSV_FILE = "tickers.csv"


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
    url = BASE_URL

    while url and len(tickers) < MAX_TICKERS:
        data = safe_request(url, params=params)

        for item in data.get("results", []):
            tickers.append(item["ticker"])

            if len(tickers) >= MAX_TICKERS:
                break

        url = data.get("next_url")
        params = {"apiKey": api_key}
        time.sleep(sleep_seconds)

    print(f"Total tickers fetched: {len(tickers)}")
    return sorted(set(tickers))


# ===== Save ke CSV =====
def save_to_csv(tickers):
    with open(CSV_FILE, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["ticker"])
        for t in tickers:
            writer.writerow([t])

    print("CSV berhasil dibuat.")


# ===== Insert dari CSV ke Snowflake =====
def insert_csv_to_snowflake():
    conn = get_snowflake_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("TRUNCATE TABLE tickers_from_csv")

        insert_query = "INSERT INTO tickers_from_csv (ticker) VALUES (%s)"

        with open(CSV_FILE, mode="r") as file:
            reader = csv.DictReader(file)
            data_to_insert = [(row["ticker"],) for row in reader]

        print(f"Inserting {len(data_to_insert)} tickers...")
        cursor.executemany(insert_query, data_to_insert)
        conn.commit()

        print("Insert selesai.")

    except Exception as e:
        print("Error inserting CSV data:", e)
        conn.rollback()
        raise

    finally:
        cursor.close()
        conn.close()


# ===== Main pipeline =====
def run_csv_pipeline():
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

    # ===== SAVE CSV =====
    csv_start = time.time()
    if tickers:
        save_to_csv(tickers)
    csv_end = time.time()

    # ===== INSERT =====
    insert_start = time.time()
    if tickers:
        insert_csv_to_snowflake()
    insert_end = time.time()

    total_end = time.time()

    result["rows"] = len(tickers)
    result["api_time_sec"] = round(api_end - api_start, 2)
    result["insert_time_sec"] = round(insert_end - insert_start, 2)
    result["total_time_sec"] = round(total_end - total_start, 2)

    return result
