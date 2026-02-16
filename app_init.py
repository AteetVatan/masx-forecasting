import logging

from dotenv import load_dotenv

from core.config.log import setup_logging
from processors.raw_process import RawProcess

logger = logging.getLogger(__name__)


def main() -> None:
    load_dotenv()
    setup_logging()
    logger.info("Initializing MASX AI")
    RawProcess.run_all()


if __name__ == "__main__":
    main()
