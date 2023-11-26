# Add the average error run length to the data

import pandas as pd
import numpy as np

# import the function
from parse_short_term_results import get_runs_until_resolved

def get_average_run_length(user_id):
    user_df = pd.read_csv(f'../data_files/student_logs/{user_id}.csv', dtype=str, lineterminator='\n')
    run_counts = get_runs_until_resolved(user_df)
    if len(run_counts) == 0:
        return None
    return np.mean(run_counts)

def add_avg_error_run_length_to_csv():
    # Load the data
    sl_and_student_data = pd.read_csv('../data_files/sl_and_student_data.csv')

    # Add a column for the average error run length
    sl_and_student_data['avg_error_run_length'] = None

    # For each row
    students_only = sl_and_student_data[sl_and_student_data['role'] == 'student']
    for i, row in students_only.iterrows():
        # Add the average error run length to the dataframe
        sl_and_student_data.at[i, 'avg_error_run_length'] = get_average_run_length(row['user_id'])

    # Save the dataframe
    sl_and_student_data.to_csv('../data_files/sl_and_student_data.csv', index=False)

if __name__ == "__main__":
    add_avg_error_run_length_to_csv()