import matplotlib.pyplot as plt

fid = [90.74, 142.93, 149.86]
map_drop = [18.7, 35.4, 43.4]

plt.figure(figsize=(8,6))
plt.scatter(fid, map_drop, color='blue', s=100)
plt.plot(fid, map_drop, color='red', linestyle='dashed')
plt.title('FID Score vs mAP Degradation')
plt.xlabel('Fréchet Inception Distance (FID)')
plt.ylabel('mAP Degradation (%)')
plt.grid(True)
plt.savefig('evidencias/fid_correlation.png')
plt.savefig('en/fid_correlation.png')
plt.savefig('es/fid_correlation.png')
