# config.py

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
FILES_DIR = BASE_DIR / "files"

ORDERS_FILE = FILES_DIR / "orders.csv"
REJECTED_ORDERS = FILES_DIR / "rejected.csv"
RUN_LOG_FILE = FILES_DIR / "run.log"
ROUTE_FILE = FILES_DIR / "route.csv"
ROUTE_IMG = FILES_DIR / "route.png"


OSLO_S_LAT = 59.9100
OSLO_S_LON = 10.7500
