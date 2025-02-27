import os
import requests
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from rich.console import Console

load_dotenv()
console = Console()

class BookingAPI:
    def __init__(self):
        self.base_url = "https://booking-com15.p.rapidapi.com/api/v1"
        self.headers = {
            "X-RapidAPI-Key": os.getenv("RAPIDAPI_KEY"),
            "X-RapidAPI-Host": "booking-com15.p.rapidapi.com"
        }
        if not self.headers["X-RapidAPI-Key"]:
            raise ValueError("RAPIDAPI_KEY not found in environment variables")

    def search_hotels(self, 
                     destination: str, 
                     checkin_date: str, 
                     checkout_date: str, 
                     adults_number: int,
                     room_number: int = 1) -> Dict[str, Any]:
        """Search for hotels in a specific destination."""
        # First get destination ID
        dest_id = self._get_destination_id(destination)
        if not dest_id:
            return {"results": []}

        # Search for hotels using destination ID
        endpoint = f"{self.base_url}/hotels/searchHotels"
        params = {
            "dest_id": dest_id,
            "search_type": "CITY",
            "arrival_date": checkin_date,
            "departure_date": checkout_date,
            "adults": str(adults_number),
            "children_age": "0,17",
            "room_qty": str(room_number),
            "page_number": "1",
            "units": "metric",
            "currency_code": "USD"
        }
        
        try:
            response = requests.get(endpoint, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
            
            if not data or 'data' not in data:
                console.print("[red]No hotels found for the given criteria[/red]")
                return {"results": []}
            
            results = []
            hotels = data.get('data', {}).get('hotels', [])
            
            for hotel in hotels:
                property_data = hotel.get('property', {})
                price_data = property_data.get('priceBreakdown', {}).get('grossPrice', {})
                
                # Get detailed information for each hotel
                hotel_details = self.get_hotel_details(
                    str(hotel.get('hotel_id', '')),
                    checkin_date,
                    checkout_date
                )
                
                hotel_data = {
                    'hotel_id': str(hotel.get('hotel_id', '')),
                    'hotel_name': property_data.get('name', 'N/A'),
                    'review_score': {
                        'score': property_data.get('reviewScore', 'N/A'),
                        'word': property_data.get('reviewScoreWord', 'N/A'),
                        'reviews_count': property_data.get('reviewCount', 0)
                    },
                    'price': {
                        'value': price_data.get('value', 'N/A'),
                        'currency': price_data.get('currency', 'USD')
                    },
                    'address': hotel_details.get('address', 'N/A'),
                    'location': f"{hotel_details.get('city', 'N/A')}, {hotel_details.get('country', 'N/A')}",
                    'website': hotel_details.get('url', 'N/A'),
                    'facilities': hotel_details.get('facilities', []),
                    'popular_facilities': hotel_details.get('popular_facilities', [])
                }
                results.append(hotel_data)
            
            return {"results": results}
            
        except requests.exceptions.RequestException as e:
            console.print(f"[red]Error making API request: {str(e)}[/red]")
            return {"results": []}

    def _get_destination_id(self, query: str) -> Optional[str]:
        """Get destination ID from location search."""
        endpoint = f"{self.base_url}/hotels/searchDestination"
        params = {"query": query}
        
        try:
            response = requests.get(endpoint, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data and 'data' in data and data['data']:
                return data['data'][0]['dest_id']
            
            console.print(f"[red]No destination found for: {query}[/red]")
            return None
            
        except requests.exceptions.RequestException as e:
            console.print(f"[red]Error searching destination: {str(e)}[/red]")
            return None

    def get_hotel_details(self, hotel_id: str, arrival_date: str, departure_date: str) -> Dict[str, Any]:
        """Get detailed information about a specific hotel."""
        endpoint = f"{self.base_url}/hotels/getHotelDetails"
        params = {
            "hotel_id": hotel_id,
            "arrival_date": arrival_date,
            "departure_date": departure_date,
            "currency_code": "USD",
            "languagecode": "en-us"
        }
        
        try:
            response = requests.get(endpoint, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
            
            if not data or 'data' not in data:
                console.print("[red]No details found for this hotel[/red]")
                return {}
            
            hotel_data = data['data']
            return {
                'name': hotel_data.get('hotel_name', 'N/A'),
                'address': hotel_data.get('address', 'N/A'),
                'city': hotel_data.get('city', 'N/A'),
                'country': hotel_data.get('country_trans', 'N/A'),
                'website': hotel_data.get('url', 'N/A'),
                'facilities': [
                    facility.get('name') 
                    for facility in hotel_data.get('property_highlight_strip', [])
                ],
                'popular_facilities': [
                    facility.get('name')
                    for facility in hotel_data.get('facilities_block', {}).get('facilities', [])
                ],
                'family_facilities': hotel_data.get('family_facilities', [])
            }
            
        except requests.exceptions.RequestException as e:
            console.print(f"[red]Error fetching hotel details: {str(e)}[/red]")
            return {}

    def search_nearby(self, 
                     latitude: float, 
                     longitude: float,
                     checkin_date: str,
                     checkout_date: str) -> Dict[str, Any]:
        """Search for hotels near a specific location."""
        endpoint = f"{self.base_url}/hotels/nearby"
        params = {
            "latitude": str(latitude),
            "longitude": str(longitude),
            "checkin_date": checkin_date,
            "checkout_date": checkout_date
        }
        
        response = requests.get(endpoint, headers=self.headers, params=params)
        return response.json() 