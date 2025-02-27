import os
from openai import OpenAI
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()

class OpenAIAPI:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def rank_hotels(self, hotels: List[Dict], user_preferences: str) -> List[Dict]:
        """Rank hotels based on user preferences using OpenAI."""
        prompt = f"""
        Given these hotels and user preferences: "{user_preferences}"
        Please rank the following hotels from best to worst match:
        {str(hotels)}
        Return only the hotel IDs in order of preference.
        """

        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful travel assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        
        return self._process_ranking_response(response.choices[0].message.content, hotels)

    def _process_ranking_response(self, response: str, hotels: List[Dict]) -> List[Dict]:
        """Process the OpenAI response and return ranked hotels."""
        # Extract hotel IDs from response and reorder the hotel list
        hotel_ids = [id.strip() for id in response.split() if id.strip().isdigit()]
        ranked_hotels = []
        
        for hotel_id in hotel_ids:
            for hotel in hotels:
                if str(hotel.get('hotel_id')) == hotel_id:
                    ranked_hotels.append(hotel)
                    break
                    
        return ranked_hotels 