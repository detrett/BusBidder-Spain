from busbidder.models import RankedOffer


def _score_lower_is_better(value, lowest_value, highest_value):
    """Convert a value into a 0–100 score where lower values score higher."""
    if lowest_value == highest_value:
        return 50.0

    return (highest_value - value) / (highest_value - lowest_value) * 100


def _departure_time_distance(offer, preferred_time):
    """Return the shortest clock-time distance from an offer to the preference."""
    departure_minutes = (offer.departure_at.hour * 60 + offer.departure_at.minute)
    preferred_minutes = (preferred_time.hour * 60 + preferred_time.minute)

    difference = abs(departure_minutes - preferred_minutes)

    # Times near midnight are close to each other
    return min(difference, 24 * 60 - difference)


def sort_key(result):
    """Put higher scores first, then sort tied offers by offer ID."""
    return -result.total_score, result.offer.offer_id


def rank_offers(offers, profile, request):
    """
    Score and sort acceptable offers using a traveller's profile weights.
        Args:
            offers: The offers that passed the hard search constraints.
            profile: The selected TravelerProfile and its ranking weights.
            request: The traveller's SearchRequest, including any preferred time.

        Returns:
            RankedOffer objects sorted from highest score to lowest.
    """
    if not offers:
        return []

    prices = [offer.price_eur for offer in offers]
    durations = [offer.duration_minutes for offer in offers]

    if request.preferred_departure_time is None:
        time_distances = None
    else:
        time_distances = [
            _departure_time_distance(offer, request.preferred_departure_time)
            for offer in offers
        ]

    ranked_offers = []

    for index, offer in enumerate(offers):
        price_score = _score_lower_is_better(offer.price_eur, min(prices), max(prices))
        duration_score = _score_lower_is_better(offer.duration_minutes, min(durations), max(durations))

        if time_distances is None:
            departure_time_score = 50.0
        else:
            departure_time_score = _score_lower_is_better(time_distances[index], min(time_distances), max(time_distances))

        flexibility_score = 0.0
        if offer.changeable:
            flexibility_score += 50.0
        if offer.refundable:
            flexibility_score += 50.0

        weights = profile.weights
        total_score = (
                weights.price * price_score
                + weights.duration * duration_score
                + weights.departure_time * departure_time_score
                + weights.flexibility * flexibility_score
        )

        ranked_offers.append(
            RankedOffer(
                offer=offer,
                price_score=price_score,
                duration_score=duration_score,
                departure_time_score=departure_time_score,
                flexibility_score=flexibility_score,
                total_score=total_score,
            )
        )

    return sorted(ranked_offers, key=sort_key)