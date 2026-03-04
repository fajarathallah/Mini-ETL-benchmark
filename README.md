# mini-etl-benchmark
Benchmark ETL Pipeline. This uses massive.com API to extract data about stocks.
This study conduct to benchmark comparison perfomance and eficiency of each method which is Direct insert (API -> snowflake) and CSV -> snowflake (API -> CSV -> snowflake)

mini-etl-benchmark/
│
├─ script_direct.py          # Pipeline langsung ke Snowflake
├─ script_csv.py             # Pipeline melalui CSV
├─ benchmark.py              # Benchmark pipeline & simpan hasil metrik
├─ snowflake_connection.py   # Fungsi koneksi Snowflake
├─ .env                      # API keys & Snowflake config
├─ tickers.csv               # Hasil CSV (opsional)
└─ README.md