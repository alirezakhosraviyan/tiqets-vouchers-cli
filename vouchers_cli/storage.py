from collections import defaultdict


class OrderStorage:
    """
    A class to manage orders, their associated customers, and barcodes.

    Attributes:
        orders_to_customers (dict[int, int]): A mapping of order IDs to customer IDs.
        customer_to_barcodes (dict[tuple[int, int], list[str]]):
        A mapping of (order_id, customer_id) pairs to the list of barcodes assigned
        to that customer.
        unused_barcodes (set[str]): barcodes that are not assigned to any order.
        used_barcodes (set[str]): barcodes that have already been used (assigned).
    """

    def __init__(self) -> None:
        """
        Initializes the OrderStorage object with empty mappings for
        orders, customers, and barcodes.
        """
        self.orders_to_customers: dict[int, int] = {}  # order_id -> customer_id
        self.customer_to_barcodes: dict[tuple[int, int], list[str]] = defaultdict(list)
        self.unused_barcodes: set[str] = set()
        self.used_barcodes: set[str] = set()

    def store_order(self, order_id: int, customer_id: int) -> None:
        """
        Store an order and associate it with a customer.

        Args:
            order_id (int): The unique identifier for the order.
            customer_id (int): The unique identifier for the customer.

        Updates:
            orders_to_customers: Maps the order ID to the corresponding customer ID.
        """
        self.orders_to_customers[order_id] = customer_id

    def store_barcode(self, barcode: str, order_id: str) -> None:
        """
        Store a barcode and associate it with an order and customer if applicable.

        Args:
            barcode (str): The barcode to be stored.
            order_id (str): The order ID associated with the barcode.

        Updates:
            customer_to_barcodes: Adds the barcode to the list for
            the given (order_id, customer_id) pair.
            unused_barcodes: Adds the barcode to unused set if no order is provided
            or the barcode is already used.
            used_barcodes: Keeps track of barcodes that have been successfully
            assigned to orders.

        Notes:
            - If the barcode is already used, it will not be added again.
            - If no valid order is associated with the barcode,
            it will be considered unused.
        """
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
            self.customer_to_barcodes[(parsed_order_id, customer_id)].append(barcode)
            # Mark the barcode as used
            self.used_barcodes.add(barcode)
