from abc import ABC, abstractmethod

# core/workers/base.py
class BaseWorker(ABC):
    def __init__(self, name):
        self.name = name

    @abstractmethod
    def start(self):
        raise NotImplementedError

    @abstractmethod
    def stop(self):
        raise NotImplementedError

    def log(self, message):
        print(f"[{self.name}]: {message}")

    def status(self):
        return {"name": self.name, "running": True}
