import time
from script_csv import run_csv_pipeline
from script_direct import run_direct_pipeline


def percent_diff(a, b):
    if a == 0:
        return 0
    return round(((b - a) / a) * 100, 2)


def benchmark_pipelines():
    print("\n===== BENCHMARK START =====\n")

    # ===== CSV PIPELINE =====
    print("Running CSV Pipeline...")
    csv_result = run_csv_pipeline()

    print("\nRunning Direct Pipeline...")
    direct_result = run_direct_pipeline()

    print("\n===== BENCHMARK RESULT =====\n")

    print(f"{'Metric':<20} | {'CSV':<10} | {'Direct':<10} | Diff (%)")
    print("-" * 60)

    metrics = ["rows", "api_time_sec", "insert_time_sec", "total_time_sec"]

    for metric in metrics:
        csv_val = csv_result.get(metric, 0)
        direct_val = direct_result.get(metric, 0)

        diff = percent_diff(csv_val, direct_val)

        print(f"{metric:<20} | {csv_val:<10} | {direct_val:<10} | {diff}")

    print("\n===== ANALYSIS =====")

    if csv_result["total_time_sec"] < direct_result["total_time_sec"]:
        print("✅ CSV Pipeline lebih cepat.")
    elif csv_result["total_time_sec"] > direct_result["total_time_sec"]:
        print("✅ Direct Pipeline lebih cepat.")
    else:
        print("⚖️ Keduanya sama cepat.")

    print("\n===== BENCHMARK END =====\n")


if __name__ == "__main__":
    benchmark_pipelines()
    