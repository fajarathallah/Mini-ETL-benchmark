
<div align="center">

# Mini-etl-benchmark

</div>

Benchmark ETL Pipeline. This uses massive.com API to extract data about stocks.
This study conduct to benchmark comparison perfomance and eficiency of each method which is:
1. Direct insert (API -> snowflake)
2. CSV -> snowflake (API -> CSV -> snowflake)

## 📑:  Folder Structure
```
mini-etl-benchmark/
│
├── src/
│   ├── pipelines/
│   │   ├── script_direct.py          # Direct API → Snowflake
│   │   └── script_csv.py             # API → CSV → Snowflake
│   │
│   ├── benchmark/
│   │   ├── benchmark.py              # Run benchmark & simpan metrik
│   │   └── benchmark_visualize.py    # Generate visualisasi dari hasil benchmark
│   │
│   └── utils/
│       └── snowflake_connection.py   # Snowflake connection helper
│
├── results/
│   ├── benchmark_chart.png           # Output visualisasi
│   └── benchmark_results.csv         # Output hasil benchmark
│
├── .env.example                      # Contoh environment config
├── requirements.txt                  # Python dependencies
├── README.md                         # Dokumentasi project
└── .gitignore                        # Ignore file sensitif
```
## ⚙️: Setup
1. Clone repository
```
git clone <repo-url>
cd mini-etl-benchmark
```
2. Install dependecies
```
uv pip install -r requirements.txt
```
3. Buat env sesuai dengan .env.example
```
# Langsung masukan nilai nya, tidak perlu tanda petik "  "

POLYGON_API_KEY=

account = 
user = 
password = 
role = 
warehouse = 
database = 
schema =
```
Pastikan database sudah tersedia dahulu si snowflake

## 🚀: Cara menjalankan
Di setiap blok kode, taruh blok kode di terminal / powershell untuk menjalankan
1. Direct Insert
```
python script_direct.py
```
- Data dari API masuk ke tabel tickers_direct

2. CSV -> snowflake
```
python script_csv.py
```
- Data dari API disimpan ke csv dahulu lalu diinsert ke tabel tickers_from_csv
3. Benchmark
```
python benchmark.py
```
- Mengukur performan pipeline
- Menyimpan metrik total_time, api_time, insert_time, load_time, rows





