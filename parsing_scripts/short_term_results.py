import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import ast
import re
import json
from scipy import stats

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
error_message_types2 = ['default', 'explain', 'messageboard', 'tigerpython', 'gpt', 'superhero']

official_error_types = {
    'default': "Standard",
    'explain': "Long\nExplanation",
    'messageboard': "Forum",
    'tigerpython': "Simple\nExplanation",
    'superhero': "GPT -\nSuperhero",
    'gpt': "GPT -\nDefault",
}

karel_assgnids = [2023, "2023", "checkerboard", "diagnostic3", "diagnostic3soln", "fillkarel", "hospital", "housekarel", "jigsaw", "midpoint", "mountain", "warmup", "steeplechase", "stepup", "stonemason", "spreadbeepers", "rhoomba", "randompainter", "outline", "piles", 
                  "es-karel-midpoint", "es-karel-cone-pile", "es-karel-stripe", "es-karel-collect-newspaper", "es-karel-hospital", "es-karel-stone-mason", "es-karel-mountain", "es-karel-beeper-line", "es-karel-jump-up", "es-karel-hurdle", "es-karel-checkerboard", 
                  "es-karel-step-up", "es-karel-dog-years", "es-karel-place-2023", "es-karel-mystery", "es-karel-invert-beeper-1d", "es-karel-un", "es-karel-random-painting", "es-karel-outline", "es-karel-fill", "es-karel-to-the-wall", "es-project-karel", "es-karel-place-100",
                  "es-karel-big-beeper", "karelflag"] # 'movebeeper',

hotpink = '#fa166e'
pink = '#ff75aa'
brightgreen = '#0f6e07'
lightgreen = '#54a14d'
colors = [hotpink, pink, brightgreen, lightgreen]

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

# Return a count of the number of times the user got the same error 
# message in subsequent runs, and the total number of times they got an error
def get_count_same_subsequent_error(df): 
    # The total number of errors that the user got
    total_error_count = 0

    # The number of times the user got the same error in the subsequent run
    same_error_count = 0

    prev_error = []
    prev_project_id = None
    for i, row in df.iterrows():
        curr_project_id = row['projectId']
        curr_error = []

        # Loop through the errors for this row
        uncleaned_errors = ast.literal_eval(row['error'])
        for error in uncleaned_errors:
            # Get a clean and generalized version of the error
            clean_error = get_clean_last_line(error)
            generalized_error = generalize_error_message(clean_error)

            # If this is the same project, and the error is the same as the previous error,
            # then increment the same error count
            if curr_project_id == prev_project_id and generalized_error in prev_error:
                same_error_count += 1

            # Update the current errors list
            curr_error.append(generalized_error)

            # Increment the total error count
            total_error_count += 1
            
        # Update the previous project id and error
        prev_project_id = curr_project_id
        prev_error = curr_error

    return same_error_count, total_error_count

# Return a list of counts of the number of runs it took to resolve each error
def get_runs_until_resolved(df):
    run_counts = []

    prev_error_counts = {}
    prev_project_id = None
    for i, row in df.iterrows():
        curr_error_counts = {}
        curr_project_id = row['projectId']

        # Check if we are on a new project
        if curr_project_id != prev_project_id:
            # Add the previous error counts to the run counts
            # Actually don't do this because we don't want to count it as resolved if the user just gave up
            # run_counts.extend(prev_error_counts.values()) 

            # Reset the current error counts
            prev_error_counts = {}

        # Update the counts with errors from this row
        uncleaned_errors = ast.literal_eval(row['error'])
        for error in uncleaned_errors:
            # Get a clean and generalized version of the error
            clean_error = get_clean_last_line(error)
            generalized_error = generalize_error_message(clean_error)
            curr_error_counts[generalized_error] = prev_error_counts.get(generalized_error, 0) + 1

        # Update run_counts with any errors that were not in this row
        for error in prev_error_counts:
            if error not in curr_error_counts:
                # Add the error count to the run counts
                run_counts.append(prev_error_counts[error])

        # Update the loop variables
        prev_project_id = curr_project_id
        prev_error_counts = curr_error_counts

    # Add the current error counts to the run counts
    run_counts.extend(curr_error_counts.values())

    return run_counts

def parse_data_on_short_term():
    same_subsequent_error_per_user_results = { 'default': [], 'explain': [], 'messageboard': [], 'tigerpython': [], 'superhero': [], 'gpt': [] }
    runs_until_resolved_per_user_results = { 'default': [], 'explain': [], 'messageboard': [], 'tigerpython': [], 'superhero': [], 'gpt': [] }

    same_subsequent_error_count_same = { 'default': 0, 'explain': 0, 'messageboard': 0, 'tigerpython': 0, 'superhero': 0, 'gpt': 0 }
    same_subsequent_error_count_total = { 'default': 0, 'explain': 0, 'messageboard': 0, 'tigerpython': 0, 'superhero': 0, 'gpt': 0 }

    runs_until_resolved_counts = { 'default': [], 'explain': [], 'messageboard': [], 'tigerpython': [], 'superhero': [], 'gpt': [] }

    # Make sure that each error exists in the demo data
    demo_df = pd.read_csv('../data_files/sl_and_student_data.csv')

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

        # Sort the dataframe by project id, and then by timestamp
        df = df.sort_values(by=['projectId', 'ogTimestamp'])

        # NOTE At this point, we have eliminated all known karel assignments,
        # and all projects of type karel, and we know that this user 
        # only used one error message type.
        same_subsequent_error_count, total_error_count = get_count_same_subsequent_error(df)

        # Append the percent of runs that the user got the same error message in subsequent runs
        same_subsequent_error_per_user_results[error_message_type].append(same_subsequent_error_count/total_error_count)

        # Add to the total count of same subsequent errors and total errors
        same_subsequent_error_count_same[error_message_type] += same_subsequent_error_count
        same_subsequent_error_count_total[error_message_type] += total_error_count

        # Get the runs until resolved for this user
        runs_until_resolved = get_runs_until_resolved(df)

        # Append the average runs until resolved to the list of runs until resolved for this error message type
        if len(runs_until_resolved) > 0:
            runs_until_resolved_per_user_results[error_message_type].append(np.mean(runs_until_resolved))

        # Append the runs until resolved to the list of runs until resolved for this error message type
        runs_until_resolved_counts[error_message_type].extend(runs_until_resolved)

    return same_subsequent_error_per_user_results, runs_until_resolved_per_user_results, same_subsequent_error_count_same, same_subsequent_error_count_total, runs_until_resolved_counts

def parse_and_write_data_on_short_term():
    (same_subsequent_error_per_user_results, 
        runs_until_resolved_per_user_results, 
        same_subsequent_error_count_same, 
        same_subsequent_error_count_total, 
        runs_until_resolved_counts) = parse_data_on_short_term()
    
    # Write each of the results to a file
    with open('same_subsequent_error_per_user_results.json', 'w') as f:
        json.dump(same_subsequent_error_per_user_results, f)

    with open('runs_until_resolved_per_user_results.json', 'w') as f:
        json.dump(runs_until_resolved_per_user_results, f)

    with open('same_subsequent_error_count_same.json', 'w') as f:
        json.dump(same_subsequent_error_count_same, f)

    with open('same_subsequent_error_count_total.json', 'w') as f:
        json.dump(same_subsequent_error_count_total, f)

    with open('runs_until_resolved_counts.json', 'w') as f:
        json.dump(runs_until_resolved_counts, f)

def graph_percent_same_error_per_user(ax, x_labels, color):
    f = open('same_subsequent_error_per_user_results.json', 'r')
    same_subsequent_error_per_user_results = json.load(f)

    avg_percent_same_error = [100 * np.mean(same_subsequent_error_per_user_results[type]) for type in error_message_types2]
    print(avg_percent_same_error)
    stderr_avg_percent_same_error = [100 * np.std(same_subsequent_error_per_user_results[type])/
                                                        np.sqrt(len(same_subsequent_error_per_user_results[type])) for type in error_message_types2]
    # ax.errorbar(x_labels, avg_percent_same_error, color=colors[0], fmt='--', alpha=0.3)
    ax.errorbar(x_labels, avg_percent_same_error, yerr=stderr_avg_percent_same_error, color=color, fmt='o', label="Avg. Rate of Repeated Errors")

def graph_percent_same_error_overall(ax, x_labels, color):
    f = open('same_subsequent_error_count_same.json', 'r')
    same_subsequent_error_count_same = json.load(f)
    f =  open('same_subsequent_error_count_total.json', 'r')
    same_subsequent_error_count_total = json.load(f)
    percent_same_error = [100 * same_subsequent_error_count_same[type]/same_subsequent_error_count_total[type] for type in error_message_types]
    stderr_percent_same_error = [np.sqrt((percent_same_error[i]/100)*(1-(percent_same_error[i]/100))/same_subsequent_error_count_total[type]) for i,type in enumerate(error_message_types)]
    ax.errorbar(x_labels, percent_same_error, color=colors[1], fmt='--', alpha=0.3)
    ax.errorbar(x_labels, percent_same_error, yerr=stderr_percent_same_error, color=color, fmt='o', label="Percent same error")

def graph_avg_runs_until_resolved_per_user(ax, x_labels, color):
    f = open('runs_until_resolved_per_user_results.json', 'r')
    runs_until_resolved_per_user_results = json.load(f)
    avg_runs_until_resolved = [np.mean(runs_until_resolved_per_user_results[type]) for type in error_message_types2]
    print(avg_runs_until_resolved)
    stderr_runs_until_resolved = [np.std(runs_until_resolved_per_user_results[type])/
                                                        np.sqrt(len(runs_until_resolved_per_user_results[type])) for type in error_message_types2]

    # ax.errorbar(x_labels, avg_runs_until_resolved, color=colors[2], fmt='--', alpha=0.3)
    ax.errorbar(x_labels, avg_runs_until_resolved, yerr=stderr_runs_until_resolved, color=color, fmt='o', label="Avg. Time to Resolve Errors")
    # ax.set_ylim(bottom=1)

def graph_avg_runs_until_resolved(ax, x_labels, color):
    f = open('runs_until_resolved_counts.json', 'r')
    runs_until_resolved_counts = json.load(f)
    avg_runs_until_resolved = [np.mean(runs_until_resolved_counts[type]) for type in error_message_types]
    stderr_runs_until_resolved = [np.std(runs_until_resolved_counts[type])/np.sqrt(len(runs_until_resolved_counts[type])) for type in error_message_types]
    ax.errorbar(x_labels, avg_runs_until_resolved, color=colors[3], fmt='--', alpha=0.3)
    ax.errorbar(x_labels, avg_runs_until_resolved, yerr=stderr_runs_until_resolved, color=color, fmt='o', label="Runs until resolved")

# Check if the difference in means between two lists is statistically significant
def independent_t_test(list1, list2):
    # Convert the lists to NumPy arrays
    data1 = np.array(list1)
    data2 = np.array(list2)
    
    # Perform the independent samples t-test
    t_statistic, p_value = stats.ttest_ind(data1, data2)
    
    # Check if the difference in means is statistically significant
    return p_value

def check_statistical_significance_of_percentages():
    f = open('same_subsequent_error_per_user_results.json', 'r')
    same_subsequent_error_per_user_results = json.load(f)

    print("Checking statistical significance of percent repeat error")
    for i in range(len(error_message_types)):
        for j in range(i+1, len(error_message_types)):
            p_value = independent_t_test(same_subsequent_error_per_user_results[error_message_types[i]], same_subsequent_error_per_user_results[error_message_types[j]])
            if p_value < 0.05:
                print("Statistically significant difference between " + error_message_types[i] + " and " + error_message_types[j])
            else:
                print("No statistically significant difference between " + error_message_types[i] + " and " + error_message_types[j])

def check_statistical_significance_of_runs_until_resolved():
    f = open('runs_until_resolved_per_user_results.json', 'r')
    runs_until_resolved_per_user_results = json.load(f)
    
    print("Checking statistical significance for runs until resolved:")
    for i in range(len(error_message_types)):
        for j in range(i+1, len(error_message_types)):
            p_value = independent_t_test(runs_until_resolved_per_user_results[error_message_types[i]], runs_until_resolved_per_user_results[error_message_types[j]])
            if p_value < 0.05:
                print("Statistically significant difference between " + error_message_types[i] + " and " + error_message_types[j])
            else:
                print("No statistically significant difference between " + error_message_types[i] + " and " + error_message_types[j])


def graph_short_term_results():
    # Initialize the figure
    fig, ax1 = plt.subplots()

    # x axis is the error message types
    official_types = [official_error_types[type] for type in error_message_types2]
    # wrapped_labels = ['\n'.join(textwrap.wrap(label, width=10)) for label in official_types]

    graph_percent_same_error_per_user(ax1, official_types, hotpink)
    # graph_percent_same_error_overall(ax1, official_types, pink)

    ax1.set_xticklabels(official_types, rotation=0, horizontalalignment='center')
    ax1.set_xlabel("Error Message Type", labelpad=20)
    ax1.set_ylabel("Rate of Repeated Errors (% of Errors)", labelpad=20)
    ax2 = ax1.twinx()

    graph_avg_runs_until_resolved_per_user(ax2, official_types, brightgreen)
    # graph_avg_runs_until_resolved(ax2, official_types, lightgreen)

    ax2.set_ylabel("Time to Resolve Errors (# of Runs)", labelpad=20)
    fig.legend(loc="upper right", bbox_to_anchor=(1,1), bbox_transform=ax1.transAxes)
    ax1.tick_params(axis='both', which='major')
    
    ax2.tick_params(axis='both', which='major')

    plt.show()

# parse_and_write_data_on_short_term()
# check_statistical_significance_of_percentages()
# print()
# check_statistical_significance_of_runs_until_resolved()
graph_short_term_results()