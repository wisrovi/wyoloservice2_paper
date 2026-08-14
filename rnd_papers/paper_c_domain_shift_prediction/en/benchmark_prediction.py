import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

rng = np.random.default_rng(42)
fid = np.array([18.3, 43.8, 72.3, 90.74, 127.6, 142.93, 149.86])
d = np.array([4.2, 4.2, 15.4, 18.7, 32.1, 35.4, 43.4])


def fit(X, y):
    return np.linalg.lstsq(X, y, rcond=None)[0]


Xo = np.column_stack([np.ones(7), fid])
bo = fit(Xo, d)

x_pred = np.linspace(0, 160, 100)
y_pred = bo[0] + bo[1] * x_pred

preds = []
for _ in range(2000):
    idx = rng.integers(0, 7, 7)
    preds.append(np.array([1, x_pred]) @ np.concatenate([[0, 0]]) if False else None)
lo, hi = np.full_like(x_pred, np.nan), np.full_like(x_pred, np.nan)
for i, x in enumerate(x_pred):
    ps = []
    for _ in range(2000):
        idx = rng.integers(0, 7, 7)
        b = fit(Xo[idx], d[idx])
        ps.append(np.array([1, x]) @ b)
    ps = np.array(ps)
    lo[i], hi[i] = np.percentile(ps, [2.5, 97.5])

fig, ax = plt.subplots(figsize=(6.2, 3.4))
ax.fill_between(x_pred, lo, hi, color="#cfe3f5", label="95% bootstrap CI")
ax.plot(x_pred, y_pred, color="#1f4e79", lw=1.8, label="Fit: $\\Delta$mAP = $-5.62 + 0.299\\cdot$FID")
ax.scatter(fid, d, color="#c0392b", s=42, zorder=5, label="Observed domain pairs")
ax.axhline(10, color="#7f8c8d", ls="--", lw=1)
ax.text(152, 11.2, "risk gate (10 pp)", ha="right", fontsize=8, color="#555")
ax.axvline(127.6, color="#2ecc71", ls=":", lw=1.2)
ax.text(127.6, 3.0, "Day$\\rightarrow$Night\n(held out, pred. 32.6 pp)", ha="center", fontsize=8, color="#1e7a34")
ax.set_xlabel("Fréchet Inception Distance (FID)")
ax.set_ylabel("Observed $\\Delta$mAP$_{50}$ (pp)")
ax.legend(loc="upper left", fontsize=7.5, framealpha=0.95)
ax.set_ylim(0, 50)
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig("figures/prediction.pdf")
print("saved figures/prediction.pdf")
print("FID-only b:", np.round(bo, 3))
print("R2:", round(1 - np.sum((d - Xo @ bo) ** 2) / np.sum((d - d.mean()) ** 2), 3))
