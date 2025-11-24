# orders.py
from log import get_logger
from config import ORDERS_FILE, REJECTED_ORDERS
from delivery import Delivery
import csv

logger = get_logger()


def get_orders():
    delivery_list = list()
    logger.info(f"READING {ORDERS_FILE}")
    with open(ORDERS_FILE, newline='') as csvfile, open(REJECTED_ORDERS, "a") as reject_csv:
        reader = csv.reader(csvfile)
        next(reader)
        for line_no, row in enumerate(reader, start=2):
            try:
                delivery_list.append(Delivery(*row))
                logger.info("ADDED ORDER in line %d: %s", line_no, row)
            except (TypeError, ValueError) as e:
                writer = csv.writer(reject_csv, delimiter=",")
                print(f"[WARNING] REJECTED ORDER - Invalid row in {ORDERS_FILE} (line {line_no}): {row} -> {e}")
                logger.warning(
                    "REJECTED ORDER Invalid row in %s (line %d): %s -> %s",
                    ORDERS_FILE, line_no, row, e
                )

                writer.writerow([str(e)] + row)
    return delivery_list


if __name__ == "__main__":
    del_list = get_orders()
    print(del_list)
