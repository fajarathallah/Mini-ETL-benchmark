import requests
import csv
import os
import time
from dotenv import load_dotenv
import snowflake.connector
from snowflake_connection import get_snowflake_connection

load_dotenv()
POLYGON_API_KEY = os.getenv("POLYGON_API_KEY")
url = "https://api.massive.com/v3/reference/tickers"


# Extract tickers from Polygon API
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

            for ticker in data["results"]:
                tickers.append(ticker["ticker"])

    except KeyboardInterrupt:
        print("process interrupted by user")
        raise
    return tickers


# Load tickers to CSV
def save_tickers_to_csv(tickers, filename="tickers.csv"):
    unique_tickers = sorted(
        set(tickers)
    )  # Transfrom ke set untuk menghilangkan duplikat, lalu sorted untuk mengurutkan
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["ticker"])  # header
        for item in unique_tickers:
            writer.writerow([item])

    print(f"csv berhasil dibuat: {filename}")
    print(f"jumlah ticker unik: {len(unique_tickers)}")


# Load csv to Snowflake
def load_csv_to_snowflake(filename="tickers.csv"):
    conn = get_snowflake_connection()
    conn.autocommit(False)
    cursor = conn.cursor()

    try:
        # DEBUG: Cek kamu sedang di database/schema mana
        cursor.execute(
            "SELECT CURRENT_DATABASE(), CURRENT_SCHEMA(), CURRENT_WAREHOUSE()"
        )
        print("🔍 Koneksi ke:", cursor.fetchone())
        cursor.execute("TRUNCATE TABLE TICKERS_FROM_CSV")

        # Baca CSV
        with open(filename, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader)  # skip header
            data = [(row[0],) for row in reader]  # buat list of tuple

        # Insert semua row ke table
        insert_query = "INSERT INTO TICKERS_FROM_CSV (ticker) VALUES (%s)"
        cursor.executemany(insert_query, data)

        conn.commit()
        print(f"{len(data)} rows berhasil masuk ke Snowflake (direct insert)")
        print("CSV path:", os.path.abspath(filename))

    except Exception as e:
        print(f"Error loading CSV to Snowflake: {e}")
        conn.rollback()
        raise

    finally:
        cursor.close()
        conn.close()


def run_csv_pipeline():
    result = {}

    total_start = time.time()

    # API
    api_start = time.time()
    tickers = fetch_all_tickers(POLYGON_API_KEY)
    api_end = time.time()

    # CSV
    csv_start = time.time()
    save_tickers_to_csv(tickers)
    csv_end = time.time()

    # LOAD
    load_start = time.time()
    load_csv_to_snowflake("tickers.csv")
    load_end = time.time()

    total_end = time.time()

    result["rows"] = len(set(tickers))
    result["api_time"] = api_end - api_start
    result["csv_time"] = csv_end - csv_start
    result["load_time"] = load_end - load_start
    result["total_time"] = total_end - total_start

    return result


if __name__ == "__main__":
    result = run_csv_pipeline()
    print(result)
