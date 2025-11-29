import pandas as pd
import ast

def main():
    """
    Processes FMA metadata to create a mapping from track_id to its top-level genre ID and name.
    """
    base_path = '/home/jay/MusicAI/fma/data/fma_metadata/'
    tracks_path = base_path + 'tracks.csv'
    genres_path = base_path + 'genres.csv'
    output_path = base_path + 'track_toplevel_genres.csv'

    try:
        print("Loading tracks.csv and genres.csv...")
        tracks = pd.read_csv(tracks_path, index_col=0, header=[0, 1])
        genres = pd.read_csv(genres_path, index_col=0)

        print("Extracting primary genre for each track...")
        track_genres_df = pd.DataFrame(tracks['track']['genres'])

        def get_primary_genre(genre_str):
            try:
                genre_list = ast.literal_eval(str(genre_str))
                if isinstance(genre_list, list) and len(genre_list) > 0:
                    return genre_list[0]
                return None
            except (ValueError, SyntaxError):
                return None

        track_genres_df['primary_genre_id'] = track_genres_df['genres'].apply(get_primary_genre)
        track_genres_df.dropna(subset=['primary_genre_id'], inplace=True)
        track_genres_df['primary_genre_id'] = track_genres_df['primary_genre_id'].astype(int)

        print("Merging to get top-level genre ID...")
        # Merge with genres table to get the 'top_level' ID for the track's primary genre
        merged_df = track_genres_df.merge(
            genres[['top_level']],
            left_on='primary_genre_id',
            right_index=True,
            how='inner'
        )

        # The 'top_level' column is the ID of the parent genre.
        # If a genre is already top-level, its 'top_level' value is NaN.
        # We fill these NaNs with the genre's own ID (from the index of the merged_df).
        merged_df['top_level'].fillna(merged_df['primary_genre_id'], inplace=True)
        merged_df['top_level'] = merged_df['top_level'].astype(int)

        print("Mapping top-level genre ID to its name...")
        # The name of any genre (including top-level ones) is in the 'title' column.
        # We can use the 'title' column as a mapping series where the index is the genre_id.
        id_to_name_map = genres['title']
        merged_df['top_level_genre_name'] = merged_df['top_level'].map(id_to_name_map)

        # Prepare the final output DataFrame
        output_df = merged_df[['top_level', 'top_level_genre_name']].reset_index()
        output_df.rename(columns={
            'track_id': 'track_id',
            'top_level': 'top_level_genre_id',
            'top_level_genre_name': 'top_level_genre_name'
        }, inplace=True)

        print(f"Saving final data to {output_path}...")
        output_df.to_csv(output_path, index=False)

        print("\n--- Processing Complete! ---")
        print(f"Successfully created {output_path}")
        print(f"Total tracks processed: {len(output_df)}")
        print("\nSample of the final data:")
        print(output_df.head())

    except FileNotFoundError as e:
        print(f"Error: {e}. Please ensure fma metadata files are in the correct directory.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == '__main__':
    main()