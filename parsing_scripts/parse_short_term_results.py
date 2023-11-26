import os
import pandas as pd
import numpy as np
import json
from error_message_types import get_error_message_type_for_df, get_raw_errors
from clean_error_message import normalize_error_message
from karel_info import not_karel

logs_folder = '../data_files/student_logs/'
output_folder = '../data_files/short_term_data/'

# Return a count of the number of times the user got the same error 
# message in subsequent runs, and the total number of times they got an error
def get_count_same_subsequent_error(df): 
    # The number of times the user got the same error in the subsequent run
    same_error_count = 0

    # The total number of errors that the user got
    total_error_count = 0

    # Variables to keep track of the previous error
    prev_error = []
    prev_project_id = None

    for i, row in df.iterrows():
        
        if not_karel(row):
            # So we can update the error counts
            raw_errors = get_raw_errors(row)
            curr_error = []
            for raw_error in raw_errors:
                normalized_error = normalize_error_message(raw_error)
                curr_error.append(normalized_error)   
                
                total_error_count += 1

                # Check if this error is the same as the previous error
                if (row['projectId'] == prev_project_id and normalized_error in prev_error):
                    same_error_count += 1
                    
            prev_project_id = row['projectId']
            prev_error = curr_error
        
        else:
            # This row is from a karel assignment, so we do not count any errors
            prev_project_id = row['projectId']
            prev_error = []

    return same_error_count, total_error_count

# Return a list of counts of the number of runs it took to resolve each error
def get_runs_until_resolved(df):
    # Keep track of the number of runs it took to resolve each error
    run_counts = []

    # A dictionary of the current errors and number of runs they have occurred
    prev_error_counts = {}
    prev_project_id = None

    for i, row in df.iterrows():
        if not_karel(row):
            # If this is a new project, reset prev_error_counts.
            # We do not save the prev run counts because they were not resolved.
            # This also has to happen so that we can correctly create curr_error_counts.
            if row['projectId'] != prev_project_id:
                prev_error_counts = {}

            # Construct the current error counts
            curr_error_counts = {}
            raw_errors = get_raw_errors(row)
            for raw_error in raw_errors:
                normalized_error = normalize_error_message(raw_error)
                curr_error_counts[normalized_error] = prev_error_counts.get(normalized_error, 0) + 1

            # Save the prev run counts that are not in the current run counts
            for error in prev_error_counts:
                if error not in curr_error_counts:
                    # Add the error count to the run counts
                    run_counts.append(prev_error_counts[error])

            # Update loop variables
            prev_project_id = row['projectId']
            prev_error_counts = curr_error_counts
        else:
            # Update loop variables
            prev_project_id = row['projectId']
            prev_error_counts = {}

    return run_counts

def parse_data_on_short_term():
    # Count the number of times the user got the same error in the subsequent run
    percent_same_subsequent_error= { 'default': [], 'explain': [], 'messageboard': [], 'tigerpython': [], 'superhero': [], 'gpt': [] }
    
    # Count the number of times it took a user to resolve their error
    average_runs_until_resolved = { 'default': [], 'explain': [], 'messageboard': [], 'tigerpython': [], 'superhero': [], 'gpt': [] }

    # Count the number of times a user got the same error in the subsequent run
    count_same_subequent_error = { 'default': 0, 'explain': 0, 'messageboard': 0, 'tigerpython': 0, 'superhero': 0, 'gpt': 0 }
    
    # Count the number of times a user made an error
    count_total_errors = { 'default': 0, 'explain': 0, 'messageboard': 0, 'tigerpython': 0, 'superhero': 0, 'gpt': 0 }

    runs_until_resolved_counts = { 'default': [], 'explain': [], 'messageboard': [], 'tigerpython': [], 'superhero': [], 'gpt': [] }

    students_counted = 0
    total_errors_counted = 0

    for filename in os.listdir(logs_folder):
        # Read in the student's log file
        df = pd.read_csv(logs_folder + filename, dtype=str, lineterminator='\n')

        # Get the error message type for this dataframe
        error_message_types = get_error_message_type_for_df(df)
        if len(error_message_types) != 1:
            continue
        error_message_type = error_message_types[0]

        students_counted += 1

        # Sort the dataframe by project id, and then by timestamp
        df = df.sort_values(by=['projectId', 'ogTimestamp'])

        # This counts the number of times the user got the same error in the subsequent run
        # and the total number of times they got an error
        same_subsequent_error_count, total_error_count = get_count_same_subsequent_error(df)

        total_errors_counted += total_error_count

        # Get the runs until resolved for this user
        runs_until_resolved = get_runs_until_resolved(df)

        # Append the percent of runs that the user got the same error message in subsequent runs
        if total_error_count > 0:
            percent_same_subsequent_error[error_message_type].append(same_subsequent_error_count/total_error_count)
        
        # Append the average runs until resolved to the list of runs until resolved for this error message type
        if len(runs_until_resolved) > 0:
            average_runs_until_resolved[error_message_type].append(np.mean(runs_until_resolved))

        count_same_subequent_error[error_message_type] += same_subsequent_error_count
        count_total_errors[error_message_type] += total_error_count
        runs_until_resolved_counts[error_message_type].extend(runs_until_resolved)

    print("Students counted: ", students_counted)
    print("Total errors counted: ", total_errors_counted)
    print(count_total_errors)


    return percent_same_subsequent_error, average_runs_until_resolved, count_same_subequent_error, count_total_errors, runs_until_resolved_counts


def parse_and_write_data_on_short_term():
    (percent_same_subsequent_error, 
     average_runs_until_resolved, 
     count_same_subequent_error, 
     count_total_errors, 
     runs_until_resolved_counts) = parse_data_on_short_term()
    
    # Write each of the results to a file
    with open(f'{output_folder}percent_same_subsequent_error.json', 'w') as f:
        json.dump(percent_same_subsequent_error, f)

    with open(f'{output_folder}average_runs_until_resolved.json', 'w') as f:
        json.dump(average_runs_until_resolved, f)

    with open(f'{output_folder}count_same_subequent_error.json', 'w') as f:
        json.dump(count_same_subequent_error, f)

    with open(f'{output_folder}count_total_errors.json', 'w') as f:
        json.dump(count_total_errors, f)

    with open(f'{output_folder}runs_until_resolved_counts.json', 'w') as f:
        json.dump(runs_until_resolved_counts, f)


if __name__ == '__main__':
    parse_and_write_data_on_short_term()