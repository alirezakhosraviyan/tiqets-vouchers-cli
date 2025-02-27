import logging
import os
import sys
from datetime import datetime
from io import StringIO
from pathlib import Path

from vouchers_cli.async_writer import FileWriter, STDOutWriter
from vouchers_cli.schemas import OutputSchema


async def test_stdout_writer_write(
    mock_logger: logging.Logger, output_schema: OutputSchema
) -> None:
    """
    Test that STDOutWriter writes the correct output to stdout asynchronously.
    """
    writer = STDOutWriter(mock_logger)

    # Capture the output written to stdout
    captured_output = StringIO()
    sys.stdout = captured_output  # Redirect stdout to capture the printed output
    await writer.write(output_schema)

    expected_output = "Top customers:\n1, 500\n2, 300\nUnused barcodes: '2'\n"
    assert captured_output.getvalue() == expected_output

    sys.stdout = sys.__stdout__


async def test_file_writer_write(
    mock_logger: logging.Logger, output_schema: OutputSchema, tmp_path: Path
) -> None:
    """
    Test that FileWriter writes the correct output to a file asynchronously.
    """
    file_path = tmp_path / "output_directory"
    writer = FileWriter(file_path, mock_logger)
    filename = f"{file_path}/output_{datetime.now().strftime('%Y-%m-%d-%H:%M:%S')}.log"
    writer._get_file_name = lambda: filename  # type: ignore[method-assign]
    await writer.write(output_schema)

    assert os.path.exists(filename)

    with open(filename, "r") as file:
        file_content = file.read()

    expected_file_content = "1,123,[barcode1,barcode2]\n2,456,[barcode3]"
    assert file_content == expected_file_content
    os.remove(filename)
