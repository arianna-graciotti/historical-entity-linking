

def compare_csv_files(file1: str, file2: str, output_file: str):
    df1 = pd.read_csv(file1).sort_index(axis=1).fillna('')
    df2 = pd.read_csv(file2, sep=';').sort_index(axis=1).fillna('')

    with open(output_file, 'w') as f:
        if df1.equals(df2):
            f.write("The files are the same\n")
        else:
            f.write("The files are different\n")
            # Find columns present in df1 but missing in df2
            missing_in_df2 = df1.columns.difference(df2.columns)
            if missing_in_df2.any():
                f.write("Columns in file1 but missing in file2: " + ', '.join(missing_in_df2) + "\n")
            # Find columns present in df2 but missing in df1
            missing_in_df1 = df2.columns.difference(df1.columns)
            if missing_in_df1.any():
                f.write("Columns in file2 but missing in file1: " + ', '.join(missing_in_df1) + "\n")
            # Find rows that are different
            diff_rows = df1.ne(df2)
            if diff_rows.any().any():
                f.write("Rows that are different:\n")
                f.write(diff_rows.to_string() + "\n")

def compare_csv_files_expl_diff(file1: str, file2: str, output_file: str):
    df1 = pd.read_csv(file1).sort_index(axis=1).fillna('')
    df2 = pd.read_csv(file2, sep=";").sort_index(axis=1).fillna('')

    with open(output_file, 'w') as f:
        if df1.equals(df2):
            f.write("The files are the same\n")
        else:
            f.write("The files are different\n")
            # Find columns present in df1 but missing in df2
            missing_in_df2 = df1.columns.difference(df2.columns)
            if missing_in_df2.any():
                f.write("Columns in file1 but missing in file2: " + ', '.join(missing_in_df2) + "\n")
            # Find columns present in df2 but missing in df1
            missing_in_df1 = df2.columns.difference(df1.columns)
            if missing_in_df1.any():
                f.write("Columns in file2 but missing in file1: " + ', '.join(missing_in_df1) + "\n")
            # Find rows that are different
            diff_mask = df1.ne(df2)
            if diff_mask.any().any():
                diff = df1.where(diff_mask)
                f.write("Rows that are different:\n")
                f.write(diff.to_string() + "\n")

# Replace with the path to your output CSV file and the expected CSV file
output_csv_file = 'data/output_prova.csv'
expected_csv_file = 'data/json_to_csv_headers_310723.csv'
comparison_output_file = 'data/comparison_output.txt'

compare_csv_files(output_csv_file, expected_csv_file, comparison_output_file)

compare_csv_files_expl_diff(output_csv_file, expected_csv_file, comparison_output_file)