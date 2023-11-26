import os
import pandas as pd
import numpy as np
import json
from error_message_types import official_error_types
from clean_error_message import normalize_error_message
import ast

logs_folder = '../data_files/student_logs/'
output_folder = '../data_files/short_term_data/'

karel_assgnids = [2023, "2023", "checkerboard", "diagnostic3", "diagnostic3soln", "fillkarel", "hospital", "housekarel", "jigsaw", "midpoint", "mountain", "warmup", "steeplechase", "stepup", "stonemason", "spreadbeepers", "rhoomba", "randompainter", "outline", "piles", 
                  "es-karel-midpoint", "es-karel-cone-pile", "es-karel-stripe", "es-karel-collect-newspaper", "es-karel-hospital", "es-karel-stone-mason", "es-karel-mountain", "es-karel-beeper-line", "es-karel-jump-up", "es-karel-hurdle", "es-karel-checkerboard", 
                  "es-karel-step-up", "es-karel-dog-years", "es-karel-place-2023", "es-karel-mystery", "es-karel-invert-beeper-1d", "es-karel-un", "es-karel-random-painting", "es-karel-outline", "es-karel-fill", "es-karel-to-the-wall", "es-project-karel", "es-karel-place-100",
                  "es-karel-big-beeper", "karelflag"] # 'movebeeper',

# Get the error message types that this user used
def get_error_message_type_for_df(df):
    # Count the number of distinct error message types
    error_message_types = df['error_message_type'].unique()

    result = []
    for error_message_type in error_message_types:
        if error_message_type in official_error_types:
            result.append(error_message_type)

    return result

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
    prev_error_message_type = None

    for i, row in df.iterrows():
        
        if row['error_message_type'] in official_error_types:
            # This is a valid error message type
            # We can look at the actual error message and compare it to the previous error message
            # We can also update the total error count

            raw_errors = ast.literal_eval(row['error'])
            curr_error = []
            for raw_error in raw_errors:
                normalized_error = normalize_error_message(raw_error)
                curr_error.append(normalized_error)   
                total_error_count += 1

                # Check if this error is the same as the previous error
                if (row['projectId'] == prev_project_id and normalized_error in prev_error):
                    assert(prev_error_message_type == row['error_message_type'])
                    assert(row['projectId'] not in karel_assgnids)
                    
                    # This is a repeated error!
                    same_error_count += 1             
            
            prev_project_id = row['projectId']
            prev_error_message_type = row['error_message_type']
            prev_error = curr_error
        
        else:
            # This is not a valid error message type (could be a karel error, or no error)
            # So we do not count any errors
            prev_project_id = row['projectId']
            prev_error_message_type = row['error_message_type']
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
        if row['error_message_type'] in official_error_types and row['projectId'] == prev_project_id:
            assert(row['projectId'] not in karel_assgnids)

            # This is a valid error message type, and we are on the same project as the previous row
            curr_error_counts = {}
            raw_errors = ast.literal_eval(row['error'])

            # Update the current run counts with the previous run counts
            for raw_error in raw_errors:
                normalized_error = normalize_error_message(raw_error)
                curr_error_counts[normalized_error] = prev_error_counts.get(normalized_error, 0) + 1

            # Save the prev run counts that are not in the current run counts
            for error in prev_error_counts:
                if error not in curr_error_counts:
                    # Add the error count to the run counts
                    run_counts.append(prev_error_counts[error])

            # Update the loop variables
            prev_error_counts = curr_error_counts
            prev_project_id = row['projectId']

        elif row['error_message_type'] in official_error_types and row['projectId'] != prev_project_id:
            # This is a valid error message type, but we are on a new project
            curr_error_counts = {}
            raw_errors = ast.literal_eval(row['error'])
            
            # Initialize the current run counts
            for raw_error in raw_errors:
                normalized_error = normalize_error_message(raw_error)
                curr_error_counts[normalized_error] = 1

            # Save the prev run counts
            for error in prev_error_counts:
                run_counts.append(prev_error_counts[error])


            # Update the loop variables
            prev_error_counts = curr_error_counts
            prev_project_id = row['projectId']
        else:
            # This is not a valid error message type (could be a karel error, or no error)

            # Save the prev run counts
            for error in prev_error_counts:
                run_counts.append(prev_error_counts[error])

            # Update the loop variables
            prev_error_counts = {}
            prev_project_id = row['projectId']

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