import json
import numpy as np
import pandas as pd
from statsmodels.formula.api import ols
import statsmodels.api as sm
from statsmodels.stats.multicomp import pairwise_tukeyhsd
from scipy import stats
from error_message_types import official_error_types

data_folder = '../data_files/long_term_data/'

error_message_types = ['default', 'explain', 'messageboard', 'tigerpython', 'superhero', 'gpt']

# Check if the difference in means between two lists is statistically significant
def independent_t_test(list1, list2):
    # Convert the lists to NumPy arrays
    data1 = np.array(list1)
    data2 = np.array(list2)
    
    # Perform the independent samples t-test
    t_statistic, p_value = stats.ttest_ind(data1, data2)
    
    # Check if the difference in means is statistically significant
    return p_value

# For each week, compare the error rate of each error message type to the overall average error rate
def check_statistical_significance_of_percents_per_week():
    # Load the data
    f = open(f'{data_folder}percent_errors_over_time.json')
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
            if p_value < 0.05:
                print('Week ' + str(week) + ': ' + str(p_value))
        print()

def check_statistical_significance_of_length_error_runs_per_week():
    # Load the data
    f = open(f'{data_folder}length_error_runs_over_time.json')
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

def analyze_runs_until_resolved_using_regression():
    # Load the data
    f = open(f'{data_folder}length_error_runs_over_time.json')
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

    for error_message_type in official_error_types:
        subset = df[df['error_message_type'] == error_message_type]

        model = ols('length_of_run ~ C(week)', data=subset).fit()

        anova_table = sm.stats.anova_lm(model, typ=2)

        print(f"\nFor error message type: {official_error_types[error_message_type]}, ANOVA results are:")
        print(anova_table)

        tukey = pairwise_tukeyhsd(endog=subset['length_of_run'],
                                    groups=subset['week'],
                                    alpha=0.05)

        print(f"\nPairwise Tukey HSD results for error_message_type: {official_error_types[error_message_type]} are:")
        print(tukey)

# For each week, compare the error rate for every combination of error message types
def analyze_percents_per_week():
    # Load the data
    f = open(f'{data_folder}percent_errors_over_time.json')
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
                    print('TRUE', mean_i, mean_j, '\t\t', official_error_types[error_message_types[i]], official_error_types[error_message_types[j]],  '\t\t', p_value)
        print()

if __name__ == '__main__':
    # Check if there is a difference in rate of error messages between the different types, each week
    analyze_percents_per_week()

    # check_statistical_significance_of_percents_per_week()
    # check_statistical_significance_of_length_error_runs_per_week()
    analyze_runs_until_resolved_using_regression()