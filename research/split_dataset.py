import json
import os
import random
from sklearn.model_selection import train_test_split
from collections import Counter

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # MUSEED/research -> MUSEED
# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # MUSEED/research -> MUSEED
OUTPUT_DIR = os.getenv("MUSEED_DATA_ROOT", os.path.join(BASE_DIR, "data"))

SOURCE_JSONL = os.path.join(OUTPUT_DIR, 'multi_axis_analysis_results.jsonl')
TRAIN_JSONL = os.path.join(OUTPUT_DIR, 'train_metadata.jsonl')
TEST_JSONL = os.path.join(OUTPUT_DIR, 'test_metadata.jsonl')

def split_dataset():
    print(f"Loading data from {SOURCE_JSONL}...")
    
    data = []
    with open(SOURCE_JSONL, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                item = json.loads(line)
                # Ensure genre exists
                if 'genre' in item and item['genre']:
                    data.append(item)
            except:
                continue
    
    print(f"Total valid tracks loaded: {len(data)}")
    
    # Extract genres for stratification
    genres = [item['genre'] for item in data]
    genre_counts = Counter(genres)
    
    # Filter out classes with only 1 sample (cannot stratify split)
    valid_indices = [i for i, g in enumerate(genres) if genre_counts[g] > 1]
    filtered_data = [data[i] for i in valid_indices]
    filtered_genres = [genres[i] for i in valid_indices]
    
    print(f"Tracks after filtering single-sample genres: {len(filtered_data)}")
    
    # Perform Stratified Split (80% Train, 20% Test)
    train_data, test_data = train_test_split(
        filtered_data, 
        test_size=0.2, 
        random_state=42, 
        stratify=filtered_genres
    )
    
    print(f"Train set size: {len(train_data)}")
    print(f"Test set size: {len(test_data)}")
    
    # Save to files
    print(f"Saving to {TRAIN_JSONL}...")
    with open(TRAIN_JSONL, 'w', encoding='utf-8') as f:
        for item in train_data:
            f.write(json.dumps(item) + '\n')
            
    print(f"Saving to {TEST_JSONL}...")
    with open(TEST_JSONL, 'w', encoding='utf-8') as f:
        for item in test_data:
            f.write(json.dumps(item) + '\n')
            
    print("Done.")

if __name__ == "__main__":
    split_dataset()
