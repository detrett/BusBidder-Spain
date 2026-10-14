from busbidder.data_loader import (
    load_companies,
    load_csv,
    load_destinations,
    validate_unique_ids,
)

# List of the required headers for each CSV file
COMPANY_COLUMNS = ("company_id", "name", "description")
DESTINATION_COLUMNS = ("destination_id", "name")
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

def main():
    """Load the marketplace data and display the number of records in each file."""
    # Load each source dataset from the data folder
    companies = load_companies(COMPANY_COLUMNS)
    destinations = load_destinations(DESTINATION_COLUMNS)

    offer_rows = load_csv("offers.csv", OFFER_COLUMNS)
    validate_unique_ids(offer_rows, "offers.csv", "offer_id")

    print (f"Loaded {len(companies)} companies")
    print (f"Loaded {len(destinations)} destinations")
    print (f"Loaded {len(offer_rows)} offers")


if __name__ == "__main__":
    main()