import csv
from datetime import datetime
from pathlib import Path

from busbidder.exceptions import DataLoadError, DataValidationError
from busbidder.helpers import parse_boolean
from busbidder.models import Company, Destination, Offer

# Find the project's data folder relative to this module
DATA_DIR = Path(__file__).resolve().parent.parent / "data"

def load_csv(filename, required_columns):
    """
    Load a CSV file and check that it has the required columns.
        Args:
            filename: The CSV file's name, such as "companies.csv".
            required_columns: The headers that must be present in the file.

        Returns:
            A list of dictionaries, one for each CSV row.

        Raises:
            DataLoadError: If the file cannot be opened or has an invalid structure.
    """
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


def validate_unique_ids(rows, filename, id_column):
    """
    Check that every row has a unique, nonblank value in the ID column.
        Args:
            rows: The CSV rows to check.
            filename: The file's name, used in error messages.
            id_column: The column whose values must be unique.

        Raises:
            DataValidationError: If an ID is blank, has extra spaces, or is duplicated.
    """
    seen_ids = set()

    # Skip the header, start on line 2
    for line_number, row in enumerate(rows, start=2):
        identifier = row[id_column]

        if identifier is None or not identifier.strip():
            raise DataValidationError(f"{filename}, line {line_number}: {id_column} cannot be blank.")

        if identifier != identifier.strip():
            raise DataValidationError(f"{filename}, line {line_number}: {id_column} has extra spaces.")

        if identifier in seen_ids:
            raise DataValidationError(f"{filename}, line {line_number}: duplicate {id_column} "
                f"'{identifier}'.")

        seen_ids.add(identifier)


def load_companies(required_columns):
    """
    Load company rows and convert them into Company objects.
        Args:
            required_columns: The headers required in companies.csv.

        Returns:
            A list of Company objects.
    """
    rows = load_csv("companies.csv", required_columns)
    validate_unique_ids(rows, "companies.csv", "company_id")

    # Convert each row into a Company object
    companies = []
    for row in rows:
        company = Company(
            company_id=row["company_id"],
            name=row["name"],
            description=row["description"],
        )
        companies.append(company)

    return companies


def load_destinations(required_columns):
    """
    Load destination rows and convert them into Destination objects.
        Args:
            required_columns: The headers required in destinations.csv.

        Returns:
            A list of Destination objects.
    """
    rows = load_csv("destinations.csv", required_columns)
    validate_unique_ids(rows, "destinations.csv", "destination_id")

    # Convert each row into a Destination object
    destinations = []
    for row in rows:
        destination = Destination(
            destination_id=row["destination_id"],
            name=row["name"],
        )
        destinations.append(destination)

    return destinations


def load_offers(required_columns):
    """
    Load offer rows and convert them into Offer objects.
       Args:
           required_columns: The headers required in offers.csv.

       Returns:
           A list of Offer objects.

       Raises:
           DataValidationError: If an offer value cannot be converted.
    """
    rows = load_csv("offers.csv", required_columns)
    validate_unique_ids(rows, "offers.csv", "offer_id")

    # Convert each row into an Offer object
    offers = []
    for line_number, row in enumerate(rows, start=2):
        try:
            offer = Offer(
                offer_id=row["offer_id"],
                company_id=row["company_id"],
                destination_id=row["destination_id"],
                departure_at=datetime.fromisoformat(row["departure_at"]),
                arrival_at=datetime.fromisoformat(row["arrival_at"]),
                price_eur=float(row["price_eur"]),
                transfers=int(row["transfers"]),
                luggage_kg=int(row["luggage_kg"]),
                changeable=parse_boolean(row["changeable"]),
                refundable=parse_boolean(row["refundable"]),
                seats_available=int(row["seats_available"]),
                rating=float(row["rating"]),
            )
        except (TypeError, ValueError) as error:
            raise DataValidationError(
                f"offers.csv, line {line_number}: invalid offer value: {error}"
            ) from error

        offers.append(offer)

    return offers