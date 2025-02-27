import asyncio
import os
import sys
from abc import ABC, abstractmethod
from datetime import datetime
from logging import Logger
from pathlib import Path

import aiofiles

from vouchers_cli.schemas import OutputSchema


class AsyncWriter(ABC):
    """
    Abstract base class for asynchronous writers.
    Defines the interface for writing output data.
    """

    @abstractmethod
    async def write(self, output: OutputSchema) -> None:
        """
        Write the given output asynchronously.

        :param output: The output data to be written.
        """
        raise NotImplementedError

    @abstractmethod
    async def _serialize_output(self, output: OutputSchema) -> str:
        """
        Serialize the output data to a string format.

        :param output: The output data to be serialized.
        :return: A string representation of the output data.
        """
        raise NotImplementedError


class STDOutWriter(AsyncWriter):
    """
    Asynchronous writer that outputs data to standard output (stdout).
    """

    def __init__(self, logger: Logger):
        self._logger = logger

    async def _serialize_output(self, output: OutputSchema) -> str:
        """
        Convert output data into a formatted string suitable for stdout.

        :param output: The output data to be serialized.
        :return: A formatted string representing the output data.
        """
        top_customers = "\n".join(
            f"{customer_id}, {amount}" for customer_id, amount in output.top_customers
        )
        return (
            f"Top customers:\n{top_customers}\n"
            f"Unused barcodes: '{len(output.unused_barcodes)}'\n"
        )

    async def write(self, output: OutputSchema) -> None:
        """
        Write the serialized output data to stdout asynchronously.

        :param output: The output data to be written.
        """
        self._logger.debug("Writing statistics to stdout:\n")

        loop = asyncio.get_event_loop()
        encoded_output = await self._serialize_output(output)
        await loop.run_in_executor(
            None,
            lambda content: sys.stdout.write(content) and sys.stdout.flush(),
            encoded_output,
        )


class FileWriter(AsyncWriter):
    """
    Asynchronous writer that writes output data to a file.
    """

    def __init__(self, file_path: Path, logger: Logger):
        self._file_path = file_path
        self._logger = logger

    async def _serialize_output(self, output: OutputSchema) -> str:
        """
        Convert output data into a formatted string suitable for file storage.

        :param output: The output data to be serialized.
        :return: A formatted string representing the output data.
        """
        lines = []
        for voucher in output.vouchers:
            lines.append(
                f"{voucher.customer_id},{voucher.order_id},[{','.join(voucher.barcodes)}]"
            )
        return "\n".join(lines)

    def _get_file_name(self) -> str:
        """
        Generate a unique file name for the output file.
        """
        return (
            f"{self._file_path}/"
            f"output_{datetime.now().strftime('%Y-%m-%d-%H:%M:%S')}.log"
        )

    async def write(self, output: OutputSchema) -> None:
        """
        Write the serialized output data to a file asynchronously.
        """
        filename = self._get_file_name()

        # Ensure the directory exists before writing
        if os.path.dirname(filename):
            os.makedirs(os.path.dirname(filename), exist_ok=True)

        async with aiofiles.open(filename, mode="w") as file:
            await file.write(await self._serialize_output(output))

        self._logger.info("Vouchers were written to %s.", filename)
