import os
from openai import OpenAI
from typing import List, Dict
from rich.console import Console
from dotenv import load_dotenv

load_dotenv()
console = Console()

class OpenAIAPI:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        self.client = OpenAI(api_key=self.api_key)

    def rank_hotels_by_preferences(self, hotels: List[Dict], preferences: str) -> List[Dict]:
        """Rank hotels based on user preferences using OpenAI."""
        if not hotels or not preferences:
            return hotels

        try:
            # Prepare hotel information for the prompt
            hotel_info = []
            for hotel in hotels:
                facilities = set()
                facilities.update(hotel.get('facilities', []))
                facilities.update(hotel.get('popular_facilities', []))
                
                hotel_info.append({
                    'name': hotel.get('hotel_name'),
                    'rating': hotel.get('review_score', {}).get('score', 'N/A'),
                    'facilities': list(facilities)
                })

            # Create the prompt
            prompt = f"""Given the following hotels and user preferences: '{preferences}',
            rank the top 3 hotels based on how well they match the preferences and their ratings.
            Consider both the facilities and the rating score.
            
            Hotels:
            {hotel_info}
            
            Return only the indices of the top 3 hotels in order (0-based index), separated by commas."""

            # Get ranking from OpenAI
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a hotel ranking assistant. Respond only with comma-separated indices."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=50,
                temperature=0.3
            )

            # Parse response
            indices_str = response.choices[0].message.content.strip()
            try:
                indices = [int(idx.strip()) for idx in indices_str.split(',')][:3]
                # Reorder hotels based on ranking
                ranked_hotels = []
                for idx in indices:
                    if 0 <= idx < len(hotels):
                        ranked_hotels.append(hotels[idx])
                return ranked_hotels
            except ValueError:
                console.print("[yellow]Error parsing OpenAI ranking response, using default ranking[/yellow]")
                return hotels[:3]

        except Exception as e:
            console.print(f"[yellow]Error using OpenAI for ranking: {str(e)}. Using default ranking.[/yellow]")
            # Fall back to simple rating-based ranking
            return sorted(hotels, 
                        key=lambda x: float(x.get('review_score', {}).get('score', 0)), 
                        reverse=True)[:3] 