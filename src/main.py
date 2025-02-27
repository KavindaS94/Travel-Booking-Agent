import typer
from rich.console import Console
from rich.table import Table
from datetime import datetime, timedelta
from typing import Optional
from api.booking_api import BookingAPI
from api.openai_api import OpenAIAPI
from models.cache import Cache

app = typer.Typer()
console = Console()
booking_api = BookingAPI()
openai_api = OpenAIAPI()
cache = Cache()

@app.command()
def search(
    destinations: str = typer.Argument(..., help="Comma-separated list of destinations"),
    checkin: Optional[str] = typer.Option(None, help="Check-in date (YYYY-MM-DD)"),
    checkout: Optional[str] = typer.Option(None, help="Check-out date (YYYY-MM-DD)"),
    adults: int = typer.Option(2, help="Number of adults"),
    rooms: int = typer.Option(1, help="Number of rooms"),
    budget: Optional[float] = typer.Option(None, help="Maximum total budget for the entire stay in USD"),
    preferences: Optional[str] = typer.Option(None, help="Comma-separated preferences (e.g., 'pool,beach,spa')")
):
    """Search for hotels in multiple destinations."""
    # Set default dates if not provided
    if not checkin:
        checkin = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    if not checkout:
        checkout = (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d")

    # Parse destinations
    destination_list = [d.strip() for d in destinations.split(",") if d.strip()]
    if not destination_list:
        console.print("[red]Please provide at least one destination[/red]")
        return

    # Calculate number of nights
    checkin_date = datetime.strptime(checkin, "%Y-%m-%d")
    checkout_date = datetime.strptime(checkout, "%Y-%m-%d")
    num_nights = (checkout_date - checkin_date).days

    console.print(f"\n[bold blue]Searching for hotels in multiple locations[/bold blue]")
    console.print(f"Destinations: {', '.join(destination_list)}")
    console.print(f"Check-in: {checkin}, Check-out: {checkout} ({num_nights} nights)")
    console.print(f"Adults: {adults}, Rooms: {rooms}")
    if budget:
        console.print(f"Total Budget: ${budget} (approx. ${budget/num_nights:.2f} per night)")
    if preferences:
        console.print(f"Preferences: {preferences}")
    
    with console.status("[bold green]Searching and ranking hotels...[/bold green]"):
        try:
            results = booking_api.search_multiple_locations(
                destinations=destination_list,
                checkin_date=checkin,
                checkout_date=checkout,
                adults_number=adults,
                room_number=rooms,
                max_price=budget,
                preferences=preferences
            )
            
            if not results.get('locations'):
                console.print("[yellow]No hotels found in any location.[/yellow]")
                return
            
            display_multiple_results(results, show_ranking=True)
                
        except Exception as e:
            console.print(f"[red]Error: {str(e)}[/red]")

def display_multiple_results(results: dict, show_ranking: bool = False):
    """Display hotel results for multiple locations."""
    locations_data = results.get('locations', {})
    
    for location, hotels in locations_data.items():
        console.print(f"\n[bold blue]Top Rated Hotels for the requirement{location}:[/bold blue]")
        
        if not hotels:
            console.print(f"[yellow]No hotels found in {location}[/yellow]")
            continue
        
        display_results({"results": hotels}, show_ranking=True)
        console.print("\n" + "="*100)  # Separator between locations

def display_results(results: dict, show_ranking: bool = False):
    """Display hotel results in a formatted table."""
    if not results.get('results'):
        return
        
    table = Table(show_header=True, header_style="bold magenta", width=150)
    if show_ranking:
        table.add_column("Rank", style="bold", width=8)
    table.add_column("Hotel ID", style="dim", width=10)
    table.add_column("Hotel Name", width=25)
    table.add_column("Rating", width=20)
    table.add_column("Price", width=25)  # Increased width for more price details
    table.add_column("Location & Contact", width=35)
    table.add_column("Facilities", width=35)

    for idx, hotel in enumerate(results['results'], 1):
        # Format rating
        review_info = hotel.get('review_score', {})
        rating_display = (
            f"Score: {review_info.get('score', 'N/A')}\n"
            f"{review_info.get('word', 'N/A')}\n"
            f"({review_info.get('reviews_count', 0)} reviews)"
        )

        # Format price with room information
        price_info = hotel.get('price', {})
        num_rooms = price_info.get('num_rooms', 1)
        room_text = "room" if num_rooms == 1 else "rooms"
        price_display = (
            f"Per night/room: ${price_info.get('per_room', 'N/A')}\n"
            f"Total for {num_rooms} {room_text}\n"
            f"({price_info.get('num_nights', 0)} nights): "
            f"${price_info.get('total', 'N/A')} {price_info.get('currency', 'USD')}"
        )

        # Format location and contact
        location_contact = (
            f"[bold]Address:[/bold]\n{hotel.get('address', 'N/A')}\n"
            f"[bold]Location:[/bold]\n{hotel.get('location', 'N/A')}\n"
            f"[bold]Website:[/bold]\n{hotel.get('website', 'N/A')}"
        )

        # Format facilities
        popular_facilities = hotel.get('popular_facilities', [])[:3]  # Show top 3
        other_facilities = hotel.get('facilities', [])[:2]  # Show top 2
        
        facilities_display = []
        if popular_facilities:
            facilities_display.append("[bold]Popular:[/bold]")
            facilities_display.extend([f"• {f}" for f in popular_facilities])
        if other_facilities:
            if facilities_display:
                facilities_display.append("")  # Add spacing
            facilities_display.append("[bold]Other:[/bold]")
            facilities_display.extend([f"• {f}" for f in other_facilities])
        
        facilities = "\n".join(facilities_display) if facilities_display else "No facilities listed"

        row_data = [
            hotel.get('hotel_id', 'N/A'),
            hotel.get('hotel_name', 'N/A'),
            rating_display,
            price_display,
            location_contact,
            facilities
        ]
        
        if show_ranking:
            rank_display = f"#{idx}"
            row_data.insert(0, rank_display)
            
        table.add_row(*row_data)

    console.print("\n[bold]Found Hotels:[/bold]")
    console.print(table)
    
    # Print a note about detailed view
    console.print("\n[italic]Note: Use 'details <hotel_id>' command to see full hotel information including all facilities.[/italic]")

@app.command()
def details(
    hotel_id: str,
    checkin: Optional[str] = typer.Option(None, help="Check-in date (YYYY-MM-DD)"),
    checkout: Optional[str] = typer.Option(None, help="Check-out date (YYYY-MM-DD)")
):
    """Get detailed information about a specific hotel."""
    # Set default dates if not provided
    if not checkin:
        checkin = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    if not checkout:
        checkout = (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d")

    with console.status("[bold green]Fetching hotel details...[/bold green]"):
        try:
            details = booking_api.get_hotel_details(hotel_id, checkin, checkout)
            display_hotel_details(details)
        except Exception as e:
            console.print(f"[red]Error: {str(e)}[/red]")

def display_hotel_details(details: dict):
    """Display detailed hotel information."""
    if not details:
        console.print("[yellow]No details found for this hotel.[/yellow]")
        return
        
    console.print("\n[bold]Hotel Details[/bold]")
    console.print(f"Name: {details.get('name', 'N/A')}")
    console.print(f"Address: {details.get('address', 'N/A')}")
    console.print(f"Location: {details.get('city', 'N/A')}, {details.get('country', 'N/A')}")
    console.print(f"Website: {details.get('website', 'N/A')}")
    
    # Display facilities in categories
    if details.get('popular_facilities'):
        console.print("\n[bold]Popular Facilities:[/bold]")
        for facility in details['popular_facilities']:
            console.print(f"• {facility}")
            
    if details.get('family_facilities'):
        console.print("\n[bold]Family Facilities:[/bold]")
        for facility in details['family_facilities']:
            console.print(f"• {facility}")
            
    if details.get('facilities'):
        console.print("\n[bold]Other Amenities:[/bold]")
        for facility in details['facilities']:
            console.print(f"• {facility}")

    console.print("\n[italic]Note: Some facilities may be subject to additional charges.[/italic]")

if __name__ == "__main__":
    console.print("[bold blue]Welcome to Travel Booking Agent![/bold blue]")
    app() 