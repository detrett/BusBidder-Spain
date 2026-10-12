# BusBidder Spain

ACIT4420 Scripting final project: a simulated bus offer marketplace for journeys from Madrid. The application will load offers from CSV files, validate and filter them, rank acceptable offers using traveller preferences, explain recommendations, and support simulated bookings.

## Requirements

- Python 3.10 or later
- No third-party packages are required for the initial implementation; it uses the Python standard library.

## Run the application

From the project root, run:

```text
python main.py
```

The entry point is currently a placeholder and will be implemented during development.

## Data files

- `data/companies.csv` contains the five simulated bus companies.
- `data/destinations.csv` contains the fifteen destinations.
- `data/offers.csv` contains 75 sample offers, one for every company-destination combination. Sample departures are dated November 1–7, 2026.

## Run the tests

From the project root, run:

```text
python -m unittest discover -s tests
```

Test cases will be added as the application is developed.
