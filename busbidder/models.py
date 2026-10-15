from dataclasses import dataclass
from datetime import date, datetime, time

@dataclass
class Company:
    """Represent one simulated bus company."""

    company_id: str
    name: str
    description: str


@dataclass
class Destination:
    """Represent one destination served by the marketplace."""

    destination_id: str
    name: str


@dataclass
class Offer:
    """Represent one journey offered for booking"""

    offer_id: str
    company_id: str
    destination_id: str
    departure_at: datetime
    arrival_at: datetime
    price_eur: float
    transfers: int
    luggage_kg: int
    changeable: bool
    refundable: bool
    seats_available: int
    rating: float

    @property
    def duration_minutes(self):
        """Calculate the journey duration in whole minutes"""

        duration = self.arrival_at - self.departure_at
        return int(duration.total_seconds() // 60)


@dataclass
class SearchRequest:
    """Store the constraints and preferences for one journey search."""

    destination_id: str
    earliest_date: date
    latest_date: date
    max_price_eur: float
    max_transfers: int
    require_changeable: bool
    preferred_departure_time: time | None = None


@dataclass
class RankingWeights:
    """Store the importance assigned to each ranking criterion."""

    price: float
    duration: float
    departure_time: float
    flexibility: float


@dataclass
class TravelerProfile:
    """Represent a traveler's named set of ranked preferences"""

    name: str
    weights: RankingWeights