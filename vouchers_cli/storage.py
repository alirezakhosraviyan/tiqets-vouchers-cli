import asyncio
from collections import defaultdict


class OrderStorage:
    """
    A class to manage orders, their associated customers,
    and barcodes in an async-safe manner.
    """

    def __init__(self) -> None:
        """
        Initializes the OrderStorage object with empty mappings for
        orders, customers, and barcodes, and a lock for async-safety.
        """
        self.orders_to_customers: dict[int, int] = {}  # order_id -> customer_id
        self.customer_to_barcodes: dict[tuple[int, int], list[str]] = defaultdict(list)
        self.unused_barcodes: set[str] = set()
        self.used_barcodes: set[str] = set()

        # Async lock for protecting access to shared data
        self._lock = asyncio.Lock()

    async def store_order(self, order_id: int, customer_id: int) -> None:
        """
        Store an order and associate it with a customer, with async-safe access.

        Args:
            order_id (int): The unique identifier for the order.
            customer_id (int): The unique identifier for the customer.
        """
        async with self._lock:
            self.orders_to_customers[order_id] = customer_id

    async def store_barcode(self, barcode: str, order_id: str) -> None:
        """
        Store a barcode and associate it with an order and customer
        if applicable, with async-safe access.

        Args:
            barcode (str): The barcode to be stored.
            order_id (str): The order ID associated with the barcode.
        """
        async with self._lock:
            # If the barcode has already been used, don't store it again
            if barcode in self.used_barcodes:
                return

            # If no valid order_id is provided, mark the barcode as unused
            if not order_id:
                self.unused_barcodes.add(barcode)
                return

            # Parse order_id and attempt to associate the barcode with
            # the corresponding customer
            parsed_order_id = int(order_id)
            if customer_id := self.orders_to_customers.get(parsed_order_id, None):
                # Associate the barcode with the order and customer
                self.customer_to_barcodes[(parsed_order_id, customer_id)].append(
                    barcode
                )
                # Mark the barcode as used
                self.used_barcodes.add(barcode)

    async def get_vouchers(self) -> dict[tuple[int, int], list[str]]:
        """
        Retrieve a mapping of (order_id, customer_id) to barcodes,
        with async-safe access.

        :return: Dictionary mapping order-customer pairs to
        lists of barcodes.
        """
        async with self._lock:
            return self.customer_to_barcodes

    async def get_unused_barcodes(self) -> set[str]:
        """
        Retrieve unused barcodes that are not associated with any orders,
        with async-safe access.

        :return: Set of unused barcode strings.
        """
        async with self._lock:
            return self.unused_barcodes
