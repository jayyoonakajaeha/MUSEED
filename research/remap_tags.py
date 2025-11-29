
import pandas as pd
import os

def remap_mood_tags():
    # --- 설정 ---
    input_csv_path = '/home/jay/MusicAI/fma/data/fma_metadata/track_mood_tags.csv'
    output_csv_path = '/home/jay/MusicAI/fma/data/fma_metadata/track_mood_tags_grouped.csv'

    # 1. 태그 그룹 정의
    TAG_GROUPS = {
        'High Energy': ['energetic', 'upbeat', 'powerful'],
        'Low Energy': ['calm', 'relaxing', 'peaceful', 'ambient'],
        'Positive Valence': ['happy', 'cheerful', 'bright'],
        'Negative Valence': ['sad', 'dark', 'melancholic', 'dramatic'],
        'Romantic': ['romantic', 'love', 'sentimental'],
        'Rhythmic/Dance': ['groovy', 'funky', 'danceable'],
        'Grandiose': ['epic', 'orchestral', 'cinematic'],
        'Abstract/Structural': ['experimental', 'strange', 'minimalist']
    }

    # 2. 빠른 조회를 위해 {기존 태그: 새 그룹} 형태의 딕셔너리 생성
    tag_to_group_map = {tag: group for group, tags in TAG_GROUPS.items() for tag in tags}

    # 3. 원본 CSV 파일 읽기
    print(f"Loading original tags from {input_csv_path}...")
    try:
        df = pd.read_csv(input_csv_path)
    except FileNotFoundError:
        print(f"Error: Input file not found at {input_csv_path}")
        return

    # 4. 'mood_tag'를 새로운 그룹으로 매핑하는 함수 정의
    def get_new_group(tag):
        return tag_to_group_map.get(tag, 'Other') # 그룹에 없는 태그는 'Other'로 분류

    # 5. 새로운 그룹 태그 열 추가
    print("Mapping old tags to new groups...")
    df['mood_group'] = df['mood_tag'].apply(get_new_group)

    # 6. 필요한 열만 선택하여 새 DataFrame 생성
    output_df = df[['track_id', 'mood_group']]

    # 7. 결과 저장
    print(f"Saving remapped tags to {output_csv_path}...")
    output_df.to_csv(output_csv_path, index=False)

    print("\n--- Remapping Complete! ---")
    print(f"Successfully created {output_csv_path}")
    
    # 8. 새로운 그룹 분포 확인 및 출력
    print("\nNew tag group distribution:")
    print(output_df['mood_group'].value_counts())

if __name__ == '__main__':
    remap_mood_tags()
