from math import isfinite

from busbidder.exceptions import DataValidationError
from busbidder.models import Company, Destination, Offer


def validate_offer_values(offer, line_number):
    """
    Check that an offer's converted numerical values are valid (logically).
        Args:
            offer: The Offer object to check.
            line_number: The offer's line number in offers.csv.

        Raises:
            DataValidationError: If an offer value is impossible or out of range.
    """

    # The value of prices and ratings has to be a finite number within a defined range
    if not isfinite(offer.price_eur) or offer.price_eur < 0:
        raise DataValidationError( f"offers.csv, line {line_number}: price_eur must be a positive number")

    if offer.transfers < 0:
        raise DataValidationError(f"offers.csv, line {line_number}: transfers cannot be negative.")

    if offer.luggage_kg < 0:
        raise DataValidationError(f"offers.csv, line {line_number}: luggage_kg cannot be negative.")

    if offer.seats_available < 0:
        raise DataValidationError(f"offers.csv, line {line_number}: seats_available cannot be negative.")

    if not isfinite(offer.rating) or not 0 <= offer.rating <= 5:
        raise DataValidationError(f"offers.csv, line {line_number}: rating must be between 0 and 5.")

    if offer.arrival_at <= offer.departure_at:
        raise DataValidationError(f"offers.csv, line {line_number}: arrival_at must be after departure_at.")


def validate_offer_references(offers, companies, destinations):
    """
    Check that every offer refers to a known, valid company and destination.
        Args:
            offers: The Offer objects to check.
            companies: The Company objects available in the marketplace.
            destinations: The Destination objects available in the marketplace.

        Raises:
            DataValidationError: If an offer refers to an unknown company or destination.
    """
    company_ids = {company.company_id for company in companies}
    destination_ids = {destination.destination_id for destination in destinations}

    for line_number, offer in enumerate(offers, start=2):
        if offer.company_id not in company_ids:
            raise DataValidationError(f"offers.csv, line {line_number}: unknown company_id ({offer.company_id})")

        if offer.destination_id not in destination_ids:
            raise DataValidationError(f"offers.csv, line {line_number}: unknown destination_id ({offer.destination_id})")
