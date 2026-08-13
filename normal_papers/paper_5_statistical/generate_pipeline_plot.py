import matplotlib.pyplot as plt
import matplotlib.patches as patches

fig, ax = plt.subplots(figsize=(10, 4))
ax.axis('off')

# Draw boxes for the pipeline
boxes = [
    ("COCO128\nValidation Set", 0.1, 0.4),
    ("YOLO Inference\n(mAP per image)", 0.35, 0.4),
    ("Non-parametric\nBootstrap (B=1000)", 0.6, 0.4),
    ("95% CI &\np-value", 0.85, 0.4)
]

for text, x, y in boxes:
    rect = patches.FancyBboxPatch((x, y), 0.15, 0.2, boxstyle="round,pad=0.05", 
                                  ec="black", fc="lightblue", lw=2)
    ax.add_patch(rect)
    ax.text(x + 0.075, y + 0.1, text, ha='center', va='center', fontsize=10, fontweight='bold')

# Draw arrows
for i in range(len(boxes)-1):
    x_start = boxes[i][1] + 0.2
    x_end = boxes[i+1][1] - 0.02
    ax.annotate('', xy=(x_end, 0.5), xytext=(x_start, 0.5),
                arrowprops=dict(arrowstyle="->", lw=2, color="gray"))

plt.title("Statistical Validation Pipeline for YOLO", fontsize=14, fontweight='bold', pad=20)
plt.tight_layout()
plt.savefig('en/pipeline.png', dpi=300)
plt.savefig('es/pipeline.png', dpi=300)
