import pandas as pd
import os

RAW_TRACKS_CSV_PATH = '/home/jay/MusicAI/fma/data/fma_metadata/raw_tracks.csv'

def inspect_image_column():
    """
    Reads the raw_tracks.csv file and inspects the 'track_image_file' column.
    """
    print(f"--- Inspecting 'track_image_file' column from {RAW_TRACKS_CSV_PATH} ---")
    try:
        df = pd.read_csv(RAW_TRACKS_CSV_PATH)
        
        if 'track_image_file' not in df.columns:
            print("FATAL: 'track_image_file' column not found in the CSV.")
            print("Available columns are:", df.columns.tolist())
            return

        print("\nFirst 5 values from the 'track_image_file' column:")
        for i, value in enumerate(df['track_image_file'].head(5)):
            print(f"  Row {i+1}: {value}")
            
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    inspect_image_column()
