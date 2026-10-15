from busbidder.booking import (
    apply_bookings_to_offers,
    create_booking,
    load_bookings,
    save_booking,
)
from busbidder.cli import (
    choose_offer_to_book,
    choose_traveler_profile,
    collect_search_request,
    confirm_booking,
)
from busbidder.data_loader import (
    load_companies,
    load_destinations,
    load_offers,
)
from busbidder.profiles import get_traveler_profiles
from busbidder.ranking import rank_offers
from busbidder.recommendations import explain_recommendation
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

    bookings = load_bookings()
    apply_bookings_to_offers(offers, bookings)

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

    ranked_offers = rank_offers(matching_offers, selected_profile, request)

    print(f"\nOffers ranked for a {selected_profile.name} profile:")

    company_names = {
        company.company_id: company.name
        for company in companies
    }

    for position, result in enumerate(ranked_offers, start=1):
        offer = result.offer
        company_name = company_names[offer.company_id]
        changeable_text = "Yes" if offer.changeable else "No"
        refundable_text= "Yes" if offer.refundable else "No"

        print(
            f"\n{position}. {company_name} | "
            f"Total score: {result.total_score:.2f}/100"
        )
        print(
            f"   {offer.departure_at:%Y-%m-%d %H:%M} to "
            f"{offer.arrival_at:%Y-%m-%d %H:%M} | "
            f"EUR {offer.price_eur:.2f} | "
            f"{offer.duration_minutes} minutes | "
            f"{offer.transfers} transfers | "
            f"Seats available: {offer.seats_available}"
        )
        print(
            f"   Changeable: {changeable_text} | "
            f"Refundable: {refundable_text}"
        )
        print(
            f"   Scores - Price: {result.price_score:.1f}, "
            f"Duration: {result.duration_score:.1f}, "
            f"Departure time: {result.departure_time_score:.1f}, "
            f"Flexibility: {result.flexibility_score:.1f}"
        )

    top_result = ranked_offers[0]
    top_company_name = company_names[top_result.offer.company_id]

    print("\nWhy this offer ranks first:")
    print(
        explain_recommendation(
            top_result,
            request,
            selected_profile,
            top_company_name,
        )
    )

    selected_offer = choose_offer_to_book(ranked_offers)

    if selected_offer is None:
        print("No booking was made.")
        return

    if not confirm_booking():
        print("Booking cancelled.")
        return

    booking = create_booking(selected_offer, bookings)
    save_booking(booking)

    print("\nBooking confirmed!")
    print(f"Booking reference: {booking.booking_reference}")
    print(f"Offer: {booking.offer_id}")
    print(f"Price: EUR {booking.price_eur:.2f}")



if __name__ == "__main__":
    main()