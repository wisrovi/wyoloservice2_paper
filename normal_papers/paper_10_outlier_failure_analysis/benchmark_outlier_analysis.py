#!/usr/bin/env python3
"""
benchmark_outlier_analysis.py
=============================
Empirical benchmark for the OutlierFailureAnalyzer (step 13 of the
train_service2 worker pipeline). This is a DIRECTED MICRO-BENCHMARK on the
COCO128 subset (no proprietary industrial data or GPU was available to the
authors). Every number reported in the manuscript is generated AS OUTPUT of
this script and persisted under `evidencias/`.

Protocol (fully reproducible, seed = 42):
  1. Real inference with the off-the-shelf pretrained YOLOv8n over COCO128.
  2. Step-13 outlier analysis: high-confidence false positives (conf >= 0.5
     that fail to match any ground-truth box at IoU >= 0.5), false negatives,
     and IoU disparity.
  3. Hard-negative mining: the high-confidence FP regions are cropped and
     stored as background-only samples.
  4. Controlled A/B fine-tuning:
       control    = YOLOv8n fine-tuned on COCO128 (128 images)
       treatment  = YOLOv8n fine-tuned on COCO128 + mined hard negatives
     Both arms share epochs, learning rate, seed and optimizer.
  5. Both arms are evaluated on the same COCO128 validation set; the primary
     operational metric is the high-confidence false-positive rate
     (FP / (FP + TP) at conf >= 0.75), which matches the step-13 focus on
     high-confidence false positives.

Usage:
    python benchmark_outlier_analysis.py [--epochs N] [--imgsz 640]
"""

import argparse
import csv
import json
import os
import shutil
import sys
import warnings

warnings.filterwarnings("ignore")

import numpy as np
import cv2

try:
    import ultralytics
except ImportError:
    import subprocess
    print("Installing ultralytics...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "ultralytics"])
    import ultralytics

from ultralytics import YOLO

PAPER_DIR = os.path.dirname(os.path.abspath(__file__))
EVID_DIR = os.path.join(PAPER_DIR, "evidencias")
ROOT = os.path.abspath(os.path.join(PAPER_DIR, "..", ".."))
MODEL_PATH = os.path.join(ROOT, "yolov8n.pt")
DATASET_YAML = os.path.join(ROOT, "datasets", "coco128", "coco128.yaml")
IMG_DIR = os.path.join(ROOT, "datasets", "coco128", "images", "train2017")
LBL_DIR = os.path.join(ROOT, "datasets", "coco128", "labels", "train2017")

SEED = 42
CONF_DEPLOY = 0.5      # deployment operating point for mining hard negatives
CONF_HC = 0.75         # "high-confidence" operating point for the FP-rate metric
IOU_THRESHOLD = 0.5    # step-13 strict IoU threshold


def ensure_assets():
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(
            f"Model weights not found at {MODEL_PATH}. Download yolov8n.pt "
            "into the repository root first."
        )
    if not os.path.exists(DATASET_YAML):
        raise FileNotFoundError(
            f"COCO128 dataset not found at {DATASET_YAML}. Run the dataset "
            "setup step described in the paper first."
        )


def load_gt():
    gt = {}
    for fn in sorted(os.listdir(LBL_DIR)):
        if not fn.endswith(".txt"):
            continue
        img_id = int(fn.split(".")[0])
        boxes = []
        with open(os.path.join(LBL_DIR, fn)) as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) != 5:
                    continue
                cx, cy, w, h = (float(p) for p in parts[1:])
                boxes.append((cx, cy, w, h))
        gt[img_id] = boxes
    return gt


def xywh_to_corners(xywh):
    cx, cy, w, h = xywh
    return (cx - w / 2.0, cy - h / 2.0, cx + w / 2.0, cy + h / 2.0)


def bbox_iou(a, b):
    ax1, ay1, ax2, ay2 = xywh_to_corners(a)
    bx1, by1, bx2, by2 = xywh_to_corners(b)
    ix1, iy1 = max(ax1, bx1), max(ay1, by1)
    ix2, iy2 = min(ax2, bx2), min(ay2, by2)
    iw, ih = max(0.0, ix2 - ix1), max(0.0, iy2 - iy1)
    inter = iw * ih
    if inter <= 0:
        return 0.0
    union = (ax2 - ax1) * (ay2 - ay1) + (bx2 - bx1) * (by2 - by1) - inter
    return inter / union if union > 0 else 0.0


def analyze_predictions(preds_json, gt, conf_deploy=CONF_DEPLOY,
                        conf_hc=CONF_HC, iou_thresh=IOU_THRESHOLD):
    """
    Match predictions to ground truth at IoU >= 0.5. Returns per-sample outlier
    rows plus aggregated totals for both the deployment (>= CONF_DEPLOY) and
    the high-confidence (>= CONF_HC) operating points.
    """
    preds_by_img = {}
    for p in preds_json:
        preds_by_img.setdefault(p["image_id"], []).append(p)

    rows = []
    totals = {
        "total_images": 0,
        "total_gt_objects": 0,
        "tp": 0, "fp": 0, "fn": 0,
        "tp_hc": 0, "fp_hc": 0, "fn_hc": 0,
        "hard_negatives": 0,
    }

    for img_id in sorted(gt.keys()):
        gt_boxes = gt[img_id]
        preds = preds_by_img.get(img_id, [])
        totals["total_images"] += 1
        totals["total_gt_objects"] += len(gt_boxes)

        img_path = os.path.join(IMG_DIR, f"{img_id:012d}.jpg")
        img_shape = cv2.imread(img_path).shape if os.path.exists(img_path) else (640, 640, 3)
        ih, iw = img_shape[0], img_shape[1]

        matched_gt = set()
        matched_gt_hc = set()
        for p in preds:
            score = p["score"]
            if score < conf_deploy:
                continue
            bx, by, bw, bh = p["bbox"]
            pb = (bx / iw + bw / iw / 2.0, by / ih + bh / ih / 2.0, bw / iw, bh / ih)
            best_iou, best_gi = 0.0, -1
            for gi, gb in enumerate(gt_boxes):
                if gi in matched_gt:
                    continue
                iou = bbox_iou(pb, gb)
                if iou > best_iou:
                    best_iou, best_gi = iou, gi

            if best_iou >= iou_thresh:
                totals["tp"] += 1
                matched_gt.add(best_gi)
                if score >= conf_hc:
                    totals["tp_hc"] += 1
                    matched_gt_hc.add(best_gi)
            else:
                totals["fp"] += 1
                mine = score >= conf_deploy
                if mine:
                    totals["hard_negatives"] += 1
                if score >= conf_hc:
                    totals["fp_hc"] += 1
                rows.append({
                    "image_id": img_id,
                    "confidence": round(score, 3),
                    "iou_to_best_gt": round(best_iou, 3),
                    "iou_disparity": round(1.0 - best_iou, 3),
                    "category_id": p["category_id"],
                    "bbox_xywh": p["bbox"],
                    "action_taken": "mine_hard_negative" if mine else "review",
                })
        for gi in range(len(gt_boxes)):
            if gi not in matched_gt:
                totals["fn"] += 1
                if gi not in matched_gt_hc:
                    totals["fn_hc"] += 1
                rows.append({
                    "image_id": img_id,
                    "confidence": 0.0,
                    "iou_to_best_gt": 0.0,
                    "iou_disparity": 1.0,
                    "category_id": -1,
                    "bbox_xywh": None,
                    "action_taken": "reannotate_fn",
                })
    return rows, totals


def fp_rate(totals, hc=False):
    if hc:
        denom = totals["fp_hc"] + totals["tp_hc"]
        return totals["fp_hc"] / denom if denom > 0 else 0.0
    denom = totals["fp"] + totals["tp"]
    return totals["fp"] / denom if denom > 0 else 0.0


def fn_rate(totals):
    denom = totals["fn"] + totals["tp"]
    return totals["fn"] / denom if denom > 0 else 0.0


def build_dataset(include_hard_negatives, rows=None):
    """COCO128 (+ optionally the mined hard negatives) as a YOLO dataset."""
    tag = "hn" if include_hard_negatives else "ctrl"
    aug_dir = os.path.join(PAPER_DIR, "runs", f"ds_{tag}")
    if os.path.exists(aug_dir):
        shutil.rmtree(aug_dir)
    imgs_dir = os.path.join(aug_dir, "images", "train")
    lbls_dir = os.path.join(aug_dir, "labels", "train")
    os.makedirs(imgs_dir, exist_ok=True)
    os.makedirs(lbls_dir, exist_ok=True)

    for fn in sorted(os.listdir(IMG_DIR)):
        if not fn.endswith(".jpg"):
            continue
        shutil.copy2(os.path.join(IMG_DIR, fn), os.path.join(imgs_dir, "base_" + fn))
        lbl = os.path.join(LBL_DIR, fn.replace(".jpg", ".txt"))
        dst = os.path.join(lbls_dir, "base_" + fn.replace(".jpg", ".txt"))
        if os.path.exists(lbl):
            shutil.copy2(lbl, dst)
        else:
            open(dst, "w").close()

    n_crops = 0
    if include_hard_negatives:
        for r in rows:
            if r["action_taken"] != "mine_hard_negative" or r["bbox_xywh"] is None:
                continue
            img_path = os.path.join(IMG_DIR, f"{r['image_id']:012d}.jpg")
            img = cv2.imread(img_path)
            if img is None:
                continue
            h, w = img.shape[:2]
            bx, by, bw, bh = r["bbox_xywh"]
            x1 = int(max(0, bx - 0.25 * bw)); y1 = int(max(0, by - 0.25 * bh))
            x2 = int(min(w, bx + 1.25 * bw)); y2 = int(min(h, by + 1.25 * bh))
            if x2 - x1 < 16 or y2 - y1 < 16:
                continue
            crop = cv2.resize(img[y1:y2, x1:x2], (320, 320))
            cv2.imwrite(os.path.join(imgs_dir, f"hn_{n_crops:04d}.jpg"), crop)
            open(os.path.join(lbls_dir, f"hn_{n_crops:04d}.txt"), "w").close()
            n_crops += 1
        print(f"  reintegrated {n_crops} hard-negative crops")

    import yaml as pyyaml
    with open(DATASET_YAML) as bf:
        base = pyyaml.safe_load(bf)
    yaml_path = os.path.join(aug_dir, "ds.yaml")
    with open(yaml_path, "w") as f:
        f.write("path: %s\n" % aug_dir)
        f.write("train: images/train\n")
        f.write("val: %s\n" % os.path.join(ROOT, "datasets", "coco128", "images", "train2017"))
        f.write("names:\n")
        for k, v in base["names"].items():
            f.write("  %s: %s\n" % (k, v))
    return yaml_path, n_crops


def fine_tune(ds_yaml, tag, epochs, imgsz, seed=SEED, freeze=0, lr0=5e-4):
    project = os.path.join(PAPER_DIR, "runs", "ab")
    model = YOLO(MODEL_PATH)
    model.train(
        data=ds_yaml, epochs=epochs, imgsz=imgsz, batch=8, device="cpu",
        project=project, name=tag, verbose=False, seed=seed, workers=0,
        lr0=lr0, optimizer="Adam", pretrained=True, freeze=freeze, patience=30,
    )
    best = os.path.join(project, tag, "weights", "best.pt")
    if not os.path.exists(best):
        raise RuntimeError(f"Fine-tuning {tag} did not produce best.pt")
    return best


def evaluate(model_path, gt):
    m = YOLO(model_path)
    res = m.val(data=DATASET_YAML, imgsz=640, batch=8, save_json=True,
                plots=False, verbose=False, seed=SEED)
    map50 = float(res.box.map50)
    with open(os.path.join(res.save_dir, "predictions.json")) as f:
        preds = json.load(f)
    rows, tot = analyze_predictions(preds, gt)
    return {
        "map50": round(map50, 4),
        "tp": tot["tp"], "fp": tot["fp"], "fn": tot["fn"],
        "fp_hc": tot["fp_hc"], "tp_hc": tot["tp_hc"],
        "fp_rate": round(fp_rate(tot), 4),
        "fp_rate_hc": round(fp_rate(tot, hc=True), 4),
        "fn_rate": round(fn_rate(tot), 4),
        "total_images": tot["total_images"],
        "total_gt_objects": tot["total_gt_objects"],
    }, rows, tot


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--epochs", type=int, default=10)
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--freeze", type=int, default=0)
    parser.add_argument("--lr", type=float, default=5e-4)
    args = parser.parse_args()

    ensure_assets()
    os.makedirs(EVID_DIR, exist_ok=True)

    print("=== Step 1: Real YOLOv8n inference over COCO128 ===")
    model = YOLO(MODEL_PATH)
    base_res = model.val(data=DATASET_YAML, imgsz=args.imgsz, batch=8,
                         save_json=True, plots=False, verbose=False, seed=SEED)
    base_map50 = float(base_res.box.map50)
    with open(os.path.join(base_res.save_dir, "predictions.json")) as f:
        base_preds = json.load(f)

    print("=== Step 2: Outlier analysis (step-13 criteria) ===")
    gt = load_gt()
    rows, base_tot = analyze_predictions(base_preds, gt)
    base_stats = {
        "map50": round(base_map50, 4),
        "tp": base_tot["tp"], "fp": base_tot["fp"], "fn": base_tot["fn"],
        "fp_hc": base_tot["fp_hc"], "tp_hc": base_tot["tp_hc"],
        "fp_rate": round(fp_rate(base_tot), 4),
        "fp_rate_hc": round(fp_rate(base_tot, hc=True), 4),
        "fn_rate": round(fn_rate(base_tot), 4),
        "hard_negatives": base_tot["hard_negatives"],
    }
    print(f"  baseline: {base_stats}")

    csv_rows = [{k: v for k, v in r.items() if k != "bbox_xywh"} for r in rows]
    with open(os.path.join(EVID_DIR, "outlier_samples.csv"), "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "image_id", "confidence", "iou_to_best_gt", "iou_disparity",
            "category_id", "action_taken",
        ])
        writer.writeheader()
        writer.writerows(csv_rows)

    print("=== Step 3: Controlled A/B fine-tuning ===")
    ctrl_yaml, _ = build_dataset(include_hard_negatives=False)
    hn_yaml, n_hn = build_dataset(include_hard_negatives=True, rows=rows)

    ctrl_weights = fine_tune(ctrl_yaml, "control", args.epochs, args.imgsz,
                             freeze=args.freeze, lr0=args.lr)
    print("  control fine-tune done")
    hn_weights = fine_tune(hn_yaml, "treatment", args.epochs, args.imgsz,
                           freeze=args.freeze, lr0=args.lr)
    print("  treatment fine-tune done")

    print("=== Step 4: Evaluation of both variants ===")
    ctrl_stats, _, ctrl_tot = evaluate(ctrl_weights, gt)
    hn_stats, _, hn_tot = evaluate(hn_weights, gt)
    print(f"  control:   {ctrl_stats}")
    print(f"  treatment: {hn_stats}")

    with open(os.path.join(EVID_DIR, "outlier_results.csv"), "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "stage", "total_images", "total_gt_objects", "tp", "fp", "fn",
            "fp_hc", "tp_hc", "hard_negatives_mined", "fp_rate", "fp_rate_hc",
            "fn_rate", "map50",
        ])
        writer.writerow([
            "baseline", base_tot["total_images"], base_tot["total_gt_objects"],
            base_stats["tp"], base_stats["fp"], base_stats["fn"],
            base_stats["fp_hc"], base_stats["tp_hc"], base_stats["hard_negatives"],
            base_stats["fp_rate"], base_stats["fp_rate_hc"], base_stats["fn_rate"],
            base_stats["map50"],
        ])
        writer.writerow([
            "control_ft", ctrl_tot["total_images"], ctrl_tot["total_gt_objects"],
            ctrl_stats["tp"], ctrl_stats["fp"], ctrl_stats["fn"],
            ctrl_stats["fp_hc"], ctrl_stats["tp_hc"], base_stats["hard_negatives"],
            ctrl_stats["fp_rate"], ctrl_stats["fp_rate_hc"], ctrl_stats["fn_rate"],
            ctrl_stats["map50"],
        ])
        writer.writerow([
            "treatment_hn", hn_tot["total_images"], hn_tot["total_gt_objects"],
            hn_stats["tp"], hn_stats["fp"], hn_stats["fn"],
            hn_stats["fp_hc"], hn_stats["tp_hc"], base_stats["hard_negatives"],
            hn_stats["fp_rate"], hn_stats["fp_rate_hc"], hn_stats["fn_rate"],
            hn_stats["map50"],
        ])

    print("=== Step 5: Ablation over IoU threshold (baseline) ===")
    abl_rows = []
    for iou_t in [0.4, 0.5, 0.6, 0.7]:
        _, ab_tot = analyze_predictions(base_preds, gt, iou_thresh=iou_t)
        abl_rows.append({
            "iou_threshold": iou_t,
            "tp": ab_tot["tp"], "fp": ab_tot["fp"], "fn": ab_tot["fn"],
            "fp_rate": round(fp_rate(ab_tot), 4),
            "fp_rate_hc": round(fp_rate(ab_tot, hc=True), 4),
            "hard_negatives": ab_tot["hard_negatives"],
        })
    with open(os.path.join(EVID_DIR, "ablation_iou_threshold.csv"), "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "iou_threshold", "tp", "fp", "fn", "fp_rate", "fp_rate_hc",
            "hard_negatives",
        ])
        writer.writeheader()
        writer.writerows(abl_rows)

    print("DONE. Evidence written to %s" % EVID_DIR)


if __name__ == "__main__":
    main()