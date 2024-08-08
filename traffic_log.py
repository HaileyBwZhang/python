import pandas as pd
from datetime import datetime

# Define a function to parse each line of the text file
def parse_line(line):
    # Skip empty lines or lines with only whitespace
    if line.strip() == "":
        return None
    
    parts = line.split()
    
    # Ignore lines that do not fit the expected format
    if parts[0] in ['.', '..', '.:'] or parts[0].startswith('./') or parts[0] == 'total':
        return None

    try:
        # Check if the line contains a standard file entry
        permissions = parts[0]
        links = parts[1]
        owner = parts[2]
        group = parts[3]
        size = int(parts[4])
        
        # Handle date and time formats
        month = parts[5]
        day = int(parts[6])
        if ':' in parts[7]:  # Current year, no year provided
            year = datetime.now().year
            time = parts[7]
        else:
            year = int(parts[7])
            time = None

        filename = ' '.join(parts[8:])

        return [permissions, links, owner, group, size, month, day, year, time, filename]
    except IndexError as e:
        # Print the problematic line for debugging
        print(f"Error parsing line: {line}")
        print(f"Error: {e}")
        return None

# Read and parse the text file
with open("txt/www2007data.txt", "r") as file:
    lines = file.readlines()
    data = [parse_line(line) for line in lines]

# Remove None values (invalid lines)
data = [entry for entry in data if entry is not None]

# Check if all entries have the correct length
for entry in data:
    if len(entry) != 10:
        print(f"Entry with incorrect length: {entry}")

# Create a DataFrame
columns = ["permissions", "links", "owner", "group", "size", "month", "day", "year", "time", "filename"]
df = pd.DataFrame(data, columns=columns)

# Convert size to numeric and date to datetime
df["size"] = pd.to_numeric(df["size"], errors='coerce')
df["date"] = pd.to_datetime(df[["year", "month", "day"]].astype(str).agg('-'.join, axis=1), format="%Y-%b-%d", errors='coerce')

# # Save the DataFrame to a CSV file
# df.to_csv("parsed_traffic_data.csv", index=False)

# Display the first few rows of the DataFrame
print(df.head())

# Filter for regular files (permissions do not start with 'd')
regular_files = df[df['permissions'].str.startswith('-')]

# Drop duplicates based on filename to ensure unique filenames
unique_regular_files = regular_files.drop_duplicates(subset=['filename'])

# Count the number of different unique regular files
num_unique_regular_files = unique_regular_files.shape[0]

# Calculate the aggregate size of these unique files
total_size_unique_regular_files = unique_regular_files['size'].sum()

# Display the results
print(f"Number of different unique regular files: {num_unique_regular_files}")
print(f"Aggregate size of unique regular files: {total_size_unique_regular_files} bytes")

# Find the largest file
largest_file = unique_regular_files.loc[unique_regular_files['size'].idxmax()]
largest_file_name = largest_file['filename']
largest_file_size = largest_file['size']

# Count the number of empty files
num_empty_files = unique_regular_files[unique_regular_files['size'] == 0].shape[0]

# Find the smallest non-empty file
non_empty_files = unique_regular_files[unique_regular_files['size'] > 0]
if not non_empty_files.empty:
    smallest_file = non_empty_files.loc[non_empty_files['size'].idxmin()]
    smallest_file_name = smallest_file['filename']
    smallest_file_size = smallest_file['size']
else:
    smallest_file_name = None
    smallest_file_size = None

# Display the results
print(f"Largest file: {largest_file_name} with size {largest_file_size} bytes")
print(f"Number of empty files: {num_empty_files}")
if smallest_file_name:
    print(f"Smallest non-empty file: {smallest_file_name} with size {smallest_file_size} bytes")
else:
    print("No non-empty files found.")

# Calculate statistical metrics
mean_file_size = df["size"].mean()
std_dev_file_size = df["size"].std()
median_file_size = df["size"].median()
mode_file_size = df["size"].mode().tolist()

# Statistical calculations
print(f"Mean file size: {mean_file_size:.2f} bytes")
print(f"Standard deviation of file size: {std_dev_file_size:.2f} bytes")
print(f"Median file size: {median_file_size:.2f} bytes")
print(f"Mode(s) of file size distribution: {', '.join(map(str, mode_file_size))} bytes")


# Extract file extension
df['extension'] = df['filename'].apply(lambda x: x.split('.')[-1].lower() if '.' in x else 'Unknown')

# Group by file type and calculate counts and total size
file_type_stats = df.groupby('extension').agg(
    file_count=('filename', 'size'),
    total_size=('size', 'sum')
).reset_index()

# Calculate percentages
total_files = file_type_stats['file_count'].sum()
total_bytes = file_type_stats['total_size'].sum()
print(f"total file num {total_files}")
print(f"total file bytes {total_bytes}")


file_type_stats['file_percentage'] = file_type_stats['file_count'] / total_files
file_type_stats['size_percentage'] = file_type_stats['total_size'] / total_bytes 

# Sort by file count and get top 10
known_file_types = file_type_stats[file_type_stats['extension'] != 'Unknown']
top_file_types = known_file_types.sort_values(by='file_count', ascending=False).head(10)

#top_file_types = file_type_stats.sort_values(by='file_count', ascending=False).head(10)

# Add 'Other' category
# other_files = file_type_stats.sort_values(by='file_count', ascending=False).iloc[10:]
# other_files_sum = other_files[['file_count', 'total_size']].sum()
# other_files_sum['extension'] = 'Other'
# other_files_sum['file_percentage'] = other_files_sum['file_count'] / total_files
# other_files_sum['size_percentage'] = other_files_sum['total_size'] / total_bytes

# Convert other_files_sum to a DataFrame for concatenation
# other_files_df = pd.DataFrame([other_files_sum])

# Concatenate top 10 with 'Other'
# result_df = pd.concat([top_file_types, other_files_df], ignore_index=True)

# Format the output
top_file_types['file_percentage'] = top_file_types['file_percentage'].apply(lambda x: f'{x:.2%}')
top_file_types['size_percentage'] = top_file_types['size_percentage'].apply(lambda x: f'{x:.2%}')

# Print the table
print(top_file_types.to_string(index=False))

# Optionally, save to a CSV file
top_file_types.to_csv('csv/file_type_distribution1.csv', index=False)
