import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde, mode
import itertools
# Example array

matrix =[
    [1, 2, 3,1,1,1,2,2,3,4,5,7],
    [1,1,1,6,6,6,6,6,6,6,7],
    [-1,-1,-1,-1,-1,-1, 34,100]
]

data =  list(itertools.chain(*matrix))




# Plot histogram
# plt.figure(figsize=(12, 6))
# plt.hist(data, bins=10, alpha=0.6, color='g', edgecolor='black')
# plt.axvline(mean_value, color='r', linestyle='dashed', linewidth=1, label=f'Mean: {mean_value:.2f}')
# plt.axvline(median_value, color='b', linestyle='dashed', linewidth=1, label=f'Median: {median_value:.2f}')
# plt.axvline(mode_value, color='purple', linestyle='dashed', linewidth=1, label=f'Mode: {mode_value:.2f}')
# plt.title('Data Distribution')
# plt.xlabel('Value')
# plt.ylabel('Frequency')
# plt.legend()
# plt.show()
data =  list(itertools.chain(*matrix))
kde = gaussian_kde(data)
new_ab = []
data_set = {}
value_set = set(data)
print(np.var(list(value_set)))
x_range = np.linspace(min(data), max(data), len(data))

for item in value_set:
    data_set[item] = kde(item)

sorted(data_set.items(), key=lambda item: item[1], reverse=True)
plotnost = 0.8
sum_value = 0 
for key, value in data_set.items():
    if sum_value < plotnost:
        sum_value += value[0]
        new_ab.append(key)
    else:
        break

print(list(data_set.keys())[0])



plt.plot(x_range, kde(x_range), label='KDE')
plt.title('Kernel Density Estimation')
plt.xlabel('Value')
plt.ylabel('Density')
plt.legend()
plt.show()
