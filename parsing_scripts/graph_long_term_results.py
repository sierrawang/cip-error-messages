import matplotlib.pyplot as plt
import numpy as np
import json
from error_message_types import official_error_types

from matplotlib import rcParams
rcParams['font.family'] = 'Times New Roman'
rcParams['font.size'] = '24'

data_folder = '../data_files/long_term_data/'

colors = ['r', 'darkorange', 'g', 'b', 'indigo', 'violet']

# Return a dictionary of the average rate of error per week, independent of error message type
def get_percent_error_averages_per_week(percent_errors_over_time):
    total = { 1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: [] }
    
    # For each error message type
    for error_message_type in percent_errors_over_time:
        # For each week
        for week in range(1, 8):
            # Add the percent errors for this week to the list of percent errors for this week
            total[week].extend(percent_errors_over_time[error_message_type][f'{week}'])
    
    # Calculate the average percent errors per week
    avgs_per_week = { week: np.mean(total[week]) for week in range(1, 8)}

    return avgs_per_week

def graph_percent_errors_over_time(ax, x_labels):
    # Load the data
    f = open(f'{data_folder}percent_errors_over_time.json')
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

def graph_length_error_runs_over_time(ax, x_labels):
    # Load the data
    f = open(f'{data_folder}length_error_runs_over_time.json')
    length_error_runs_over_time = json.load(f)

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

if __name__ == '__main__':
    graph_long_term_results_side_by_side()