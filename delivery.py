# delivery.py
import re


PRIORITY_PATTERN = re.compile(r"^(High|Medium|Low)$")
class Delivery:
    VALID_PRIORITIES = {"High":0.6, "Medium":1.0, "Low":1.2}

    def __init__(self, name, latitude, longitude, priority, weight_kg):
        self.name = name
        self.latitude = latitude
        self.longitude = longitude
        self.priority = priority
        self.weight_kg = weight_kg

    # --- name ---
    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("customer name must be a non-empty string")
        self._name = value.strip()

    # --- latitude ---
    @property
    def latitude(self):
        return self._latitude

    @latitude.setter
    def latitude(self, value):
        try:
            lat = float(value)
        except (TypeError, ValueError):
            raise ValueError("latitude must be numeric")
        if not (-90.0 <= lat <= 90.0):
            raise ValueError("latitude must be in [-90, 90]")
        self._latitude = lat

    # --- longitude ---
    @property
    def longitude(self):
        return self._longitude

    @longitude.setter
    def longitude(self, value):
        try:
            lon = float(value)
        except (TypeError, ValueError):
            raise ValueError("longitude must be numeric")
        if not (-180.0 <= lon <= 180.0):
            raise ValueError("longitude must be in [-180, 180]")
        self._longitude = lon

    # --- priority ---
    @property
    def priority(self):
        return self._priority

    @priority.setter
    def priority(self, value: str) -> None:
        """Validate and set priority as numeric weight."""
        if not PRIORITY_PATTERN.fullmatch(value):
            raise ValueError("priority must be 'High', 'Medium' or 'Low'")
        self._priority = self.VALID_PRIORITIES[value]


    # --- weight_kg ---
    @property
    def weight_kg(self):
        return self._weight_kg

    @weight_kg.setter
    def weight_kg(self, value):
        try:
            w = float(value)
        except (TypeError, ValueError):
            raise ValueError("weight_kg must be numeric")
        if w < 0:
            raise ValueError("weight_kg must be non-negative")
        self._weight_kg = w

    def __repr__(self):
        return (
            f"Delivery(name={self.name!r}, lat={self.latitude}, "
            f"lon={self.longitude}, priority={self.priority!r}, "
            f"weight_kg={self.weight_kg})"
        )


if __name__ == "__main__":
    d = Delivery("John", "1", 1, "High", 1)
    print(d)
