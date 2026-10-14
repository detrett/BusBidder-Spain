import csv
from pathlib import Path

from busbidder.exceptions import DataLoadError

# Find the project's data folder relative to this module
DATA_DIR = Path(__file__).resolve().parent.parent / "data"

def load_csv(filename, required_columns):
    # Path to the CSV file
    path = DATA_DIR / filename

    try:
        # Open the file and read each row as a dictionary
        with path.open("r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)

            # Check that the file has a header row
            if reader.fieldnames is None:
                raise DataLoadError(f"{filename} is empty or is missing a header.")

            # Check that the file has all columns the program needs
            missing_columns = set(required_columns) - set(reader.fieldnames)
            if missing_columns:
                missing = ", ".join(sorted(missing_columns))
                raise DataLoadError(f"{filename} is missing the required column(s): {missing}")

            rows = list(reader)

            if not rows:
                raise DataLoadError(f"{filename} has a header but no data rows.")

            return rows
    # Catch file access errors
    except OSError as error:
        raise DataLoadError(f"Could not open {filename}: {error}") from error