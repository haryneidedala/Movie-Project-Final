from jinja2 import Environment, FileSystemLoader
import os
from datetime import datetime

def generate_user_website(user_id, username):
    """Generate personalized website for a user"""
    try:
        from database import list_movies
        
        os.makedirs("websites", exist_ok=True)
        
        env = Environment(loader=FileSystemLoader('templates'))
        template = env.get_template('user_index.html')
        
        movies = sorted(
            list_movies(user_id),
            key=lambda x: x['rating'],
            reverse=True
        )
        
        filename = f"websites/{username}_movies.html"
        with open(filename, "w") as f:
            f.write(template.render(
                username=username,
                movies=movies,
                generated_at=datetime.now().strftime("%Y-%m-%d %H:%M")
            ))
        
        print(f"\nSuccessfully generated website: {filename}")
        return True
    except Exception as e:
        print(f"\nError generating website: {str(e)}")
        return False
