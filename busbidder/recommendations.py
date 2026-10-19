def explain_recommendation(result, request, profile, company_name):
    """Explain why the top ranked offer scores well and describe its downsides.
         Args:
            result: The top offer's RankedOffer object.
            request: The traveler's SearchRequest.
            profile: The selected TravelerProfile.
            company_name: The name of the offer's bus company.

        Returns:
            A short explanation of the offer's ranking.
        """
    offer = result.offer

    # Describe the flexibility of the offer
    if offer.changeable and offer.refundable:
        flexibility_detail = "the ticket is changeable and refundable"
    elif offer.changeable:
        flexibility_detail = "the ticket is changeable, but not refundable"
    elif offer.refundable:
        flexibility_detail = "the ticket is refundable, but not changeable"
    else:
        flexibility_detail = "the ticket is neither changeable nor refundable"

    criteria = [
        ("price", result.price_score, f"the fare is EUR {offer.price_eur:.2f}"),
        (
            "duration",
            result.duration_score,
            f"the journey takes {offer.duration_minutes} minutes",
        ),
        (
            "rating",
            result.rating_score,
            f"the customer rating is {offer.rating:.1f}/5",
        ),
        (
            "flexibility",
            result.flexibility_score,
            flexibility_detail,
        ),
    ]

    # Departure time only mentioned if the traveler expressed a preference
    if request.preferred_departure_time is not None:
        criteria.append(
            (
                "departure time",
                result.departure_time_score,
                f"it departs at {offer.departure_at:%H:%M}, "
                f"near your preferred time of "
                f"{request.preferred_departure_time:%H:%M}",
            )
        )

    strongest = criteria[0]
    weakest = criteria[0]

    # Find the highest and lowest criterion scores for this offer
    for criterion in criteria[1:]:
        if criterion[1] > strongest[1]:
            strongest = criterion

        if criterion[1] < weakest[1]:
            weakest = criterion

    explanation = (
        f"{company_name} ranks first for the {profile.name} profile "
        f"with a total score of {result.total_score:.2f}/100. "
    )

    # In case of total tie
    if strongest[1] == weakest[1]:
        explanation += (
            "Its criterion scores are tied, so none stands out as a "
            "particular strength or trade-off. "
        )
    else:
        explanation += (
            f"Its strongest relative score is {strongest[0]} "
            f"({strongest[1]:.1f}/100; {strongest[2]}), while its main "
            f"trade-off is {weakest[0]} "
            f"({weakest[1]:.1f}/100; {weakest[2]}). "
        )

    explanation += (
        "The criterion scores compare this offer with the offers that "
        "passed your search filters."
    )

    return explanation