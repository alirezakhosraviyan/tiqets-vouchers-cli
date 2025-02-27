import logging
import os
from logging import Logger
from pathlib import Path
from typing import Generator
from unittest.mock import AsyncMock

import pytest

from vouchers_cli.async_reader import AsyncCSVReader, FileReader
from vouchers_cli.async_writer import FileWriter, STDOutWriter
from vouchers_cli.extractor import VouchersExtractor
from vouchers_cli.repository import Repository
from vouchers_cli.schemas import ExtractorConfig, OutputSchema, VoucherSchema
from vouchers_cli.storage import OrderStorage


@pytest.fixture
def mock_logger() -> logging.Logger:
    """Provides a test logger."""
    logger = logging.getLogger("test_logger")
    logger.setLevel(logging.DEBUG)
    return logger


@pytest.fixture
def csv_file_path() -> str:
    """Returns the path to the real CSV file."""
    return "data/test-orders.csv"


@pytest.fixture(autouse=True)
def create_test_csv(csv_file_path: str) -> Generator[None]:
    """Creates a test CSV file before tests and removes it after."""
    os.makedirs(os.path.dirname(csv_file_path), exist_ok=True)
    content = "order_id,customer_id\n123,456\n789,101\n"

    with open(csv_file_path, "w", encoding="utf-8") as f:
        f.write(content)

    yield  # Run the tests

    os.remove(csv_file_path)  # Clean up after tests


@pytest.fixture(autouse=True)
def create_test_txt() -> Generator[None]:
    """Creates a test TXT file before tests and removes it after."""
    txt_file_path = "data/orders.txt"
    os.makedirs(os.path.dirname(txt_file_path), exist_ok=True)

    with open(txt_file_path, "w", encoding="utf-8") as f:
        f.write("")

    yield  # Run the tests

    os.remove(txt_file_path)  # Clean up after tests


@pytest.fixture
def mock_repository() -> AsyncMock:
    """
    Fixture for mock repository.
    """
    mock_repo = AsyncMock(Repository)
    mock_repo.get_vouchers.return_value = {
        (1, 1): ["barcode1", "barcode2"],
        (2, 2): ["barcode3"],
    }
    mock_repo.get_top_customers.return_value = [(1, 3), (2, 1)]
    mock_repo.get_unused_barcodes.return_value = {"barcode4", "barcode5"}
    return mock_repo


@pytest.fixture
def mock_writers() -> list[AsyncMock]:
    """
    Fixture for mock writers.
    """
    stdout_writer = AsyncMock(STDOutWriter)
    file_writer = AsyncMock(FileWriter)
    return [stdout_writer, file_writer]


@pytest.fixture
def extractor(
    mock_logger: logging.Logger,
    mock_repository: AsyncMock,
    mock_writers: list[AsyncMock],
) -> VouchersExtractor:
    """
    Fixture to create an instance of VouchersExtractor.
    """
    config = ExtractorConfig(
        orders_file_path=Path("data/orders.csv"),
        barcodes_file_path=Path("data/barcodes.csv"),
        output_dir=Path("output"),
    )
    return VouchersExtractor.create(config, mock_logger)


@pytest.fixture
def output_schema() -> OutputSchema:
    """Creates a mock OutputSchema."""
    vouchers = [
        VoucherSchema(customer_id=1, order_id=123, barcodes=["barcode1", "barcode2"]),
        VoucherSchema(customer_id=2, order_id=456, barcodes=["barcode3"]),
    ]
    return OutputSchema(
        top_customers=[(1, 500), (2, 300)],
        unused_barcodes={"barcode4", "barcode5"},
        vouchers=vouchers,
    )


@pytest.fixture
def mock_storage(mock_logger: Logger) -> OrderStorage:
    """Provides a fresh instance of OrderStorage."""
    return OrderStorage(mock_logger)


@pytest.fixture
def mock_reader(mock_logger: Logger) -> AsyncCSVReader:
    """Provides a real FileReader instance."""
    return AsyncCSVReader(mock_logger)


@pytest.fixture
async def repository(
    csv_file_path: str,
    mock_logger: logging.Logger,
    mock_reader: FileReader,
    mock_storage: OrderStorage,
) -> Repository:
    """
    Creates a Repository instance using real CSV data.
    """
    repo = Repository(
        order_file_path=Path(csv_file_path),
        barcodes_file_path=Path("data/barcodes.csv"),  # Ensure barcodes file exists
        logger=mock_logger,
        reader=mock_reader,
        storage=mock_storage,
    )
    await repo._load_data()
    return repo
