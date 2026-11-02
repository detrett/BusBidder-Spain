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
