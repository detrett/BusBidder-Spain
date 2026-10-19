from datetime import date
import unittest

from busbidder.models import (
    RankingWeights,
    SearchRequest,
    TravelerProfile,
)
from busbidder.ranking import rank_offers
from tests.helpers import make_offer


class TestRankOffers(unittest.TestCase):
    """Test weighted scoring and ordering of offers."""

    def setUp(self):
        """Create a search request and a profile that prioritizes price."""
        self.request = SearchRequest(
            destination_id="VAL",
            earliest_date=date(2026, 11, 2),
            latest_date=date(2026, 11, 2),
            max_price_eur=100.0,
            max_transfers=2,
            require_changeable=False,
        )
        self.price_profile = TravelerProfile(
            name="Price-focused",
            weights=RankingWeights(
                price=1.0,
                duration=0.0,
                departure_time=0.0,
                flexibility=0.0,
            ),
        )

    def test_lower_price_ranks_higher_when_only_price_matters(self):
        expensive = make_offer("O002", price_eur=50.0)
        cheaper = make_offer("O001", price_eur=30.0)

        results = rank_offers(
            [expensive, cheaper],
            self.price_profile,
            self.request,
        )

        self.assertEqual(
            [result.offer.offer_id for result in results],
            ["O001", "O002"],
        )

    def test_equal_scores_are_sorted_by_offer_id(self):
        second_id = make_offer("O002", price_eur=40.0)
        first_id = make_offer("O001", price_eur=40.0)

        results = rank_offers(
            [second_id, first_id],
            self.price_profile,
            self.request,
        )

        self.assertEqual(
            [result.offer.offer_id for result in results],
            ["O001", "O002"],
        )

    def test_departure_time_score_is_neutral_without_a_preference(self):
        time_profile = TravelerProfile(
            name="Time-focused",
            weights=RankingWeights(
                price=0.0,
                duration=0.0,
                departure_time=1.0,
                flexibility=0.0,
            ),
        )
        morning_offer = make_offer("O001", price_eur=40.0, departure_hour=8)
        evening_offer = make_offer("O002", price_eur=40.0, departure_hour=22)

        results = rank_offers(
            [morning_offer, evening_offer],
            time_profile,
            self.request,
        )

        self.assertEqual(
            [result.departure_time_score for result in results],
            [50.0, 50.0],
        )

    def test_empty_offer_list_returns_empty_list(self):
        results = rank_offers([], self.price_profile, self.request)

        self.assertEqual(results, [])


if __name__ == "__main__":
    unittest.main()