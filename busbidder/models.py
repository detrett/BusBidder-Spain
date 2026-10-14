from dataclasses import dataclass
from datetime import datetime

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
    