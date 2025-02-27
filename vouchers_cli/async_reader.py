import csv
from io import StringIO
from logging import Logger
from pathlib import Path
from typing import Iterable, Protocol

import aiofiles


class FileReader(Protocol):
    """
    Protocol for asynchronous CSV file readers.
    Defines the expected method signature for reading CSV files.
    """

    async def read_csv(self, file_path: Path) -> Iterable[list[str]]:
        """
        Asynchronously read a CSV file and return its contents as
        an iterable of string lists.

        :param file_path: The path to the CSV file.
        :return: An iterable containing lists of strings, representing the CSV rows.
        """
        ...


class AsyncCSVReader:
    """
    Asynchronous CSV file reader that reads and parses CSV files.
    """

    def __init__(self, logger: Logger):
        """
        Initialize the CSV reader with a logger.

        :param logger: Logger instance for logging messages.
        """
        self._logger = logger

    async def read_csv(self, file_path: Path) -> Iterable[list[str]]:
        """
        Read a CSV file asynchronously and return its contents as
        an iterable of string lists.

        :param file_path: The path to the CSV file.
        :return: An iterable containing lists of strings,
        representing the CSV rows.
        """
        self._logger.debug(f"Reading from {file_path}")
        try:
            async with aiofiles.open(file_path, mode="r", encoding="utf-8") as file:
                content = await file.read()
                reader = csv.reader(StringIO(content))
                next(reader, None)  # Skip header row
                return list(reader)
        except FileNotFoundError:
            self._logger.error(f"File not found: {file_path}")
            return []
