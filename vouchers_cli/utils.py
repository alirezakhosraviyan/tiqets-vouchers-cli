import argparse
import logging
import sys
from argparse import Namespace
from pathlib import Path


def setup_logger(name: str, log_level: int = logging.INFO) -> logging.Logger:
    """
    Sets up and returns a logger with the specified name and log level.
    """
    logger = logging.getLogger(name)
    logger.setLevel(log_level)

    # Create a StreamHandler to log to console (stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)

    # Define the log message format
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_handler.setFormatter(formatter)

    # Add the handler to the logger
    logger.addHandler(console_handler)

    return logger


def parse_arguments(app_description: str) -> Namespace:
    """
    Set up CLI options for the application.
    """
    # Initialize the argument parser with the application description
    parser = argparse.ArgumentParser(description=app_description)

    # Add argument for enabling debug mode
    parser.add_argument(
        "--debug",
        action="store_true",  # Defaults to False if not provided
        help="Run in debug mode",
    )

    # Add argument for specifying the orders file
    parser.add_argument(
        "--orders-file",
        type=Path,
        default=Path("data/orders.csv"),
        help="Path to orders.csv file (default: 'data/orders.csv')",
    )

    # Add argument for specifying the barcodes file
    parser.add_argument(
        "--barcodes-file",
        type=Path,
        default=Path("data/barcodes.csv"),
        help="Path to barcodes.csv file (default: 'data/barcodes.csv')",
    )

    # Add argument for specifying the output directory
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("output"),
        help="Path to output directory (default: 'output')",
    )

    # Parse the command line arguments
    return parser.parse_args()
