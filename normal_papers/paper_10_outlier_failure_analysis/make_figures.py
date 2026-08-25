#!/usr/bin/env python3
"""
make_figures.py
===============
Vector (PDF) + raster (PNG) figures for paper_10_outlier_failure_analysis,
driven exclusively by the CSVs under `evidencias/`. Every axis is labeled
with units; no raw screenshots are used.

Outputs (written to <lang>/figures/ for en and es):
  - step13_flow.{pdf,png}   : step-13 feedback loop diagram
  - results.{pdf,png}       : FP rate / mAP50 across the A/B arms
  - ablation_iou.{pdf,png}  : IoU matching threshold sweep on the baseline
  - ablation_hn.{pdf,png}   : hard-negative fraction reintegration sweep
"""

import csv
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

PAPER_DIR = os.path.dirname(os.path.abspath(__file__))
EVID = os.path.join(PAPER_DIR, "evidencias")
OUT_DIRS = [os.path.join(PAPER_DIR, "en", "figures"),
            os.path.join(PAPER_DIR, "es", "figures")]

STAGE_LABELS = {
    "baseline": "Baseline\n(pretrained)",
    "control_ft": "Control\n(no HNM)",
    "treatment_50": "HN 50%",
    "treatment_100": "HN 100%",
    "treatment_fn": "HN 100%\n+ FN rebal.",
}

COLORS = {"baseline": "#7f7f7f", "control_ft": "#1f77b4",
          "treatment_50": "#ff7f0e", "treatment_100": "#d62728",
          "treatment_fn": "#2ca02c"}


def load_results():
    rows = {}
    with open(os.path.join(EVID, "outlier_results.csv")) as f:
        for r in csv.DictReader(f):
            rows[r["stage"]] = r
    return rows


def load_ablation_iou():
    with open(os.path.join(EVID, "ablation_iou_threshold.csv")) as f:
        return list(csv.DictReader(f))


def load_ablation_hn():
    with open(os.path.join(EVID, "ablation_hn_fraction.csv")) as f:
        return list(csv.DictReader(f))


def ensure_dirs():
    for d in OUT_DIRS:
        os.makedirs(d, exist_ok=True)


def savefig(fig, name):
    for d in OUT_DIRS:
        fig.savefig(os.path.join(d, f"{name}.pdf"), bbox_inches="tight")
        fig.savefig(os.path.join(d, f"{name}.png"), bbox_inches="tight",
                    dpi=220)
    plt.close(fig)
    print(f"  wrote {name}.{{pdf,png}}")


def fig_step13_flow():
    fig, ax = plt.subplots(figsize=(5.6, 4.2))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis("off")

    def box(x, y, w, h, text, fc="#eef2f7", ec="#2f5b8a", fs=8.2):
        from matplotlib.patches import FancyBboxPatch
        p = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.12",
                           linewidth=1.1, edgecolor=ec, facecolor=fc)
        ax.add_patch(p)
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
                fontsize=fs, color="#1a1a1a", linespacing=1.35)

    def arrow(x1, y1, x2, y2):
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="-|>", color="#2f5b8a",
                                    lw=1.4))

    box(0.4, 8.2, 4.2, 1.4,
        "Worker inference\n(standard validation pass,\nstep 12)", fc="#fdf2e3")
    box(5.2, 8.2, 4.4, 1.4,
        "Step 13\nOutlierFailureAnalyzer\n(post-training module)",
        fc="#e3f0fd")
    arrow(4.65, 8.9, 5.15, 8.9)

    box(0.4, 5.6, 2.95, 1.9,
        "High-confidence false\npositives\n(conf \u2265 0.5, IoU < 0.5)")
    box(3.55, 5.6, 2.95, 1.9,
        "False negatives\n(ground-truth objects\nentirely missed)")
    box(6.7, 5.6, 2.95, 1.9,
        "Misclassifications\nwith high\noverlap")
    arrow(6.2, 8.2, 1.5, 7.55)
    arrow(6.8, 8.2, 4.3, 7.55)
    arrow(7.4, 8.2, 8.0, 7.55)

    box(1.2, 2.9, 4.0, 1.7,
        "Mine hard negatives\n(crops with context, resized to 640\n"
        "kept as background-only samples)", fc="#fdf2e3")
    box(6.4, 2.9, 3.2, 1.7,
        "Feedback loop\n(reintegrate crops into\nthe next epoch)",
        fc="#e8f5e9")
    arrow(2.8, 5.6, 3.0, 4.6)
    arrow(6.5, 5.6, 7.4, 4.6)

    box(1.2, 0.4, 8.4, 1.6,
        "Evaluation on a held-out validation split (25%, never used for "
        "fine-tuning)\n\u2014 no leakage between mining, training and evaluation \u2014",
        fc="#f3e5f5", ec="#7b1fa2")
    arrow(3.1, 2.9, 3.5, 2.0)
    arrow(7.0, 2.9, 6.5, 2.0)

    fig.tight_layout()
    return fig


def fig_results():
    data = load_results()
    stages = ["baseline", "control_ft", "treatment_50", "treatment_100",
              "treatment_fn"]
    fp = [float(data[s]["fp_rate"]) * 100 for s in stages]
    fp_hc = [float(data[s]["fp_rate_hc"]) * 100 for s in stages]
    map50 = [float(data[s]["map50"]) for s in stages]
    labels = [STAGE_LABELS[s] for s in stages]
    x = np.arange(len(stages))

    fig, ax1 = plt.subplots(figsize=(5.4, 3.6))
    b1 = ax1.bar(x - 0.21, fp, 0.42, color="#d62728", label="FP rate (conf \u2265 0.5)")
    b2 = ax1.bar(x + 0.21, fp_hc, 0.42, color="#ff9896",
                 label="High-conf. FP rate (conf \u2265 0.75)")
    ax1.set_xticks(x)
    ax1.set_xticklabels(labels, fontsize=8)
    ax1.set_ylabel("False-positive rate (%)")
    ax1.set_ylim(0, max(fp + fp_hc) * 1.25)
    ax1.tick_params(axis="y", labelsize=8)
    ax1.axhline(0, color="#333", lw=0.8)
    for b in list(b1) + list(b2):
        ax1.annotate(f"{b.get_height():.1f}", (b.get_x() + b.get_width() / 2,
                                               b.get_height()),
                     ha="center", va="bottom", fontsize=7, color="#333")

    ax2 = ax1.twinx()
    ax2.plot(x, map50, "o-", color="#1f77b4", lw=1.6, ms=5,
             label="mAP50")
    for xi, v in zip(x, map50):
        ax2.annotate(f"{v:.3f}", (xi, v), textcoords="offset points",
                     xytext=(0, 7), ha="center", fontsize=7, color="#1f77b4")
    ax2.set_ylabel("mAP50", color="#1f77b4")
    ax2.set_ylim(0, 1.0)
    ax2.tick_params(axis="y", labelcolor="#1f77b4", labelsize=8)

    h1, l1 = ax1.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax1.legend(h1 + h2, l1 + l2, loc="upper left", fontsize=7, frameon=False)
    ax1.set_title("A/B evaluation on the held-out validation split "
                  "(32 images, seed=42)", fontsize=9)
    fig.tight_layout()
    return fig


def fig_ablation_iou():
    rows = load_ablation_iou()
    t = [float(r["iou_threshold"]) for r in rows]
    fp = [float(r["fp_rate"]) * 100 for r in rows]
    hn = [int(r["hard_negatives"]) for r in rows]

    fig, ax1 = plt.subplots(figsize=(5.2, 3.4))
    ax1.plot(t, fp, "s-", color="#d62728", lw=1.6, label="FP rate (%)")
    ax1.set_xlabel("IoU matching threshold")
    ax1.set_ylabel("Baseline FP rate (%)", color="#d62728")
    ax1.tick_params(axis="y", labelcolor="#d62728", labelsize=8)
    ax1.tick_params(axis="x", labelsize=8)
    for xi, v in zip(t, fp):
        ax1.annotate(f"{v:.1f}", (xi, v), textcoords="offset points",
                     xytext=(0, 6), ha="center", fontsize=7, color="#d62728")
    ax1.set_ylim(0, max(fp) * 1.4)

    ax2 = ax1.twinx()
    ax2.bar(t, hn, width=0.055, color="#1f77b4", alpha=0.45,
            label="Mined hard negatives")
    ax2.set_ylabel("Mined hard negatives", color="#1f77b4")
    ax2.tick_params(axis="y", labelcolor="#1f77b4", labelsize=8)
    ax2.set_ylim(0, max(hn) * 1.6)

    h1, l1 = ax1.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax1.legend(h1 + h2, l1 + l2, loc="upper left", fontsize=7, frameon=False)
    ax1.set_title("IoU threshold sensitivity (baseline, held-out val)",
                  fontsize=9)
    fig.tight_layout()
    return fig


def fig_ablation_hn():
    rows = load_ablation_hn()
    frac = [float(r["hn_fraction"]) * 100 for r in rows]
    fp = [float(r["fp_rate"]) * 100 for r in rows]
    map50 = [float(r["map50"]) for r in rows]

    fig, ax1 = plt.subplots(figsize=(5.2, 3.4))
    ax1.plot(frac, fp, "o-", color="#d62728", lw=1.6, label="FP rate (%)")
    ax1.set_xlabel("Hard-negative fraction reintegrated (%)")
    ax1.set_ylabel("FP rate (%)", color="#d62728")
    ax1.set_xticks(frac)
    ax1.tick_params(axis="both", labelsize=8)
    for xi, v in zip(frac, fp):
        ax1.annotate(f"{v:.1f}", (xi, v), textcoords="offset points",
                     xytext=(0, 6), ha="center", fontsize=7, color="#d62728")
    ax1.set_ylim(0, max(fp) * 1.35)

    ax2 = ax1.twinx()
    ax2.plot(frac, map50, "s--", color="#1f77b4", lw=1.5, label="mAP50")
    ax2.set_ylabel("mAP50", color="#1f77b4")
    ax2.tick_params(axis="y", labelcolor="#1f77b4", labelsize=8)
    ax2.set_ylim(0, 1.0)

    h1, l1 = ax1.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax1.legend(h1 + h2, l1 + l2, loc="best", fontsize=7, frameon=False)
    ax1.set_title("Hard-negative reintegration fraction (held-out val)",
                  fontsize=9)
    fig.tight_layout()
    return fig


def main():
    ensure_dirs()
    print("Generating figures from evidence...")
    savefig(fig_step13_flow(), "step13_flow")
    savefig(fig_results(), "results")
    savefig(fig_ablation_iou(), "ablation_iou")
    savefig(fig_ablation_hn(), "ablation_hn")
    print("DONE.")


if __name__ == "__main__":
    main()