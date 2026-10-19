from datetime import datetime, date
import unittest

from busbidder.models import SearchRequest
from busbidder.search import filter_offers
from tests.helpers import make_offer


def make_request(**overrides):
    """
    Create a basic SearchRequest for a test, replacing specified values.
    Args:
        overrides: SearchRequest fields to change for a particular test.

    Returns:
        A SearchRequest object.
    """
    values = {
        "destination_id": "VAL",
        "earliest_date": date(2026, 11, 2),
        "latest_date": date(2026, 11, 2),
        "max_price_eur": 50.0,
        "max_transfers": 0,
        "require_changeable": False,
    }
    values.update(overrides)
    return SearchRequest(**values)

class TestFilterOffers(unittest.TestCase):
    """Test that search filters out offers that break the request constraints."""

    def test_keeps_offer_that_meets_all_constraints(self):
        offer = make_offer()

        results = filter_offers([offer], make_request())

        self.assertEqual(results, [offer])

    def test_excludes_offer_for_different_destination(self):
        offer = make_offer(destination_id="BCN")

        results = filter_offers([offer], make_request())

        self.assertEqual(results, [])

    def test_excludes_offer_over_budget(self):
        offer = make_offer(price_eur=50.01)

        results = filter_offers([offer], make_request())

        self.assertEqual(results, [])

    def test_excludes_offer_with_too_many_transfers(self):
        offer = make_offer(transfers=1)

        results = filter_offers([offer], make_request())

        self.assertEqual(results, [])

    def test_excludes_offer_without_available_seats(self):
        offer = make_offer(seats_available=0)

        results = filter_offers([offer], make_request())

        self.assertEqual(results, [])

    def test_changeable_requirement_only_excludes_non_changeable_offers(self):
        changeable_offer = make_offer(changeable=True)
        non_changeable_offer = make_offer(offer_id="O002", changeable=False)
        request = make_request(require_changeable=True)

        results = filter_offers(
            [changeable_offer, non_changeable_offer],
            request,
        )

        self.assertEqual(results, [changeable_offer])

    def test_excludes_offer_outside_requested_dates(self):
        offer = make_offer(
            departure_at=datetime(2026, 11, 3, 8, 0),
            arrival_at=datetime(2026, 11, 3, 12, 0),
        )

        results = filter_offers([offer], make_request())

        self.assertEqual(results, [])


if __name__ == "__main__":
    unittest.main()