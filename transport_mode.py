# transport_mode.py
from dataclasses import dataclass


@dataclass
class BaseTransportMode:
    mode: str
    speed: float
    cost: float
    co2: float

    def travel_time(self, distance):
        """Return travel time in hours for the given distance."""
        return distance / self.speed

    def travel_cost(self, distance):
        """Return travel cost in NOK for the given distance."""
        return distance * self.cost

    def travel_co2(self, distance):
        """Return CO2 emissions in grams for the given distance."""
        return distance * self.co2


car = BaseTransportMode("Car", 50, 4, 120)
bike = BaseTransportMode("Bicycle", 15, 0, 0)
walk = BaseTransportMode("Walking", 5, 0, 0)
