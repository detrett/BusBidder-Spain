import unittest
from datetime import datetime, timedelta

from busbidder.exceptions import DataValidationError
from busbidder.models import Company, Destination, RankingWeights
from busbidder.validators import validate_ranking_weights, validate_offer_references, validate_offer_values
from tests.helpers import make_offer


class TestRankingWeightValidation(unittest.TestCase):
    """Test that ranking weights contain valid values and total 1.0."""

    def test_accepts_weights_that_sum_to_one(self):
        weights = RankingWeights(
            price=0.4,
            duration=0.3,
            departure_time=0.2,
            flexibility=0.1,
        )

        validate_ranking_weights(weights)

    def test_rejects_weights_that_do_not_sum_to_one(self):
        weights = RankingWeights(
            price=0.4,
            duration=0.3,
            departure_time=0.2,
            flexibility=0.2,
        )

        with self.assertRaises(DataValidationError):
            validate_ranking_weights(weights)

    def test_rejects_negative_weight(self):
        weights = RankingWeights(
            price=-0.1,
            duration=0.5,
            departure_time=0.3,
            flexibility=0.3,
        )

        with self.assertRaises(DataValidationError):
            validate_ranking_weights(weights)

    def test_rejects_weight_greater_than_one(self):
        weights = RankingWeights(
            price=1.1,
            duration=0.0,
            departure_time=0.0,
            flexibility=0.0,
        )

        with self.assertRaises(DataValidationError):
            validate_ranking_weights(weights)

    def test_rejects_non_finite_weight(self):
        weights = RankingWeights(
            price=float("nan"),
            duration=0.5,
            departure_time=0.3,
            flexibility=0.2,
        )

        with self.assertRaises(DataValidationError):
            validate_ranking_weights(weights)


class TestOfferValueValidation(unittest.TestCase):
    """Test validation of individual offer values."""

    def test_accepts_valid_offer(self):
        validate_offer_values(make_offer(), line_number=2)

    def test_rejects_negative_price(self):
        with self.assertRaises(DataValidationError):
            validate_offer_values(
                make_offer(price_eur=-1.0),
                line_number=2,
            )

    def test_rejects_arrival_before_departure(self):
        departure_at = datetime(2026, 11, 2, 8, 0)

        with self.assertRaises(DataValidationError):
            validate_offer_values(
                make_offer(
                    departure_at=departure_at,
                    arrival_at=departure_at - timedelta(minutes=1),
                ),
                line_number=2,
            )

    def test_rejects_rating_above_five(self):
        with self.assertRaises(DataValidationError):
            validate_offer_values(
                make_offer(rating=5.1),
                line_number=2,
            )


class TestOfferReferenceValidation(unittest.TestCase):
    """Test that offers refer to existing companies and destinations."""

    def setUp(self):
        """Create the company and destination used by the valid offer."""
        self.companies = [
            Company(
                company_id="C001",
                name="SolRuta",
                description="A sample bus company.",
            )
        ]
        self.destinations = [
            Destination(
                destination_id="VAL",
                name="Valencia",
            )
        ]

    def test_accepts_offer_with_known_references(self):
        validate_offer_references(
            [make_offer()],
            self.companies,
            self.destinations,
        )

    def test_rejects_unknown_company(self):
        offer = make_offer(company_id="C999")

        with self.assertRaises(DataValidationError):
            validate_offer_references(
                [offer],
                self.companies,
                self.destinations,
            )

    def test_rejects_unknown_destination(self):
        offer = make_offer(destination_id="XXX")

        with self.assertRaises(DataValidationError):
            validate_offer_references(
                [offer],
                self.companies,
                self.destinations,
            )


if __name__ == "__main__":
    unittest.main()