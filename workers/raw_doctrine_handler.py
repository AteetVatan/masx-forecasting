"""Event handler for raw doctrine files."""
from pathlib import Path
from watchdog.events import FileSystemEventHandler
from core.config import Paths
from core.doctrine.metadata import DoctrineMetadata
#from core.doctrine.processor import DoctrineProcessor

RAW_DIR = "data/doctrines/raw"
METADATA_DIR = "data/doctrines/metadata"
CLEANED_DIR = "data/doctrines/cleaned"
CHUNK_DIR = "data/doctrines/chunks"

class RawDoctrineHandler(FileSystemEventHandler):
    def on_created(self, event):
        self.process(event)

    def on_modified(self, event):
        self.process(event)

    def process(self, event):
        if event.is_directory or not event.src_path.endswith((".txt", ".pdf", ".html")):
            return

        file_path = Path(event.src_path)
        filename = file_path.name
        slug = DoctrineMetadata.extract_slug(filename)

        print(f"⚡ Event for doctrine: {slug}")

        # Process only the matching slug group
        DoctrineMetadata(slug, [filename], Paths.RAW_DIR, METADATA_DIR).save()
        #DoctrineProcessor(slug, [filename], RAW_DIR, CLEANED_DIR, CHUNK_DIR).process()