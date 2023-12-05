import numpy as np
import json
from scipy import stats

data_folder = "../data_files/short_term_data/"

error_message_types = ['default', 'explain', 'messageboard', 'tigerpython', 'superhero', 'gpt']

def compare(baseline, test):
    res = (baseline - test) / baseline
    res = res * 100
    return res

# Print out the percent of runs that users repeat their error for each error message type
def print_percent_same_error():
    f = open(f'{data_folder}percent_same_subsequent_error.json', 'r')
    same_subsequent_error_per_user_results = json.load(f)

    for error_message_type in error_message_types:
        print(f"Average percent same subsequent error for {error_message_type}: {np.mean(same_subsequent_error_per_user_results[error_message_type])}")

    print("Comparing Standard vs GPT-Default", compare(np.mean(same_subsequent_error_per_user_results['default']), np.mean(same_subsequent_error_per_user_results['gpt'])))
    print("Comparing Long Explnation vs GPT-Default", compare(np.mean(same_subsequent_error_per_user_results['explain']), np.mean(same_subsequent_error_per_user_results['gpt'])))

def print_average_runs_until_resolved():
    f = open(f'{data_folder}average_runs_until_resolved.json', 'r')
    runs_until_resolved_per_user_results = json.load(f)

    for error_message_type in error_message_types:
        print(f"Average runs until resolved for {error_message_type}: {np.mean(runs_until_resolved_per_user_results[error_message_type])}")

    print("Comparing Standard vs GPT-Superhero", compare(np.mean(runs_until_resolved_per_user_results['default']) - 1, np.mean(runs_until_resolved_per_user_results['superhero']) - 1))
    print("Comparing Long Explanation vs GPT-Superhero", compare(np.mean(runs_until_resolved_per_user_results['explain']) - 1, np.mean(runs_until_resolved_per_user_results['superhero']) - 1))


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
    f = open(f'{data_folder}percent_same_subsequent_error.json', 'r')
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
    f = open(f'{data_folder}average_runs_until_resolved.json', 'r')
    runs_until_resolved_per_user_results = json.load(f)

    print("Checking statistical significance for runs until resolved:")
    for i in range(len(error_message_types)):
        for j in range(i+1, len(error_message_types)):
            p_value = independent_t_test(runs_until_resolved_per_user_results[error_message_types[i]], runs_until_resolved_per_user_results[error_message_types[j]])
            if p_value < 0.05:
                print("Statistically significant difference between " + error_message_types[i] + " and " + error_message_types[j])
            else:
                print("No statistically significant difference between " + error_message_types[i] + " and " + error_message_types[j])

if __name__ == '__main__':
    print_percent_same_error()
    print_average_runs_until_resolved()
    # check_statistical_significance_of_percentages()
    # print()
    # check_statistical_significance_of_runs_until_resolved()