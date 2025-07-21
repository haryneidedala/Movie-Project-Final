import requests

class OMDBClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "http://www.omdbapi.com/"
        self.timeout = 10  # seconds

    def get_movie_details(self, title):
        """Fetch complete movie details from OMDB API"""
        try:
            params = {
                'apikey': self.api_key,
                't': title,
                'r': 'json'
            }
            response = requests.get(self.base_url, params=params, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            
            if data.get('Response') == 'False':
                return None
                
            return {
                'title': data.get('Title', title),
                'year': int(data['Year']) if data.get('Year', '').isdigit() else 0,
                'rating': float(data.get('imdbRating', 0)),
                'director': data.get('Director'),
                'poster_url': data.get('Poster') if data.get('Poster') != 'N/A' else None,
                'plot': data.get('Plot'),
                'actors': data.get('Actors'),
                'genre': data.get('Genre')
            }
            
        except requests.exceptions.RequestException as e:
            print(f"API Error: {str(e)}")
            return None
        except (ValueError, KeyError) as e:
            print(f"Data Error: {str(e)}")
            return None
