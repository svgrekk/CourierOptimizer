from dataclasses import dataclass, field
from typing import Optional

from CourierOptimizer import config as cfg
from CourierOptimizer import orders
from CourierOptimizer.planner import RoutPlanner
from CourierOptimizer.transport_mode import car, bike, walk
from CourierOptimizer.log import get_logger


@dataclass
class Settings:
    """Holds current CLI settings."""
    orders_path: str = field(default_factory=lambda: orders.ORDERS_FILE)
    mode: str = "car"              # car / bike / walk
    objective: str = "FASTEST"     # FASTEST / CHEAPEST / LOWEST_CO2
    depot_lat: Optional[float] = field(
        default_factory=lambda: cfg.OSLO_S_LAT
    )
    depot_lon: Optional[float] = field(
        default_factory=lambda: cfg.OSLO_S_LON
    )


def print_menu(settings: Settings) -> None:
    """Print the main text menu and current settings."""
    print("\n=== NordicExpress Courier Optimizer ===")
    print(f"Current orders file: {settings.orders_path}")
    print(f"Transport mode:      {settings.mode}")
    print(f"Objective:           {settings.objective}")
    if settings.depot_lat is not None and settings.depot_lon is not None:
        depot_str = f"{settings.depot_lat:.5f}, {settings.depot_lon:.5f}"
    else:
        depot_str = "NOT SET"
    print(f"Depot coordinates:   {depot_str}")
    print("---------------------------------------")
    print("1) Change orders file")
    print("2) Choose transport mode (car / bike / walk)")
    print("3) Choose objective (FASTEST / CHEAPEST / LOWEST_CO2)")
    print("4) Change depot coordinates")
    print("5) Run optimization")
    print("0) Exit")


def input_non_empty(prompt: str) -> str:
    """Prompt until a non-empty string is entered."""
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("Empty input, please try again.")


def input_float(prompt: str) -> float:
    """Prompt until a valid float is entered."""
    while True:
        value = input(prompt).strip()
        try:
            return float(value)
        except ValueError:
            print("Please enter a valid number (e.g., 59.91).")


def choose_mode() -> str:
    """Interactive selection of transport mode."""
    print("\nChoose transport mode:")
    print("1) car")
    print("2) bike")
    print("3) walk")
    while True:
        choice = input("> ").strip()
        if choice == "1":
            return "car"
        if choice == "2":
            return "bike"
        if choice == "3":
            return "walk"
        print("Invalid choice, please enter 1, 2 or 3.")


def choose_objective() -> str:
    """Interactive selection of optimization objective."""
    print("\nChoose optimization objective:")
    print("1) FASTEST    (minimize total time)")
    print("2) CHEAPEST   (minimize total cost)")
    print("3) LOWEST_CO2 (minimize total CO2)")
    while True:
        choice = input("> ").strip()
        if choice == "1":
            return "FASTEST"
        if choice == "2":
            return "CHEAPEST"
        if choice == "3":
            return "LOWEST_CO2"
        print("Invalid choice, please enter 1, 2 or 3.")


def _get_mode_object(mode_name: str):
    """Map mode name to transport mode object."""
    if mode_name == "car":
        return car
    if mode_name == "bike":
        return bike
    if mode_name == "walk":
        return walk
    raise ValueError(f"Unknown transport mode: {mode_name}")


def run_optimization(settings: Settings) -> None:
    """Run the route optimization with current settings and generate plot."""
    logger = get_logger()

    if settings.depot_lat is None or settings.depot_lon is None:
        print("Please change depot coordinates first (menu option 4).")
        return

    # Make sure orders.get_orders() uses the chosen file
    orders.ORDERS_FILE = settings.orders_path

    logger.info(
        "RUN START mode=%s objective=%s depot=(%f,%f) orders_file=%s",
        settings.mode,
        settings.objective,
        settings.depot_lat,
        settings.depot_lon,
        settings.orders_path,
    )

    mode_obj = _get_mode_object(settings.mode)

    planner = RoutPlanner(
        mode=mode_obj,
        strategy=settings.objective,
        lat=settings.depot_lat,
        lon=settings.depot_lon,
    )

    rows = planner.gen_route()

    if not rows:
        print("No valid route generated.")
        logger.warning("No route rows returned from gen_route()")
        return

    planner.plot_route()

    last = rows[-1]
    total_distance = last.get("cumulative_distance_km", 0.0)
    total_time = last.get("eta_hours", 0.0)
    total_cost = sum(r.get("cost_leg_nok", 0.0) for r in rows)
    total_co2 = sum(r.get("co2_leg_g", 0.0) for r in rows)

    print("\n=== Route summary ===")
    print(f"Transport mode: {settings.mode}")
    print(f"Objective:      {settings.objective}")
    print(f"Total distance: {total_distance:.2f} km")
    print(f"Total time:     {total_time:.2f} h")
    print(f"Total cost:     {total_cost:.2f} NOK")
    print(f"Total CO2:      {total_co2:.2f} g")

    print(f"\nRoute CSV:  {cfg.ROUTE_FILE}")
    print("Log file:    run.log")
    print(f"Route plot:  {cfg.ROUTE_IMG}")

    logger.info(
        "RUN END total_distance=%.3f total_time=%.3f total_cost=%.2f total_co2=%.1f",
        total_distance,
        total_time,
        total_cost,
        total_co2,
    )


def main() -> None:
    """Main loop for the console menu."""
    settings = Settings()

    while True:
        print_menu(settings)
        choice = input("\nSelect menu option: ").strip()

        if choice == "1":
            settings.orders_path = input_non_empty("Enter path to orders CSV: ")
        elif choice == "2":
            settings.mode = choose_mode()
        elif choice == "3":
            settings.objective = choose_objective()
        elif choice == "4":
            print("\nChange depot coordinates:")
            settings.depot_lat = input_float("Latitude:  ")
            settings.depot_lon = input_float("Longitude: ")
        elif choice == "5":
            run_optimization(settings)
        elif choice == "0":
            print("Exiting CourierOptimizer.")
            break
        else:
            print("Unknown option, please try again.")
