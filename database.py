from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

DB_URL = "sqlite:///movies.db"
engine = create_engine(DB_URL, echo=True)

def initialize_database():
    """Initialize database with complete schema"""
    with engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS movies"))
        conn.commit()
        conn.execute(text("""
            CREATE TABLE movies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT UNIQUE NOT NULL,
                year INTEGER NOT NULL,
                rating REAL NOT NULL,
                director TEXT,
                poster_url TEXT,
                plot TEXT,
                actors TEXT,
                genre TEXT
            )
        """))
        conn.commit()

def list_movies():
    """Get all movies with full details"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT * FROM movies"))
            return {row['title']: dict(row) for row in result.mappings()}
    except SQLAlchemyError as e:
        print(f"Database error: {e}")
        return {}

def add_movie(title, year, rating, **kwargs):
    """Add movie with all metadata"""
    try:
        with engine.connect() as conn:
            conn.execute(text("""
                INSERT INTO movies 
                (title, year, rating, director, poster_url, plot, actors, genre)
                VALUES 
                (:title, :year, :rating, :director, :poster_url, :plot, :actors, :genre)
            """), {
                "title": title,
                "year": year,
                "rating": rating,
                "director": kwargs.get('director'),
                "poster_url": kwargs.get('poster_url'),
                "plot": kwargs.get('plot'),
                "actors": kwargs.get('actors'),
                "genre": kwargs.get('genre')
            })
            conn.commit()
        return True
    except IntegrityError:
        print(f"Movie '{title}' already exists!")
        return False
    except SQLAlchemyError as e:
        print(f"Database error: {e}")
        return False

def delete_movie(title):
    """Delete a movie by title"""
    try:
        with engine.connect() as conn:
            result = conn.execute(
                text("DELETE FROM movies WHERE title = :title"),
                {"title": title}
            )
            conn.commit()
            return result.rowcount > 0
    except SQLAlchemyError as e:
        print(f"Database error: {e}")
        return False

def update_movie(title, rating):
    """Update movie rating"""
    try:
        with engine.connect() as conn:
            result = conn.execute(
                text("UPDATE movies SET rating = :rating WHERE title = :title"),
                {"rating": rating, "title": title}
            )
            conn.commit()
            return result.rowcount > 0
    except SQLAlchemyError as e:
        print(f"Database error: {e}")
        return False

def get_movie_by_title(title):
    """Get single movie by title"""
    try:
        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT * FROM movies WHERE title = :title"),
                {"title": title}
            )
            movie = result.mappings().first()
            return dict(movie) if movie else None
    except SQLAlchemyError as e:
        print(f"Database error: {e}")
        return None

initialize_database()
