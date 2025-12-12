import json
import pandas as pd
import sys

RESULTS_PATH = '/home/jay/MusicAI/MUSEED/results/jamendo_evaluation_results.json'

def main():
    try:
        with open(RESULTS_PATH, 'r') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error loading results: {e}")
        return

    # Valid axes
    axes = ['genre', 'source', 'valence', 'energy', 'mood_style']
    
    records = []
    
    for entry in data:
        model_name = entry.get('model_name', 'Unknown')
        
        # Filter for relevant models (optional, or just show all)
        # Showing all is better.
        
        row = {'Model': model_name}
        
        # Silhouette (Average?)
        # entry['silhouette_scores'] is a dict
        sil_scores = entry.get('silhouette_scores', {})
        # Maybe average silhouette across axes? Or just Genre?
        # Let's show Genre Silhouette.
        row['Sil(Genre)'] = sil_scores.get('genre', 'N/A')
        
        for axis in axes:
            # KNN Accuracy
            knn_acc = entry.get(f'knn_accuracy_{axis}', 'N/A')
            if isinstance(knn_acc, float): knn_acc = round(knn_acc, 3)
            
            # Linear Accuracy
            lin_acc = entry.get(f'linear_accuracy_{axis}', 'N/A')
            if isinstance(lin_acc, float): lin_acc = round(lin_acc, 3)
            
            row[f'{axis.capitalize()}(KNN)'] = knn_acc
            row[f'{axis.capitalize()}(Lin)'] = lin_acc
            
        records.append(row)

    df = pd.DataFrame(records)
    # Reorder columns: Model, then Axis pairs
    cols = ['Model', 'Sil(Genre)']
    for axis in axes:
        cols.append(f'{axis.capitalize()}(KNN)')
        cols.append(f'{axis.capitalize()}(Lin)')
    
    # Filter cols that exist
    cols = [c for c in cols if c in df.columns]
    df = df[cols]
    
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 1000)
    print(df.to_string(index=False))

if __name__ == '__main__':
    main()
