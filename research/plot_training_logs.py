import os
import matplotlib.pyplot as plt
from tensorboard.backend.event_processing.event_accumulator import EventAccumulator
import pandas as pd
import seaborn as sns

# 설정
LOG_PATHS = {
    "Contrastive Loss": "/home/jay/MusicAI/MUSEED/runs/fma_contrastive_v2/20251205_013014/events.out.tfevents.1764865814.DESKTOP-5HA0UAA.6983.0",
    "Triplet Loss": "/home/jay/MusicAI/MUSEED/runs/fma_triplet_finetuning_v1/20251208_203716/events.out.tfevents.1765193836.DESKTOP-5HA0UAA.64378.0"
}
OUTPUT_DIR = "/home/jay/MusicAI/MUSEED/research/plots"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def extract_scalar_events(log_path, scalar_tag):
    """텐서보드 로그에서 스칼라 데이터를 추출합니다."""
    event_acc = EventAccumulator(log_path)
    event_acc.Reload()
    
    # 태그 확인 (디버깅용)
    # print(f"Available tags in {log_path}: {event_acc.Tags()['scalars']}")

    if scalar_tag not in event_acc.Tags()['scalars']:
        print(f"Warning: Tag '{scalar_tag}' not found in {log_path}")
        return None

    events = event_acc.Scalars(scalar_tag)
    steps = [e.step for e in events]
    values = [e.value for e in events]
    return pd.DataFrame({"Step": steps, "Value": values})

def plot_logs(data, title, filename, color):
    """데이터프레임을 받아 그래프를 그리고 저장합니다."""
    plt.figure(figsize=(10, 6))
    sns.set_theme(style="whitegrid")
    
    sns.lineplot(data=data, x="Step", y="Value", color=color, linewidth=2)
    
    plt.title(title, fontsize=16, fontweight='bold')
    plt.xlabel("Step", fontsize=12)
    plt.ylabel("Loss", fontsize=12)
    plt.tight_layout()
    
    save_path = os.path.join(OUTPUT_DIR, filename)
    plt.savefig(save_path, dpi=300)
    print(f"Saved plot to {save_path}")
    plt.close()

def main():
    # 1. Contrastive Loss 처리
    print("Processing Contrastive Loss logs...")
    contrastive_df = extract_scalar_events(LOG_PATHS["Contrastive Loss"], "Loss/epoch") # 올바른 태그 사용
    if contrastive_df is not None:
         plot_logs(contrastive_df, "Contrastive Learning Training Loss", "contrastive_loss_plot.png", "blue")
    else:
        # 태그를 찾지 못했을 경우 모든 태그 출력해보기
        event_acc = EventAccumulator(LOG_PATHS["Contrastive Loss"])
        event_acc.Reload()
        print(f"Available tags for Contrastive: {event_acc.Tags()['scalars']}")
        # 흔한 태그 이름으로 재시도 (예: 'train_loss', 'loss')
        for tag in ['train_loss', 'loss', 'Loss/train_loss']:
             contrastive_df = extract_scalar_events(LOG_PATHS["Contrastive Loss"], tag)
             if contrastive_df is not None:
                 plot_logs(contrastive_df, "Contrastive Learning Training Loss", "contrastive_loss_plot.png", "blue")
                 break

    # 2. Triplet Loss 처리
    print("Processing Triplet Loss logs...")
    triplet_df = extract_scalar_events(LOG_PATHS["Triplet Loss"], "Loss/step") # 상세한 step 데이터 사용
    if triplet_df is not None:
        plot_logs(triplet_df, "Triplet Learning Training Loss (Per Step)", "triplet_loss_plot.png", "red")
    else:
        event_acc = EventAccumulator(LOG_PATHS["Triplet Loss"])
        event_acc.Reload()
        print(f"Available tags for Triplet: {event_acc.Tags()['scalars']}")
        for tag in ['train_loss', 'loss', 'Loss/train_loss']:
             triplet_df = extract_scalar_events(LOG_PATHS["Triplet Loss"], tag)
             if triplet_df is not None:
                 plot_logs(triplet_df, "Triplet Learning Training Loss", "triplet_loss_plot.png", "red")
                 break

if __name__ == "__main__":
    main()
