import os
import csv
import numpy as np
import krippendorff

def read_third_column_from_file(filepath):
    """
    Read the third column from a TSV file, skipping rows starting with #, and return as a list.
    """
    with open(filepath, 'r', encoding='utf-8') as file:
        reader = csv.reader(file, delimiter='\t')
        column_data = []
        for row in reader:
            if not row:  # Skip empty rows
                continue
            if row[0].startswith('#'):  # Skip rows starting with #
                continue
            if len(row) > 2:  # Check if the row has at least 3 columns
                column_data.append(row[2])
            else:
                print(f"Warning: Missing data in {filepath} on line {reader.line_num}.")
                column_data.append(None)  # Or any default value you prefer
    return column_data


def process_tsv_files(folder_A, folder_B):
    """
    Process TSV files from folder_A and folder_B and return a dictionary.
    Each key is a filename, and each value is a dictionary with folder names as keys and lists
    (IAA-A or IAA-B) as values.
    """
    filenames_in_A = set([f for f in os.listdir(folder_A) if f.endswith('.tsv')])
    filenames_in_B = set([f for f in os.listdir(folder_B) if f.endswith('.tsv')])

    common_files = filenames_in_A.intersection(filenames_in_B)

    result = {}

    for filename in common_files:
        filepath_A = os.path.join(folder_A, filename)
        filepath_B = os.path.join(folder_B, filename)

        IAA_A = read_third_column_from_file(filepath_A)
        IAA_B = read_third_column_from_file(filepath_B)

        folder_name_A = os.path.basename(folder_A)
        folder_name_B = os.path.basename(folder_B)

        result[filename] = {
            folder_name_A: IAA_A,
            folder_name_B: IAA_B
        }

    # Files exclusive to A or B
    exclusive_to_A = filenames_in_A.difference(filenames_in_B)
    exclusive_to_B = filenames_in_B.difference(filenames_in_A)

    if exclusive_to_A:
        print("Files exclusive to Folder A:")
        for f in exclusive_to_A:
            print(f)

    if exclusive_to_B:
        print("\nFiles exclusive to Folder B:")
        for f in exclusive_to_B:
            print(f)

    return result


def process_list_refined(lst):
    # Process the list to remove "_" and retain non-consecutive duplicates
    result = []
    prev_item = None
    for item in lst:
        if item == "_":
            continue
        current_item = item.replace('_', '')
        if current_item != prev_item:
            result.append(current_item)
        prev_item = current_item

    return result

IAA_values = process_tsv_files('benchmark/v0.1/iaa/filtering/output/tsv/user_23628', 'benchmark/v0.1/iaa/filtering/output/tsv/user_36136')

# Extracting and flattening values for 'Key A' and 'Key B'
user23628_values = [item for sublist in [inner['user_23628'] for inner in IAA_values.values()] for item in sublist]
user36136_values = [item for sublist in [inner['user_36136'] for inner in IAA_values.values()] for item in sublist]

user23628_values_str = ' '.join(user23628_values)
user36136_values_str = ' '.join(user36136_values)

'''CALCULATE KIPPENDORFF'''

reliability_data_str = (user23628_values_str, user36136_values_str)

reliability_data = [[np.nan if v == "_" else v for v in coder.split()] for coder in reliability_data_str]

print("Krippendorff's alpha for nominal metric: ", krippendorff.alpha(reliability_data=reliability_data, level_of_measurement="nominal"))