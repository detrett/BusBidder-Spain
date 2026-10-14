from datetime import datetime, time
from math import isfinite

from busbidder.models import SearchRequest

def choose_destination(destinations):
    """
    Ask the traveler to choose a destination from the loaded destinations.
        Args:
            destinations: The available Destination objects.

        Returns:
            The chosen destination's ID.
    """
    print("\nAvailable destinations:")
    for destination in destinations:
        print(f"{destination.destination_id} - {destination.name}")

    valid_ids = {destination.destination_id.upper() for destination in destinations}

    while True:
        chosen_id = input("Enter a destination ID: ").strip().upper()

        if chosen_id in valid_ids:
            return chosen_id

        print("That destination ID was not found. Please choose one from the list.")


def choose_travel_dates():
    """
    Ask for a valid start and end date for the journey search.
        Returns:
            A tuple containing the earliest and latest travel dates.
    """
    while True:
        start_text = input("Enter the first travel date (YYYY-MM-DD): ").strip()
        end_text = input("Enter the last travel date (YYYY-MM-DD): ").strip()

        try:
            earliest_date = datetime.strptime(start_text, "%Y-%m-%d").date()
            latest_date = datetime.strptime(end_text, "%Y-%m-%d").date()
        except ValueError:
            print("Please enter valid dates in YYYY-MM-DD format.")
            continue

        if earliest_date > latest_date:
            print("The last travel date cannot be earlier than the first.")
            continue

        return earliest_date, latest_date


def choose_search_limits():
    """
    Ask for the traveller's maximum budget and transfer count.
        Returns:
            A tuple containing the maximum budget and number of transfers.
    """
    while True:
        try:
            max_price_eur = float(input("Enter your maximum budget in EUR: "))
        except ValueError:
            print("Please enter a valid number for the budget.")
            continue

        if isfinite(max_price_eur) and max_price_eur >= 0:
            break

        print("The budget must be a nonnegative, finite number.")

    while True:
        try:
            max_transfers = int(input("Enter the maximum number of transfers: "))
        except ValueError:
            print("Please enter a whole number for the transfer limit.")
            continue

        if max_transfers >= 0:
            break

        print("The transfer limit cannot be negative.")

    return max_price_eur, max_transfers


def choose_changeable_requirement():
    """
    Ask whether the traveller requires a changeable ticket.
        Returns:
            True if a changeable ticket is required, otherwise False.
    """
    while True:
        answer = input("Require a changeable ticket? (yes/no): ").strip().lower()

        if answer in ("yes", "y"):
            return True

        if answer in ("no", "n"):
            return False

        print("Please answer yes or no.")


def choose_preferred_departure_time():
    """
    Ask for an optional preferred departure time.
        Returns:
            A time object, or None if the traveller has no time preference.
    """
    while True:
        time_text = input(
            "Preferred departure time (24-hour HH:MM, or Enter to skip): "
        ).strip()

        if not time_text:
            return None

        try:
            return datetime.strptime(time_text, "%H:%M").time()
        except ValueError:
            print("Please enter a valid time in HH:MM format, such as 08:30, or press 'Enter' to skip")



def collect_search_request(destinations):
    """
    Collect the traveller's search details and build a SearchRequest.
        Args:
            destinations: The available Destination objects.

        Returns:
            A SearchRequest containing the traveller's inputs.
    """
    destination_id = choose_destination(destinations)
    earliest_date, latest_date = choose_travel_dates()
    max_price_eur, max_transfers = choose_search_limits()
    require_changeable = choose_changeable_requirement()
    preferred_departure_time = choose_preferred_departure_time()

    return SearchRequest(
        destination_id=destination_id,
        earliest_date=earliest_date,
        latest_date=latest_date,
        max_price_eur=max_price_eur,
        max_transfers=max_transfers,
        require_changeable=True,
        preferred_departure_time=time(8, 0),
    )