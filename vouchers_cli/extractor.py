import asyncio
from logging import Logger

from vouchers_cli.async_reader import AsyncCSVReader
from vouchers_cli.async_writer import AsyncWriter, FileWriter, STDOutWriter
from vouchers_cli.repository import Repository
from vouchers_cli.schemas import ExtractorConfig, OutputSchema, VoucherSchema
from vouchers_cli.storage import OrderStorage


class VouchersExtractor:
    """
    Handles the extraction of voucher-related data and writes the results
    using multiple asynchronous writers.
    """

    def __init__(
        self,
        logger: Logger,
        repository: Repository,
        writers: list[AsyncWriter],
    ):
        """
        Initialize the VouchersExtractor with necessary dependencies.

        :param logger: Logger instance for logging messages.
        :param repository: Repository instance for fetching voucher data.
        :param writers: List of writer instances for outputting data.
        """
        self._logger = logger
        self._repository = repository
        self._writers = writers

    @classmethod
    def create(cls, configs: ExtractorConfig, logger: Logger) -> "VouchersExtractor":
        """
        Factory method to create an instance of VouchersExtractor.

        :param configs: Configuration containing file paths and output directory.
        :param logger: Logger instance for logging messages.
        :return: An instance of VouchersExtractor.
        """
        async_reader = AsyncCSVReader(logger)
        storage = OrderStorage()
        repository = Repository(
            configs.orders_file_path,
            configs.barcodes_file_path,
            logger,
            async_reader,
            storage,
        )
        stdout_writer = STDOutWriter(logger)
        file_writer = FileWriter(configs.output_dir, logger)

        return cls(logger, repository, [stdout_writer, file_writer])

    async def _extract_data(self) -> OutputSchema:
        """
        Extracts voucher-related data from the repository.

        :return: An OutputSchema instance containing extracted data.
        """
        vouchers = [
            VoucherSchema(
                customer_id=customer_id,
                order_id=order_id,
                barcodes=barcodes,
            )
            for (order_id, customer_id), barcodes in (
                await self._repository.get_vouchers()
            ).items()
        ]

        return OutputSchema(
            top_customers=await self._repository.get_top_customers(),
            unused_barcodes=await self._repository.get_unused_barcodes(),
            vouchers=vouchers,
        )

    async def run(self) -> None:
        """
        Run the extraction process and write output using all configured writers.
        """
        # Extracting data from files
        output = await self._extract_data()

        # Writing output using all writers
        await asyncio.gather(
            *[writer.write(output) for writer in self._writers],
        )
