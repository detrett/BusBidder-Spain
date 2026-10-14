from busbidder.data_loader import load_csv, validate_unique_ids

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
    companies = load_csv("companies.csv", COMPANY_COLUMNS)
    destinations = load_csv("destinations.csv", DESTINATION_COLUMNS)
    offers = load_csv("offers.csv", OFFER_COLUMNS)

    # Check that each type of record has a distinct ID.
    validate_unique_ids(companies, "companies.csv", "company_id")
    validate_unique_ids(destinations, "destinations.csv", "destination_id")
    validate_unique_ids(offers, "offers.csv", "offer_id")

    print (f"Loaded {len(companies)} companies")
    print (f"Loaded {len(destinations)} destinations")
    print (f"Loaded {len(offers)} offers")


if __name__ == "__main__":
    main()