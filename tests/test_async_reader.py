import logging
import os
from pathlib import Path

from vouchers_cli.async_reader import AsyncCSVReader


async def test_read_csv_success(
    mock_logger: logging.Logger, csv_file_path: str
) -> None:
    """
    Test that the read_csv method successfully reads and parses a real CSV file.
    """

    # Create an instance of AsyncCSVReader with the mock logger
    reader = AsyncCSVReader(mock_logger)

    # Test reading the CSV file
    result = await reader.read_csv(Path(csv_file_path))

    # Assert that the result matches the expected parsed data
    expected_data = [["123", "456"], ["789", "101"]]
    assert result == expected_data


async def test_read_csv_file_not_found(mock_logger: logging.Logger) -> None:
    """
    Test that the read_csv method handles FileNotFoundError correctly.
    """

    # Create an instance of AsyncCSVReader with the mock logger
    reader = AsyncCSVReader(mock_logger)

    # Simulate FileNotFoundError by using a non-existent path
    non_existent_file = Path("data/non_existent_file.csv")

    # Call the read_csv method
    result = await reader.read_csv(non_existent_file)

    # Assert that the result is an empty list since the file was not found
    assert result == []


async def test_read_csv_empty_file(mock_logger: logging.Logger) -> None:
    """
    Test that the read_csv method correctly handles an empty CSV file.
    """

    # Create a new empty CSV file for the test
    empty_csv_path = "data/empty.csv"
    empty_content = ""
    with open(empty_csv_path, "w", encoding="utf-8") as f:
        f.write(empty_content)

    # Create an instance of AsyncCSVReader with the mock logger
    reader = AsyncCSVReader(mock_logger)

    # Test reading the empty CSV file
    result = await reader.read_csv(Path(empty_csv_path))

    # Assert that the result is an empty list
    assert result == []

    # Clean up the empty file after the test
    os.remove(empty_csv_path)
