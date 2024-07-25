import pandas as pd
import os
import re

# Input and output folders
input_folder = 'raw_data'
output_folder = 'processed_data'
os.makedirs(output_folder, exist_ok=True)

# Function to process each file
def process_file(file_path):
    # Read the input CSV file starting from row 3 (index 2)
    df = pd.read_csv(file_path, skiprows=2)

    # Initialize a dictionary to store the processed data
    processed_data = {}

    # Process each row in the DataFrame
    for index, row in df.iterrows():
        filename = row['FileName'].strip()  # Strip any leading/trailing whitespace
        peak_area = row['Peak Area']
        
        # Handle filenames with dashes (strains with replicates)
        match_strain = re.search(r'(\d+)-(\d+)', filename)
        # Handle filenames with underscores (standards)
        match_standard = re.search(r'(\d+)_(\d+)', filename)
        
        if match_strain:
            strain_number = f'Strain{int(match_strain.group(1)):02d}'
            replicate_number = int(match_strain.group(2))
            
            # Initialize the strain entry in the dictionary if not already present
            if strain_number not in processed_data:
                processed_data[strain_number] = {}
            
            # Store the peak area value for the replicate
            processed_data[strain_number][replicate_number] = peak_area
        elif match_standard:
            standard_name = f"{match_standard.group(1)}.{match_standard.group(2)}"
            
            # Initialize the standard entry in the dictionary if not already present
            if standard_name not in processed_data:
                processed_data[standard_name] = {}
            
            # Store the peak area value for the standard
            processed_data[standard_name][1] = peak_area

    # Create a DataFrame from the processed data
    final_df = pd.DataFrame(processed_data).sort_index()

    # Extract the compound number from the file name
    file_name = os.path.basename(file_path)
    compound_match = re.search(r'(\d+)', file_name)
    if compound_match:
        compound_number = compound_match.group(1)
    else:
        compound_number = 'unknown'

    # Save the final DataFrame to a new CSV file
    output_file = os.path.join(output_folder, f'compound{compound_number}Cleaned.csv')
    final_df.to_csv(output_file, index_label='Replicate')

    print(f"Processed data saved to {output_file}")

# Iterate over all CSV files in the input folder
for file_name in os.listdir(input_folder):
    if file_name.endswith('.csv'):
        file_path = os.path.join(input_folder, file_name)
        process_file(file_path)