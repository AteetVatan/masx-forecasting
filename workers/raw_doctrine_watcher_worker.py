# workers/raw_doctrine_handler.py
from core.workers.base_worker import BaseWorker
from core.handlers.raw_doctrine_handler import RawDoctrineHandler
from pathlib import Path
from watchdog.observers import Observer
import time

RAW_DIR = "data/doctrines/raw"
METADATA_DIR = "data/doctrines/metadata"
CLEANED_DIR = "data/doctrines/cleaned"
CHUNK_DIR = "data/doctrines/chunks"


class RawDoctrineWatcherWorker(BaseWorker):
    def __init__(self):
        super().__init__(name="RawDoctrineWatcher")
        self.observer = None

    def start(self):
        self.log("👀 Starting file watcher...")
        path = Path(RAW_DIR)
        self.observer = Observer()
        self.observer.schedule(RawDoctrineHandler(), path=str(path), recursive=False)
        self.observer.start()

        try:
            while True:
                time.sleep(5)
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        if self.observer:
            self.log("🛑 Stopping file watcher...")
            self.observer.stop()
            self.observer.join()
            self.observer = None
