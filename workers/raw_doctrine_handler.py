from pathlib import Path
from watchdog.events import FileSystemEventHandler
from core.config import Paths
from core.doctrine.metadata import DoctrineMetadata


SUPPORTED_EXTENSIONS = (".txt", ".pdf", ".html")


class RawDoctrineHandler(FileSystemEventHandler):
    def on_created(self, event) -> None:
        self._process(event)

    def on_modified(self, event) -> None:
        self._process(event)

    def _process(self, event) -> None:
        if event.is_directory or not event.src_path.endswith(SUPPORTED_EXTENSIONS):
            return

        file_path = Path(event.src_path)
        slug = DoctrineMetadata.extract_slug(file_path.name)

        DoctrineMetadata(slug, [file_path.name], Paths.RAW_DIR).save()
