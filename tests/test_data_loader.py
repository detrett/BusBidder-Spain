import csv
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from busbidder.data_loader import load_csv, load_offers
from busbidder.exceptions import DataLoadError, DataValidationError
from busbidder.models import Offer


OFFER_COLUMNS = (
    "offer_id",
    "company_id",
    "destination_id",
    "departure_at",
    "arrival_at",
    "price_eur",
    "transfers",
    "luggage_kg",
    "changeable",
    "refundable",
    "seats_available",
    "rating",
)


class TestDataLoader(unittest.TestCase):
    """Test CSV structure checks and conversion of offer rows."""

    def setUp(self):
        """Set up a temporary data folder so tests don't alter project CSVs."""
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)

        self.data_directory = Path(self.temporary_directory.name)
        data_directory_patch = patch(
            "busbidder.data_loader.DATA_DIR",
            self.data_directory,
        )
        data_directory_patch.start()
        self.addCleanup(data_directory_patch.stop)

    def write_csv(self, filename, headers, rows):
        """
        Write a small CSV file into the temporary data folder.

        Args:
            filename: The CSV file's name.
            headers: The column names to write.
            rows: The row dictionaries to write.
        """
        path = self.data_directory / filename

        with path.open("w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=headers)
            writer.writeheader()
            writer.writerows(rows)

    def test_load_csv_returns_rows(self):
        headers = ("company_id", "name")
        rows = [{"company_id": "C001", "name": "SolRuta"}]
        self.write_csv("companies.csv", headers, rows)

        result = load_csv("companies.csv", headers)

        self.assertEqual(result, list(rows))

    def test_load_csv_rejects_missing_required_column(self):
        headers = ("company_id", "name")
        self.write_csv(
            "companies.csv",
            headers,
            [{"company_id": "C001", "name": "SolRuta"}],
        )

        with self.assertRaises(DataLoadError):
            load_csv(
                "companies.csv",
                ("company_id", "name", "description"),
            )

    def test_load_csv_rejects_file_with_header_but_no_rows(self):
        headers = ("company_id", "name")
        self.write_csv("companies.csv", headers, [])

        with self.assertRaises(DataLoadError):
            load_csv("companies.csv", headers)

    def test_load_offers_converts_csv_values_to_correct_types(self):
        row = {
            "offer_id": "O001",
            "company_id": "C001",
            "destination_id": "VAL",
            "departure_at": "2026-11-02T08:00:00",
            "arrival_at": "2026-11-02T10:00:00",
            "price_eur": "40.0",
            "transfers": "0",
            "luggage_kg": "20",
            "changeable": "true",
            "refundable": "false",
            "seats_available": "5",
            "rating": "4.5",
        }
        self.write_csv("offers.csv", OFFER_COLUMNS, [row])

        offers = load_offers(OFFER_COLUMNS)

        self.assertEqual(len(offers), 1)
        self.assertIsInstance(offers[0], Offer)
        self.assertEqual(offers[0].price_eur, 40.0)
        self.assertTrue(offers[0].changeable)
        self.assertFalse(offers[0].refundable)

    def test_load_offers_rejects_invalid_price_text(self):
        row = {
            "offer_id": "O001",
            "company_id": "C001",
            "destination_id": "VAL",
            "departure_at": "2026-11-02T08:00:00",
            "arrival_at": "2026-11-02T10:00:00",
            "price_eur": "not-a-price",
            "transfers": "0",
            "luggage_kg": "20",
            "changeable": "true",
            "refundable": "false",
            "seats_available": "5",
            "rating": "4.5",
        }
        self.write_csv("offers.csv", OFFER_COLUMNS, [row])

        with self.assertRaisesRegex(DataValidationError, "line 2"):
            load_offers(OFFER_COLUMNS)


if __name__ == "__main__":
    unittest.main()