import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime
from scipy import stats



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
            year = datetime.now().year - 14
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
df["date"] = pd.to_datetime(df[["year", "month", "day"]].astype(str).agg('-'.join, axis=1), format="%Y-%b-%d", errors='coerce')

df['file_age'] = (datetime.now() - df['date']).dt.days
df.to_csv("csv/parsed_traffic_date.csv", index=False)


# Find the oldest and newest files
oldest_file = df.loc[df['file_age'].idxmax()]
newest_file = df.loc[df['file_age'].idxmin()]

# Calculate mean, median, and mode of the file ages
mean_age = df['file_age'].mean()
median_age = df['file_age'].median()
file_age_counts = df['file_age'].value_counts()
mode_age = file_age_counts.idxmax()
# mode_age = stats.mode(df['file_age'])[0][0]

# Print the results
print(f"The oldest file is '{oldest_file['filename']}' with an age of {oldest_file['file_age']} days.")
print(f"The newest file is '{newest_file['filename']}' with an age of {newest_file['file_age']} days.")
print(f"Mean file age: {mean_age:.2f} days")
print(f"Median file age: {median_age} days")
print(f"Mode file age: {mode_age} days")

# Plotting
sorted_ages = np.sort(df['file_age'])
cdf = np.arange(1, len(sorted_ages) + 1) / len(sorted_ages)


plt.figure(figsize=(10, 6))

# Plot the CDF with the correct x-axis positions and y-values
plt.step(sorted_ages, cdf, where='post', color='skyblue', linewidth=2)

# Set x-axis ticks and labels
# plt.xticks(ticks=custom_ticks, labels=[str(tick) for tick in custom_ticks])


# Plot the CDF with enhanced aesthetics
plt.xlabel('File Age (days)')
plt.ylabel('Probability')
plt.title('Cumulative Distribution Function (CDF) of File Ages')
plt.grid(True, which="both", ls="--")

plt.savefig("plots/cdf_date_plot.png")  # Save CDF plot

# Adjust layout and show plots
plt.tight_layout()
plt.show()


