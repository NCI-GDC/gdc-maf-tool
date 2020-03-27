import sys

import cdislogging

logger = cdislogging.get_logger("gdc-maf-tool", log_level="info")


def fatal(message: str):
    """
    Report the error and exit the program.

    Python's logger.fatal does not exit the program.
    """
    logger.fatal(message)
    sys.exit(2)
