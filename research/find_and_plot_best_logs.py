import os
import glob
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from tensorboard.backend.event_processing.event_accumulator import EventAccumulator
from datetime import datetime

# 설정
RUNS_DIR = "/home/jay/MusicAI/MUSEED/runs"
OUTPUT_DIR = "/home/jay/MusicAI/MUSEED/research/plots"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 로그 그룹 정의
LOG_GROUPS = {
    "Contrastive V1": "fma_contrastive_v1",
    "Contrastive V2": "fma_contrastive_v2",
    "Triplet": "fma_triplet_finetuning" # v1, v2, v3 등 포함
}

def get_best_log(group_keyword):
    """
    주어진 키워드가 포함된 경로의 로그 파일 중
    1. Step 수가 가장 많은 것
    2. 최신 파일인 것
    순으로 정렬하여 1위를 반환합니다.
    """
    # 키워드로 후보 디렉토리 찾기
    candidate_files = []
    # 재귀적으로 모든 tfevents 파일 검색
    search_pattern = os.path.join(RUNS_DIR, "**", "events.out.tfevents*")
    all_files = glob.glob(search_pattern, recursive=True)
    
    for f in all_files:
        if group_keyword in f:
            candidate_files.append(f)
            
    print(f"Checking {len(candidate_files)} logs for '{group_keyword}'...")
    
    best_log = None
    max_steps = -1
    best_mtime = -1
    
    # 가능한 태그 후보들 (Step 데이터가 있는 것들)
    step_tags = ['Loss/step', 'Loss/train', 'train/loss', 'train_loss', 'loss']

    for log_path in candidate_files:
        try:
            # 파일 수정 시간
            mtime = os.path.getmtime(log_path)
            
            # 텐서보드 파일 로드 (size_guidance를 0으로 설정하여 모든 이벤트를 로드하지 않고 빠르게 스캔 시도...하지만 step 수를 세려면 다 읽어야 함)
            # 여기서는 정확한 step 수를 위해 다 읽습니다.
            ea = EventAccumulator(log_path)
            ea.Reload()
            
            found_tag = None
            step_count = 0
            
            available_tags = ea.Tags()['scalars']
            
            for tag in step_tags:
                if tag in available_tags:
                    found_tag = tag
                    step_count = len(ea.Scalars(tag))
                    break
            
            if step_count > 0:
                # 1순위: Step 수 (압도적으로 긴 로그 선호)
                # 2순위: 수정 시간 (최신)
                if step_count > max_steps:
                    max_steps = step_count
                    best_mtime = mtime
                    best_log = (log_path, found_tag, step_count)
                elif step_count == max_steps:
                    if mtime > best_mtime:
                        best_mtime = mtime
                        best_log = (log_path, found_tag, step_count)
                        
        except Exception as e:
            print(f"Error reading {log_path}: {e}")
            continue

    return best_log

def plot_log(log_info, title, filename, color):
    if not log_info:
        print(f"Skipping {title}: No valid log found.")
        return

    log_path, tag, step_count = log_info
    print(f"Selected Best Log for {title}:")
    print(f"  - Path: {log_path}")
    print(f"  - Tag: {tag}")
    print(f"  - Steps: {step_count}")
    
    ea = EventAccumulator(log_path)
    ea.Reload()
    events = ea.Scalars(tag)
    
    steps = [e.step for e in events]
    values = [e.value for e in events]
    data = pd.DataFrame({"Step": steps, "Value": values})
    
    plt.figure(figsize=(12, 6))
    sns.set_theme(style="whitegrid")
    
    sns.lineplot(data=data, x="Step", y="Value", color=color, linewidth=1.5, alpha=0.8)
    
    plt.title(f"{title} (Steps: {step_count})", fontsize=16, fontweight='bold')
    plt.xlabel("Step", fontsize=12)
    plt.ylabel("Loss", fontsize=12)
    
    # 로그 파일명 등 메타데이터를 그래프 아래에 작게 표시
    plt.figtext(0.5, 0.01, f"Source: ...{log_path[-50:]}", wrap=True, horizontalalignment='center', fontsize=8)
    
    plt.tight_layout()
    
    save_path = os.path.join(OUTPUT_DIR, filename)
    plt.savefig(save_path, dpi=300)
    print(f"Saved plot to {save_path}\n")
    plt.close()

def main():
    # 1. Contrastive V1
    v1_log = get_best_log("fma_contrastive_v1")
    plot_log(v1_log, "Contrastive V1 Training Loss", "contrastive_v1_loss_step.png", "blue")
    
    # 2. Contrastive V2
    v2_log = get_best_log("fma_contrastive_v2")
    plot_log(v2_log, "Contrastive V2 Training Loss", "contrastive_v2_loss_step.png", "green")
    
    # 3. Triplet
    # "triplet" 키워드가 들어간 경로 중 겹치지 않게 주의 (여기서는 그냥 다 뒤짐)
    # V1, V2와 겹치지 않게 fma_contrastive는 제외됨 (키워드가 다르므로)
    triplet_log = get_best_log("fma_triplet_finetuning")
    plot_log(triplet_log, "Triplet Training Loss", "triplet_loss_step.png", "red")

if __name__ == "__main__":
    main()
