import numpy as np
import matplotlib.pyplot as plt
import json
from scipy import stats

from matplotlib import rcParams
rcParams['font.family'] = 'Times New Roman'
rcParams['font.size'] = '24'

# NOTE - The error_message column are the typed error messages that were shown to the user
# The error column are the standard error messages output by pyodide

test_folder = "../data_files/student_logs/"

data_folder = "../data_files/short_term_data/"

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

hotpink = '#fa166e'
pink = '#ff75aa'
brightgreen = '#0f6e07'
lightgreen = '#54a14d'
colors = [hotpink, pink, brightgreen, lightgreen]

def graph_percent_same_error_per_user(ax, color):
    f = open(f'{data_folder}percent_same_subsequent_error.json', 'r')
    percent_same_subsequent_error = json.load(f)

    x = []
    y = []
    stderr = []
    for i, error_message_type in enumerate(error_message_types2):
        percentages = [100 * percent for percent in percent_same_subsequent_error[error_message_type]]

        x.append(official_error_types[error_message_type])
        y.append(np.mean(percentages)) # The average of all users
        stderr.append(np.std(percentages)/np.sqrt(len(percentages)))

    ax.errorbar(x, y, yerr=stderr, color=color, fmt='o', label="Avg. Rate of Repeated Errors")

def graph_avg_runs_until_resolved_per_user(ax, color):
    f = open(f'{data_folder}average_runs_until_resolved.json', 'r')
    runs_until_resolved_per_user_results = json.load(f)

    x = []
    y = []
    stderr = []
    for i, error_message_type in enumerate(error_message_types2):
        x.append(official_error_types[error_message_type])
        y.append(np.mean(runs_until_resolved_per_user_results[error_message_type]))
        stderr.append(np.std(runs_until_resolved_per_user_results[error_message_type])/np.sqrt(len(runs_until_resolved_per_user_results[error_message_type])))

    ax.errorbar(x, y, yerr=stderr, color=color, fmt='o', label="Avg. Runs until Resolved")

def graph_short_term_results():
    # Initialize the figure
    fig, ax1 = plt.subplots()

    # x axis is the error message types
    official_types = [official_error_types[type] for type in error_message_types2]

    graph_percent_same_error_per_user(ax1, hotpink)

    ax1.set_xticklabels(official_types, rotation=0, horizontalalignment='center')
    ax1.set_xlabel("Error Message Type", labelpad=20)
    ax1.set_ylabel("Rate of Repeated Errors (% of Errors)", labelpad=20)
    ax2 = ax1.twinx()

    graph_avg_runs_until_resolved_per_user(ax2, brightgreen)

    ax2.set_ylabel("Time to Resolve Errors (# of Runs)", labelpad=20)
    fig.legend(loc="upper right", bbox_to_anchor=(1,1), bbox_transform=ax1.transAxes)
    ax1.tick_params(axis='both', which='major')
    
    ax2.tick_params(axis='both', which='major')

    plt.show()

if __name__ == '__main__':
    graph_short_term_results()