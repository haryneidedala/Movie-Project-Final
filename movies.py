import random
import statistics
import matplotlib.pyplot as plt
from database import (
    add_user,
    get_users,
    get_user_by_id,
    add_movie,
    list_movies,
    delete_movie,
    update_movie_rating,
    get_movie_by_title
)
from api_client import OMDBClient
from website_generator import generate_user_website

API_KEY = "http://www.omdbapi.com/?i=tt3896198&apikey=f006317d"  # Replace with your OMDB API key
omdb_client = OMDBClient(API_KEY)

class MovieApp:
    def __init__(self):
        self.current_user = None
    
    def format_rating(self, rating):
        """Format rating to 1 decimal place"""
        return f"{float(rating):.1f}"
    
    def display_main_menu(self):
        """Display user selection menu"""
        print("\n===== Movie Database =====")
        print("1. Select user")
        print("2. Create new user")
        print("0. Exit")
    
    def display_user_menu(self):
        """Display menu for logged-in user"""
        print(f"\n===== {self.current_user['username']}'s Collection =====")
        print("1. List my movies")
        print("2. Add movie (OMDB)")
        print("3. Delete movie")
        print("4. Update movie rating")
        print("5. View statistics")
        print("6. Get random movie")
        print("7. Search my movies")
        print("8. Sort by rating")
        print("9. Rating histogram")
        print("10. Generate my website")
        print("0. Logout")
    
    def select_user_interactive(self):
        """Handle user selection"""
        users = get_users()
        if not users:
            print("\nNo users found. Please create a new user.")
            return False
        
        print("\nSelect a user:")
        for i, user in enumerate(users, 1):
            print(f"{i}. {user['username']}")
        print(f"{len(users)+1}. Cancel")
        
        try:
            choice = int(input("Enter choice: "))
            if 1 <= choice <= len(users):
                self.current_user = users[choice-1]
                print(f"\nWelcome back, {self.current_user['username']}!")
                return True
            elif choice == len(users)+1:
                return False
            print("Invalid choice")
        except ValueError:
            print("Please enter a number")
        return False
    
    def create_user_interactive(self):
        """Handle new user creation"""
        username = input("Enter new username: ").strip()
        if not username:
            print("Username cannot be empty")
            return False
        
        user_id = add_user(username)
        if user_id:
            self.current_user = {'id': user_id, 'username': username}
            print(f"\nWelcome, {username}! Account created successfully.")
            return True
        return False
    
    def list_user_movies(self):
        """List all movies for current user"""
        if not self.current_user:
            print("Please select a user first")
            return
        
        movies = list_movies(self.current_user['id'])
        if not movies:
            print(f"\n{self.current_user['username']}, your collection is empty!")
            return
        
        print(f"\n{self.current_user['username']}'s Movie Collection:")
        for movie in movies:
            print(f"\n{movie['title']} ({movie['year']})")
            print(f"Rating: {self.format_rating(movie['rating'])}")
            if movie.get('poster_url'):
                print("Poster available")
            if movie.get('director'):
                print(f"Director: {movie['director']}")
            if movie.get('plot'):
                print(f"Plot: {movie['plot'][:100]}...")
    
    def add_movie_interactive(self):
        """Add movie to current user's collection"""
        if not self.current_user:
            print("Please select a user first")
            return
        
        title = input("Enter movie title: ").strip()
        if not title:
            print("Error: Title cannot be empty")
            return
        
        # Check if movie already exists for this user
        if get_movie_by_title(self.current_user['id'], title):
            print(f"Error: '{title}' already exists in your collection!")
            return
        
        print(f"\nSearching OMDB for '{title}'...")
        movie_data = omdb_client.get_movie_details(title)
        
        if not movie_data:
            print("Error: Movie not found or API error")
            return
        
        print("\nFound movie details:")
        print(f"Title: {movie_data['title']}")
        print(f"Year: {movie_data['year']}")
        print(f"Rating: {self.format_rating(movie_data['rating'])}")
        if movie_data.get('poster_url'):
            print("Poster available")
        
        confirm = input("\nAdd this movie to your collection? (y/n): ").lower()
        if confirm == 'y':
            if add_movie(self.current_user['id'], **movie_data):
                print(f"\nAdded '{movie_data['title']}' to your collection!")
            else:
                print("Failed to add movie")
    
    def delete_movie_interactive(self):
        """Delete movie from current user's collection"""
        if not self.current_user:
            print("Please select a user first")
            return
        
        title = input("Enter movie title to delete: ").strip()
        if not title:
            print("Error: Title cannot be empty")
            return
        
        if delete_movie(self.current_user['id'], title):
            print(f"\nDeleted '{title}' from your collection")
        else:
            print(f"\nError: '{title}' not found in your collection")
    
    def update_movie_interactive(self):
        """Update movie rating in current user's collection"""
        if not self.current_user:
            print("Please select a user first")
            return
        
        title = input("Enter movie title to update: ").strip()
        if not title:
            print("Error: Title cannot be empty")
            return
        
        movie = get_movie_by_title(self.current_user['id'], title)
        if not movie:
            print(f"\nError: '{title}' not found in your collection")
            return
        
        print(f"\nCurrent rating: {self.format_rating(movie['rating'])}")
        try:
            new_rating = float(input("Enter new rating (1-10): "))
            if not 1 <= new_rating <= 10:
                print("Error: Rating must be between 1-10")
                return
            
            if update_movie_rating(self.current_user['id'], title, new_rating):
                print(f"\nUpdated '{title}' rating to {self.format_rating(new_rating)}")
            else:
                print("\nFailed to update rating")
        except ValueError:
            print("Error: Please enter a valid number")
    
    def show_statistics(self):
        """Show statistics for current user's collection"""
        if not self.current_user:
            print("Please select a user first")
            return
        
        movies = list_movies(self.current_user['id'])
        if not movies:
            print(f"\n{self.current_user['username']}, your collection is empty!")
            return
        
        ratings = [m['rating'] for m in movies]
        
        print(f"\n===== {self.current_user['username']}'s Statistics =====")
        print(f"Total movies: {len(movies)}")
        print(f"Average rating: {self.format_rating(sum(ratings)/len(ratings))}")
        print(f"Median rating: {self.format_rating(statistics.median(ratings))}")
        print(f"Highest rating: {self.format_rating(max(ratings))}")
        print(f"Lowest rating: {self.format_rating(min(ratings))}")
    
    def get_random_movie(self):
        """Show random movie from current user's collection"""
        if not self.current_user:
            print("Please select a user first")
            return
        
        movies = list_movies(self.current_user['id'])
        if not movies:
            print(f"\n{self.current_user['username']}, your collection is empty!")
            return
        
        movie = random.choice(movies)
        print(f"\n===== Random Movie =====")
        print(f"Title: {movie['title']} ({movie['year']})")
        print(f"Rating: {self.format_rating(movie['rating'])}")
        if movie.get('director'):
            print(f"Director: {movie['director']}")
        if movie.get('plot'):
            print(f"Plot: {movie['plot']}")
    
    def search_movies(self):
        """Search movies in current user's collection"""
        if not self.current_user:
            print("Please select a user first")
            return
        
        search_term = input("Enter search term: ").strip().lower()
        if not search_term:
            print("Error: Please enter a search term")
            return
        
        movies = list_movies(self.current_user['id'])
        found = False
        
        for movie in movies:
            if search_term in movie['title'].lower():
                found = True
                print(f"\n{movie['title']} ({movie['year']})")
                print(f"Rating: {self.format_rating(movie['rating'])}")
                if movie.get('plot'):
                    print(f"Plot: {movie['plot'][:100]}...")
        
        if not found:
            print("\nNo matching movies found in your collection")
    
    def sort_by_rating(self):
        """Show movies sorted by rating"""
        if not self.current_user:
            print("Please select a user first")
            return
        
        movies = sorted(
            list_movies(self.current_user['id']),
            key=lambda x: x['rating'],
            reverse=True
        )
        
        if not movies:
            print(f"\n{self.current_user['username']}, your collection is empty!")
            return
        
        print(f"\n{self.current_user['username']}'s Movies Sorted by Rating:")
        for movie in movies:
            print(f"{movie['title']}: {self.format_rating(movie['rating'])}")
    
    def show_histogram(self):
        """Show rating histogram for current user's collection"""
        if not self.current_user:
            print("Please select a user first")
            return
        
        movies = list_movies(self.current_user['id'])
        if not movies:
            print(f"\n{self.current_user['username']}, your collection is empty!")
            return
        
        ratings = [m['rating'] for m in movies]
        
        plt.figure(figsize=(10, 6))
        plt.hist(ratings, bins=10, range=(1, 10), color='skyblue', edgecolor='black')
        plt.title(f"{self.current_user['username']}'s Movie Ratings")
        plt.xlabel('Rating')
        plt.ylabel('Number of Movies')
        plt.xticks(range(1, 11))
        plt.grid(axis='y', alpha=0.75)
        
        avg = sum(ratings)/len(ratings)
        plt.axvline(avg, color='red', linestyle='--', label=f'Average: {self.format_rating(avg)}')
        plt.legend()
        
        plt.show()
    
    def generate_website_interactive(self):
        """Generate website for current user"""
        if not self.current_user:
            print("Please select a user first")
            return
        
        if generate_user_website(self.current_user['id'], self.current_user['username']):
            print(f"Website generated for {self.current_user['username']}")
        else:
            print("Failed to generate website")
    
    def run(self):
        """Main application loop"""
        print("\nWelcome to the Movie Database App! 🎬")
        
        while True:
            if not self.current_user:
                self.display_main_menu()
                choice = input("\nEnter choice: ").strip()
                
                if choice == "1":
                    self.select_user_interactive()
                elif choice == "2":
                    self.create_user_interactive()
                elif choice == "0":
                    print("\nGoodbye!")
                    break
                else:
                    print("\nInvalid choice")
            else:
                self.display_user_menu()
                choice = input("\nEnter choice: ").strip()
                
                if choice == "1":
                    self.list_user_movies()
                elif choice == "2":
                    self.add_movie_interactive()
                elif choice == "3":
                    self.delete_movie_interactive()
                elif choice == "4":
                    self.update_movie_interactive()
                elif choice == "5":
                    self.show_statistics()
                elif choice == "6":
                    self.get_random_movie()
                elif choice == "7":
                    self.search_movies()
                elif choice == "8":
                    self.sort_by_rating()
                elif choice == "9":
                    self.show_histogram()
                elif choice == "10":
                    self.generate_website_interactive()
                elif choice == "0":
                    print(f"\nGoodbye, {self.current_user['username']}!")
                    self.current_user = None
                else:
                    print("\nInvalid choice")

if __name__ == "__main__":
    app = MovieApp()
    app.run()
