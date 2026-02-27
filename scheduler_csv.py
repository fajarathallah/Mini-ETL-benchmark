import schedule
import time
from script_csv import run_pipeline

from datetime import datetime

def basic_job():
    print(f"Basic job executed at {datetime.now()}")

#run every minute
def main():
    schedule.every().minutes.do(basic_job)
    schedule.every().minutes.do(run_pipeline)

    try:
        print("Scheduler started. Press Ctrl+C to exit.")
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        print("Scheduler stopped by user.")
        raise

if __name__ == "__main__":
    main()

