# BusBidder Spain

BusBidder Spain is a Python application for searching and comparing simulated bus offers from Madrid. It filters offers against a traveler's requirements, ranks the remaining offers using a selected traveler profile, explains the highest-ranked offer, and supports simulated bookings.

## Requirements

- Python 3.10 or later
- Python standard library
- Tkinter for the GUI

Run the commands below from the project root folder.

## Run the command-line application

```text
python main.py
```

## Run the graphical application

```text
python -m busbidder.gui
```

## Data and log

- `data/companies.csv` contains the five simulated bus companies.
- `data/destinations.csv` contains fifteen destinations served from Madrid.
- `data/offers.csv` contains 75 sample offers.
- `data/bookings.csv` is created automatically when the first booking is made. It stores bookings locally so seat availability is reduced on later runs.

The application writes its log to `busbidder.log` in the project root.

## Run the tests

```text
python -m unittest discover -s tests
```

## Reproduce the report's profile comparison

The report compares the traveler profiles using the same search:

- Destination: Valencia (`VAL`)
- First and last travel dates: `2026-11-02`
- Maximum budget: `80` EUR
- Maximum transfers: `0`
- Require a changeable ticket: No
- Preferred departure time: None

To reproduce the results, make sure `data/bookings.csv` is absent so previous bookings do not affect seat counts. Run `python main.py` three times. For each run, enter the search values above, press Enter at the preferred departure time prompt, and choose a different profile:

1. `1` — Budget focused
2. `2` — Business
3. `3` — Flexibility focused

At the offer booking prompt, press Enter to skip booking.

Each run should find 5 offers. The top-ranked results should be:

| Profile | Top offer | Total score | Criterion scores: price, duration, departure, flexibility, rating |
| --- | --- | ---: | --- |
| Budget focused | SolRuta (`O0201`) | 68.82/100 | 100.0, 19.7, 50.0, 0.0, 78.0 |
| Business | Camino Express (`O0202`) | 62.30/100 | 0.0, 100.0, 50.0, 50.0, 82.0 |
| Flexibility focused | VerdeBus (`O0204`) | 79.98/100 | 78.9, 24.2, 50.0, 100.0, 90.0 |

The budget profile ranks SolRuta first, the cheapest offer. The Business profile ranks Camino Express first, with the shortest journey. The Flexibility focused profile ranks VerdeBus first as its ticket is both changeable and refundable.
