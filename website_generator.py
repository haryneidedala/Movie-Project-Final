from jinja2 import Environment, FileSystemLoader
from database import list_movies
import os
from datetime import datetime

def generate_website():
    """Generate static website with movie data"""
    try:
        os.makedirs("website", exist_ok=True)
        
        env = Environment(loader=FileSystemLoader('templates'))
        template = env.get_template('index.html')
        
        movies = sorted(
            list_movies().items(),
            key=lambda x: x[1]['rating'],
            reverse=True
        )
        
        with open("website/index.html", "w") as f:
            f.write(template.render(
                movies=movies,
                generated_at=datetime.now().strftime("%Y-%m-%d %H:%M")
            ))
        
        print("Successfully generated website in 'website' directory")
    except Exception as e:
        print(f"Error generating website: {str(e)}")
