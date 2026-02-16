from .base_worker import BaseWorker
from .raw_doctrine_handler import RawDoctrineHandler
from core.config import Paths
from watchdog.observers import Observer
import time


class RawDoctrineWatcherWorker(BaseWorker):
    def __init__(self) -> None:
        super().__init__(name="RawDoctrineWatcher")
        self.observer: Observer | None = None

    def start(self) -> None:
        self.log("Starting file watcher...")
        self.observer = Observer()
        self.observer.schedule(
            RawDoctrineHandler(),
            path=str(Paths.RAW_DIR),
            recursive=False,
        )
        self.observer.start()

        try:
            while True:
                time.sleep(5)
        except KeyboardInterrupt:
            self.stop()

    def stop(self) -> None:
        if self.observer:
            self.log("Stopping file watcher...")
            self.observer.stop()
            self.observer.join()
            self.observer = None
