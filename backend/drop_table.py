import sqlalchemy
from app.config import settings

# Connect to the database
engine = sqlalchemy.create_engine(settings.DATABASE_URL)

try:
    with engine.connect() as connection:
        # We need to use a transaction to drop the tables
        with connection.begin():
            print("Dropping all known tables with CASCADE...")
            # Drop tables in an order that respects dependencies, or use CASCADE
            # Using CASCADE is more robust if more tables are added.
            connection.execute(sqlalchemy.text("DROP TABLE IF EXISTS listening_history;"))
            connection.execute(sqlalchemy.text("DROP TABLE IF EXISTS users CASCADE;"))
            print("Tables dropped successfully.")

except Exception as e:
    print(f"An error occurred: {e}")

