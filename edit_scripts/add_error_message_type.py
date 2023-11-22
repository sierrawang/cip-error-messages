import pandas as pd
import os
import ast
import numpy as np

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

if __name__ == '__main__':

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