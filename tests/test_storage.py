import asyncio
from logging import Logger

from vouchers_cli.storage import OrderStorage


async def test_store_order(mock_logger: Logger) -> None:
    """
    Test the store_order method to ensure orders are correctly mapped to customers.
    """
    order_storage = OrderStorage(mock_logger)
    await order_storage.store_order(1, 100)

    assert order_storage.orders_to_customers[1] == 100


async def test_store_barcode_with_valid_order(mock_logger: Logger) -> None:
    """
    Test store_barcode with a valid order_id and customer_id.
    It ensures that the barcode is added to the correct customer’s list of barcodes.
    """
    order_storage = OrderStorage(mock_logger)

    await order_storage.store_order(1, 100)
    await order_storage.store_barcode("barcode123", "1")

    assert "barcode123" in order_storage.customer_to_barcodes[(1, 100)]


async def test_store_barcode_with_no_order(mock_logger: Logger) -> None:
    """
    Test store_barcode when no valid order_id is provided.
    The barcode should be added to the unused barcodes set.
    """
    order_storage = OrderStorage(mock_logger)

    # Store a barcode with no valid order_id
    await order_storage.store_barcode("barcode123", "")

    assert "barcode123" in order_storage.unused_barcodes


async def test_store_barcode_with_already_used_barcode(mock_logger: Logger) -> None:
    """
    Test store_barcode when the barcode has already been used.
    The barcode should not be added again.
    """
    order_storage = OrderStorage(mock_logger)

    # Store an order
    await order_storage.store_order(1, 100)

    # Store a barcode for the order
    await order_storage.store_barcode("barcode123", "1")

    # Try storing the same barcode again
    await order_storage.store_barcode("barcode123", "1")

    # Assert the barcode is not added again
    assert order_storage.customer_to_barcodes[(1, 100)].count("barcode123") == 1


async def test_unused_barcodes_set(mock_logger: Logger) -> None:
    """
    Test that unused barcodes are correctly tracked.
    """
    order_storage = OrderStorage(mock_logger)

    # Store barcodes with no order
    await order_storage.store_barcode("barcode123", "")
    await order_storage.store_barcode("barcode456", "")

    assert "barcode123" in order_storage.unused_barcodes
    assert "barcode456" in order_storage.unused_barcodes


async def test_used_barcodes_set(mock_logger: Logger) -> None:
    """
    Test that used barcodes are correctly tracked.
    """
    order_storage = OrderStorage(mock_logger)

    # Store an order
    await order_storage.store_order(1, 100)

    # Store a barcode for the order
    await order_storage.store_barcode("barcode123", "1")

    # Assert that the barcode is in the used barcodes set
    assert "barcode123" in order_storage.used_barcodes


async def test_locking_in_storage(mock_logger: Logger) -> None:
    """
    Test that concurrent access to storage is properly locked.
    Ensures that data is not overwritten or accessed simultaneously.
    """
    order_storage = OrderStorage(mock_logger)

    async def store_data_concurrently() -> None:
        await order_storage.store_order(1, 100)
        await order_storage.store_barcode("barcode123", "1")

    # Run two tasks concurrently to simulate race conditions
    await asyncio.gather(store_data_concurrently(), store_data_concurrently())

    # Assert that the order is stored correctly without race conditions
    assert order_storage.orders_to_customers[1] == 100
    assert "barcode123" in order_storage.customer_to_barcodes[(1, 100)]
