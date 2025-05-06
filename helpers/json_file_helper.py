"""Module to create, read and write JSON data"""

import json
import os

from .logs_helper import LogsHelper


class JsonFileHelper:
    """Helper Class responsible for JSON file operations."""

    @staticmethod
    def read_data(file_path):
        """Method to read JSON data."""
        d = None
        try:
            with open(file_path, mode="r", encoding="utf-8") as data:
                d = json.load(data)
        except FileNotFoundError as f:
            LogsHelper.error(f)
            raise f
        except IOError as e:
            LogsHelper.error("I/O error occurred: ", os.strerror(e.errno))
            raise e
        return d

    @staticmethod
    def write_data(data, file_path):
        """Method to write JSON data to file"""
        try:
            if data is None:
                data = {}
            with open(file_path, mode="w", encoding="utf-8") as file:
                json.dump(data, file, indent=4)
        except FileNotFoundError as f:
            LogsHelper.error(f)
        except IOError as e:
            LogsHelper.error("I/O error occurred: ", os.strerror(e.errno))
