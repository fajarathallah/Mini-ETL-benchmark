import time
from script_direct import run_direct_pipeline


def run_benchmark(runs=3):
    print("\n=== Direct Insert Benchmark ===\n")

    all_results = []

    for i in range(runs):
        print(f"Run {i+1}...")
        result = run_direct_pipeline()
        throughput = result["rows"] / result["total_time"]

        print(f"Rows: {result['rows']}")
        print(f"API Time:{result['api_time']:.2f} seconds")
        print(f"Insert Time: {result['insert_time']:.2f} seconds")
        print(f"Total Time: {result['total_time']:.2f} seconds")
        print(f"Throughput: {throughput:.2f} rows/second\n")

        all_results.append(result)

        time.sleep(5)  # Sleep between runs to reduce rate limit issues

    return all_results


if __name__ == "__main__":
    run_benchmark()
