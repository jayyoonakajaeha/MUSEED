import sqlalchemy
from app.config import settings

# Connect to the database
engine = sqlalchemy.create_engine(settings.DATABASE_URL)

try:
    with engine.connect() as connection:
        # We need to use a transaction to drop the tables
        with connection.begin():
            print("Dropping all known tables...")
            # Drop tables in reverse order of dependency
            connection.execute(sqlalchemy.text("DROP TABLE IF EXISTS playlist_tracks;"))
            connection.execute(sqlalchemy.text("DROP TABLE IF EXISTS playlists;"))
            connection.execute(sqlalchemy.text("DROP TABLE IF EXISTS listening_history;"))
            connection.execute(sqlalchemy.text("DROP TABLE IF EXISTS tracks;"))
            connection.execute(sqlalchemy.text("DROP TABLE IF EXISTS users;"))
            print("All tables dropped successfully.")

except Exception as e:
    print(f"An error occurred: {e}")

