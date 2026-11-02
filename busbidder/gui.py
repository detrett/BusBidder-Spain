from datetime import datetime
from math import isfinite
import tkinter as tk
from tkinter import messagebox, ttk
import logging


from busbidder.booking import (
    apply_bookings_to_offers,
    create_booking,
    load_bookings,
    save_booking,
)
from busbidder.data_loader import (
    load_companies,
    load_destinations,
    load_offers,
)
from busbidder.exceptions import (
    DataLoadError,
    DataSaveError,
    DataValidationError,
)
from busbidder.logging_config import configure_logging
from busbidder.models import SearchRequest
from busbidder.profiles import get_traveler_profiles
from busbidder.ranking import rank_offers
from busbidder.recommendations import explain_recommendation
from busbidder.search import filter_offers
from busbidder.validators import validate_offer_references

COLORS = {
    "background": "#FCF4F5",
    "surface": "#FFFFFF",
    "text": "#29252A",
    "heading": "#432B45",
    "berry": "#A54150",
    "berry_hover": "#873641",
    "selected": "#F2E8EC",
    "muted": "#6B626A",
    "border": "#E3DADF",
}

logger = logging.getLogger(__name__)

class RoundedButton(tk.Canvas):
    """ Draw a clickable button with rounded corners."""

    def __init__(
        self,
        parent,
        text,
        command,
        color,
        hover_color,
        width=150,
        height=46,
        radius=10,
    ):
        """Create the button shape, label, and mouse and keyboard bindings"""
        super().__init__(
            parent,
            width=width,
            height=height,
            bg=COLORS["background"],
            bd=0,
            highlightthickness=0,
            cursor="hand2",
            takefocus=True,
        )

        self.command = command
        self.color = color
        self.hover_color = hover_color

        shape_options = {
            "fill": color,
            "outline": color,
            "tags": "button_shape",
        }

        # These overlapping shapes create the rounded rectangle.
        self.create_rectangle(
            radius, 0, width - radius, height, **shape_options
        )
        self.create_rectangle(
            0, radius, width, height - radius, **shape_options
        )
        self.create_oval(
            0, 0, radius * 2, radius * 2, **shape_options
        )
        self.create_oval(
            width - radius * 2, 0, width, radius * 2, **shape_options
        )
        self.create_oval(
            0, height - radius * 2, radius * 2, height, **shape_options
        )
        self.create_oval(
            width - radius * 2,
            height - radius * 2,
            width,
            height,
            **shape_options,
        )

        self.create_text(
            width / 2,
            height / 2,
            text=text,
            fill=COLORS["surface"],
            font=("Segoe UI", 10, "bold"),
        )

        self.bind("<Enter>", lambda event: self._set_color(self.hover_color))
        self.bind("<Leave>", lambda event: self._set_color(self.color))
        self.bind("<Button-1>", self._activate)
        self.bind("<Return>", self._activate)
        self.bind("<space>", self._activate)

    def _set_color(self, color):
        """Change the button fill when the pointer enters or leaves."""
        self.itemconfigure("button_shape", fill=color, outline=color)

    def _activate(self, event=None):
        """Run the button's assigned command."""
        self.command()
        return "break"


def clear_combobox_selection(event):
    """ Clear the text highlight after a dropdown receives focus."""
    event.widget.after_idle(event.widget.selection_clear)

def clear_entry_selection(event):
    """ Clear text highlight when leaving an entry field. """
    event.widget.after_idle(event.widget.selection_clear)

def main():
    """ Create the search form and display the BusBidder window """
    configure_logging()
    logger.info("BusBidder GUI started.")

    root = tk.Tk()
    root.withdraw()
    root.title("BusBidder Spain")
    root.geometry("1050x650")
    root.minsize(850, 500)

    root.bind_class("TEntry", "<FocusOut>", clear_entry_selection, add="+")

    root.option_add("*TCombobox*Listbox.background", COLORS["surface"])
    root.option_add("*TCombobox*Listbox.foreground", COLORS["text"])
    root.option_add("*TCombobox*Listbox.selectBackground", COLORS["selected"])
    root.option_add("*TCombobox*Listbox.selectForeground", COLORS["text"])

    # Style
    root.configure(bg=COLORS["background"])

    style = ttk.Style(root)

    if "clam" in style.theme_names():
        style.theme_use("clam")

    style.configure(
        "TFrame",
        background=COLORS["background"],
    )
    style.configure(
        "TLabel",
        background=COLORS["background"],
        foreground=COLORS["text"],
        font=("Segoe UI", 10),
    )
    style.configure(
        "Title.TLabel",
        background=COLORS["background"],
        foreground=COLORS["heading"],
        font=("Segoe UI", 20, "bold"),
    )
    style.configure(
        "Card.TFrame",
        background=COLORS["surface"],
    )
    style.configure(
        "Card.TLabel",
        background=COLORS["background"],
        foreground=COLORS["text"],
    )
    style.configure(
        "Card.TCheckbutton",
        background=COLORS["background"],
        foreground=COLORS["text"],
    )
    style.map(
        "Card.TCheckbutton",
        background=[("active", COLORS["background"])],
    )
    style.configure(
        "Status.TLabel",
        background=COLORS["background"],
        foreground=COLORS["heading"],
        font=("Segoe UI", 10, "bold"),
    )
    style.configure(
        "Details.TLabel",
        background=COLORS["background"],
        foreground=COLORS["text"],
        font=("Segoe UI", 10),
        padding=12,
    )

    style.configure(
        "TEntry",
        fieldbackground=COLORS["surface"],
        foreground=COLORS["text"],
        padding=7,
    )
    style.map(
        "TEntry",
        bordercolor=[("focus", COLORS["heading"])],
        lightcolor=[("focus", COLORS["heading"])],
        darkcolor=[("focus", COLORS["heading"])],
        selectbackground=[
            ("focus", COLORS["selected"]),
            ("!focus", COLORS["surface"]),
        ],
        selectforeground=[("focus", COLORS["text"])],
    )

    style.configure(
        "TCombobox",
        fieldbackground=COLORS["surface"],
        background=COLORS["surface"],
        foreground=COLORS["text"],
        padding=7,
    )

    style.map(
        "TCombobox",
        fieldbackground=[
            ("readonly", COLORS["surface"]),
            ("focus", COLORS["surface"]),
        ],
        background=[
            ("readonly", COLORS["surface"]),
            ("active", COLORS["surface"]),
        ],
        foreground=[
            ("readonly", COLORS["text"]),
            ("focus", COLORS["text"]),
        ],
        selectbackground=[
            ("readonly", COLORS["selected"]),
            ("focus", COLORS["selected"]),
        ],
        selectforeground=[
            ("readonly", COLORS["text"]),
            ("focus", COLORS["text"]),
        ],
        bordercolor=[("focus", COLORS["heading"])],
        lightcolor=[("focus", COLORS["heading"])],
        darkcolor=[("focus", COLORS["heading"])],
    )

    style.configure(
        "Primary.TButton",
        background=COLORS["berry"],
        foreground=COLORS["surface"],
        font=("Segoe UI", 10, "bold"),
        padding=(16, 9),
        borderwidth=0,
    )
    style.map(
        "Primary.TButton",
        background=[
            ("pressed", COLORS["heading"]),
            ("active", COLORS["berry_hover"]),
        ],
    )
    style.configure(
        "Secondary.TButton",
        background=COLORS["heading"],
        foreground=COLORS["surface"],
        font=("Segoe UI", 10, "bold"),
        padding=(16, 9),
        borderwidth=0,
    )
    style.map(
        "Secondary.TButton",
        background=[
            ("active", COLORS["berry_hover"]),
            ("pressed", COLORS["berry_hover"]),
        ],
        foreground=[
            ("active", COLORS["surface"]),
            ("pressed", COLORS["surface"]),
        ],
    )
    style.configure(
        "Treeview",
        background=COLORS["surface"],
        fieldbackground=COLORS["surface"],
        foreground=COLORS["text"],
        rowheight=29,
        font=("Segoe UI", 9),
    )

    style.configure(
        "Treeview.Heading",
        background=COLORS["heading"],
        foreground=COLORS["surface"],
        font=("Segoe UI", 9, "bold"),
        padding=(6, 8),
    )
    style.configure("Treeview", rowheight=32)
    style.configure("Treeview.Heading", padding=(6, 8))
    style.map(
        "Treeview.Heading",
        background=[
            ("pressed", COLORS["berry"]),
            ("active", COLORS["berry_hover"]),
        ],
        foreground=[
            ("pressed", COLORS["surface"]),
            ("active", COLORS["surface"]),
        ],
    )
    style.map(
        "Treeview",
        background=[("selected", COLORS["selected"])],
        foreground=[("selected", COLORS["text"])],
    )

    scroll_container = ttk.Frame(root)
    scroll_container.pack(fill="both", expand=True)

    canvas = tk.Canvas(
        scroll_container,
        highlightthickness=0,
        bg=COLORS["background"],
    )

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

    try:
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

    except (DataLoadError, DataValidationError) as error:
        logger.exception("BusBidder GUI could not load startup data.")
        messagebox.showerror(
            "Startup error",
            str(error),
            parent=root,
        )
        root.destroy()
        return

    logger.info(
        "Loaded %d companies, %d destinations, %d offers, and %d bookings.",
        len(companies),
        len(destinations),
        len(offers),
        len(bookings),
    )

    destination_options = [
        f"{destination.destination_id} - {destination.name}"
        for destination in destinations
    ]
    profile_options = [profile.name for profile in profiles]

    heading = ttk.Label(
        content_frame,
        text="Search for bus offers",
        style="Title.TLabel",
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
            details.append("")
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

        results_tree.configure(height=max(3, min(len(ranked_offers), 8)))

        logger.info(
            "GUI search for %s from %s to %s using profile '%s' found %d offers.",
            request.destination_id,
            request.earliest_date,
            request.latest_date,
            selected_profile.name,
            len(ranked_offers),
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
                    f"{result.total_score:.2f}",
                    offer.departure_at.strftime("%Y-%m-%d %H:%M"),
                    offer.arrival_at.strftime("%Y-%m-%d %H:%M"),
                    f"EUR {offer.price_eur:.2f}",
                    f"{offer.duration_minutes} min",
                    offer.transfers,
                    offer.seats_available,
                    f"{offer.rating:.1f}/5",
                    f"{result.price_score:.1f}",
                    f"{result.duration_score:.1f}",
                    f"{result.departure_time_score:.1f}",
                    f"{result.flexibility_score:.1f}",
                    f"{result.rating_score:.1f}",
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

    def book_selected_offer():
        """Confirm and save a booking for the selected result."""
        selection = results_tree.selection()

        if not selection:
            messagebox.showwarning(
                "No offer selected",
                "Select an offer in the results table first.",
            )
            return

        offer_id = selection[0]
        result = ranked_by_offer_id.get(offer_id)

        if result is None:
            return

        offer = result.offer

        # Check again in case the available seats changed after the search.
        if offer.seats_available <= 0:
            logger.warning(
                "GUI booking attempt for sold-out offer %s.",
                offer.offer_id,
            )
            messagebox.showerror(
                "No seats available",
                "This offer no longer has any seats available.",
            )
            search()
            return

        company_name = company_names[offer.company_id]
        confirmed = messagebox.askyesno(
            "Confirm booking",
            f"Book this offer with {company_name}?\n\n"
            f"Departure: {offer.departure_at:%Y-%m-%d %H:%M}\n"
            f"Price: EUR {offer.price_eur:.2f}\n"
            f"Changeable: {'Yes' if offer.changeable else 'No'}\n"
            f"Refundable: {'Yes' if offer.refundable else 'No'}",
        )

        if not confirmed:
            return

        try:
            booking = create_booking(offer, bookings)
            save_booking(booking)
        except (DataLoadError, DataSaveError, DataValidationError) as error:
            logger.exception("GUI booking failed for offer %s.", offer.offer_id)
            messagebox.showerror("Booking failed", str(error))
            return

        logger.info(
            "GUI booking %s saved for offer %s.",
            booking.booking_reference,
            booking.offer_id,
        )

        # Update the in-memory data after the booking has been saved.
        bookings.append(booking)
        offer.seats_available -= 1

        messagebox.showinfo(
            "Booking confirmed",
            f"Booking reference: {booking.booking_reference}\n"
            f"Offer: {booking.offer_id}\n"
            f"Price: EUR {booking.price_eur:.2f}",
        )

        # Run the current search again so the seat count and results refresh.
        search()

    ttk.Label(
        form, text="Destination", style="Card.TLabel"
    ).grid(row=0, column=0, sticky="w", padx=(0, 12), pady=8)

    destination_combo = ttk.Combobox(
        form,
        textvariable=destination_value,
        values=destination_options,
        state="readonly",
    )
    destination_combo.grid(row=0, column=1, columnspan=3, sticky="ew", pady=8)
    destination_combo.bind("<FocusIn>", clear_combobox_selection)
    destination_combo.bind("<<ComboboxSelected>>", clear_combobox_selection)

    ttk.Label(
        form, text="First travel date (YYYY-MM-DD)", style="Card.TLabel"
    ).grid(row=1, column=0, sticky="w", padx=(0, 12), pady=8)

    ttk.Entry(
        form, textvariable=first_date_value
    ).grid(row=1, column=1, sticky="ew", padx=(0, 18), pady=8)

    ttk.Label(
        form, text="Last travel date (YYYY-MM-DD)", style="Card.TLabel"
    ).grid(row=1, column=2, sticky="w", padx=(0, 12), pady=8)

    ttk.Entry(
        form, textvariable=last_date_value
    ).grid(row=1, column=3, sticky="ew", pady=8)

    ttk.Label(
        form, text="Maximum budget (EUR)", style="Card.TLabel"
    ).grid(row=2, column=0, sticky="w", padx=(0, 12), pady=8)

    ttk.Entry(
        form, textvariable=budget_value
    ).grid(row=2, column=1, sticky="ew", padx=(0, 18), pady=8)

    ttk.Label(
        form, text="Maximum transfers", style="Card.TLabel"
    ).grid(row=2, column=2, sticky="w", padx=(0, 12), pady=8)

    ttk.Entry(
        form, textvariable=transfers_value
    ).grid(row=2, column=3, sticky="ew", pady=8)

    ttk.Checkbutton(
        form,
        text="Require a changeable ticket",
        variable=changeable_value,
        style="Card.TCheckbutton",
    ).grid(row=3, column=0, columnspan=2, sticky="w", pady=8)

    ttk.Label(
        form,
        text="Preferred departure time (HH:MM, optional)",
        style="Card.TLabel",
    ).grid(row=3, column=2, sticky="w", padx=(0, 12), pady=8)

    ttk.Entry(
        form, textvariable=departure_time_value
    ).grid(row=3, column=3, sticky="ew", pady=8)

    ttk.Label(
        form, text="Traveler profile", style="Card.TLabel"
    ).grid(row=4, column=0, sticky="w", padx=(0, 12), pady=8)

    profile_combo = ttk.Combobox(
        form,
        textvariable=profile_value,
        values=profile_options,
        state="readonly",
    )
    profile_combo.grid(row=4, column=1, columnspan=3, sticky="ew", pady=8)
    profile_combo.bind("<FocusIn>", clear_combobox_selection)
    profile_combo.bind("<<ComboboxSelected>>", clear_combobox_selection)

    form.columnconfigure(1, weight=1)
    form.columnconfigure(3, weight=1)

    search_button = RoundedButton(
        content_frame,
        text="Search",
        command=search,
        color=COLORS["berry"],
        hover_color=COLORS["berry_hover"],
        width=150,
    )
    search_button.pack(pady=10)

    results_count = tk.StringVar(value="Enter your search details above.")

    ttk.Label(
        content_frame,
        textvariable=results_count,
        style="Status.TLabel",
    ).pack(pady=(16, 10))

    results_frame = ttk.Frame(
        content_frame,
        padding=0,
        style="TFrame",
    )
    results_frame.pack(
        fill="both",
        expand=True,
        padx=12,
        pady=(0, 14),
    )

    columns = (
        "company",
        "score",
        "departure",
        "arrival",
        "price",
        "duration",
        "transfers",
        "seats",
        "rating",
        "price_score",
        "duration_score",
        "departure_score",
        "flexibility_score",
        "rating_score",
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
        style="Details.TLabel",
        wraplength=850,
        justify="left",
        padding=16,
    )
    details_label.pack(fill="x", padx=10, pady=(5, 10))

    book_button = RoundedButton(
        content_frame,
        text="Book selected offer",
        command=book_selected_offer,
        color=COLORS["heading"],
        hover_color=COLORS["berry"],
        width=220,
    )
    book_button.pack(pady=(0, 22))

    column_settings = {
        "company": ("Company", 120, "w"),
        "score": ("Total", 75, "center"),
        "departure": ("Departure", 130, "center"),
        "arrival": ("Arrival", 130, "center"),
        "price": ("Price", 85, "center"),
        "duration": ("Duration", 80, "center"),
        "transfers": ("Transfers", 65, "center"),
        "seats": ("Seats", 50, "center"),
        "rating": ("Rating", 65, "center"),
        "price_score": ("Price sc.", 75, "center"),
        "duration_score": ("Duration sc.", 80, "center"),
        "departure_score": ("Time sc.", 80, "center"),
        "flexibility_score": ("Flex sc.", 80, "center"),
        "rating_score": ("Rating sc.", 75, "center"),
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

    horizontal_scrollbar = ttk.Scrollbar(
        results_frame,
        orient="horizontal",
        command=results_tree.xview,
    )
    vertical_scrollbar = ttk.Scrollbar(
        results_frame,
        orient="vertical",
        command=results_tree.yview,
    )

    results_tree.configure(
        xscrollcommand=horizontal_scrollbar.set,
        yscrollcommand=vertical_scrollbar.set,
    )

    results_frame.columnconfigure(0, weight=1)
    results_frame.rowconfigure(0, weight=1)

    results_tree.grid(row=0, column=0, sticky="nsew")
    vertical_scrollbar.grid(row=0, column=1, sticky="ns")
    horizontal_scrollbar.grid(row=1, column=0, sticky="ew")

    root.deiconify()
    root.mainloop()

    logger.info("BusBidder GUI closed.")

if __name__ == "__main__":
    main()