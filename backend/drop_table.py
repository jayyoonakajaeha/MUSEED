import sqlalchemy
from app.config import settings

# Connect to the database
engine = sqlalchemy.create_engine(settings.DATABASE_URL)

try:
    with engine.connect() as connection:
        # We need to use a transaction to drop the table
        with connection.begin():
            print("Dropping 'users' table...")
            connection.execute(sqlalchemy.text("DROP TABLE IF EXISTS users;"))
            print("'users' table dropped successfully.")

except Exception as e:
    print(f"An error occurred: {e}")

