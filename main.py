from busbidder.cli import (
    choose_traveler_profile,
    collect_search_request,
)
from busbidder.data_loader import (
    load_companies,
    load_destinations,
    load_offers,
)
from busbidder.profiles import get_traveler_profiles
from busbidder.search import filter_offers
from busbidder.validators import validate_offer_references

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
    """Load the marketplace data, collect a search request, show matching offers."""
    # Load each source dataset from the data folder
    companies = load_companies(COMPANY_COLUMNS)
    destinations = load_destinations(DESTINATION_COLUMNS)
    offers = load_offers(OFFER_COLUMNS)

    validate_offer_references(offers, companies, destinations)

    print (f"Loaded {len(companies)} companies")
    print (f"Loaded {len(destinations)} destinations")
    print (f"Loaded {len(offers)} offers")

    request = collect_search_request(destinations)
    matching_offers = filter_offers(offers, request)

    print(f"\nOffers meeting your constraints: {len(matching_offers)}")

    if not matching_offers:
        print("No offers match this search.")
        return

    profiles = get_traveler_profiles()
    selected_profile = choose_traveler_profile(profiles)

    print(f"\nSelected profile: {selected_profile.name}")
    print("Matching offers (not ranked yet):")

    company_names = {
        company.company_id: company.name
        for company in companies
    }

    for offer in matching_offers:
        changeable_text = "Yes" if offer.changeable else "No"
        print(
            f"{company_names[offer.company_id]} | "
            f"{offer.departure_at:%Y-%m-%d %H:%M} to "
            f"{offer.arrival_at:%Y-%m-%d %H:%M} | "
            f"EUR {offer.price_eur:.2f} | "
            f"{offer.transfers} transfers | "
            f"Changeable: {changeable_text}"
        )

if __name__ == "__main__":
    main()