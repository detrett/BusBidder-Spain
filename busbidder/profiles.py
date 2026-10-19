from busbidder.models import RankingWeights, TravelerProfile
from busbidder.validators import validate_ranking_weights


def get_traveler_profiles():
    """
    Create and validate the marketplace's example traveler profiles.
        Returns:
            A list of TravelerProfile objects.
    """
    profiles = [
        TravelerProfile(
            name="Budget-focused",
            weights=RankingWeights(
                price=0.55,
                duration=0.25,
                departure_time=0.10,
                flexibility=0.05,
                rating=0.05,
            ),
        ),
        TravelerProfile(
            name="Business",
            weights=RankingWeights(
                price=0.20,
                duration=0.35,
                departure_time=0.25,
                flexibility=0.05,
                rating=0.15,
            ),
        ),
        TravelerProfile(
            name="Flexibility-focused",
            weights=RankingWeights(
                price=0.15,
                duration=0.15,
                departure_time=0.10,
                flexibility=0.55,
                rating=0.05,
            ),
        ),
    ]

    for profile in profiles:
        validate_ranking_weights(profile.weights)

    return profiles