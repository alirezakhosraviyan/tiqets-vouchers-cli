import asyncio
from collections import Counter
from logging import Logger
from pathlib import Path

from vouchers_cli.async_reader import FileReader
from vouchers_cli.storage import OrderStorage


class Repository:
    """
    Repository class responsible for loading and providing access to order
    and barcode data.
    """

    def __init__(
        self,
        order_file_path: Path,
        barcodes_file_path: Path,
        logger: Logger,
        reader: FileReader,
        storage: OrderStorage,
    ):
        """
        Initialize the repository with file paths, logger, data reader, and storage.

        :param order_file_path: Path to the orders CSV file.
        :param barcodes_file_path: Path to the barcodes CSV file.
        :param logger: Logger instance for logging messages.
        :param reader: FileReader instance for reading CSV files asynchronously.
        :param storage: OrderStorage instance for managing orders and barcodes.
        """
        self._order_file_path = order_file_path
        self._barcodes_file_path = barcodes_file_path

        # Injected dependencies
        self._logger = logger
        self._reader = reader
        self._storage = storage

        self._loaded = False

    async def _load_data(self) -> None:
        """
        Load data from CSV files into storage if not already loaded.
        """
        if self._loaded:
            return

        orders, barcodes = await asyncio.gather(
            self._reader.read_csv(self._order_file_path),
            self._reader.read_csv(self._barcodes_file_path),
        )

        # Store orders in storage asynchronously
        for order_id, customer_id in orders:
            await self._storage.store_order(int(order_id), int(customer_id))

        # Store barcodes in storage asynchronously
        for barcode, order_id in barcodes:
            await self._storage.store_barcode(barcode, order_id)

        self._loaded = True

    async def get_vouchers(self) -> dict[tuple[int, int], list[str]]:
        """
        Retrieve a mapping of (order_id, customer_id) to barcodes.

        :return: Dictionary mapping order-customer pairs to lists of barcodes.
        """
        await self._load_data()
        return await self._storage.get_vouchers()

    async def get_unused_barcodes(self) -> set[str]:
        """
        Retrieve unused barcodes that are not associated with any orders.

        :return: Set of unused barcode strings.
        """
        await self._load_data()
        return await self._storage.get_unused_barcodes()

    async def get_top_customers(self) -> list[tuple[int, int]]:
        """
        Retrieve the top 5 customers based on the number of orders placed.
        """
        await self._load_data()
        customer_order_count = Counter(self._storage.orders_to_customers.values())
        return customer_order_count.most_common(5)
