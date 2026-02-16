import logging

from workers import RawDoctrineWatcherWorker

logger = logging.getLogger(__name__)

_watcher = RawDoctrineWatcherWorker()


def start_workers() -> None:
    logger.info("Starting workers")
    _watcher.start()


def stop_workers() -> None:
    logger.info("Stopping workers")
    _watcher.stop()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logger.info("Welcome to MASX AI")
