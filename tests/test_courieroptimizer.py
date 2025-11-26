# tests/test_courieroptimizer.py

import csv
import pytest

from CourierOptimizer.distance import haver_dist
from CourierOptimizer.delivery import Delivery
from CourierOptimizer import orders, config as cfg


"""
Basic pytest-based tests for the core components of the CourierOptimizer package.

The tests focus on:
- the haversine distance helper,
- validation behaviour in the Delivery class,
- CSV loading and rejection logic in the orders module.
"""


# ---------- distance tests ----------


def test_haver_dist_zero():
    """Distance between identical points should be (close to) zero."""
    d = haver_dist(59.91, 10.75, 59.91, 10.75)
    assert d == pytest.approx(0.0, abs=1e-6)


def test_haver_dist_symmetry():
    """Distance function should be symmetric: d(a,b) == d(b,a)."""
    lat1, lon1 = 59.91, 10.75   # Oslo (approximate)
    lat2, lon2 = 60.39, 5.32    # Bergen (approximate)
    d1 = haver_dist(lat1, lon1, lat2, lon2)
    d2 = haver_dist(lat2, lon2, lat1, lon1)
    assert d1 == pytest.approx(d2, rel=1e-6)


def test_haver_dist_reasonable_range():
    """
    Distance between Oslo and Bergen should lie in a plausible range.

    This is not an exact check, but a sanity check that the implementation
    is returning a value of the right order of magnitude.
    """
    lat1, lon1 = 59.91, 10.75   # Oslo
    lat2, lon2 = 60.39, 5.32    # Bergen
    d = haver_dist(lat1, lon1, lat2, lon2)
    assert 300 <= d <= 600


# ---------- Delivery validation tests ----------


def test_delivery_valid_high_priority():
    """
    A valid delivery with textual priority 'High' should map
    to the expected numeric priority weight (0.6).
    """
    # Use positional arguments so the test does not depend on parameter names.
    d = Delivery("Test Customer", 59.91, 10.75, "High", 1.5)

    # In the implementation, the public 'priority' property
    # stores the numeric weight, not the original label.
    assert d.priority == pytest.approx(0.6)


def test_delivery_invalid_priority_raises_value_error():
    """An invalid textual priority should raise ValueError."""
    with pytest.raises(ValueError):
        Delivery("Test Customer", 59.91, 10.75, "Urgent", 1.0)


def test_delivery_invalid_latitude_raises_value_error():
    """Latitude outside the valid range [-90, 90] should raise ValueError."""
    with pytest.raises(ValueError):
        Delivery("Bad Coords", 200.0, 10.75, "Medium", 1.0)


# ---------- orders + rejected.csv tests ----------


def test_orders_invalid_row_does_not_crash(tmp_path, monkeypatch):
    """
    When loading a CSV with one valid and one invalid row:
    - the valid row should produce a Delivery object,
    - the invalid row should be rejected without crashing the program.

    The exact location of rejected.csv is determined by the project
    configuration, so this test only checks the behaviour of get_orders().
    """
    orders_file = tmp_path / "orders.csv"

    # Redirect the input orders file to a temporary location
    monkeypatch.setattr(orders, "ORDERS_FILE", str(orders_file))

    # Create a minimal CSV file: one valid row and one deliberately invalid row
    with orders_file.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["customer", "latitude", "longitude", "priority", "weight_kg"])
        writer.writerow(["Valid Customer", "59.91", "10.75", "High", "1.0"])
        writer.writerow(["Bad Customer", "abc", "xyz", "Low", "-5"])

    deliveries = orders.get_orders()

    # Only the valid row should have been converted into a Delivery
    assert len(deliveries) == 1
    assert isinstance(deliveries[0], Delivery)

