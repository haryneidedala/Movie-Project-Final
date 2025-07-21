from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

DB_URL = "sqlite:///movies.db"
engine = create_engine(DB_URL, echo=True)

def initialize_database():
    """Initialize database with users and movies tables"""
    with engine.connect() as conn:
        # Create users table
        conn.execute(text("DROP TABLE IF EXISTS users"))
        conn.execute(text("DROP TABLE IF EXISTS movies"))
        
        conn.execute(text("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        
        # Movies table with user_id foreign key
        conn.execute(text("""
            CREATE TABLE movies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                year INTEGER NOT NULL,
                rating REAL NOT NULL,
                director TEXT,
                poster_url TEXT,
                plot TEXT,
                actors TEXT,
                genre TEXT,
                user_id INTEGER NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id),
                UNIQUE(title, user_id)
            )
        """))
        conn.commit()

def add_user(username):
    """Add a new user"""
    try:
        with engine.connect() as conn:
            result = conn.execute(
                text("INSERT INTO users (username) VALUES (:username)"),
                {"username": username}
            )
            conn.commit()
            return result.lastrowid
    except IntegrityError:
        print(f"Username '{username}' already exists!")
        return None

def get_users():
    """Get all users"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT id, username FROM users"))
            return [dict(row) for row in result.mappings()]
    except SQLAlchemyError as e:
        print(f"Database error: {e}")
        return []

def get_user_by_id(user_id):
    """Get user by ID"""
    try:
        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT * FROM users WHERE id = :user_id"),
                {"user_id": user_id}
            )
            user = result.mappings().first()
            return dict(user) if user else None
    except SQLAlchemyError as e:
        print(f"Database error: {e}")
        return None

def add_movie(user_id, title, year, rating, **kwargs):
    """Add movie to user's collection"""
    try:
        with engine.connect() as conn:
            conn.execute(text("""
                INSERT INTO movies 
                (title, year, rating, director, poster_url, plot, actors, genre, user_id)
                VALUES 
                (:title, :year, :rating, :director, :poster_url, :plot, :actors, :genre, :user_id)
            """), {
                "title": title,
                "year": year,
                "rating": rating,
                "director": kwargs.get('director'),
                "poster_url": kwargs.get('poster_url'),
                "plot": kwargs.get('plot'),
                "actors": kwargs.get('actors'),
                "genre": kwargs.get('genre'),
                "user_id": user_id
            })
            conn.commit()
        return True
    except IntegrityError:
        print(f"Movie '{title}' already exists in your collection!")
        return False
    except SQLAlchemyError as e:
        print(f"Database error: {e}")
        return False

def list_movies(user_id):
    """Get all movies for a user"""
    try:
        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT * FROM movies WHERE user_id = :user_id"),
                {"user_id": user_id}
            )
            return [dict(row) for row in result.mappings()]
    except SQLAlchemyError as e:
        print(f"Database error: {e}")
        return []

def delete_movie(user_id, title):
    """Delete movie from user's collection"""
    try:
        with engine.connect() as conn:
            result = conn.execute(
                text("DELETE FROM movies WHERE user_id = :user_id AND title = :title"),
                {"user_id": user_id, "title": title}
            )
            conn.commit()
            return result.rowcount > 0
    except SQLAlchemyError as e:
        print(f"Database error: {e}")
        return False

def update_movie_rating(user_id, title, new_rating):
    """Update movie rating"""
    try:
        with engine.connect() as conn:
            result = conn.execute(
                text("""
                    UPDATE movies 
                    SET rating = :rating 
                    WHERE user_id = :user_id AND title = :title
                """),
                {"rating": new_rating, "user_id": user_id, "title": title}
            )
            conn.commit()
            return result.rowcount > 0
    except SQLAlchemyError as e:
        print(f"Database error: {e}")
        return False

def get_movie_by_title(user_id, title):
    """Get specific movie from user's collection"""
    try:
        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT * FROM movies WHERE user_id = :user_id AND title = :title"),
                {"user_id": user_id, "title": title}
            )
            movie = result.mappings().first()
            return dict(movie) if movie else None
    except SQLAlchemyError as e:
        print(f"Database error: {e}")
        return None

# Initialize database when module loads
initialize_database()
