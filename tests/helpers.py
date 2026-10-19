from datetime import datetime, timedelta

from busbidder.models import Offer


def make_offer(offer_id="O001", price_eur=40.0, departure_hour=8, **overrides):
    """
    Create a standard Offer for tests, with optional field changes.
    Args:
        offer_id: The offer's ID.
        price_eur: Its fare.
        departure_hour: The hour it departs.
        overrides: Other Offer fields to change.

    Returns:
        An Offer object.
    """
    departure_at = overrides.pop(
        "departure_at",
        datetime(2026, 11, 2, departure_hour),
    )
    arrival_at = overrides.pop(
        "arrival_at",
        departure_at + timedelta(hours=2),
    )

    values = {
        "offer_id": offer_id,
        "company_id": "C001",
        "destination_id": "VAL",
        "departure_at": departure_at,
        "arrival_at": arrival_at,
        "price_eur": price_eur,
        "transfers": 0,
        "luggage_kg": 20,
        "changeable": True,
        "refundable": True,
        "seats_available": 5,
        "rating": 4.5,
    }
    values.update(overrides)
    return Offer(**values)