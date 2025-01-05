from syn_pg import Scheduler

if __name__ == "__main__":
    scheduler = Scheduler()
    try:
        print("Starting the scheduler...")
        scheduler.start()
        input("Press Ctrl+C to stop the scheduler.\n")
    except (KeyboardInterrupt, SystemExit):
        print("\nStopping the scheduler...")
        scheduler.stop()
        print("Scheduler stopped.")