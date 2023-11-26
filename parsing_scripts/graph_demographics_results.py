import matplotlib.pyplot as plt
import pandas as pd
from error_message_types import official_error_types
import numpy as np

from matplotlib import rcParams
rcParams['font.family'] = 'Times New Roman'
rcParams['font.size'] = '24'

error_message_types = ['default', 'explain', 'messageboard', 'tigerpython', 'superhero', 'gpt']
colors = ['r', 'darkorange', 'g', 'b', 'indigo', 'violet']

data_file = '../data_files/sl_and_student_data.csv'

def graph_hdi_vs_error_message_type(ax):
    # Only include students who only used one error message type
    data_df = pd.read_csv(data_file)
    df = data_df[(data_df['error_message_type'] != 'other') & (data_df['avg_error_run_length'] != 'None') & (data_df['hdi'] != 'None')]

    # Assuming that your DataFrame is df
    bins = [0, 0.54999, 0.69999, 0.79999, 1]
    df['hdi_bin'] = pd.cut(df['hdi'], bins)

    grouped_df = df.groupby(['error_message_type', 'hdi_bin'])

    bin_means = grouped_df['avg_error_run_length'].mean()
    bin_errors = grouped_df['avg_error_run_length'].sem()

    labels = ['Low', 'Medium', 'High', 'Very High']

    for i, error_message_type in enumerate(error_message_types):
        ax.errorbar(labels, 
                    bin_means[error_message_type], 
                    yerr=bin_errors[error_message_type], 
                    color=colors[i], 
                    fmt='--', 
                    alpha=0.3)
        ax.errorbar(labels, 
                    bin_means[error_message_type], 
                    yerr=bin_errors[error_message_type], 
                    color=colors[i], 
                    fmt='o', 
                    label=official_error_types[error_message_type])

    
    ax.set_xlabel('Human Development Index (HDI)', labelpad=20)
    ax.set_ylabel('Time to Resolve Errors (# of Runs)', labelpad=20)
    ax.set_ylim(bottom=1, top=3.5)

def graph_gender_vs_error_message_type(ax):
    # Only include students who only used one error message type
    data_df = pd.read_csv(data_file)
    df = data_df[(data_df['error_message_type'] != 'other') & (data_df['avg_error_run_length'] != 'None')]

    genders = ['Male', 'Female', 'Other']

    # For each unique error_message_type 
    for i, error_message_type in enumerate(error_message_types):
        # Subset the DataFrame
        df_for_type = df[df['error_message_type'] == error_message_type]

        # Manually compute the mean and the standard error of the mean for each gender
        averages = []
        errors = []

        male_results = df_for_type[df_for_type['gender'] == 'male']['avg_error_run_length']
        averages.append(np.mean(male_results))
        errors.append(np.std(male_results)/np.sqrt(len(male_results)))

        female_results = df_for_type[df_for_type['gender'] == 'female']['avg_error_run_length']
        averages.append(np.mean(female_results))
        errors.append(np.std(female_results)/np.sqrt(len(female_results)))

        other_results = df_for_type[df_for_type['gender'] == 'other']['avg_error_run_length']
        averages.append(np.mean(other_results))
        errors.append(np.std(other_results)/np.sqrt(len(other_results)))

        ax.errorbar(genders, averages, color=colors[i], fmt='--', alpha=0.3)
        ax.errorbar(genders, averages, yerr=errors, color=colors[i], fmt='o')

    # Set the labels for x and y axis
    ax.set_xlabel('Gender', labelpad=20)
    # ax.set_ylabel('Number of Runs', fontsize=16)
    ax.set_ylim(bottom=1, top=3.5)

def graph_experience_vs_error_message_type(ax):
    # Only include students who only used one error message type
    data_df = pd.read_csv(data_file)
    df = data_df[(data_df['error_message_type'] != 'other') & (data_df['avg_error_run_length'] != 'None') & (data_df['experience'] != 'None')]

    # Multiply all values in 'experience' column by -1 because 
    # -18 is the most experienced and 0 is the least experienced
    df['experience'] = df['experience'] * -1

    # Assuming your 'experience' is a continuous variable, we will create buckets using pandas "cut"
    experience_labels = ["Least", " ", "  ", "   ", "Most"]
    df["experience_bucket"] = pd.cut(df['experience'], bins=5)

    # Group by 'experience_bucket' and 'error_message_type' then calculate mean and standard deviation.
    grouped_df = df.groupby(['error_message_type', 'experience_bucket'])

    # print the description of the grouped DataFrame
    print(grouped_df.describe())

    bin_means = grouped_df['avg_error_run_length'].mean()
    bin_errors = grouped_df['avg_error_run_length'].sem()

    for i, error_message_type in enumerate(error_message_types):
        ax.errorbar(experience_labels, 
                    bin_means[error_message_type], 
                    yerr=bin_errors[error_message_type], 
                    color=colors[i], 
                    fmt='--', 
                    alpha=0.3)
        ax.errorbar(experience_labels, 
                    bin_means[error_message_type], 
                    yerr=bin_errors[error_message_type], 
                    color=colors[i], 
                    fmt='o')

    ax.set_xlabel('Programming Experience', labelpad=20)
    ax.set_ylim(bottom=1, top=3.5)

def graph_demo_results_side_by_side():
    fig, axes = plt.subplots(nrows=1, ncols=3, figsize=(20, 5))

    # Graph the percent errors over time
    graph_hdi_vs_error_message_type(axes[0])
    graph_gender_vs_error_message_type(axes[1])
    graph_experience_vs_error_message_type(axes[2])

    # Create a single legend with all lines from all subplots
    lines_labels = [ax.get_legend_handles_labels() for ax in fig.axes]
    lines, labels = [sum(lol, []) for lol in zip(*lines_labels)]

    # Create one legend for all subplots on the right side
    # fig.legend(lines, labels, loc = 'center right', fontsize=16)
    plt.legend(lines, labels, bbox_to_anchor=(1.05, 1), loc='upper left')

    axes[0].tick_params(axis='both', which='major', pad=10)
    axes[1].tick_params(axis='both', which='major', pad=10)
    axes[2].tick_params(axis='both', which='major', pad=10)

    # Display the plot
    plt.subplots_adjust(wspace = 0.3)
    plt.show()

if __name__ == "__main__":
    graph_demo_results_side_by_side()
 