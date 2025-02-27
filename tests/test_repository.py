from vouchers_cli.repository import Repository


async def test_get_vouchers(repository: Repository) -> None:
    """
    Test `get_vouchers` method returns correct mappings of orders to barcodes.
    """
    expected = {(123, 456): ["11111111232", "11111111549"]}
    result = await repository.get_vouchers()
    assert result == expected


async def test_get_unused_barcodes(
    repository: Repository, create_test_csv: object
) -> None:
    """
    Test `get_unused_barcodes` method returns expected unused barcodes.
    """
    result = await repository.get_unused_barcodes()
    assert len(result) == 103


async def test_get_top_customers(repository: Repository) -> None:
    """
    Test `get_top_customers` method correctly identifies top 5 customers.
    """
    expected = [(456, 1), (101, 1)]  # Each customer placed 1 order in the test CSV
    result = await repository.get_top_customers()
    assert result == expected
