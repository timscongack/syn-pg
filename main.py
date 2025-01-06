import signal
import sys
from src import Scheduler

def signal_handler(sig, frame):
    print("\nStopping the scheduler...")
    scheduler.stop()
    print("Scheduler stopped successfully.")
    sys.exit(0)

if __name__ == "__main__":
    scheduler = Scheduler()
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    try:
        print("Starting the scheduler...")
        scheduler.start()
        print("Scheduler is running. Press Ctrl+C to stop.")
        while True:
            pass
    except Exception as e:
        print(f"An error occurred: {e}")
        scheduler.stop()