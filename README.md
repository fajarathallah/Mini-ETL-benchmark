
< div align = "center">

# mini-etl-benchmark
Benchmark ETL Pipeline. This uses massive.com API to extract data about stocks.
This study conduct to benchmark comparison perfomance and eficiency of each method which is:
1. Direct insert (API -> snowflake)
2. CSV -> snowflake (API -> CSV -> snowflake)

</div>

mini-etl-benchmark/
│
|--- script_direct.py          # Pipeline langsung ke Snowflake
|--- script_csv.py             # Pipeline melalui CSV
|--- benchmark.py              # Benchmark pipeline & simpan hasil metrik
|--- benchmark_visualize.py    # Menampilkan visualisasi                            
|--- snowflake_connection.py   # Fungsi koneksi Snowflake
|--- .env.example              # API keys & Snowflake config example
|--- README.md            
