import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

# Define a function to parse each line of the text file
def parse_line(line):
    if line.strip() == "":
        return None
    
    parts = line.split()
    
    if parts[0] in ['.', '..', '.:'] or parts[0].startswith('./') or parts[0] == 'total':
        return None

    try:
        permissions = parts[0]
        links = parts[1]
        owner = parts[2]
        group = parts[3]
        size = int(parts[4])
        
        month = parts[5]
        day = int(parts[6])
        if ':' in parts[7]:
            year = datetime.now().year
            time = parts[7]
        else:
            year = int(parts[7])
            time = None

        filename = ' '.join(parts[8:])

        return [permissions, links, owner, group, size, month, day, year, time, filename]
    except IndexError as e:
        print(f"Error parsing line: {line}")
        print(f"Error: {e}")
        return None

# Function to read and parse a file into a DataFrame
def read_and_parse_file(filename):
    with open(filename, "r") as file:
        lines = file.readlines()
        data = [parse_line(line) for line in lines]

    # Remove None values (invalid lines)
    data = [entry for entry in data if entry is not None]

    # Create a DataFrame
    columns = ["permissions", "links", "owner", "group", "size", "month", "day", "year", "time", "filename"]
    df = pd.DataFrame(data, columns=columns)

    df = df.dropna(subset=['size'])
    df['size'] = pd.to_numeric(df['size'], errors='coerce')

    # Remove rows with NaN sizes
    df = df.dropna(subset=['size'])
    
    return df['size']

# Read and parse the text files
sizes1 = read_and_parse_file("txt/paperdata.txt")
sizes2 = read_and_parse_file("txt/posterdata.txt")



# Calculate frequency of each unique file size
size_counts1 = sizes1.value_counts().sort_index()

# Calculate probabilities
total_files1 = size_counts1.sum()
probabilities1 = size_counts1 / total_files1

# Prepare data for plotting
unique_sizes1 = probabilities1.index


# Calculate frequency of each unique file size
size_counts2 = sizes2.value_counts().sort_index()

# Calculate probabilities
total_files2 = size_counts2.sum()
probabilities2 = size_counts2 / total_files2

# Prepare data for plotting
unique_sizes2 = probabilities2.index

sorted_sizes1 = np.sort(unique_sizes1)
cumulative_probabilities1 = np.cumsum([probabilities1[size] for size in sorted_sizes1])

sorted_sizes2 = np.sort(unique_sizes2)
cumulative_probabilities2 = np.cumsum([probabilities2[size] for size in sorted_sizes2])

# Plotting
bar_width = 0.35  # 设置条形图的宽度

fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# Add titles and labels
# 绘制第一个数据集
axes[0].bar(unique_sizes1, probabilities1, width=bar_width, color='skyblue', edgecolor='black', align='center')
axes[0].set_xscale('log')  # Log scale for x-axis
axes[0].set_xlabel("File Size (bytes, log scale)")
axes[0].set_ylabel("Probability")
axes[0].set_title("PDF - Paper")
axes[0].set_ylim(0, max(probabilities1) * 1.1)  # Extend y-axis for better visibility

log_ticks = [4, 5, 6, 7]  # 指数部分
axes[0].set_xticks([10**x for x in log_ticks])
axes[0].set_xticklabels([f'$10^{x}$' for x in log_ticks])


# 绘制第二个数据集，调整条形的位置以避免重叠
axes[1].bar(unique_sizes2, probabilities2, width=bar_width, color='salmon', edgecolor='black', align='center')
axes[1].set_xscale('log')  # Log scale for x-axis
axes[1].set_xlabel("File Size (bytes, log scale)")
axes[1].set_ylabel("Probability")
axes[1].set_title("PDF - Poster")
axes[1].set_ylim(0, max(probabilities2) * 1.1)  # Extend y-axis for better visibility
axes[1].set_xticks([10**x for x in log_ticks])
axes[1].set_xticklabels([f'$10^{x}$' for x in log_ticks])

# Save and show the plot
plt.savefig("plots/pdf_plot_paper.png")
plt.show()
