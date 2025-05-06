from core.doctrine.metadata import DoctrineMetadata
from core.doctrine.processor import DoctrineProcessor
from core.config import Paths

# RAW_DIR = "data/doctrines/raw"
# METADATA_DIR = "data/doctrines/metadata"
# CLEANED_DIR = "data/doctrines/cleaned"
# CHUNK_DIR = "data/doctrines/chunks"


class RawProcess:
    @staticmethod
    def run_all():
        print("📦 Running batch doctrine processing...")
        DoctrineMetadata.bulk_generate(Paths.RAW_DIR, Paths.METADATA_DIR)
        DoctrineProcessor.batch_process(
            Paths.RAW_DIR, Paths.CLEANED_DIR, Paths.CHUNK_DIR
        )
