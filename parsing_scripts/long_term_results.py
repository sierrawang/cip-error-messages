import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import ast
import re
import json
from scipy import stats 
import statsmodels.api as sm

from statsmodels.formula.api import ols
from statsmodels.stats.multicomp import pairwise_tukeyhsd

from matplotlib import rcParams
rcParams['font.family'] = 'Times New Roman'
rcParams['font.size'] = '24'

# NOTE - The error_message column are the typed error messages that were shown to the user
# The error column are the standard error messages output by pyodide

# NOTE - After removing all karel assignments to the best of my ability, there are 56 
# users that still have the line "from karel.stanfordkarel import *" in their code. 
# There are 9260 users in total. For now, I will treat these 56 users as normal, 
# and not remove them from the dataset.

# NOTE - There are 4 users that received error messages that do not have a type. Every single time, the user
# received the error "object is not iterable (cannot read property Symbol(Symbol.iterator))"
# I am not confident that the user ever saw this error because the error_message column is empty.
# I will not perform any special parsing for this case.

# NOTE - For some reason, some of the values in the error column look like weird_error_pattern.
# I think it is because it's somehow being incorrectly logged as a chunk of the error message.
# We can still extract the last line of the standard error message from this.

weird_error_pattern = r"^\(Line \d+\) (.+)\x1b$"

test_folder = "./logs_per_student_720/"

error_message_types = ['default', 'explain', 'messageboard', 'tigerpython', 'superhero', 'gpt']

official_error_types = {
    'default': "Standard",
    'explain': "Long Explanation",
    'messageboard': "Forum",
    'tigerpython': "Simple Explanation",
    'superhero': "GPT - Superhero",
    'gpt': "GPT - Default",
}

abbreviated_error_types = {
    'default': "Std",
    'explain': "L.Ex",
    'messageboard': "Frm",
    'tigerpython': "S.Ex",
    'superhero': "Sup",
    'gpt': "Def",
}

karel_assgnids = [2023, "2023", "checkerboard", "diagnostic3", "diagnostic3soln", "fillkarel", "hospital", "housekarel", "jigsaw", "midpoint", "mountain", "warmup", "steeplechase", "stepup", "stonemason", "spreadbeepers", "rhoomba", "randompainter", "outline", "piles", 
                  "es-karel-midpoint", "es-karel-cone-pile", "es-karel-stripe", "es-karel-collect-newspaper", "es-karel-hospital", "es-karel-stone-mason", "es-karel-mountain", "es-karel-beeper-line", "es-karel-jump-up", "es-karel-hurdle", "es-karel-checkerboard", 
                  "es-karel-step-up", "es-karel-dog-years", "es-karel-place-2023", "es-karel-mystery", "es-karel-invert-beeper-1d", "es-karel-un", "es-karel-random-painting", "es-karel-outline", "es-karel-fill", "es-karel-to-the-wall", "es-project-karel", "es-karel-place-100",
                  "es-karel-big-beeper", "karelflag"] # 'movebeeper',


# colors = ['r', 'darkorange', 'g', 'b', 'indigo', 'violet', 'pink', 'gray', 'black', 'cyan', 'magenta', 'yellow', 'brown', 'olive', 'teal', 'lime', 'aqua', 'navy', 'maroon', 'purple']
colors = ['r', 'darkorange', 'g', 'b', 'indigo', 'violet']

colors_for_error_types = {
    'default': "black",
    'explain': "#8B0000",
    'messageboard': "#FF8C00",
    'tigerpython': "#006400",
    'superhero': "#800080",
    'gpt': "#00008B",
}

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

# Add a column to the dataframe that indicates the type of error message for each row
def add_error_message_type_column(df):
    df['error_message_type'] = df.apply(lambda row: get_row_error_message_type(row), axis=1)
    return df

# Remove all rows with karel assignment ids and all projects of type karel
def remove_karel_rows(df):
    # Remove all rows with karel assignment ids
    df = df[~df['assnId'].isin(karel_assgnids)]

    # Remove all projects of type karel
    df = df[df['type'] != 'karel']
    return df

# Get the error message type that this user used, 
# return None if there are multiple or None
def get_error_message_type_for_df(df):
    # Remove rows where the error message type is None
    df = df[~df['error_message_type'].isnull()]

    # Count the number of distinct error message types
    error_message_types = df['error_message_type'].unique()

    if len(error_message_types) == 1:
        return error_message_types[0]
    else:
        return None

# Get the last line of a standard error
def get_last_line_of_error(str):
    lines = str.strip().split('\n')
    return lines[-1]

# Takes in a standard error, and returns the last line
# If the last line is a weird error, then it will that line cleaned up into a normal last line
def get_clean_last_line(error):
    # Get the last line of the error
    last_line = get_last_line_of_error(error)

    # Use re.match() to find the pattern at the beginning of the string
    match = re.match(weird_error_pattern, last_line)

    # Check if the pattern is found
    if match:
        modified_string = match.group(1)
        return modified_string
    else:
        # If no pattern is found, simply print the original string
        return last_line

def generalize_error_message(error_message):
    # Replace numbers with zeroes
    error_message = re.sub(r'\b\d+\b', '0', error_message)

    # Replace variables inside single quotes with empty quotes
    error_message = re.sub(r"'[^'\s]*'", "''", error_message)

    # Replace variables inside double quotes with empty quotes
    error_message = re.sub(r'"[^"\s]*"', "''", error_message)

    # Replace function functionname with function fn, unless it's function definition
    error_message = re.sub(r'function (?!definition\b)\w+', 'function fn', error_message)

    # Replace any functionname() with fn()
    error_message = re.sub(r'\w+\([^()]*\)', 'fn()', error_message)

    # Replace anything inside parentheses with empty parentheses
    error_message = re.sub(r'\([^()]*\)', '()', error_message)

    # Replace this super common assertion error message with a generic one
    error_message = re.sub(r"^AssertionError: (.*) should be one of the following types: (.*?) in function (.*?)(?: Recieved (.*?))?(?: instead)?.$", 
                           'AssertionError: type should be one of the following types: type in function fn. Recieved type instead.', error_message)

    # Replace this super common ValueError error message with a generic one
    error_message = re.sub(r"^ValueError: invalid literal for fn\(\) with base 0: '.*'$","ValueError: invalid literal for fn() with base 0: literal", error_message)

    return error_message

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

def percent_errors_over_time_for_user(df):
    errors_per_week = { 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6:0, 7: 0 }
    runs_per_week = { 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6:0, 7: 0 }

    # Count the runs and errors per week
    for index, row in df.iterrows():
        week = get_week(row['ogTimestamp'])
        if week:
            error_messages = ast.literal_eval(row['error_message'])
            if len(error_messages) > 0:
                errors_per_week[week] += 1
            runs_per_week[week] += 1

    # Calculate the percent errors per week
    percent_errors_per_week = {}
    for week in range(1, 8):
        if runs_per_week[week] != 0:
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
        # These variables will get updated based on this row
        curr_error_counts = {}
        curr_error_counts_track_week = {}
        curr_project_id = row['projectId']

        # Check if we are on a new project
        if curr_project_id != prev_project_id:
            # Add the previous error run lengths to the run counts
            for error in prev_error_counts:
                week_of_run = prev_error_counts_track_week[error]
                length_of_run = prev_error_counts[error]
                run_counts[week_of_run].append(length_of_run)

            # Reset the current error counts
            prev_error_counts = {}
            prev_error_counts_track_week = {}

        # Update the counts with errors from this row
        uncleaned_errors = ast.literal_eval(row['error'])
        for error in uncleaned_errors:
            # Get a clean and generalized version of the error
            clean_error = get_clean_last_line(error)
            generalized_error = generalize_error_message(clean_error)
    
            # Add this error to the current error counts either with a new count or incrementing the count
            # and track the week this error occured
            curr_error_counts[generalized_error] = prev_error_counts.get(generalized_error, 0) + 1
            curr_error_counts_track_week[generalized_error] = prev_error_counts_track_week.get(
                generalized_error, get_week(row['ogTimestamp']))

        # Update run_counts with any errors that were not in this row
        for error in prev_error_counts:
            # If the error was not in this row, that run has ended, so add the length to the run counts
            if error not in curr_error_counts:
                week_of_run = prev_error_counts_track_week[error]
                length_of_run = prev_error_counts[error]
                run_counts[week_of_run].append(length_of_run)

        # Update the loop variables
        prev_project_id = curr_project_id
        prev_error_counts = curr_error_counts
        prev_error_counts_track_week = curr_error_counts_track_week

    # Add the current error counts to the run counts
    for error in prev_error_counts:
        week_of_run = prev_error_counts_track_week[error]
        length_of_run = prev_error_counts[error]
        run_counts[week_of_run].append(length_of_run)

    return run_counts

def parse_data_on_long_term():
    percent_errors_over_time = { 
        'default': { 1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: [] }, 
        'explain': { 1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: [] },
        'messageboard': { 1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: [] },
        'tigerpython': { 1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: [] },
        'superhero': { 1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: [] },
        'gpt': { 1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: [] } }

    length_error_runs_over_time = {
        'default': { 0: [], 1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: [] }, 
        'explain': { 0: [], 1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: [] },
        'messageboard': { 0: [], 1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: [] },
        'tigerpython': { 0: [], 1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: [] },
        'superhero': { 0: [], 1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: [] },
        'gpt': { 0: [], 1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: [] } }
    
    # Make sure that each error exists in the demo data
    demo_df1 = pd.read_csv('../admission/accept_adults_original.csv')
    demo_df2 = pd.read_csv('../admission/accept_minors.csv')
    demo_df = pd.concat([demo_df1, demo_df2], ignore_index=True)

    for filename in os.listdir(test_folder):
        # Check if the user exists in the demographics data
        user_id = filename.split('.')[0]
        if user_id not in demo_df['uid'].values:
            continue # Skip this user if they don't exist in the demographics data

        # Init and clean the dataframe
        df = pd.read_csv(test_folder + filename)
        df = add_error_message_type_column(df)
        df = remove_karel_rows(df)

        # Get the error message type for this dataframe
        error_message_type = get_error_message_type_for_df(df)

        if error_message_type is None:
            continue

        # Get the percent errors over time for this user
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
    with open('percent_errors_over_time.json', 'w') as f:
        json.dump(percent_errors_over_time, f)

    with open('length_error_runs_over_time.json', 'w') as f:
        json.dump(length_error_runs_over_time, f)


def get_percent_error_averages_per_week(percent_errors_over_time):
    no_error_message_types = { 1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: [] }
    
    # For each error message type
    for error_message_type in percent_errors_over_time:
        # For each week
        for week in range(1, 8):
            # Add the percent errors for this week to the list of percent errors for this week
            no_error_message_types[week].extend(percent_errors_over_time[error_message_type][str(week)])
    
    # Calculate the average percent errors per week
    avgs_per_week = { week: np.mean(no_error_message_types[week]) for week in range(1, 8)}

    return avgs_per_week

def graph_percent_errors_over_time(ax, x_labels):
    # Load the data
    f = open('percent_errors_over_time.json')
    percent_errors_over_time = json.load(f)

    # Get the average percent errors per week
    avgs_per_week = get_percent_error_averages_per_week(percent_errors_over_time)

    for i, error_message_type in enumerate(percent_errors_over_time):
        if not error_message_type in ['default','tigerpython','gpt']:
            continue

        # Map of each week to the rate of errors that week, for this error message type
        results_for_type = percent_errors_over_time[error_message_type]

        # Calculate the average percent errors for this error message type
        avg_percent_errors_for_type = [np.mean(results_for_type[str(week)]) - avgs_per_week[week]
                                       for week in range(2, 7)]
        
        # Calculate the standard error of the percent errors for this error message type
        stderr_percent_errors_for_type = [np.std(results_for_type[str(week)]) / np.sqrt(len(results_for_type[str(week)])) 
                                          for week in range(2, 7)]
        
        # Plot the average percent errors for this error message type
        ax.errorbar(x_labels, avg_percent_errors_for_type, yerr=stderr_percent_errors_for_type, color=colors[i], fmt='o', label=official_error_types[error_message_type])

        # Draw a faint line for each run
        ax.errorbar(x_labels, avg_percent_errors_for_type, color=colors[i], fmt='--', alpha=0.3)      

    ax.set_ylabel('Deviation from Average Error Rate')  
    ax.set_xlabel('Week')  


def get_avg_runs_per_week(length_error_runs_over_time):
    no_error_message_types = { 1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: [] }
    
    # For each error message type
    for error_message_type in length_error_runs_over_time:
        # For each week
        for week in range(1, 8):
            # Add the percent errors for this week to the list of percent errors for this week
            no_error_message_types[week].extend(length_error_runs_over_time[error_message_type][str(week)])
    
    # Calculate the average percent errors per week
    avgs_per_week = { week: np.mean(no_error_message_types[week]) for week in range(1, 8)}

    return avgs_per_week

def graph_length_error_runs_over_time(ax, x_labels):
    # Load the data
    f = open('length_error_runs_over_time.json')
    length_error_runs_over_time = json.load(f)

    # avg_runs_per_week = get_avg_runs_per_week(length_error_runs_over_time)

    for i, error_message_type in enumerate(length_error_runs_over_time):
        if not error_message_type in ['default','tigerpython','gpt']:
            continue

        # Calculate the average length error runs for this error message type
        avg_length_error_runs_for_type = [np.mean(length_error_runs_over_time[error_message_type][str(week)])
                                          for week in range(2, 7)]
        
        # Calculate the standard error of the length error runs for this error message type
        stderr_length_error_runs_for_type = [np.std(length_error_runs_over_time[error_message_type][str(week)]) / 
                                             np.sqrt(len(length_error_runs_over_time[error_message_type][str(week)])) 
                                             for week in range(2, 7)]
        ax.errorbar(x_labels, avg_length_error_runs_for_type, yerr=stderr_length_error_runs_for_type, color=colors[i], fmt='o')        
        ax.errorbar(x_labels, avg_length_error_runs_for_type, color=colors[i], fmt='--', alpha=0.3)   

    ax.set_ylabel('Time to Resolve Errors (# of Runs)')   
    ax.set_xlabel('Week')  
    ax.set_ylim(bottom=1)

# Check if the difference in means between two lists is statistically significant
def independent_t_test(list1, list2):
    # Convert the lists to NumPy arrays
    data1 = np.array(list1)
    data2 = np.array(list2)
    
    # Perform the independent samples t-test
    t_statistic, p_value = stats.ttest_ind(data1, data2)
    
    # Check if the difference in means is statistically significant
    return p_value

def check_statistical_significance_of_percents_per_week():
    # Load the data
    f = open('percent_errors_over_time.json')
    percent_errors_over_time = json.load(f)

    # Get the average percent errors per week
    no_error_message_types = { 1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: [] }
    
    # For each error message type
    for error_message_type in percent_errors_over_time:
        # For each week
        for week in range(1, 8):
            # Add the percent errors for this week to the list of percent errors for this week
            no_error_message_types[week].extend(percent_errors_over_time[error_message_type][str(week)])

    for error_message_type in percent_errors_over_time:
        print(official_error_types[error_message_type])
        for week in range(2, 7):
            # print(error_message_type, week, percent_errors_over_time[error_message_type][str(week)])
            # print('no_error_message_types[week]', no_error_message_types[week])
            p_value = independent_t_test(percent_errors_over_time[error_message_type][str(week)], no_error_message_types[week])
            print('Week ' + str(week) + ': ' + str(p_value))
        print()

def check_statistical_significance_of_length_error_runs_per_week():
    # Load the data
    f = open('length_error_runs_over_time.json')
    length_error_runs_over_time = json.load(f)

    # All of the length error runs for each week
    no_error_message_types = { 1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: [] }
    
    # For each error message type
    for error_message_type in length_error_runs_over_time:
        # For each week
        for week in range(1, 8):
            # Add the percent errors for this week to the list of percent errors for this week
            no_error_message_types[week].extend(length_error_runs_over_time[error_message_type][str(week)])

    for error_message_type in length_error_runs_over_time:
        print(official_error_types[error_message_type])
        for week in range(2, 7):
            p_value = independent_t_test(length_error_runs_over_time[error_message_type][str(week)], no_error_message_types[week])
            print('Week ' + str(week) + ': ' + str(p_value))
        print()

def graph_long_term_results_on_top_of_each_other():
    # Initialize the figure
    fig, ax1 = plt.subplots()

    x_labels = ['Week 2', 'Week 3', 'Week 4', 'Week 5', 'Week 6']

    # Graph the percent errors over time
    graph_percent_errors_over_time(ax1, x_labels)

    ax1.set_xlabel('Week', fontsize=16)
    ax1.set_ylabel('Deviation from Average Error Rate', fontsize=16)
    ax2 = ax1.twinx()

    # graph_length_error_runs_over_time(ax2, x_labels)
    graph_length_error_runs_over_time(ax1, x_labels)

    ax2.set_ylabel("Number of Runs", fontsize=16)
    # ax1.set_ylabel("Number of Runs", fontsize=16)
    fig.legend(loc="upper right", bbox_to_anchor=(1,1), bbox_transform=ax1.transAxes, fontsize=16)
    ax1.tick_params(axis='both', which='major', labelsize=16)
    ax2.tick_params(axis='both', which='major', labelsize=16)

    plt.show()

def graph_long_term_results_side_by_side():
    fig, axes = plt.subplots(nrows=1, ncols=2)

    x_labels = ['2', '3', '4', '5', '6']

    # Graph the percent errors over time
    graph_percent_errors_over_time(axes[0], x_labels)
    graph_length_error_runs_over_time(axes[1], x_labels)

    # Create a single legend with all lines from all subplots
    lines_labels = [ax.get_legend_handles_labels() for ax in fig.axes]
    lines, labels = [sum(lol, []) for lol in zip(*lines_labels)]

    # Create one legend for all subplots on the right side
    # fig.legend(lines, labels, loc = 'center right', fontsize=16)
    plt.legend(lines, labels, bbox_to_anchor=(1.05, 1), loc='upper left')

    axes[0].tick_params(axis='both', which='major', pad=10)
    axes[1].tick_params(axis='both', which='major', pad=10)

    # Display the plot
    plt.subplots_adjust(wspace = 0.3)
    plt.show()

def analyze_runs_until_resolved_using_regression():
    # Load the data
    f = open('length_error_runs_over_time.json')
    length_error_runs_over_time = json.load(f)

    # Make a dataframe with column for the error message type, the number of runs until resolved, and the week number
    data = { 'error_message_type': [], 'length_of_run': [], 'week': [] }
    for error_message_type in length_error_runs_over_time:
        for week in range(2, 7):
            for run in length_error_runs_over_time[error_message_type][str(week)]:
                data['error_message_type'].append(error_message_type)
                data['length_of_run'].append(run)
                data['week'].append(week)

    # Create a dataframe from the data
    df = pd.DataFrame(data)

    for error_message_type in error_message_types:
        subset = df[df['error_message_type'] == error_message_type]

        model = ols('length_of_run ~ week', data=subset).fit()

        anova_table = sm.stats.anova_lm(model, typ=2)

        print(f"\nFor error message type: {official_error_types[error_message_type]}, ANOVA results are:")
        print(anova_table)

        tukey = pairwise_tukeyhsd(endog=subset['length_of_run'],
                                    groups=subset['week'],
                                    alpha=0.05)

        print(f"\nPairwise Tukey HSD results for error_message_type: {official_error_types[error_message_type]} are:")
        print(tukey)

        # Get the data for this error message type
        # df_this_error_message_type = df[df['error_message_type'] == error_message_type]

        # # Specify the dependent variable and independent variable(s)
        # Y = df_this_error_message_type['length_of_run']
        # X = df_this_error_message_type[['constant', 'week']]

        # # Run the model
        # model = sm.OLS(Y, X)
        # results = model.fit()

        # # Print out the statistics
        # print(official_error_types[error_message_type])
        # print(results.summary())
        # print()


def analyze_percents_per_week():
    # Load the data
    f = open('percent_errors_over_time.json')
    percent_errors_over_time = json.load(f)

    print("Checking statistical significance for percents per week:")
    for week in range(2, 7):
        wk_str = str(week)
        print("Week " + wk_str)
        for i in range(len(error_message_types)):
            for j in range(i+1, len(error_message_types)):
                mean_i = round(np.mean(percent_errors_over_time[error_message_types[i]][wk_str]), 3)
                mean_j = round(np.mean(percent_errors_over_time[error_message_types[j]][wk_str]), 3)
                
                p_value = independent_t_test(percent_errors_over_time[error_message_types[i]][wk_str], percent_errors_over_time[error_message_types[j]][wk_str])
                p_value = round(p_value, 3)

                if p_value < 0.05:
                    # print("Statistically significant difference between " + error_message_types[i] + " and " + error_message_types[j])
                    print('TRUE', mean_i, mean_j, '\t\t', official_error_types[error_message_types[i]], official_error_types[error_message_types[j]],  '\t\t', p_value)
                # else:
                #     # print("No statistically significant difference between " + error_message_types[i] + " and " + error_message_types[j])
                #     print('FALSE', mean_i, mean_j, '\t\t', official_error_types[error_message_types[i]], official_error_types[error_message_types[j]], '\t\t', p_value)

        print()



# parse_and_write_data_on_long_term()
# check_statistical_significance_of_percents_per_week()
# check_statistical_significance_of_length_error_runs_per_week()
# analyze_percents_per_week()
# analyze_percents_per_week_using_regression()
# analyze_runs_until_resolved_using_regression()
graph_long_term_results_side_by_side()