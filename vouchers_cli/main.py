import asyncio
import logging

from vouchers_cli.extractor import VouchersExtractor
from vouchers_cli.schemas import ExtractorConfig
from vouchers_cli.utils import parse_arguments, setup_logger


async def main() -> None:
    """
    Main entry point for the command-line tool that extracts voucher data.
    """
    app_description = "Command-line tool for extracting vouchers data."
    args = parse_arguments(app_description)
    logger = setup_logger(
        name=app_description,
        log_level=logging.INFO if args.debug else logging.DEBUG,
    )

    try:
        configs = ExtractorConfig(
            orders_file_path=args.orders_file,
            barcodes_file_path=args.barcodes_file,
            output_dir=args.output_dir,
        )

        extractor = VouchersExtractor.create(configs, logger)
        await extractor.run()
    except ValueError as e:
        logger.error(e)


def entry() -> None:
    """
    Synchronous entry point for running the extraction process.
    """
    asyncio.run(main())
