#!/usr/bin/env python3
"""
benchmark_outlier_analysis.py
=============================
Empirical benchmark for the OutlierFailureAnalyzer (step 13 of the
train_service2 worker pipeline). This is a DIRECTED MICRO-BENCHMARK on the
public COCO128 subset (no proprietary industrial data or GPU was available to
the authors). Every number reported in the manuscript is generated AS OUTPUT of
this script and persisted under `evidencias/`.

Leakage-free protocol (fully reproducible, seed = 42):
  1. COCO128 (126 valid images after removing image/label mismatches) is split
     ~75/25 (train / held-out val) with seed = 42. The held-out images are
     copied to images/val2017 and NEVER take part in fine-tuning, so every
     reported metric is measured on unseen data.
  2. Real inference with the off-the-shelf pretrained YOLOv8n over the 32
     held-out images produces the BASELINE row of outlier_results.csv.
  3. Step-13 outlier analysis runs over the 96 working (train) images: the
     module mines high-confidence false positives (conf >= 0.5 that fail to
     match any ground-truth box at IoU >= 0.5), false negatives and IoU
     disparity. This mirrors the production feedback loop where the module
     inspects the working set and returns corrections for the next iteration.
  4. Controlled A/B fine-tuning (all arms share epochs, lr, batch, optimizer
     and seed):
       control         = YOLOv8n fine-tuned on the 96 train images only.
       treatment_50    = control + 50% of the mined hard-negative crops.
       treatment_100   = control + 100% of the mined hard-negative crops.
       treatment_fn    = control + 100% hard-negative crops + FN rebalance
                         (working images with >= 3 missed objects are
                         duplicated once).
  5. Every arm is evaluated on the SAME 32 held-out images. Fine-tuning
       freezes the YOLOv8n backbone (freeze=10) at lr 1e-4 to prevent
       catastrophic forgetting on the 94-image working set. The primary
       operational metric is the high-confidence false-positive rate
       (FP / (FP + TP) at conf >= 0.75), which matches the step-13 focus on
       high-confidence false positives; mean Average Precision at IoU 0.5
       (mAP50) and the false-negative rate are reported alongside.
  6. Ablations: (a) IoU matching threshold sweep 0.4-0.7 on the baseline over
     the held-out set; (b) fraction of mined hard negatives reintegrated
     (0%, 50%, 100%) and the FN-rebalance variant.

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
VAL_IMG_DIR = os.path.join(ROOT, "datasets", "coco128", "images", "val2017")
VAL_LBL_DIR = os.path.join(ROOT, "datasets", "coco128", "labels", "val2017")

SEED = 42
VAL_FRACTION = 0.25
CONF_DEPLOY = 0.5      # deployment operating point for mining hard negatives
CONF_HC = 0.75         # "high-confidence" operating point for the FP-rate metric
IOU_THRESHOLD = 0.5    # step-13 strict IoU threshold
FN_DUP_THRESHOLD = 3   # images with >= this many FNs are duplicated in treatment_fn

# Ultralytics resolves a relative `path:` in a dataset yaml against its global
# `datasets_dir` setting, NOT against the yaml's own location. We therefore
# materialize a resolved copy with an absolute path and use it for every
# val()/train() call so the benchmark always reads the repo-local COCO128.
import yaml as pyyaml
_RESOLVED_DIR = os.path.join(PAPER_DIR, "runs", "ds_base")
_RESOLVED_YAML = os.path.join(_RESOLVED_DIR, "dataset.yaml")


def resolve_dataset_yaml():
    os.makedirs(_RESOLVED_DIR, exist_ok=True)
    with open(DATASET_YAML) as f:
        cfg = pyyaml.safe_load(f)
    cfg["path"] = os.path.join(ROOT, "datasets", "coco128")
    cfg["val"] = "images/val2017"
    with open(_RESOLVED_YAML, "w") as f:
        pyyaml.safe_dump(cfg, f, sort_keys=False)
    return _RESOLVED_YAML


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


def all_image_ids():
    """Ids that have BOTH a label file and a readable image (COCO128 has a
    few label/image mismatches; we only use the valid ones)."""
    return sorted(
        int(fn.split(".")[0]) for fn in os.listdir(LBL_DIR)
        if fn.endswith(".txt")
        and os.path.exists(os.path.join(IMG_DIR, f"{int(fn.split('.')[0]):012d}.jpg"))
    )


def setup_val_split():
    """Create the honest 96/32 split. Copies the 32 held-out images to
    images/val2017 and returns (train_ids, val_ids). Idempotent."""
    ids = all_image_ids()
    rng = np.random.RandomState(SEED)
    n_val = int(round(len(ids) * VAL_FRACTION))
    val_ids = set(int(x) for x in rng.choice(ids, size=n_val, replace=False))
    train_ids = [i for i in ids if i not in val_ids]

    os.makedirs(VAL_IMG_DIR, exist_ok=True)
    os.makedirs(VAL_LBL_DIR, exist_ok=True)
    for f in os.listdir(VAL_IMG_DIR):
        if f.endswith(".jpg"):
            os.remove(os.path.join(VAL_IMG_DIR, f))
    for f in os.listdir(VAL_LBL_DIR):
        if f.endswith(".txt"):
            os.remove(os.path.join(VAL_LBL_DIR, f))
    for i in val_ids:
        src = os.path.join(IMG_DIR, f"{i:012d}.jpg")
        dst = os.path.join(VAL_IMG_DIR, f"{i:012d}.jpg")
        if os.path.exists(src) and not os.path.exists(dst):
            shutil.copy2(src, dst)
        src_l = os.path.join(LBL_DIR, f"{i:012d}.txt")
        dst_l = os.path.join(VAL_LBL_DIR, f"{i:012d}.txt")
        if os.path.exists(src_l):
            if not os.path.exists(dst_l):
                shutil.copy2(src_l, dst_l)
        else:
            open(dst_l, "w").close()
    print(f"  split: {len(train_ids)} train / {len(val_ids)} val "
          f"(seed={SEED})")
    return train_ids, val_ids


def load_gt(ids=None):
    gt = {}
    for fn in sorted(os.listdir(LBL_DIR)):
        if not fn.endswith(".txt"):
            continue
        img_id = int(fn.split(".")[0])
        if ids is not None and img_id not in ids:
            continue
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
    fn_per_image = {}

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
        fn_count = 0
        for gi in range(len(gt_boxes)):
            if gi not in matched_gt:
                totals["fn"] += 1
                fn_count += 1
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
        fn_per_image[img_id] = fn_count
    return rows, totals, fn_per_image


def fp_rate(totals, hc=False):
    if hc:
        denom = totals["fp_hc"] + totals["tp_hc"]
        return totals["fp_hc"] / denom if denom > 0 else 0.0
    denom = totals["fp"] + totals["tp"]
    return totals["fp"] / denom if denom > 0 else 0.0


def fn_rate(totals):
    denom = totals["fn"] + totals["tp"]
    return totals["fn"] / denom if denom > 0 else 0.0


def build_dataset(include_hard_negatives, rows=None, train_ids=None,
                  fraction=1.0, rebalance_fn=False, fn_per_image=None):
    """COCO128 working set (+ optionally the mined hard negatives and the FN
    rebalance) as a YOLO dataset. The val split points to the 32 held-out
    images, which are NEVER copied into the training partition."""
    tag = "ctrl"
    if include_hard_negatives and not rebalance_fn:
        tag = f"hn_{int(round(fraction * 100))}"
    if rebalance_fn:
        tag = "hn_fn"
    aug_dir = os.path.join(PAPER_DIR, "runs", f"ds_{tag}")
    if os.path.exists(aug_dir):
        shutil.rmtree(aug_dir)
    imgs_dir = os.path.join(aug_dir, "images", "train")
    lbls_dir = os.path.join(aug_dir, "labels", "train")
    os.makedirs(imgs_dir, exist_ok=True)
    os.makedirs(lbls_dir, exist_ok=True)

    train_ids = train_ids or [i for i in all_image_ids()]
    for img_id in sorted(train_ids):
        src = os.path.join(IMG_DIR, f"{img_id:012d}.jpg")
        dst = os.path.join(imgs_dir, "base_" + os.path.basename(src))
        if os.path.exists(src):
            shutil.copy2(src, dst)
        lbl = os.path.join(LBL_DIR, f"{img_id:012d}.txt")
        dst_l = os.path.join(lbls_dir, "base_" + os.path.basename(lbl))
        if os.path.exists(lbl):
            shutil.copy2(lbl, dst_l)
        else:
            open(dst_l, "w").close()

    if rebalance_fn and fn_per_image:
        for img_id in sorted(train_ids):
            if fn_per_image.get(img_id, 0) >= FN_DUP_THRESHOLD:
                src = os.path.join(IMG_DIR, f"{img_id:012d}.jpg")
                dst = os.path.join(imgs_dir, "fndup_" + os.path.basename(src))
                if os.path.exists(src):
                    shutil.copy2(src, dst)
                lbl = os.path.join(LBL_DIR, f"{img_id:012d}.txt")
                dst_l = os.path.join(lbls_dir, "fndup_" + os.path.basename(lbl))
                if os.path.exists(lbl):
                    shutil.copy2(lbl, dst_l)
                else:
                    open(dst_l, "w").close()

    n_crops = 0
    if include_hard_negatives:
        mine_rows = [r for r in (rows or [])
                     if r["action_taken"] == "mine_hard_negative"
                     and r["bbox_xywh"] is not None]
        n_take = int(round(len(mine_rows) * fraction))
        for r in mine_rows[:n_take]:
            img_path = os.path.join(IMG_DIR, f"{r['image_id']:012d}.jpg")
            img = cv2.imread(img_path)
            if img is None:
                continue
            h, w = img.shape[:2]
            bx, by, bw, bh = r["bbox_xywh"]
            cx, cy = bx + bw / 2.0, by + bh / 2.0
            side = max(320, int(max(bw, bh) * 1.5))
            x1 = int(max(0, cx - side / 2)); y1 = int(max(0, cy - side / 2))
            x2 = int(min(w, cx + side / 2)); y2 = int(min(h, cy + side / 2))
            if x2 - x1 < 32 or y2 - y1 < 32:
                continue
            crop = cv2.resize(img[y1:y2, x1:x2], (640, 640))
            cv2.imwrite(os.path.join(imgs_dir, f"hn_{n_crops:04d}.jpg"), crop)
            open(os.path.join(lbls_dir, f"hn_{n_crops:04d}.txt"), "w").close()
            n_crops += 1
        print(f"  reintegrated {n_crops}/{len(mine_rows)} hard-negative crops "
              f"(fraction={fraction})")

    import yaml as pyyaml
    with open(DATASET_YAML) as bf:
        base = pyyaml.safe_load(bf)
    yaml_path = os.path.join(aug_dir, "ds.yaml")
    with open(yaml_path, "w") as f:
        f.write("path: %s\n" % aug_dir)
        f.write("train: images/train\n")
        f.write("val: %s\n" % VAL_IMG_DIR)
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
        lr0=lr0, optimizer="Adam", pretrained=True, freeze=freeze,
        patience=30, plots=False,
    )
    best = os.path.join(project, tag, "weights", "best.pt")
    if not os.path.exists(best):
        raise RuntimeError(f"Fine-tuning {tag} did not produce best.pt")
    return best


def evaluate(model_path, gt, data_yaml=None):
    m = YOLO(model_path)
    res = m.val(data=data_yaml or _RESOLVED_YAML, imgsz=640, batch=8,
                save_json=True, plots=False, verbose=False, seed=SEED)
    map50 = float(res.box.map50)
    with open(os.path.join(res.save_dir, "predictions.json")) as f:
        preds = json.load(f)
    rows, tot, _ = analyze_predictions(preds, gt)
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
    parser.add_argument("--freeze", type=int, default=10,
                        help="freeze the YOLOv8n backbone (layers 0-9) to "
                             "avoid catastrophic forgetting on tiny datasets")
    parser.add_argument("--lr", type=float, default=1e-4)
    args = parser.parse_args()

    ensure_assets()
    os.makedirs(EVID_DIR, exist_ok=True)
    resolved_yaml = resolve_dataset_yaml()

    print("=== Step 0: Honest ~75/25 train/val split ===")
    train_ids, val_ids = setup_val_split()
    train_gt = load_gt(ids=set(train_ids))
    val_gt = load_gt(ids=set(val_ids))

    print("=== Step 1: Baseline (pretrained YOLOv8n) over held-out val ===")
    model = YOLO(MODEL_PATH)
    base_res = model.val(data=resolved_yaml, imgsz=args.imgsz, batch=8,
                         save_json=True, plots=False, verbose=False, seed=SEED)
    base_map50 = float(base_res.box.map50)
    with open(os.path.join(base_res.save_dir, "predictions.json")) as f:
        base_preds = json.load(f)
    _, base_tot, _ = analyze_predictions(base_preds, val_gt)
    base_stats = {
        "map50": round(base_map50, 4),
        "tp": base_tot["tp"], "fp": base_tot["fp"], "fn": base_tot["fn"],
        "fp_hc": base_tot["fp_hc"], "tp_hc": base_tot["tp_hc"],
        "fp_rate": round(fp_rate(base_tot), 4),
        "fp_rate_hc": round(fp_rate(base_tot, hc=True), 4),
        "fn_rate": round(fn_rate(base_tot), 4),
        "total_images": base_tot["total_images"],
        "total_gt_objects": base_tot["total_gt_objects"],
        "hard_negatives": base_tot["hard_negatives"],
    }
    print(f"  baseline (held-out): {base_stats}")

    print("=== Step 2: Step-13 outlier analysis over the working set ===")
    # Run inference over the working (train) partition with a dedicated mining
    # yaml; predictions for the 96 working images are used for mining only and
    # are never reported as evaluation metrics.
    mining_dir = os.path.join(PAPER_DIR, "runs", "ds_mining")
    os.makedirs(mining_dir, exist_ok=True)
    with open(DATASET_YAML) as bf:
        base_yaml = __import__("yaml").safe_load(bf)
    mining_yaml = os.path.join(mining_dir, "ds.yaml")
    with open(mining_yaml, "w") as f:
        f.write("path: %s\n" % os.path.join(ROOT, "datasets", "coco128"))
        f.write("train: images/train2017\n")
        f.write("val: images/train2017\n")
        f.write("names:\n")
        for k, v in base_yaml["names"].items():
            f.write("  %s: %s\n" % (k, v))
    train_res = YOLO(MODEL_PATH).val(data=mining_yaml, imgsz=args.imgsz,
                                     batch=8, save_json=True, plots=False,
                                     verbose=False, seed=SEED)
    with open(os.path.join(train_res.save_dir, "predictions.json")) as f:
        train_preds_all = json.load(f)
    train_preds = [p for p in train_preds_all if p["image_id"] in set(train_ids)]
    rows, mine_tot, fn_per_image = analyze_predictions(train_preds, train_gt)
    n_hn = mine_tot["hard_negatives"]
    print(f"  mined {n_hn} hard negatives from the working set "
          f"({mine_tot['total_images']} images, {mine_tot['total_gt_objects']} "
          f"objects, {mine_tot['fn']} FNs)")

    csv_rows = [{k: v for k, v in r.items() if k != "bbox_xywh"} for r in rows]
    with open(os.path.join(EVID_DIR, "outlier_samples.csv"), "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "image_id", "confidence", "iou_to_best_gt", "iou_disparity",
            "category_id", "action_taken",
        ])
        writer.writeheader()
        writer.writerows(csv_rows)

    print("=== Step 3: Controlled A/B fine-tuning (4 arms, shared hparams) ===")
    ctrl_yaml, _ = build_dataset(include_hard_negatives=False,
                                 train_ids=train_ids)
    hn50_yaml, _ = build_dataset(include_hard_negatives=True, rows=rows,
                                 train_ids=train_ids, fraction=0.5)
    hn100_yaml, _ = build_dataset(include_hard_negatives=True, rows=rows,
                                  train_ids=train_ids, fraction=1.0)
    hnfn_yaml, _ = build_dataset(include_hard_negatives=True, rows=rows,
                                 train_ids=train_ids, fraction=1.0,
                                 rebalance_fn=True,
                                 fn_per_image=fn_per_image)

    arms = [
        ("control", ctrl_yaml),
        ("treatment_50", hn50_yaml),
        ("treatment_100", hn100_yaml),
        ("treatment_fn", hnfn_yaml),
    ]
    weights = {}
    for name, yaml_path in arms:
        print(f"  fine-tuning {name}...")
        weights[name] = fine_tune(yaml_path, name, args.epochs, args.imgsz,
                                  freeze=args.freeze, lr0=args.lr)
        print(f"  {name} fine-tune done")

    print("=== Step 4: Evaluation of all variants on the held-out val ===")
    evals = {"baseline": base_stats}
    for name in ("control", "treatment_50", "treatment_100", "treatment_fn"):
        stats, _, _ = evaluate(weights[name], val_gt)
        evals[name] = stats
        print(f"  {name}: {stats}")

    with open(os.path.join(EVID_DIR, "outlier_results.csv"), "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "stage", "total_images", "total_gt_objects", "tp", "fp", "fn",
            "fp_hc", "tp_hc", "hard_negatives_mined", "fp_rate", "fp_rate_hc",
            "fn_rate", "map50",
        ])
        for stage in ("baseline", "control_ft", "treatment_50", "treatment_100",
                      "treatment_fn"):
            s = evals[{"baseline": "baseline", "control_ft": "control",
                       "treatment_50": "treatment_50",
                       "treatment_100": "treatment_100",
                       "treatment_fn": "treatment_fn"}[stage]]
            writer.writerow([
                stage, s["total_images"], s["total_gt_objects"],
                s["tp"], s["fp"], s["fn"], s["fp_hc"], s["tp_hc"], n_hn,
                s["fp_rate"], s["fp_rate_hc"], s["fn_rate"], s["map50"],
            ])

    print("=== Step 5: Ablation over IoU threshold (baseline, held-out val) ===")
    abl_rows = []
    for iou_t in [0.4, 0.5, 0.6, 0.7]:
        _, ab_tot, _ = analyze_predictions(base_preds, val_gt, iou_thresh=iou_t)
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

    print("=== Step 6: Ablation over hard-negative fraction ===")
    frac_rows = [
        {"hn_fraction": 0.0, "n_reintegrated": 0,
         **{k: evals["control"][k] for k in
            ("fp_rate", "fp_rate_hc", "fn_rate", "map50")}},
        {"hn_fraction": 0.5,
         "n_reintegrated": int(round(n_hn * 0.5)),
         **{k: evals["treatment_50"][k] for k in
            ("fp_rate", "fp_rate_hc", "fn_rate", "map50")}},
        {"hn_fraction": 1.0, "n_reintegrated": n_hn,
         **{k: evals["treatment_100"][k] for k in
            ("fp_rate", "fp_rate_hc", "fn_rate", "map50")}},
    ]
    with open(os.path.join(EVID_DIR, "ablation_hn_fraction.csv"), "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "hn_fraction", "n_reintegrated", "fp_rate", "fp_rate_hc",
            "fn_rate", "map50",
        ])
        writer.writeheader()
        writer.writerows(frac_rows)

    print("DONE. Evidence written to %s" % EVID_DIR)


if __name__ == "__main__":
    main()