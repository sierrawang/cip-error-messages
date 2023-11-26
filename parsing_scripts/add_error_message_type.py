import pandas as pd
import os
import ast
import numpy as np
from error_message_types import get_error_message_type_for_df

# Add the error message type column to every log file

log_folder = '../data_files/student_logs/'

# Get the first error message type for a given row
def get_row_error_message_type(row):
    error_messages = ast.literal_eval(row['error_message'])

    if len(error_messages) > 0:
        # Get the error message type
        error_message = error_messages[0]
        return error_message.split(':')[0].strip()
    else:
        # If there is no error message, return None
        return None

def add_error_message_type_to_logs():
    for log_file in os.listdir(log_folder):
        try:
            df = pd.read_csv(log_folder + log_file)
            df['error_message_type'] = None

            for index, row in df.iterrows():
                df.at[index, 'error_message_type'] = get_row_error_message_type(row)

            df.to_csv(log_folder + log_file, index=False)
            
        except Exception as e:
            print(f"Error processing {log_file}")
            continue

def add_error_message_type_to_overall_data():
    # Load the data
    sl_and_student_data = pd.read_csv('../data_files/sl_and_student_data.csv')

    # Add a column for the error message type
    sl_and_student_data['error_message_type'] = None

    # For each row
    students_only = sl_and_student_data[sl_and_student_data['role'] == 'student']
    for i, row in students_only.iterrows():
        # Get the error message type for this student
        df = pd.read_csv(f'../data_files/student_logs/{row["user_id"]}.csv', dtype=str, lineterminator='\n')
        error_message_types = get_error_message_type_for_df(df)
        if len(error_message_types) == 1:
            sl_and_student_data.at[i, 'error_message_type'] = error_message_types[0]
        else:
            sl_and_student_data.at[i, 'error_message_type'] = 'other'

    # Save the dataframe
    sl_and_student_data.to_csv('../data_files/sl_and_student_data.csv', index=False)

if __name__ == '__main__':
    # add_error_message_type_to_logs()
    add_error_message_type_to_overall_data()
    