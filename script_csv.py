import requests
import csv
import os
import time
from dotenv import load_dotenv

load_dotenv()
POLYGON_API_KEY = os.getenv("POLYGON_API_KEY")
url = f"https://api.massive.com/v3/reference/tickers"


# Extraxt tickers from Polygon API
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


def run_pipeline():
    print("memulai pengambilan data ticker...")
    tickers = fetch_all_tickers(POLYGON_API_KEY)
    save_tickers_to_csv(tickers)
    print("pipeline selesai.")


if __name__ == "__main__":
    run_pipeline()
