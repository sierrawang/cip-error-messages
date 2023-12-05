import json
import pandas as pd
import os
import ast
import numpy as np
from clean_error_message import normalize_error_message
from error_message_types import get_error_message_type_for_df, get_raw_errors, valid_error_message_type
from karel_info import not_karel

logs_folder = '../data_files/student_logs/'
output_folder = '../data_files/long_term_data/'

# Get the week of the given timestamp
def get_week(timestamp):
    ts = pd.to_datetime(timestamp, format='mixed')
    # Compare timestamps as pd.
    # week1 if timestamp is before April 30th, 2023 12:00 AM
    if ts < pd.Timestamp('2023-04-30 00:00:00', tz='America/Los_Angeles'):
        return 1
    # week2 if timestamp is before May 7th, 2023 12:00 AM
    elif ts < pd.Timestamp('2023-05-07 00:00:00', tz='America/Los_Angeles'):
        return 2
    # week3 if timestamp is before May 14th, 2023 12:00 AM
    elif ts < pd.Timestamp('2023-05-14 00:00:00', tz='America/Los_Angeles'):
        return 3
    # week4 if timestamp is before May 21st, 2023 12:00 AM
    elif ts < pd.Timestamp('2023-05-21 00:00:00', tz='America/Los_Angeles'):
        return 4
    # week5 if timestamp is before May 28th, 2023 12:00 AM
    elif ts < pd.Timestamp('2023-05-28 00:00:00', tz='America/Los_Angeles'):
        return 5
    # week6 if timestamp is before June 4th, 2023 12:00 AM
    elif ts < pd.Timestamp('2023-06-04 00:00:00', tz='America/Los_Angeles'):
        return 6
    # week7 if timestamp is before June 8th, 2023 12:00 AM
    elif ts < pd.Timestamp('2023-06-08 00:00:00', tz='America/Los_Angeles'):
        return 7
    else:
        return None

# Return a dictionary of the percent of runs that are errors each week for this user
def percent_errors_over_time_for_user(df):
    errors_per_week = { 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, None: 0 }
    runs_per_week = { 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, None: 0 }

    # Count the runs and errors per week
    for index, row in df.iterrows():
        if not_karel(row):
            week = get_week(row['ogTimestamp'])

            runs_per_week[week] += 1

            error_messages = get_raw_errors(row)
            if len(error_messages) > 0:
                errors_per_week[week] += 1
                assert(valid_error_message_type(row))
            
    # Calculate the percent errors per week
    percent_errors_per_week = {}
    for week in range(1, 8):
        if runs_per_week[week] > 0:
            percent_errors_per_week[week] = errors_per_week[week] / runs_per_week[week]

    return percent_errors_per_week

def length_error_runs_over_time_for_user(df):
    # Sort the dataframe by project id and timestamp
    df = df.sort_values(by=['projectId', 'ogTimestamp'])

    # For each week, store the lengths of all error runs
    run_counts = { 1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: [], None: [] }

    # Keep track of the current error run lengths that we are tracking
    prev_error_counts = {}

    # Keep track of the week that each error run started
    prev_error_counts_track_week = {}

    # Keep track of the current project id
    prev_project_id = None

    # Loop through the runs in chronological order
    for i, row in df.iterrows():
        if not_karel(row):
            # If this is a new project, reset prev_error_counts.
            # We do not save the prev run counts because they were not resolved.
            if row['projectId'] != prev_project_id:
                prev_error_counts = {}
                prev_error_counts_track_week = {}

            # Construct the current error counts
            curr_error_counts = {}
            curr_error_counts_track_week = {}
            raw_errors = get_raw_errors(row)
            for raw_error in raw_errors:
                assert(row['error_message_type'] in ['default', 'gpt', 'superhero', 'messageboard', 'explain', 'tigerpython'])
                normalized_error = normalize_error_message(raw_error)
                curr_error_counts[normalized_error] = prev_error_counts.get(normalized_error, 0) + 1
                curr_error_counts_track_week[normalized_error] = prev_error_counts_track_week.get(
                    normalized_error, get_week(row['ogTimestamp']))

            # Update run_counts with any errors that were not in this row
            for error in prev_error_counts:
                # If the error was not in this row, that run has ended, so add the length to the run counts
                if error not in curr_error_counts:
                    week_of_run = prev_error_counts_track_week[error]
                    length_of_run = prev_error_counts[error]
                    run_counts[week_of_run].append(length_of_run)

            # Update the loop variables
            prev_project_id = row['projectId']
            prev_error_counts = curr_error_counts
            prev_error_counts_track_week = curr_error_counts_track_week
        
        else:
            # Update the loop variables
            prev_project_id = row['projectId']
            prev_error_counts = {}
            prev_error_counts_track_week = {}

    return run_counts

def parse_data_on_long_term():
    # Get the percent of runs that are errors each week for each student for each error message type
    percent_errors_over_time = { 
        'default': { 1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: [] }, 
        'explain': { 1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: [] },
        'messageboard': { 1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: [] },
        'tigerpython': { 1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: [] },
        'superhero': { 1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: [] },
        'gpt': { 1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: [] } }

    # Get the average length of error runs each week for each student for each error message type
    length_error_runs_over_time = {
        'default': { 0: [], 1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: [] }, 
        'explain': { 0: [], 1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: [] },
        'messageboard': { 0: [], 1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: [] },
        'tigerpython': { 0: [], 1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: [] },
        'superhero': { 0: [], 1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: [] },
        'gpt': { 0: [], 1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: [] } }

    for filename in os.listdir(logs_folder):

        # Init and clean the dataframe
        df = pd.read_csv(logs_folder + filename, dtype=str, lineterminator='\n')

        # Get the error message type for this dataframe
        error_message_types = get_error_message_type_for_df(df)
        if len(error_message_types) != 1:
            continue
        error_message_type = error_message_types[0]

        # Get the percent of runs that are errors each week for this user
        errors_over_time_for_user = percent_errors_over_time_for_user(df)

        # Update the percent errors over time for this error message type
        for week in errors_over_time_for_user:
            percent_errors_over_time[error_message_type][week].append(errors_over_time_for_user[week])

        # Get the length error runs over time for this user
        runs_over_time_for_user = length_error_runs_over_time_for_user(df)

        # Update the length error runs over time for this error message type
        for week in range(1, 8):
            if len(runs_over_time_for_user[week]) > 0:
                # If the student had any error runs this week, add the average length of the runs to the list
                length_error_runs_over_time[error_message_type][week].append(np.mean(runs_over_time_for_user[week]))

    return percent_errors_over_time, length_error_runs_over_time



def parse_and_write_data_on_long_term():
    percent_errors_over_time, length_error_runs_over_time = parse_data_on_long_term()

    # Write each of the results to a file
    with open(f'{output_folder}percent_errors_over_time.json', 'w') as f:
        json.dump(percent_errors_over_time, f)

    with open(f'{output_folder}length_error_runs_over_time.json', 'w') as f:
        json.dump(length_error_runs_over_time, f)

if __name__ == '__main__':
    parse_and_write_data_on_long_term()