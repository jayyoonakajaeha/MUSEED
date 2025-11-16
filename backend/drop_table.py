import os
import sys
from sqlalchemy import create_engine

# Add the app's root directory to the Python path to allow for model imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from app.config import settings
from app.database import Base
from app import models # Import all models to ensure they are registered with Base

# Connect to the database
engine = create_engine(settings.DATABASE_URL)

try:
    print("Dropping all known tables...")
    # drop_all handles dependencies automatically
    Base.metadata.drop_all(engine)
    print("All tables dropped successfully.")

except Exception as e:
    print(f"An error occurred: {e}")

