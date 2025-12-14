import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import json
import os

# Paths
BASE_DIR = "/home/jay/MusicAI/MUSEED"
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "docs/images")

def load_jsonl(path):
    data = []
    with open(path, 'r') as f:
        for line in f:
            data.append(json.loads(line))
    return pd.DataFrame(data)

def plot_genre_distribution(df, genre_col, title, filename):
    plt.figure(figsize=(14, 8))  # Increased width
    
    # Count genres
    genre_counts = df[genre_col].value_counts()
    total = len(df)
    
    # Define colors
    colors = sns.color_palette('pastel')[0:len(genre_counts)]
    
    # Create Pie Chart
    def autopct_format(pct):
        return ('%1.1f%%' % pct) if pct > 1.5 else ''

    wedges, texts, autotexts = plt.pie(
        genre_counts, 
        labels=None, 
        autopct=autopct_format,
        startangle=140,
        colors=colors,
        pctdistance=0.85
    )
    
    # Legend
    labels = [f"{idx} ({val} - {val/total*100:.1f}%)" for idx, val in zip(genre_counts.index, genre_counts.values)]
    
    # Place legend to the right
    plt.legend(wedges, labels, title="Genres", loc="center left", bbox_to_anchor=(1.0, 0.5))
    
    plt.title(f"{title}\n(Total: {total} Tracks)", fontsize=16, fontweight='bold')
    
    # Adjust layout to make room for legend
    plt.subplots_adjust(left=0.1, bottom=0.1, right=0.75) 
    
    plt.savefig(os.path.join(OUTPUT_DIR, filename))
    print(f"Saved {filename}")
    plt.close()

def main():
    # 1. Load FMA Data (Train + Test)
    print("Loading FMA Data...")
    train_path = os.path.join(DATA_DIR, "train_metadata.jsonl")
    test_path = os.path.join(DATA_DIR, "test_metadata.jsonl")
    
    if os.path.exists(train_path) and os.path.exists(test_path):
        df_train = load_jsonl(train_path)
        df_test = load_jsonl(test_path)
        df_fma = pd.concat([df_train, df_test], ignore_index=True)
        
        # Identify Genre Column
        # Check for 'genre', 'top_level_genre', 'genre_top'
        genre_col = None
        for col in ['genre', 'top_level_genre', 'genre_top', 'mapped_genre']:
            if col in df_fma.columns:
                genre_col = col
                break
        
        if genre_col:
            plot_genre_distribution(df_fma, genre_col, "FMA Dataset Distribution", "fma_genre_dist.png")
        else:
            print("Could not find genre column in FMA data", df_fma.columns)
    else:
        print("FMA metadata files not found.")

    # 2. Load Jamendo Data
    print("Loading Jamendo Data...")
    jamendo_path = os.path.join(DATA_DIR, "jamendo_rich_metadata.jsonl")
    
    if os.path.exists(jamendo_path):
        df_jam = load_jsonl(jamendo_path)
        
        # Define FMA Mapping (Based on Report Table 2)
        # Priorities can be managed by order or logic. 
        # Here we map specific keywords to FMA Genres.
        
        # Mapping Rules (Tag Keyword -> FMA Genre)
        MAPPING_RULES = {
            'pop': 'Pop', 'indie': 'Pop', 'pop-rock': 'Pop', 'dream pop': 'Pop', 'synthpop': 'Pop',
            'rock': 'Rock',
            'electronic': 'Electronic', 'house': 'Electronic', 'dance': 'Electronic', 'dubstep': 'Electronic', 'chillout': 'Electronic', '8bit': 'Electronic',
            'rnb': 'Soul-RnB', 'soul': 'Soul-RnB', 'funk': 'Soul-RnB',
            'folk': 'Folk',
            'jazz': 'Jazz',
            'new age': 'Instrumental', 'film score': 'Instrumental', 'soundtrack': 'Instrumental',
            'ambient': 'Experimental', 'experimental': 'Experimental',
            'hip-hop': 'Hip-Hop', 'hip hop': 'Hip-Hop', 'rap': 'Hip-Hop',
            'country': 'Country'
        }
        
        def map_genre(row):
            # Try to find tags
            tags = []
            if 'tags' in row and isinstance(row['tags'], list):
                tags = row['tags']
            elif 'genre' in row and row['genre']:
                tags = [row['genre']]
            elif 'mapped_genre' in row and row['mapped_genre']:
                # If already mapped, maybe trust it? But user asked for RE-MAPPING based on FMA logic.
                # Let's treat it as a tag if it exists.
                tags.append(row['mapped_genre'])
            
            # Normalize tags to lowercase
            tags = [str(t).lower() for t in tags]
            
            # Find match
            for tag in tags:
                # Check exact match or keyword presence? Report implies specific tag list.
                # We check if known keywords appear in the tag.
                for keyword, target in MAPPING_RULES.items():
                    if keyword == tag or keyword in tag: # simple containment
                        return target
            
            return 'Unknown'

        # Apply mapping
        df_jam['fma_mapped_genre'] = df_jam.apply(map_genre, axis=1)
        
        # Plot
        plot_genre_distribution(df_jam, 'fma_mapped_genre', "Jamendo Dataset Distribution (FMA Mapped)", "jamendo_genre_dist.png")

    else:
        print("Jamendo metadata file not found.")

if __name__ == "__main__":
    main()
