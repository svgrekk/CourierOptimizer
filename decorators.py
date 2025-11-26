# decorators.py
import datetime
from functools import wraps
from CourierOptimizer.log import get_logger

logger = get_logger()

def timed(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = datetime.datetime.now()
        logger.info("START %s", func.__name__)
        result = func(*args, **kwargs)  # <-- важно: **kwargs
        finish = datetime.datetime.now()
        duration = (finish - start).total_seconds()
        logger.info("FINISH %s duration = %.6f seconds", func.__name__, duration)
        return result
    return wrapper
