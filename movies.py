import random
import statistics
import matplotlib.pyplot as plt
from database import (
    list_movies,
    add_movie,
    delete_movie,
    update_movie,
    get_movie_by_title
)
from api_client import OMDBClient
from website_generator import generate_website  # Added this import

API_KEY = "your_api_key_here"  # Replace with your OMDB API key
omdb_client = OMDBClient(API_KEY)

def format_rating(rating):
    """Format rating to 1 decimal place"""
    return f"{float(rating):.1f}"

def display_menu():
    """Show main menu"""
    print("\n===== Movie Database =====")
    print("1. List all movies")
    print("2. Add movie (OMDB)")
    print("3. Delete movie")
    print("4. Update movie rating")
    print("5. View statistics")
    print("6. Get random movie")
    print("7. Search movies")
    print("8. Sort by rating")
    print("9. Rating histogram")
    print("10. Generate website")
    print("0. Exit")

def add_movie_interactive():
    """Add movie using OMDB API"""
    title = input("Enter movie title: ").strip()
    if not title:
        print("Error: Title cannot be empty")
        return
    
    if get_movie_by_title(title):
        print(f"Error: '{title}' already exists!")
        return
    
    print(f"\nSearching OMDB for '{title}'...")
    movie_data = omdb_client.get_movie_details(title)
    
    if not movie_data:
        print("Error: Movie not found or API error")
        return
    
    print("\nFound movie details:")
    print(f"Title: {movie_data['title']}")
    print(f"Year: {movie_data['year']}")
    print(f"Rating: {format_rating(movie_data['rating'])}")
    if movie_data.get('poster_url'):
        print("Poster available")
    
    confirm = input("\nAdd this movie? (y/n): ").lower()
    if confirm == 'y':
        if add_movie(**movie_data):
            print(f"\nAdded '{movie_data['title']}' successfully!")
        else:
            print("Failed to add movie")

def list_all_movies():
    """Display all movies with details"""
    movies = list_movies()
    print(f"\nFound {len(movies)} movies:")
    for title, details in movies.items():
        print(f"\n{title} ({details['year']})")
        print(f"Rating: {format_rating(details['rating'])}")
        if details.get('poster_url'):
            print("Poster available")
        if details.get('director'):
            print(f"Director: {details['director']}")
        if details.get('plot'):
            print(f"Plot: {details['plot'][:100]}...")

def delete_movie_interactive():
    """Delete a movie by title"""
    title = input("Enter movie title to delete: ").strip()
    if not title:
        print("Error: Title cannot be empty")
        return
    
    if delete_movie(title):
        print(f"Deleted '{title}' successfully")
    else:
        print(f"Error: Could not delete '{title}'")

def update_movie_interactive():
    """Update a movie's rating"""
    title = input("Enter movie title to update: ").strip()
    if not title:
        print("Error: Title cannot be empty")
        return
    
    movie = get_movie_by_title(title)
    if not movie:
        print(f"Error: '{title}' not found in database")
        return
    
    try:
        new_rating = float(input(f"Current rating: {movie['rating']}\nEnter new rating (1-10): "))
        if not 1 <= new_rating <= 10:
            print("Error: Rating must be between 1-10")
            return
        
        if update_movie(title, new_rating):
            print(f"Updated '{title}' rating to {new_rating}")
        else:
            print("Error: Failed to update rating")
    except ValueError:
        print("Error: Please enter a valid number")

def show_statistics():
    """Display movie statistics"""
    movies = list_movies()
    if not movies:
        print("No movies in database")
        return
    
    ratings = [m['rating'] for m in movies.values()]
    
    print("\n===== Statistics =====")
    print(f"Total movies: {len(movies)}")
    print(f"Average rating: {format_rating(sum(ratings)/len(ratings))}")
    print(f"Median rating: {format_rating(statistics.median(ratings))}")
    print(f"Highest rating: {format_rating(max(ratings))}")
    print(f"Lowest rating: {format_rating(min(ratings))}")

def get_random_movie():
    """Display a random movie"""
    movies = list_movies()
    if not movies:
        print("No movies in database")
        return
    
    title = random.choice(list(movies.keys()))
    movie = movies[title]
    
    print("\n===== Random Movie =====")
    print(f"Title: {title} ({movie['year']})")
    print(f"Rating: {format_rating(movie['rating'])}")
    if movie.get('director'):
        print(f"Director: {movie['director']}")
    if movie.get('plot'):
        print(f"Plot: {movie['plot']}")

def search_movies():
    """Search movies by title"""
    search_term = input("Enter search term: ").strip().lower()
    if not search_term:
        print("Error: Please enter a search term")
        return
    
    movies = list_movies()
    found = False
    
    for title, details in movies.items():
        if search_term in title.lower():
            found = True
            print(f"\n{title} ({details['year']})")
            print(f"Rating: {format_rating(details['rating'])}")
            if details.get('plot'):
                print(f"Plot: {details['plot'][:100]}...")
    
    if not found:
        print("No matching movies found")

def sort_by_rating():
    """Display movies sorted by rating"""
    movies = list_movies()
    if not movies:
        print("No movies in database")
        return
    
    sorted_movies = sorted(movies.items(), key=lambda x: x[1]['rating'], reverse=True)
    
    print("\nMovies sorted by rating (highest first):")
    for title, details in sorted_movies:
        print(f"{title}: {format_rating(details['rating'])}")

def show_histogram():
    """Display rating distribution histogram"""
    movies = list_movies()
    if not movies:
        print("No movies in database")
        return
    
    ratings = [m['rating'] for m in movies.values()]
    
    plt.figure(figsize=(10, 6))
    plt.hist(ratings, bins=10, range=(1, 10), color='skyblue', edgecolor='black')
    plt.title('Movie Ratings Distribution')
    plt.xlabel('Rating')
    plt.ylabel('Number of Movies')
    plt.xticks(range(1, 11))
    plt.grid(axis='y', alpha=0.75)
    
    avg = sum(ratings)/len(ratings)
    plt.axvline(avg, color='red', linestyle='--', label=f'Average: {format_rating(avg)}')
    plt.legend()
    
    plt.show()

def main():
    """Main application loop"""
    while True:
        display_menu()
        choice = input("\nEnter choice (0-10): ").strip()
        
        if choice == "1":
            list_all_movies()
        elif choice == "2":
            add_movie_interactive()
        elif choice == "3":
            delete_movie_interactive()
        elif choice == "4":
            update_movie_interactive()
        elif choice == "5":
            show_statistics()
        elif choice == "6":
            get_random_movie()
        elif choice == "7":
            search_movies()
        elif choice == "8":
            sort_by_rating()
        elif choice == "9":
            show_histogram()
        elif choice == "10":
            generate_website()  # Now properly imported
        elif choice == "0":
            print("Goodbye!")
            break
        else:
            print("Invalid choice!")

if __name__ == "__main__":
    main()
