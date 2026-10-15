from busbidder.models import SearchRequest, Offer


def filter_offers(offers, request):
    """
    Return offers that meet the traveler's search constraints.
        Args:
            offers: All available Offer objects.
            request: The traveler's SearchRequest.

        Returns:
            A list of offers that meet every hard constraint.
    """
    matching_offers = []

    for offer in offers:

        if offer.destination_id != request.destination_id:
            continue

        travel_date = offer.departure_at.date()
        if not request.earliest_date <= travel_date <= request.latest_date:
            continue

        if offer.price_eur > request.max_price_eur:
            continue

        if offer.transfers > request.max_transfers:
            continue

        if request.require_changeable and not offer.changeable:
            continue

        if offer.seats_available <= 0:
            continue

        matching_offers.append(offer)

    return matching_offers