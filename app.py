"""Welcome to MASX AI"""

from workers import raw_doctrine_watcher


def start_workers():
    print("Starting workers")
    raw_doctrine_watcher.start()


def stop_workers():
    print("Stopping workers")
    raw_doctrine_watcher.stop()


if __name__ == "__main__":
    print("Welcome to MASX AI")
