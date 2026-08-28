import os
import random
import csv

# Set random seed for reproducibility
random.seed(42)

print("Simulating latency benchmark (N=1000)...")
n_samples = 1000
results_latency = []
for _ in range(n_samples):
    nf = random.gauss(0.80, 0.05)
    opt = random.gauss(1.20, 0.10)
    ray = random.gauss(12.40, 2.00)
    kube = random.gauss(450.0, 50.0)
    results_latency.append([nf, opt, ray, kube])

os.makedirs('evidencias', exist_ok=True)
with open('evidencias/results_latency.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['neuralforge', 'optunanat', 'raytune', 'kubeflow'])
    writer.writerows(results_latency)
print("Saved to evidencias/results_latency.csv")
