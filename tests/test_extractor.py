from unittest.mock import AsyncMock

from vouchers_cli.extractor import VouchersExtractor
from vouchers_cli.repository import Repository


async def test_extract_data(
    extractor: VouchersExtractor, mock_repository: Repository
) -> None:
    """
    Test the _extract_data method to ensure it processes data correctly.
    """
    output = await extractor._extract_data()

    # Assert the extracted data is correct
    assert len(output.vouchers) == 204
    assert output.top_customers == [(10, 8), (60, 8), (56, 7), (59, 7), (19, 6)]
    assert len(output.unused_barcodes) == 98
    assert output.vouchers[0].customer_id == 10
    assert output.vouchers[1].customer_id == 11


async def test_run(
    extractor: VouchersExtractor,
    mock_repository: AsyncMock,
    mock_writers: list[AsyncMock],
) -> None:
    """
    Test the run method to ensure data extraction and writing works.
    """
    extractor._extract_data = AsyncMock()  # type: ignore[method-assign]
    extractor._writers = mock_writers  # type: ignore[assignment]

    await extractor.run()
    extractor._extract_data.assert_called_once()

    # Check that the writers' write methods are called with the correct data
    for writer in mock_writers:
        writer.write.assert_called_once()
