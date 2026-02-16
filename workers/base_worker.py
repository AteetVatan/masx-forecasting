import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class BaseWorker(ABC):
    def __init__(self, *, name: str) -> None:
        self.name = name

    @abstractmethod
    def start(self) -> None: ...

    @abstractmethod
    def stop(self) -> None: ...

    def log(self, message: str) -> None:
        logger.info("%s: %s", self.name, message)

    def status(self) -> dict[str, str | bool]:
        return {"name": self.name, "running": True}
