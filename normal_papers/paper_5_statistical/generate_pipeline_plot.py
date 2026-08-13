import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(6, 3))
ax.axis('off')
ax.text(0.5, 0.5, "Bootstrap Pipeline\n(Generated Placeholder)", size=20, ha="center", va="center")
plt.savefig('en/pipeline.png')
plt.savefig('es/pipeline.png')
