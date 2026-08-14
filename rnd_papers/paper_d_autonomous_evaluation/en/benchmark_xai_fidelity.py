import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

del_df = pd.read_csv("/home/william.rodriguez/Documents/w_libraries/train_service2/results_xai_deletion.csv")
ins_df = pd.read_csv("/home/william.rodriguez/Documents/w_libraries/train_service2/results_xai_insertion.csv")

groups = ["Grad-CAM++", "Eigen-CAM", "Random"]
del_means = [
    del_df["grad_cam_deletion_auc"].mean(),
    del_df["eigen_cam_deletion_auc"].mean(),
    del_df["random_deletion_auc"].mean(),
]
ins_means = [
    ins_df["grad_cam_insertion_auc"].mean(),
    ins_df["eigen_cam_insertion_auc"].mean(),
    ins_df["random_insertion_auc"].mean(),
]
del_std = [
    del_df["grad_cam_deletion_auc"].std(),
    del_df["eigen_cam_deletion_auc"].std(),
    del_df["random_deletion_auc"].std(),
]
ins_std = [
    ins_df["grad_cam_insertion_auc"].std(),
    ins_df["eigen_cam_insertion_auc"].std(),
    ins_df["random_insertion_auc"].std(),
]

x = np.arange(len(groups))
width = 0.38
fig, ax = plt.subplots(figsize=(6.2, 3.4))
b1 = ax.bar(x - width / 2, ins_means, width, yerr=ins_std, capsize=3,
            color="#1f4e79", label="Insertion AUC (higher = more faithful)")
b2 = ax.bar(x + width / 2, del_means, width, yerr=del_std, capsize=3,
            color="#c0392b", label="Deletion AUC (lower = more faithful)")
ax.set_ylabel("Area Under Curve (mean $\\pm$ std, 500 images)")
ax.set_xticks(x)
ax.set_xticklabels(groups)
ax.legend(loc="upper right", fontsize=7.5)
ax.grid(axis="y", alpha=0.3)
for bars in (b1, b2):
    for r in bars:
        ax.text(r.get_x() + r.get_width() / 2, r.get_height() + 0.02,
                f"{r.get_height():.3f}", ha="center", va="bottom", fontsize=8)
ax.set_ylim(0, 1.05)
fig.tight_layout()
fig.savefig("figures/xai_fidelity.pdf")
print("saved figures/xai_fidelity.pdf")
