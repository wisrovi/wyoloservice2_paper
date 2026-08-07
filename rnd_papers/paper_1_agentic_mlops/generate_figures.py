import os
import matplotlib.pyplot as plt

os.makedirs('en/figures', exist_ok=True)
os.makedirs('es/figures', exist_ok=True)

# 1. Flowchart using Matplotlib
fig, ax = plt.subplots(figsize=(12, 2))
ax.axis('off')

nodes = ['User', 'LLM', 'MCP Server', 'Celery Broker', 'Invoker Daemon', 'Ephemeral Docker Container']
x_pos = [0.1, 0.25, 0.45, 0.65, 0.85, 1.1]

for i, text in enumerate(nodes):
    ax.text(x_pos[i], 0.5, text, ha='center', va='center', bbox=dict(boxstyle='round,pad=0.5', fc='white', ec='black'))
    if i < len(nodes) - 1:
        ax.annotate('', xy=(x_pos[i+1]-0.08, 0.5), xytext=(x_pos[i]+0.08, 0.5), arrowprops=dict(arrowstyle="->", color='black'))

plt.savefig('en/figures/flowchart.pdf', bbox_inches='tight')
plt.savefig('es/figures/flowchart.pdf', bbox_inches='tight')
plt.close()

# 2. Bar Chart
labels = ['Legacy Daemon', 'Invoker-Executor']
crashes = [12, 0]
peak_memory = [28, 16]

x = range(len(labels))
fig, ax1 = plt.subplots()

color = 'tab:red'
ax1.set_xlabel('Architecture')
ax1.set_ylabel('OOM Crashes', color=color)
ax1.bar([i - 0.2 for i in x], crashes, 0.4, color=color, label='OOM Crashes')
ax1.tick_params(axis='y', labelcolor=color)
ax1.set_ylim(0, 14)

ax2 = ax1.twinx()
color = 'tab:blue'
ax2.set_ylabel('Peak Memory (GB)', color=color)
ax2.bar([i + 0.2 for i in x], peak_memory, 0.4, color=color, label='Peak Memory')
ax2.tick_params(axis='y', labelcolor=color)
ax2.set_ylim(0, 30)

ax1.set_xticks(x)
ax1.set_xticklabels(labels)

fig.tight_layout()
plt.savefig('en/figures/barchart.pdf')
plt.savefig('es/figures/barchart.pdf')
plt.close()
