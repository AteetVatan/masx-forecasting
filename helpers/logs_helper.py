"""The LogsHelper Module."""

import logging


class LogsHelper:
    """Helper class for logging with all logging levels."""

    # Configure logging format
    logging.basicConfig(
        format="%(asctime)s - %(levelname)s - %(message)s", level=logging.DEBUG
    )

    @staticmethod
    def debug(msg):
        """Log a debug message."""
        logging.debug(msg)

    @staticmethod
    def info(msg):
        """Log an info message."""
        logging.info(msg)

    @staticmethod
    def warning(msg):
        """Log a warning message."""
        logging.warning(msg)

    @staticmethod
    def error(msg, args=None):
        """Log an error message."""
        args = {} if not args else args
        logging.error(msg, args)

    @staticmethod
    def critical(msg):
        """Log a critical message."""
        logging.critical(msg)

    @staticmethod
    def exception(msg):
        """Log an exception message."""
        logging.exception(msg)

    @staticmethod
    def set_level(level):
        """Set the logging level dynamically."""
        logging.getLogger().setLevel(level)


# # Example usage
# if __name__ == "__main__":
#     LogsHelper.debug("This is a debug message.")
#     LogsHelper.info("This is an info message.")
#     LogsHelper.warning("This is a warning message.")
#     LogsHelper.error("This is an error message.")
#     LogsHelper.critical("This is a critical message.")
