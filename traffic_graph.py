import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
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

# Read and parse the text file
with open("txt/www2007data.txt", "r") as file:
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

# Get the size data
sizes = df['size']

# Calculate frequency of each unique file size
size_counts = sizes.value_counts().sort_index()

# Calculate probabilities
total_files = size_counts.sum()
probabilities = size_counts / total_files

# Prepare data for plotting
unique_sizes = probabilities.index
pdf_probabilities = probabilities.values

# Plotting
plt.figure(figsize=(14, 6))

# Plot the PDF
plt.subplot(1, 2, 1)
plt.bar(unique_sizes, pdf_probabilities, width=0.8, color='skyblue', edgecolor='black')
plt.xscale('log')  # Log scale for x-axis
plt.xlabel("File Size (bytes, log scale)")
plt.ylabel("Probability")
plt.title("PDF")
plt.ylim(0, max(pdf_probabilities) * 1.1)  # Extend y-axis for better visibility
log_ticks = [0,1, 2, 3, 4, 5, 6, 7, 8, 9]  # 指数部分
plt.xticks([10**x for x in log_ticks], [f'$10^{x}$' for x in log_ticks])



# Plot the CDF
plt.subplot(1, 2, 2)
sorted_sizes = np.sort(unique_sizes)
cumulative_probabilities = np.cumsum([probabilities[size] for size in sorted_sizes])
plt.step(sorted_sizes, cumulative_probabilities, where='post', color='salmon')
plt.xscale('log')  # Log scale for x-axis
plt.xlabel("File Size (bytes, log scale)")
plt.ylabel("Cumulative Probability")
plt.title("CDF")
plt.ylim(0, 1.1)  # Extend y-axis for better visibility
plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x:.0%}'))  # Percentage format
plt.savefig("plots/cdf_plot.png")  # Save CDF plot

# Adjust layout and show plots
plt.tight_layout()
plt.show()


