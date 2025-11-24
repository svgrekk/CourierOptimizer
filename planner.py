from orders import get_orders
from config import OSLO_S_LAT, OSLO_S_LON, ROUTE_FILE, ROUTE_IMG
from distance import haver_dist
import numpy as np
from log import get_logger
from transport_mode import car, bike, walk
import csv
from decorators import timed
import matplotlib.pyplot as plt
from typing import List, Dict

logger = get_logger()


class RoutPlanner:
    def __init__(self, mode, strategy, lat=OSLO_S_LAT, lon=OSLO_S_LON):
        self.mode = mode
        self.orders = get_orders()
        self.strategy = strategy
        self.depot_lat = lat
        self.depot_lon = lon
        self.compute = self.get_compute()

    def get_compute(self):
        if self.strategy == "FASTEST":
            return lambda distance: self.mode.travel_time(distance)
        elif self.strategy == "CHEAPEST":
            return lambda distance: self.mode.travel_cost(distance)
        elif self.strategy == "LOWEST_CO2":
            return lambda distance: self.mode.travel_co2(distance)

    def calculate_distances(self):
        """Build a full pairwise distance matrix between all orders."""
        n = len(self.orders)
        dist_matrix = np.zeros((n, n))

        for i in range(n):
            for j in range(n):
                if i == j:
                    dist_matrix[i, j] = np.nan

                else:
                    point_1 = (self.orders[i].latitude, self.orders[i].longitude)
                    point_2 = (self.orders[j].latitude, self.orders[j].longitude)
                    dist_matrix[i, j] = haver_dist(*point_1, *point_2)
        logger.info("CALCULATED DISTANCES MATRIX for %d orders (shape %dx%d)", n, n, n)
        return dist_matrix

    def get_strategy_matrix(self):
        dist_matrix = self.calculate_distances()
        n = dist_matrix.shape[0]
        strategy_matrix = np.zeros((n, n))
        for i in range(n):
            for j in range(n):
                if i == j:
                    strategy_matrix[i, j] = np.nan
                else:
                    value = self.compute(dist_matrix[i, j])
                    weight = self.orders[j].priority
                    strategy_matrix[i, j] = value * weight
        logger.info(
            "CALCULATED STRATEGY MATRIX for Transport Mode: %s, Strategy: %s",
            self.mode.mode, self.strategy)
        return strategy_matrix

    def from_depot_distances(self):
        n = len(self.orders)
        distances = np.zeros(n)
        for i in range(n):
            point_1 = (self.depot_lat, self.depot_lon)
            point_2 = (self.orders[i].latitude, self.orders[i].longitude)
            distances[i] = haver_dist(*point_1, *point_2)
        logger.info("Calculated distances from depot.")
        return distances

    def from_depot_strategy(self):
        from_depot_dist = self.from_depot_distances()
        n = len(self.orders)
        weighted_dist = np.zeros(n)
        for i in range(n):
            value = self.compute(from_depot_dist[i])
            weight = self.orders[i].priority
            weighted_dist[i] = value * weight
        logger.info(
            "Calculated weighted depot->stop values "
            "(mode=%s, strategy=%s, orders=%d)",
            self.mode.mode,
            self.strategy,
            len(self.orders),
        )
        return weighted_dist

    @timed
    def optimize(self) -> List[int]:
        """
        Build a greedy route starting from the depot using the current
        transport mode and objective strategy.

        The algorithm:
        1. Computes priority-weighted objective values from the depot to each stop
           and selects the best first stop.
        2. Iteratively selects the next stop among unvisited ones by choosing
           the minimum value in the strategy matrix row of the current stop.
        3. Returns the route as a list of order indices in visiting order.

        Returns:
            list[int]: Indices of orders in the optimized visiting order.
        """
        n = len(self.orders)
        unvisited = set(range(n))
        logger.info(
            "Starting route optimization (orders=%d, mode=%s, strategy=%s)",
            n,
            self.mode.mode,
            self.strategy,
        )
        from_depot = self.from_depot_strategy()
        current = int(np.nanargmin(from_depot))
        unvisited.remove(current)
        route = [current, ]
        strategy_matrix = self.get_strategy_matrix()
        logger.debug("Initial stop from depot chosen: index=%d, name=%s",
                     current, self.orders[current].name)

        while unvisited:
            row = strategy_matrix[current].copy()
            for i in range(n):
                if i not in unvisited:
                    row[i] = np.nan
            next_idx = int(np.nanargmin(row))
            row[next_idx] = np.nan
            unvisited.remove(next_idx)
            route.append(next_idx)
            current = next_idx

        return route

    def gen_route(self) -> List[Dict]:
        """
        Generate the detailed route for the current transport mode and strategy.

        The method:
          1. Calls optimize() to obtain the visiting order of stops.
          2. Computes per-leg distance, time, cost and CO2 from the depot
             to the first stop and between consecutive stops.
          3. Accumulates total distance and time for ETA.
          4. Writes the route to ROUTE_FILE as CSV.

        Returns:
            list[dict]: List of rows describing each leg of the route.
                        Each row contains: from, to, distance_km,
                        cumulative_distance_km, eta_hours, cost_leg_nok, co2_leg_g.
        """
        logger.info(
            "Generating route CSV (mode=%s, strategy=%s)",
            self.mode.mode,
            self.strategy,
        )
        # route as list of order indices in visiting order
        idx_list = self.optimize()

        # pure distances in km
        depot_distances = self.from_depot_distances()  # length n
        dist_matrix = self.calculate_distances()  # n x n

        rows = []
        cumulative_distance = 0.0
        cumulative_time = 0.0
        total_cost: float = 0.0
        total_co2: float = 0.0

        for pos, curr_idx in enumerate(idx_list):
            # determine distance from previous point
            if pos == 0:
                # first leg: from depot (Oslo S) to first stop
                distance = depot_distances[curr_idx]
                from_label = "OSLO S"
            else:
                prev_idx = idx_list[pos - 1]
                distance = dist_matrix[prev_idx, curr_idx]
                from_label = self.orders[prev_idx].name

            # compute leg metrics for the current transport mode
            leg_time = self.mode.travel_time(distance)
            leg_cost = self.mode.travel_cost(distance)
            leg_co2 = self.mode.travel_co2(distance)

            cumulative_distance += distance
            cumulative_time += leg_time
            total_cost += leg_cost
            total_co2 += leg_co2

            rows.append({
                "from": from_label,
                "to": self.orders[curr_idx].name,
                "distance_km": distance,
                "cumulative_distance_km": cumulative_distance,
                "eta_hours": cumulative_time,
                "cost_leg_nok": leg_cost,
                "co2_leg_g": leg_co2,
            })
        with open(ROUTE_FILE, "w") as f:
            fieldnames = rows[0].keys()
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

        logger.info(
            "Route CSV written to %s "
            "(stops=%d, total_distance=%.3f km, total_time=%.3f h, "
            "total_cost=%.2f NOK, total_co2=%.1f g)",
            ROUTE_FILE,
            len(rows),
            cumulative_distance,
            cumulative_time,
            total_cost,
            total_co2,
        )

        return rows

    def plot_route(self):
        logger.info("START generating Route plot")
        idx_list = self.optimize()
        xs = [self.depot_lon]
        ys = [self.depot_lat]
        for idx in idx_list:
            order = self.orders[idx]
            xs.append(order.longitude)
            ys.append(order.latitude)

        plt.figure(figsize=(6, 6))
        # line between points
        plt.plot(xs, ys, marker="o")

        # mark depot
        plt.scatter(self.depot_lon, self.depot_lat, s=80)
        plt.text(self.depot_lon, self.depot_lat, " depot", fontsize=12)

        # mark stops in order (1, 2, 3, ...)
        for step, idx in enumerate(idx_list, start=1):
            order = self.orders[idx]
            plt.text(order.longitude, order.latitude, f" {step}", fontsize=12)

        plt.xlabel("Longitude")
        plt.ylabel("Latitude")
        plt.title(f"Route for mode={self.mode.mode}, strategy={self.strategy}")
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(ROUTE_IMG)
        plt.close()

        logger.info("Route plot saved to %s", ROUTE_IMG)


if __name__ == "__main__":
    planner = RoutPlanner(walk, "FASTEST")
    f = planner.plot_route()
    print(f)
