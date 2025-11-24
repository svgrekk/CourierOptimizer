# decorators.py
from log import get_logger
import datetime

logger = get_logger()


def timed(func):
    def wrapper(*args, **kwargs):
        start = datetime.datetime.now()
        logger.info("START %s function", func.__name__)
        result = func(*args)
        finish = datetime.datetime.now()
        duration = (finish - start).total_seconds()
        logger.info("FINISH  %s function duration = %.6f seconds",func.__name__, duration)
        return result
    return wrapper
