# log.py
import logging
from CourierOptimizer.config import RUN_LOG_FILE


def get_logger():
    logger = logging.getLogger(__name__)
    logging.basicConfig(
        filename=RUN_LOG_FILE,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )
    return logger
