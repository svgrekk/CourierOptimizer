# CourierOptimizer – Part I of ACIT4420 Final Assignment
This repository contains **Part I** of the final assignment for the ACIT4420 Python scripting course at OsloMet.


# CourierOptimizer

CourierOptimizer is a small command-line tool for planning a courier route in Oslo.

Given a depot location and a list of customer deliveries with coordinates and urgency levels, it builds a route for a single courier and estimates:

- total travel distance,
- travel time,
- monetary cost (NOK),
- and CO₂ emissions.

The tool supports different transport modes (car, bicycle, walking), several optimisation objectives, and produces both CSV and graphical output.


## 1. Overview

The courier:

- starts from a fixed depot (latitude/longitude),
- visits each valid customer exactly once,
- optionally returns to the depot (depending on configuration),
- chooses the next stop using a greedy nearest-neighbour style heuristic.

Each delivery has:

- customer name,
- latitude and longitude (decimal degrees),
- urgency level: `High`, `Medium`, or `Low`,
- package weight (kg).

The user can choose:

- **transport mode**:
  - `car` – fastest, but with cost and emissions,
  - `bike` – slower, no cost, no emissions,
  - `walk` – slowest, no cost, no emissions;

- **objective**:
  - `FASTEST` – minimise total travel time,
  - `CHEAPEST` – minimise total monetary cost (NOK),
  - `LOWEST_CO2` – minimise total CO₂ emissions (g).

Urgency is implemented as a weight that modifies the edge cost:

- `High` → 0.6  
- `Medium` → 1.0  
- `Low` → 1.2  

High-priority customers are therefore more likely to be visited earlier in the tour.


## 2. Project Structure

Typical layout:

```text
.
├── CourierOptimizer/
│   ├── __init__.py
│   ├── __main__.py          # allows: python -m CourierOptimizer
│   ├── cli.py               # command-line menu
│   ├── delivery.py          # Delivery class, validation, priority weighting
│   ├── orders.py            # CSV loading, rejected rows
│   ├── distance.py          # haversine distance (haver_dist)
│   ├── transport_mode.py    # car / bike / walk parameters
│   ├── planner.py           # RoutPlanner, heuristic, route.csv and plot
│   ├── config.py            # paths, default depot, constants
│   ├── log.py               # logging setup (run.log)
│   ├── decorators.py        # @timed decorator for timing
│   └── files/
│       ├── orders.csv       # example input
│       ├── route.csv        # generated route
│       ├── rejected.csv     # invalid rows
│       ├── run.log          # log file
│       └── route.png        # route plot
│
└── tests/
    └── test_courieroptimizer.py
