import logging

from core.doctrine.metadata.doctrine_metadata import DoctrineMetadata
from core.doctrine.processor.doctrine_processor import DoctrineProcessor

logger = logging.getLogger(__name__)


class RawProcess:
    @staticmethod
    def run_all() -> None:
        logger.info("Starting raw doctrine processing")
        DoctrineMetadata.bulk_generate()
        DoctrineProcessor.batch_process()
        logger.info("Raw doctrine processing complete")
