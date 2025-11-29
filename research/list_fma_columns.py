import pandas as pd

FMA_TRACKS_CSV_PATH = '/home/jay/MusicAI/fma/data/fma_metadata/tracks.csv'

def list_columns():
    """
    Reads the header of the tracks.csv file and prints all available columns.
    """
    print(f"--- Reading columns from {FMA_TRACKS_CSV_PATH} ---")
    try:
        # Read only the first row to get the headers
        df = pd.read_csv(FMA_TRACKS_CSV_PATH, header=[0, 1], nrows=0, skiprows=[2])
        
        print("Available columns:")
        for col in df.columns:
            print(f"  - {col}")
            
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    list_columns()
