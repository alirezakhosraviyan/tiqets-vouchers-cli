from pathlib import Path

import pytest
from pydantic import ValidationError

from vouchers_cli.schemas import ExtractorConfig, OutputSchema, VoucherSchema


async def test_voucher_schema_valid() -> None:
    """
    Test VoucherSchema with valid data.
    """
    voucher_data = {
        "customer_id": 1,
        "order_id": 100,
        "barcodes": ["barcode1", "barcode2"],
    }

    voucher = VoucherSchema(**voucher_data)  # type: ignore[arg-type]

    # Assert that the voucher data is correctly parsed
    assert voucher.customer_id == 1
    assert voucher.order_id == 100
    assert voucher.barcodes == ["barcode1", "barcode2"]


async def test_voucher_schema_invalid_data() -> None:
    """
    Test VoucherSchema with invalid data (missing required field).
    """
    invalid_data = {"customer_id": 1, "order_id": 100}

    with pytest.raises(ValidationError):
        VoucherSchema(**invalid_data)  # type: ignore[arg-type]


async def test_output_schema_valid() -> None:
    """
    Test OutputSchema with valid data.
    """
    output_data = {
        "top_customers": [(1, 5), (2, 3)],
        "unused_barcodes": {"barcode1", "barcode2"},
        "vouchers": [
            {"customer_id": 1, "order_id": 100, "barcodes": ["barcode1", "barcode2"]}
        ],
    }

    output = OutputSchema(**output_data)  # type: ignore[arg-type]

    # Assert the output data is correctly parsed
    assert output.top_customers == [(1, 5), (2, 3)]
    assert output.unused_barcodes == {"barcode1", "barcode2"}
    assert len(output.vouchers) == 1
    assert output.vouchers[0].customer_id == 1


async def test_extractor_config_valid() -> None:
    """
    Test ExtractorConfig with valid file paths.
    """
    valid_config_data = {
        "orders_file_path": Path("data/orders.csv"),
        "barcodes_file_path": Path("data/barcodes.csv"),
        "output_dir": Path("output"),
    }

    config = ExtractorConfig(**valid_config_data)

    # Assert the config is parsed correctly
    assert config.orders_file_path == Path("data/orders.csv")
    assert config.barcodes_file_path == Path("data/barcodes.csv")
    assert config.output_dir == Path("output")


async def test_extractor_config_invalid_file() -> None:
    """
    Test ExtractorConfig with invalid file (non-existent file).
    """
    invalid_config_data = {
        "orders_file_path": Path("invalid/orders.csv"),
        "barcodes_file_path": Path("invalid/barcodes.csv"),
        "output_dir": Path("output"),
    }

    with pytest.raises(ValueError, match="File not found: invalid/orders.csv"):
        ExtractorConfig(**invalid_config_data)


async def test_extractor_config_invalid_format(create_test_txt: object) -> None:
    """
    Test ExtractorConfig with an invalid file format (non-CSV file).
    """
    invalid_config_data = {
        "orders_file_path": Path("data/orders.txt"),
        "barcodes_file_path": Path("data/barcodes.csv"),
        "output_dir": Path("output"),
    }

    with pytest.raises(
        ValueError, match="Invalid file format: data/orders.txt. Expected a CSV file."
    ):
        ExtractorConfig(**invalid_config_data)
