import time
import csv
import os
import matplotlib.pyplot as plt
from script_csv import run_csv_pipeline
from script_direct import run_direct_pipeline


RESULT_FILE = "benchmark_results.csv"


def save_results_to_csv(results):
    file_exists = os.path.exists(RESULT_FILE)

    with open(RESULT_FILE, mode="a", newline="") as f:
        writer = csv.writer(f)

        if not file_exists:
            writer.writerow([
                "method",
                "rows",
                "api_time",
                "csv_time",
                "load_time",
                "total_time"
            ])

        for r in results:
            writer.writerow([
                r["method"],
                r["rows"],
                r.get("api_time", 0),
                r.get("csv_time", 0),
                r.get("load_time", 0),
                r.get("total_time", 0)
            ])


def plot_results(results):
    methods = [r["method"] for r in results]
    total_times = [r["total_time_sec"] for r in results]
    insert_times = [r["insert_time_sec"] for r in results]

    plt.figure(figsize=(10, 6))

    x = range(len(methods))
    plt.bar(x, total_times, width=0.4, label="Total Time")
    plt.bar([i + 0.4 for i in x], insert_times, width=0.4, label="Insert Time")

    plt.xticks([i + 0.2 for i in x], methods)
    plt.ylabel("Time (seconds)")
    plt.title("ETL Pipeline Benchmark Comparison")
    plt.legend()

    plt.tight_layout()
    plt.savefig("benchmark_chart.png")
    plt.show()


def main():
    print("🚀 Running CSV Pipeline...")
    csv_result = run_csv_pipeline()
    csv_result["method"] = "CSV -> Snowflake"

    print("\n🚀 Running Direct Pipeline...")
    direct_result = run_direct_pipeline()
    direct_result["method"] = "Direct -> Snowflake"

    results = [csv_result, direct_result]

    print("\n📊 Benchmark Results:")
    for r in results:
        print(r)

    save_results_to_csv(results)
    plot_results(results)

    print("\n✅ Benchmark selesai. Hasil tersimpan di:")
    print("- benchmark_results.csv")
    print("- benchmark_chart.png")


if __name__ == "__main__":
    main()