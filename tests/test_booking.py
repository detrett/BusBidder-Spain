from datetime import datetime, timedelta
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from busbidder.booking import (
    apply_bookings_to_offers,
    create_booking,
    load_bookings,
    save_booking,
)
from busbidder.exceptions import DataValidationError
from tests.helpers import make_offer


class TestBooking(unittest.TestCase):
    """Test booking creation, seat counts, and CSV persistence."""

    def test_create_booking_snapshots_offer_details(self):
        offer = make_offer()

        booking = create_booking(offer, [])

        self.assertEqual(booking.offer_id, offer.offer_id)
        self.assertEqual(booking.price_eur, offer.price_eur)
        self.assertEqual(booking.changeable, offer.changeable)
        self.assertEqual(booking.refundable, offer.refundable)
        self.assertRegex(booking.booking_reference, r"^BB-[A-F0-9]{8}$")

    def test_applies_booking_by_decreasing_available_seats(self):
        offer = make_offer(seats_available=5)
        booking = create_booking(offer, [])

        apply_bookings_to_offers([offer], [booking])

        self.assertEqual(offer.seats_available, 4)

    def test_saving_and_loading_preserves_booking(self):
        offer = make_offer()
        booking = create_booking(offer, [])

        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary_file = Path(temporary_directory) / "bookings.csv"

            with patch("busbidder.booking.BOOKINGS_FILE", temporary_file):
                save_booking(booking)
                loaded_bookings = load_bookings()

        self.assertEqual(loaded_bookings, [booking])

    def test_rejects_booking_for_unknown_offer(self):
        available_offer = make_offer(offer_id="O001")
        booking_for_unknown_offer = create_booking(
            make_offer(offer_id="O999"),
            [],
        )

        with self.assertRaises(DataValidationError):
            apply_bookings_to_offers(
                [available_offer],
                [booking_for_unknown_offer],
            )


if __name__ == "__main__":
    unittest.main()