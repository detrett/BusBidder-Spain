from math import isfinite

from busbidder.exceptions import DataValidationError


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