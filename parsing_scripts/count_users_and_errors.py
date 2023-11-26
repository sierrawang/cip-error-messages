import pandas as pd
import os
from error_message_types import official_error_types
import ast

logs_folder = '../data_files/student_logs/'

# Return an array of error message types used in this df
def get_error_message_type(df):
    error_message_types = df['error_message_type'].unique()
    result = []
    for error_message_type in error_message_types:
        if error_message_type in official_error_types:
            result.append(error_message_type)
    return result

# Count the number of errors made of this error message type
def count_num_errors_made_of_type(df, error_message_type):
    error_rows_only = df[df['error_message_type'] == error_message_type]
    count = 0
    for i, row in error_rows_only.iterrows():
        raw_errors = ast.literal_eval(row['error'])
        count += len(raw_errors)

    return count

# Return two dictionaries. One contains counts of users that used each error message type. 
# The other contains counts of errors made of each error message type.
def get_counts_of_error_message_types(df):
    user_counts = { 'default': 0, 'explain': 0, 'messageboard': 0, 'tigerpython': 0, 'superhero': 0, 'gpt': 0 }
    error_counts = { 'default': 0, 'explain': 0, 'messageboard': 0, 'tigerpython': 0, 'superhero': 0, 'gpt': 0 }
    
    num_no_error_message_type = 0
    num_one_error_message_type = 0
    num_more_than_one_error_message_type = 0
    
    for student_logs in os.listdir(logs_folder):
        df = pd.read_csv(logs_folder + student_logs, dtype=str, lineterminator='\n')
        
        # Get the student's error message type. If they did not use exaclty one error message type, skip them.
        error_message_types = get_error_message_type(df)
        if len(error_message_types) == 0:
            num_no_error_message_type += 1
            continue
        if len(error_message_types) > 1:
            num_more_than_one_error_message_type += 1
            continue
        num_one_error_message_type += 1

        error_message_type = error_message_types[0]
        user_counts[error_message_type] += 1
        error_counts[error_message_type] += count_num_errors_made_of_type(df, error_message_type)


    print(f"Number of students with no error message type: {num_no_error_message_type}")
    print(f"Number of students with more than one error message type: {num_more_than_one_error_message_type}")
    return user_counts, error_counts

# Print out a latex table. The first column is the official error message type. 
# The second column is the number of users that used that error message type. 
# The third column is the number of errors made of that error message type.
def make_latex_table(user_counts, error_counts):
    print("\\begin{tabular}{|c|c|c|}")
    print("\\hline")
    print("Error Message Type & Number of Users & Number of Errors \\\\")
    print("\\hline")
    for error_message_type in official_error_types:
        print(f"{official_error_types[error_message_type]} & {user_counts[error_message_type]} & {error_counts[error_message_type]} \\\\ \\hline")

    # The last row is the total number of users and errors in bold
    total_users = 0
    total_errors = 0
    for error_message_type in official_error_types:
        total_users += user_counts[error_message_type]
        total_errors += error_counts[error_message_type]
    print(f"\\textbf{{Total}} & \\textbf{{{total_users}}} & \\textbf{{{total_errors}}} \\\\")

    print("\\hline")
    print("\\end{tabular}")

if __name__ == '__main__':
    user_counts, error_counts = get_counts_of_error_message_types(logs_folder)
    make_latex_table(user_counts, error_counts)


    
        
