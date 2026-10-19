from datetime import datetime
from math import isfinite
import tkinter as tk
from tkinter import messagebox, ttk

from busbidder.booking import apply_bookings_to_offers, load_bookings
from busbidder.data_loader import (
    load_companies,
    load_destinations,
    load_offers,
)
from busbidder.models import SearchRequest
from busbidder.profiles import get_traveler_profiles
from busbidder.ranking import rank_offers
from busbidder.recommendations import explain_recommendation
from busbidder.search import filter_offers
from busbidder.validators import validate_offer_references


def main():
    """Create the search form and display the BusBidder window."""
    root = tk.Tk()
    root.title("BusBidder Spain")
    root.geometry("1000x650")
    root.minsize(850, 500)

    scroll_container = ttk.Frame(root)
    scroll_container.pack(fill="both", expand=True)

    canvas = tk.Canvas(scroll_container, highlightthickness=0)
    page_scrollbar = ttk.Scrollbar(
        scroll_container,
        orient="vertical",
        command=canvas.yview,
    )
    canvas.configure(yscrollcommand=page_scrollbar.set)

    page_scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)

    content_frame = ttk.Frame(canvas)
    canvas_window = canvas.create_window(
        (0, 0),
        window=content_frame,
        anchor="nw",
    )

    content_frame.bind(
        "<Configure>",
        lambda event: canvas.configure(scrollregion=canvas.bbox("all")),
    )
    canvas.bind(
        "<Configure>",
        lambda event: canvas.itemconfigure(canvas_window, width=event.width),
    )

    def scroll_page(event):
        """Scroll the page with the mouse wheel, except over the results table."""
        if isinstance(event.widget, ttk.Treeview):
            return

        units = int(-event.delta / 120)

        # Handle small wheel movements from some mouse or touchpad settings.
        if units == 0:
            units = -1 if event.delta > 0 else 1

        canvas.yview_scroll(units, "units")

    root.bind_all("<MouseWheel>", scroll_page)

    destinations = load_destinations(("destination_id", "name"))
    companies = load_companies(("company_id", "name", "description"))
    offers = load_offers(
        (
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
    )

    validate_offer_references(offers, companies, destinations)

    bookings = load_bookings()
    apply_bookings_to_offers(offers, bookings)
    company_names = {
        company.company_id: company.name
        for company in companies
    }
    profiles = get_traveler_profiles()

    destination_options = [
        f"{destination.destination_id} - {destination.name}"
        for destination in destinations
    ]
    profile_options = [profile.name for profile in profiles]

    heading = ttk.Label(
        content_frame,
        text="Search for bus offers",
        font=("Arial", 18, "bold"),
    )
    heading.pack(pady=(20, 15))

    form = ttk.Frame(content_frame, padding=20)
    form.pack(fill="x")

    # Keep the form values in Tkinter variables so we can read them later.
    destination_value = tk.StringVar(value=destination_options[0])
    first_date_value = tk.StringVar()
    last_date_value = tk.StringVar()
    budget_value = tk.StringVar()
    transfers_value = tk.StringVar(value="0")
    changeable_value = tk.BooleanVar(value=False)
    departure_time_value = tk.StringVar()
    profile_value = tk.StringVar(value=profile_options[0])

    ranked_by_offer_id = {}
    current_search = {}
    details_value = tk.StringVar(value="Select an offer to see its details.")

    def show_selected_offer_details(event=None):
        """Display scores and information for the selected offer."""
        selection = results_tree.selection()

        if not selection:
            return

        offer_id = selection[0]
        result = ranked_by_offer_id.get(offer_id)

        if result is None:
            return

        offer = result.offer
        company_name = company_names[offer.company_id]

        details = [
            f"{company_name} | "
            f"{offer.departure_at:%Y-%m-%d %H:%M} to "
            f"{offer.arrival_at:%Y-%m-%d %H:%M}",
            (
                f"EUR {offer.price_eur:.2f} | "
                f"{offer.duration_minutes} minutes | "
                f"{offer.transfers} transfers | "
                f"{offer.seats_available} seats"
            ),
            (
                f"Changeable: {'Yes' if offer.changeable else 'No'} | "
                f"Refundable: {'Yes' if offer.refundable else 'No'} | "
                f"Rating: {offer.rating:.1f}/5"
            ),
            (
                f"Scores — Price: {result.price_score:.1f}, "
                f"Duration: {result.duration_score:.1f}, "
                f"Departure: {result.departure_time_score:.1f}, "
                f"Flexibility: {result.flexibility_score:.1f}, "
                f"Rating: {result.rating_score:.1f}"
            ),
        ]

        if offer_id == current_search.get("top_offer_id"):
            details.append(
                explain_recommendation(
                    result,
                    current_search["request"],
                    current_search["profile"],
                    company_name,
                )
            )

        details_value.set("\n".join(details))

    def search():
        """Validate the form values and create a SearchRequest."""
        try:
            earliest_date = datetime.strptime(
                first_date_value.get().strip(), "%Y-%m-%d"
            ).date()
            latest_date = datetime.strptime(
                last_date_value.get().strip(), "%Y-%m-%d"
            ).date()
        except ValueError:
            messagebox.showerror(
                "Invalid dates",
                "Enter both dates in YYYY-MM-DD format.",
            )
            return

        if earliest_date > latest_date:
            messagebox.showerror(
                "Invalid dates",
                "The last travel date cannot be earlier than the first.",
            )
            return

        try:
            max_price_eur = float(budget_value.get())
        except ValueError:
            messagebox.showerror(
                "Invalid budget",
                "Enter a number for the maximum budget.",
            )
            return

        if not isfinite(max_price_eur) or max_price_eur <= 0:
            messagebox.showerror(
                "Invalid budget",
                "The maximum budget must be a finite number greater than zero.",
            )
            return

        try:
            max_transfers = int(transfers_value.get())
        except ValueError:
            messagebox.showerror(
                "Invalid transfers",
                "Enter a whole number for maximum transfers.",
            )
            return

        if max_transfers < 0:
            messagebox.showerror(
                "Invalid transfers",
                "Maximum transfers cannot be negative.",
            )
            return

        departure_text = departure_time_value.get().strip()

        if departure_text:
            try:
                preferred_departure_time = datetime.strptime(
                    departure_text, "%H:%M"
                ).time()
            except ValueError:
                messagebox.showerror(
                    "Invalid time",
                    "Enter the preferred departure time in HH:MM format.",
                )
                return
        else:
            preferred_departure_time = None

        destination_id = destination_value.get().split(" - ", 1)[0]

        request = SearchRequest(
            destination_id=destination_id,
            earliest_date=earliest_date,
            latest_date=latest_date,
            max_price_eur=max_price_eur,
            max_transfers=max_transfers,
            require_changeable=changeable_value.get(),
            preferred_departure_time=preferred_departure_time,
        )

        selected_profile = next(
            profile
            for profile in profiles
            if profile.name == profile_value.get()
        )
        matching_offers = filter_offers(offers, request)
        ranked_offers = rank_offers(
            matching_offers,
            selected_profile,
            request,
        )

        current_search.update(
            request=request,
            profile=selected_profile,
            top_offer_id=(
                ranked_offers[0].offer.offer_id
                if ranked_offers
                else None
            ),
        )

        # Remove the previous search results before showing the new ones.
        for item in results_tree.get_children():
            results_tree.delete(item)

        ranked_by_offer_id.clear()

        results_count.set(
            f"{len(ranked_offers)} offer(s) found "
            f"for the {selected_profile.name} profile"
        )

        for result in ranked_offers:
            offer = result.offer
            ranked_by_offer_id[offer.offer_id] = result
            results_tree.insert(
                "",
                "end",
                iid=offer.offer_id,
                values=(
                    company_names[offer.company_id],
                    offer.departure_at.strftime("%Y-%m-%d %H:%M"),
                    offer.arrival_at.strftime("%Y-%m-%d %H:%M"),
                    f"EUR {offer.price_eur:.2f}",
                    f"{offer.duration_minutes} min",
                    offer.transfers,
                    offer.seats_available,
                    f"{offer.rating:.1f}/5",
                    f"{result.total_score:.2f}",
                ),
            )

        if ranked_offers:
            first_offer_id = ranked_offers[0].offer.offer_id
            results_tree.selection_set(first_offer_id)
            results_tree.focus(first_offer_id)

        if not ranked_offers:
            messagebox.showinfo(
                "No offers found",
                "No offers match these search constraints.",
            )



    ttk.Label(form, text="Destination").grid(row=0, column=0, sticky="w", pady=6)
    ttk.Combobox(
        form,
        textvariable=destination_value,
        values=destination_options,
        state="readonly",
    ).grid(row=0, column=1, sticky="ew", pady=6)

    ttk.Label(form, text="First travel date (YYYY-MM-DD)").grid(
        row=1, column=0, sticky="w", pady=6
    )
    ttk.Entry(form, textvariable=first_date_value).grid(
        row=1, column=1, sticky="ew", pady=6
    )

    ttk.Label(form, text="Last travel date (YYYY-MM-DD)").grid(
        row=2, column=0, sticky="w", pady=6
    )
    ttk.Entry(form, textvariable=last_date_value).grid(
        row=2, column=1, sticky="ew", pady=6
    )

    ttk.Label(form, text="Maximum budget (EUR)").grid(
        row=3, column=0, sticky="w", pady=6
    )
    ttk.Entry(form, textvariable=budget_value).grid(
        row=3, column=1, sticky="ew", pady=6
    )

    ttk.Label(form, text="Maximum transfers").grid(
        row=4, column=0, sticky="w", pady=6
    )
    ttk.Entry(form, textvariable=transfers_value).grid(
        row=4, column=1, sticky="ew", pady=6
    )

    ttk.Checkbutton(
        form,
        text="Require a changeable ticket",
        variable=changeable_value,
    ).grid(row=5, column=1, sticky="w", pady=6)

    ttk.Label(form, text="Preferred departure time (HH:MM, optional)").grid(
        row=6, column=0, sticky="w", pady=6
    )
    ttk.Entry(form, textvariable=departure_time_value).grid(
        row=6, column=1, sticky="ew", pady=6
    )

    ttk.Label(form, text="Traveler profile").grid(
        row=7, column=0, sticky="w", pady=6
    )
    ttk.Combobox(
        form,
        textvariable=profile_value,
        values=profile_options,
        state="readonly",
    ).grid(row=7, column=1, sticky="ew", pady=6)

    form.columnconfigure(1, weight=1)

    search_button = ttk.Button(
        content_frame,
        text="Search",
        command=search,
    )
    search_button.pack(pady=10)

    results_count = tk.StringVar(value="Enter your search details above.")

    ttk.Label(content_frame, textvariable=results_count).pack(pady=(10, 5))

    results_frame = ttk.Frame(content_frame, padding=(10, 0, 10, 10))
    results_frame.pack(fill="both", expand=True)

    columns = (
        "company",
        "departure",
        "arrival",
        "price",
        "duration",
        "transfers",
        "seats",
        "rating",
        "score",
    )

    results_tree = ttk.Treeview(
        results_frame,
        columns=columns,
        show="headings",
        height=8,
    )

    results_tree.bind(
        "<<TreeviewSelect>>",
        show_selected_offer_details,
    )

    details_label = ttk.Label(
        content_frame,
        textvariable=details_value,
        wraplength=1050,
        justify="left",
        padding=10,
    )
    details_label.pack(fill="x", padx=10, pady=(5, 10))

    column_settings = {
        "company": ("Company", 140, "w"),
        "departure": ("Departure", 150, "center"),
        "arrival": ("Arrival", 150, "center"),
        "price": ("Price", 100, "center"),
        "duration": ("Duration", 100, "center"),
        "transfers": ("Transfers", 75, "center"),
        "seats": ("Seats", 60, "center"),
        "rating": ("Rating", 80, "center"),
        "score": ("Score", 90, "center"),
    }

    for column, (heading, width, alignment) in column_settings.items():
        results_tree.heading(column, text=heading)
        results_tree.column(
            column,
            width=width,
            minwidth=width,
            anchor=alignment,
            stretch=False,
        )

    results_tree.pack(side="left", fill="both", expand=True)

    scrollbar = ttk.Scrollbar(
        results_frame,
        orient="vertical",
        command=results_tree.yview,
    )
    scrollbar.pack(side="right", fill="y")
    results_tree.configure(yscrollcommand=scrollbar.set)

    root.mainloop()


if __name__ == "__main__":
    main()