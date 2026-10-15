import csv
import re
from datetime import datetime, timezone
from math import isfinite
from pathlib import Path
from uuid import uuid4

from busbidder.exceptions import (
    DataLoadError,
    DataSaveError,
    DataValidationError,
)
from busbidder.helpers import parse_boolean
from busbidder.models import Booking


DATA_DIR = Path(__file__).resolve().parent.parent / "data"
BOOKINGS_FILE = DATA_DIR / "bookings.csv"
BOOKING_COLUMNS = (
    "booking_reference",
    "offer_id",
    "booked_at",
    "price_eur",
    "changeable",
    "refundable",
)
BOOKING_REFERENCE_PATTERN = re.compile(r"BB-[A-F0-9]{8}")


def load_bookings():
    """
    Load saved bookings from bookings.csv.
        Returns:
            A list of Booking objects, or an empty list if no booking file exists.

        Raises:
            DataLoadError: If the file cannot be read or has missing columns.
            DataValidationError: If a saved booking contains invalid values.
    """
    if not BOOKINGS_FILE.exists():
        return []

    try:
        with BOOKINGS_FILE.open("r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)

            if reader.fieldnames is None:
                raise DataLoadError("bookings.csv is missing its header.")

            missing_columns = set(BOOKING_COLUMNS) - set(reader.fieldnames)
            if missing_columns:
                missing = ", ".join(sorted(missing_columns))
                raise DataLoadError(
                    f"bookings.csv is missing required column(s): {missing}"
                )

            bookings = []
            seen_references = set()

            for line_number, row in enumerate(reader, start=2):
                reference = row["booking_reference"]
                offer_id = row["offer_id"]

                if (
                        not isinstance(reference, str)
                        or not BOOKING_REFERENCE_PATTERN.fullmatch(reference)
                ):
                    raise DataValidationError(
                        f"bookings.csv, line {line_number}: "
                        "invalid booking reference."
                    )

                if reference in seen_references:
                    raise DataValidationError(
                        f"bookings.csv, line {line_number}: "
                        f"duplicate booking reference '{reference}'."
                    )

                if not offer_id or not offer_id.strip():
                    raise DataValidationError(
                        f"bookings.csv, line {line_number}: "
                        "offer_id cannot be blank."
                    )

                try:
                    booking = Booking(
                        booking_reference=reference,
                        offer_id=offer_id,
                        booked_at=datetime.fromisoformat(row["booked_at"]),
                        price_eur=float(row["price_eur"]),
                        changeable=parse_boolean(row["changeable"]),
                        refundable=parse_boolean(row["refundable"]),
                    )
                except (TypeError, ValueError) as error:
                    raise DataValidationError(
                        f"bookings.csv, line {line_number}: "
                        f"invalid booking value: {error}"
                    ) from error

                if not isfinite(booking.price_eur) or booking.price_eur < 0:
                    raise DataValidationError(
                        f"bookings.csv, line {line_number}: "
                        "price_eur must be a nonnegative, finite number."
                    )

                bookings.append(booking)
                seen_references.add(reference)

        return bookings

    except OSError as error:
        raise DataLoadError(f"Could not read bookings.csv: {error}") from error


def generate_booking_reference(existing_bookings):
    """
    Create a booking reference that isn't already in use.
        Args:
            existing_bookings: The saved Booking objects to check against.

        Returns:
            A unique reference such as "BB-A1B2C3D4".
    """
    existing_references = {
        booking.booking_reference
        for booking in existing_bookings
    }

    while True:
        reference = f"BB-{uuid4().hex[:8].upper()}"

        if reference not in existing_references:
            return reference


def create_booking(offer, existing_bookings):
    """
    Create a booking record for one seat on an offer.
        Args:
            offer: The Offer being booked.
            existing_bookings: The saved Booking objects used to avoid duplicate references.

        Returns:
            A Booking that snapshots the offer's price and ticket conditions.
    """
    return Booking(
        booking_reference=generate_booking_reference(existing_bookings),
        offer_id=offer.offer_id,
        booked_at=datetime.now(timezone.utc),
        price_eur=offer.price_eur,
        changeable=offer.changeable,
        refundable=offer.refundable,
    )


def save_booking(booking):
    """
    Append a booking to bookings.csv, creating the file if needed.
        Args:
            booking: The Booking object to save.

        Raises:
            DataSaveError: If the booking file cannot be written.
            DataValidationError: If its reference is already saved.
    """
    existing_bookings = load_bookings()

    if any(
            saved.booking_reference == booking.booking_reference
            for saved in existing_bookings
    ):
        raise DataValidationError(
            f"Duplicate booking reference: {booking.booking_reference}"
        )

    try:
        file_needs_header = (
                not BOOKINGS_FILE.exists()
                or BOOKINGS_FILE.stat().st_size == 0
        )

        with BOOKINGS_FILE.open("a", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=BOOKING_COLUMNS)

            if file_needs_header:
                writer.writeheader()

            writer.writerow(
                {
                    "booking_reference": booking.booking_reference,
                    "offer_id": booking.offer_id,
                    "booked_at": booking.booked_at.isoformat(),
                    "price_eur": booking.price_eur,
                    "changeable": str(booking.changeable).lower(),
                    "refundable": str(booking.refundable).lower(),
                }
            )

    except OSError as error:
        raise DataSaveError(f"Could not save booking: {error}") from error


def apply_bookings_to_offers(offers, bookings):
    """
    Subtract saved bookings from the available seats on each offer.
        Args:
            offers: The Offer objects loaded from offers.csv.
            bookings: The saved Booking objects loaded from bookings.csv.

        Raises:
            DataValidationError: If a booking refers to an unknown offer or
                the saved bookings exceed an offer's original capacity.
    """
    offers_by_id = {
        offer.offer_id: offer
        for offer in offers
    }
    bookings_per_offer = {}

    # Count how many seats have been booked for each offer.
    for booking in bookings:
        if booking.offer_id not in offers_by_id:
            raise DataValidationError(
                f"Booking {booking.booking_reference} refers to unknown "
                f"offer '{booking.offer_id}'."
            )

        bookings_per_offer[booking.offer_id] = (
                bookings_per_offer.get(booking.offer_id, 0) + 1
        )

    # Subtract booked seats from the offer's original capacity.
    for offer_id, booking_count in bookings_per_offer.items():
        offer = offers_by_id[offer_id]

        if booking_count > offer.seats_available:
            raise DataValidationError(
                f"Saved bookings exceed the original capacity for offer "
                f"'{offer_id}'."
            )

        offer.seats_available -= booking_count