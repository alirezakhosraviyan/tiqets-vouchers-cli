import logging
from pathlib import Path
from unittest.mock import patch

from vouchers_cli.utils import parse_arguments, setup_logger


async def test_setup_logger() -> None:
    """
    Test the setup_logger function to ensure it correctly sets up the logger.
    It checks the logger name and log level, and that a StreamHandler is added.
    """
    logger = setup_logger("test_logger", logging.DEBUG)

    # Assert logger name and level
    assert logger.name == "test_logger"
    assert logger.level == logging.DEBUG

    # Assert StreamHandler is added
    assert len(logger.handlers) == 1
    handler = logger.handlers[0]
    assert isinstance(handler, logging.StreamHandler)


async def test_parse_arguments_default() -> None:
    """
    Test parse_arguments for default values.
    It ensures that the default values for file paths and output directory are correct.
    """
    args = parse_arguments("Test app")

    # Check default values
    assert args.orders_file == Path("data/orders.csv")
    assert args.barcodes_file == Path("data/barcodes.csv")
    assert args.output_dir == Path("output")
    assert not args.debug


async def test_parse_arguments_with_debug() -> None:
    """
    Test parse_arguments when the debug flag is provided.
    It ensures that the debug flag is set correctly.
    """
    with patch("sys.argv", ["app", "--debug"]):
        args = parse_arguments("Test app")
        assert args.debug is True


async def test_parse_arguments_with_custom_files() -> None:
    """
    Test parse_arguments with custom file paths.
    It ensures that the provided file paths are parsed correctly.
    """
    custom_orders = Path("custom_orders.csv")
    custom_barcodes = Path("custom_barcodes.csv")
    custom_output = Path("custom_output")

    with patch(
        "sys.argv",
        [
            "app",
            "--orders-file",
            str(custom_orders),
            "--barcodes-file",
            str(custom_barcodes),
            "--output-dir",
            str(custom_output),
        ],
    ):
        args = parse_arguments("Test app")

    assert args.orders_file == custom_orders
    assert args.barcodes_file == custom_barcodes
    assert args.output_dir == custom_output
