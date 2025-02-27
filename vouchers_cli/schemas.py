from pathlib import Path

from pydantic import BaseModel, field_validator


class VoucherSchema(BaseModel):
    """
    Schema to represent voucher data.

    Attributes:
        customer_id (int): The unique identifier for the customer.
        order_id (int): The unique identifier for the order.
        barcodes (list[str]): List of barcodes associated with the voucher.
    """

    customer_id: int
    order_id: int
    barcodes: list[str]


class OutputSchema(BaseModel):
    """
    Schema for the output data, which includes top customers,
    unused barcodes, and vouchers.

    Attributes:
        top_customers (list[tuple[int, int]]): List of tuples with customer IDs
            and their corresponding order counts.
        unused_barcodes (set[str]): Set of barcodes that were not used.
        vouchers (list[VoucherSchema]): List of vouchers as defined in `VoucherSchema`.
    """

    top_customers: list[tuple[int, int]]
    unused_barcodes: set[str]
    vouchers: list[VoucherSchema]


class ExtractorConfig(BaseModel):
    """
    Configuration for the Extractor, including file paths for orders,
    barcodes, and the output directory.

    Attributes:
        orders_file_path (Path): The file path to the orders CSV file.
        barcodes_file_path (Path): The file path to the barcodes CSV file.
        output_dir (Path): The directory where output will be saved.
    """

    orders_file_path: Path
    barcodes_file_path: Path
    output_dir: Path

    @field_validator("orders_file_path", "barcodes_file_path")
    @classmethod
    def validate_file_exists(cls, file_path: Path) -> Path:
        """
        Validates that the provided file paths exist and are in CSV format.
        """
        # Check if the file exists
        if not file_path.exists():
            raise ValueError(f"File not found: {file_path}")

        # Ensure the file has a .csv extension
        if file_path.suffix.lower() != ".csv":
            raise ValueError(f"Invalid file format: {file_path}. Expected a CSV file.")

        return file_path
