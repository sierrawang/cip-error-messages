import pandas as pd
import ast
import re
import matplotlib.pyplot as plt
import numpy as np
import statsmodels.api as sm
from statsmodels.formula.api import ols
from statsmodels.stats.multicomp import pairwise_tukeyhsd

from matplotlib import rcParams
rcParams['font.family'] = 'Times New Roman'
rcParams['font.size'] = '24'

weird_error_pattern = r"^\(Line \d+\) (.+)\x1b$"

colors = ['r', 'darkorange', 'g', 'b', 'indigo', 'violet']


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

def eliminate_formatting_on_error_message(error_message):
    assert 'gpt' in error_message or 'superhero' in error_message
    error_message = error_message.replace('gpt: ', '')
    error_message = error_message.replace('superhero: ', '')
    error_message = error_message.replace('\x1b[33m\x1b[1m\x1b[4:1m', '')
    error_message = error_message.replace('\x1b[0m\x1b[0m\x1b[0m\r\n\x1b[33m', '\n')
    error_message = error_message.replace('\x1b[0m', '\n')
    return error_message

# Use this to generate HDIvsShortTerm
def hdi_vs_error_message_type():
    df = pd.read_csv('demographics_with_hdi.csv')

    # Assuming that your DataFrame is df
    bins = [0, 0.54999, 0.69999, 0.79999, 1]
    df['hdi_bin'] = pd.cut(df['hdi'], bins)

    grouped_df = df.groupby(['error_message_type', 'hdi_bin'])

    # Output the number of people in each group
    print(grouped_df.size())
    print(grouped_df['avg_error_run_length'].describe())

    bin_means = grouped_df['avg_error_run_length'].mean()
    bin_errors = grouped_df['avg_error_run_length'].sem()

    fig, ax = plt.subplots()
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

    plt.xlabel('Human Development Index (HDI)', fontsize=16)
    plt.ylabel('Number of Runs', fontsize=16)
    plt.legend(loc="upper right", bbox_to_anchor=(1,1), bbox_transform=ax.transAxes, fontsize=16)
    plt.tick_params(axis='both', which='major', labelsize=16)
    plt.show()

# Analyze the HDI vs error message type using regressions
def analyze_hdi_vs_error_message_type_using_regression():
    df = pd.read_csv('demographics_with_hdi.csv')

    # Assuming your DataFrame is df
    bins = [0, 0.54999, 0.69999, 0.79999, 1]
    df['hdi_bin'] = pd.cut(df['hdi'], bins)

    # loop over error_message_type
    for eroor_message_type in error_message_types:
        
        #subset data
        subset = df[df['error_message_type'] == eroor_message_type]

        #perform anova
        model = ols('avg_error_run_length ~ C(hdi_bin)', data=subset).fit()
        anova_table = sm.stats.anova_lm(model, typ=2)

        print(f"\nFor error message type: {official_error_types[eroor_message_type]}, ANOVA results are:")
        print(anova_table)

def analyze_hdi_vs_error_message_type_using_tukey():
    df = pd.read_csv('demographics_with_hdi.csv')

    # Assuming your DataFrame is df
    bins = [0, 0.54999, 0.69999, 0.79999, 1]
    df['hdi_bin'] = pd.cut(df['hdi'], bins)

    # Remove rows without an error_message_type
    df = df[df['error_message_type'].notna()]

    # loop over hdi bins
    for hdi_bin in df['hdi_bin'].unique():        
        # subset data
        subset = df[df['hdi_bin'] == hdi_bin]

        # perform anova
        model = ols('avg_error_run_length ~ C(error_message_type)', data=subset).fit()
        anova_table = sm.stats.anova_lm(model, typ=2)

        print(f"\nFor hdi bin: {hdi_bin}, ANOVA results are:")
        print(anova_table)
        
        # perform pairwise comparison
        tukey = pairwise_tukeyhsd(endog=subset['avg_error_run_length'],
                                  groups=subset['error_message_type'],
                                  alpha=0.05)
        print(f"\nPairwise Tukey HSD results for hdi bin: {hdi_bin} are:")
        print(tukey)

def gender_vs_error_message_type():
    # Load your DataFrame
    df = pd.read_csv('demographics_with_error_data.csv')

    genders = ['Male', 'Female', 'Other']

    # Create a figure and a set of subplots
    fig, ax = plt.subplots()

    # For each unique error_message_type 
    for i, error_message_type in enumerate(error_message_types):
        # Subset the DataFrame
        df_for_type = df[df['error_message_type'] == error_message_type]

        # Manually compute the mean and the standard error of the mean for each gender
        averages = []
        errors = []

        male_results = df_for_type[df_for_type['gender'] == 'male']['avg_error_run_length']
        print(error_message_type, "male", len(male_results))
        averages.append(np.mean(male_results))
        errors.append(np.std(male_results)/np.sqrt(len(male_results)))

        female_results = df_for_type[df_for_type['gender'] == 'female']['avg_error_run_length']
        print(error_message_type, "female", len(female_results))
        averages.append(np.mean(female_results))
        errors.append(np.std(female_results)/np.sqrt(len(female_results)))

        other_results = pd.concat([df_for_type[df_for_type['gender'] == 'non-binary']['avg_error_run_length'],
                            df_for_type[df_for_type['gender'] == 'other']['avg_error_run_length'],
                            df_for_type[df_for_type['gender'] == 'na']['avg_error_run_length']])
        print(error_message_type, "other", len(other_results))
        averages.append(np.mean(other_results))
        errors.append(np.std(other_results)/np.sqrt(len(other_results)))

        ax.errorbar(genders, averages, color=colors[i], fmt='--', alpha=0.3)
        ax.errorbar(genders, averages, yerr=errors, color=colors[i], fmt='o', label=official_error_types[error_message_type])
        print()

    # Set the labels for x and y axis
    ax.set_xlabel('Gender')
    ax.set_ylabel('Average Error Run Length')

    # Title of the graph
    ax.set_title('Average Error Run Length by Gender for each Error Message Type')

    # Place a legend on the axes.
    ax.legend()

    # Show the plot
    plt.show()

def analyze_gender_vs_error_message_type_regression():
    df = pd.read_csv('demographics_with_error_data.csv')

    # loop over error_message_type
    for eroor_message_type in error_message_types:
        
        #subset data
        subset = df[df['error_message_type'] == eroor_message_type]

        #perform anova
        model = ols('avg_error_run_length ~ C(gender)', data=subset).fit()
        anova_table = sm.stats.anova_lm(model, typ=2)

        print(f"\nFor error message type: {official_error_types[eroor_message_type]}, ANOVA results are:")
        print(anova_table)

def analyze_gender_vs_error_message_type_tukey():
    df = pd.read_csv('demographics_with_error_data.csv')

    genders = ['male', 'female', 'non-binary', 'other', 'na']

    df = df[df['error_message_type'].notna()]

    # Print number of people in each gender in dataset
    total = 0
    for gender in genders:
        d = df[df['gender'] == gender]
        print(gender, len(d))
        total += len(d)

    print(total)


    # for gender in genders:
    subset = df[(df['gender'] == 'non-binary') | (df['gender'] == 'non-other') | (df['gender'] == 'na')]

    #perform anova
    model = ols('avg_error_run_length ~ C(error_message_type)', data=subset).fit()
    anova_table = sm.stats.anova_lm(model, typ=2)

    print(f"\nFor hdi bin: Other, ANOVA results are:")
    print(anova_table)
    
    # perform pairwise comparison
    tukey = pairwise_tukeyhsd(endog=subset['avg_error_run_length'],
                                groups=subset['error_message_type'],
                                alpha=0.05)
    print(f"\nPairwise Tukey HSD results for gender: Other are:")
    print(tukey)

    


def experience_vs_error_message_type():
    df = pd.read_csv('demographics_with_error_data.csv')

    # Multiply all values in 'experience' column by -1 because 
    # -18 is the most experienced and 0 is the least experienced
    df['experience'] = df['experience'] * -1

    # Assuming your 'experience' is a continuous variable, we will create buckets using pandas "cut"
    experience_labels = ["Least", " ", "  ", "   ", "Most"]
    df["experience_bucket"] = pd.cut(df['experience'], bins=5)

    # Group by 'experience_bucket' and 'error_message_type' then calculate mean and standard deviation.
    grouped_df = df.groupby(['error_message_type', 'experience_bucket'])

    # Output the number of people in each group
    print(grouped_df.size())
    print(grouped_df['avg_error_run_length'].describe())

    bin_means = grouped_df['avg_error_run_length'].mean()
    bin_errors = grouped_df['avg_error_run_length'].sem()

    fig, ax = plt.subplots()

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
                    fmt='o', 
                    label=official_error_types[error_message_type])

    plt.xlabel('Programming Experience', fontsize=16)
    plt.ylabel('Number of Runs', fontsize=16)
    plt.legend(loc="upper right", bbox_to_anchor=(1,1), bbox_transform=ax.transAxes, fontsize=16)
    plt.tick_params(axis='both', which='major', labelsize=16)

    plt.ylim(bottom=1)

    plt.show()

def graph_fluency_vs_error_message_type():
    df = pd.read_csv('demographics_with_error_data.csv')

    # Assuming your 'experience' is a continuous variable, we will create buckets using pandas "cut"
    experience_labels = ["Least", " ", "  ", "   ", "Most"]
    df["fluency_bucket"] = pd.cut(df['fluency'], bins=5)

    # Group by 'experience_bucket' and 'error_message_type' then calculate mean and standard deviation.
    grouped_df = df.groupby(['error_message_type', 'fluency_bucket'])

    # Output the number of people in each group
    print(grouped_df.size())
    print(grouped_df['avg_error_run_length'].describe())

    bin_means = grouped_df['avg_error_run_length'].mean()
    bin_errors = grouped_df['avg_error_run_length'].sem()

    fig, ax = plt.subplots()

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
                    fmt='o', 
                    label=official_error_types[error_message_type])

    plt.xlabel('Fluency', fontsize=16)
    plt.ylabel('Number of Runs', fontsize=16)
    plt.legend(loc="upper right", bbox_to_anchor=(1,1), bbox_transform=ax.transAxes, fontsize=16)
    plt.tick_params(axis='both', which='major', labelsize=16)

    plt.ylim(bottom=1)

    plt.show()



def graph_hdi_vs_error_message_type(ax):
    df = pd.read_csv('demographics_with_hdi.csv')

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
        # Load your DataFrame
    df = pd.read_csv('demographics_with_error_data.csv')

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

        other_results = pd.concat([df_for_type[df_for_type['gender'] == 'non-binary']['avg_error_run_length'],
                            df_for_type[df_for_type['gender'] == 'other']['avg_error_run_length'],
                            df_for_type[df_for_type['gender'] == 'na']['avg_error_run_length']])
        averages.append(np.mean(other_results))
        errors.append(np.std(other_results)/np.sqrt(len(other_results)))

        ax.errorbar(genders, averages, color=colors[i], fmt='--', alpha=0.3)
        ax.errorbar(genders, averages, yerr=errors, color=colors[i], fmt='o')

    # Set the labels for x and y axis
    ax.set_xlabel('Gender', labelpad=20)
    # ax.set_ylabel('Number of Runs', fontsize=16)
    ax.set_ylim(bottom=1, top=3.5)

def graph_experience_vs_error_message_type(ax):
    df = pd.read_csv('demographics_with_error_data.csv')

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

# This is the one I used for the graph in the paper 8/9
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

def download_hdi_vs_error_message_type_data():
    df = pd.read_csv('demographics_with_hdi.csv')
    bins = [0, 0.54999, 0.69999, 0.79999, 1]
    df['hdi_bin'] = pd.cut(df['hdi'], bins)
    grouped_df = df.groupby(['error_message_type', 'hdi_bin'])
    bin_means = grouped_df['avg_error_run_length'].mean()
    bin_errors = grouped_df['avg_error_run_length'].sem()

    labels = ['Low', 'Medium', 'High', 'Very High']
    data_frames = []

    for i, error_message_type in enumerate(error_message_types):
        df_i = pd.DataFrame({
            'labels': labels,
            'avg': bin_means[error_message_type],
            'std_err': bin_errors[error_message_type],
            'error_message_type': error_message_type  # add the column during dataframe creation
        })
        data_frames.append(df_i)  # we will concat all these dataframes together at the end
    
    result = pd.concat(data_frames) 
    result.to_csv('hdi_vs_error_message_type.csv', index=False)

def analyze_experience_vs_error_message_type_using_regression():
    df = pd.read_csv('demographics_with_error_data.csv')

    # Multiply all values in 'experience' column by -1 because 
    # -18 is the most experienced and 0 is the least experienced
    df['experience'] = df['experience'] * -1

    # Assuming your 'experience' is a continuous variable, we will create buckets using pandas "cut"
    df["experience_bucket"] = pd.cut(df['experience'], bins=5)

    grouped_df = df.groupby(['error_message_type', 'experience_bucket'])
    print(grouped_df.describe())
    bin_means = grouped_df['avg_error_run_length'].mean()
    print(bin_means)

    # loop over error_message_type
    for eroor_message_type in error_message_types:
        
        #subset data
        subset = df[df['error_message_type'] == eroor_message_type]

        #perform anova
        model = ols('avg_error_run_length ~ C(experience_bucket)', data=subset).fit()
        anova_table = sm.stats.anova_lm(model, typ=2)

        print(f"\nFor error message type: {official_error_types[eroor_message_type]}, ANOVA results are:")
        print(anova_table)

def analyze_experience_vs_error_message_type_using_tukey():
    df = pd.read_csv('demographics_with_error_data.csv')

    # Multiply all values in 'experience' column by -1 because 
    # -18 is the most experienced and 0 is the least experienced
    df['experience'] = df['experience'] * -1

    # Assuming your 'experience' is a continuous variable, we will create buckets using pandas "cut"
    df["experience_bucket"] = pd.cut(df['experience'], bins=5)

    # Remove rows without an error_message_type
    df = df[df['error_message_type'].notna()]
    
    # experience_buckets = df['experience_bucket'].unique()

    # for experience_bucket in experience_buckets: 
    for error_message_type in error_message_types:       
        # subset data
        # subset = df[df['experience_bucket'] == experience_bucket]
        subset = df[df['error_message_type'] == error_message_type]

        # perform anova
        # model = ols('avg_error_run_length ~ C(error_message_type)', data=subset).fit()
        model = ols('avg_error_run_length ~ C(experience_bucket)', data=subset).fit()
        anova_table = sm.stats.anova_lm(model, typ=2)

        # print(f"\nFor experience_bucket: {experience_bucket}, ANOVA results are:")
        print(f"\nFor error_message_type: {official_error_types[error_message_type]}, ANOVA results are:")
        print(anova_table)
        
        # perform pairwise comparison
        # tukey = pairwise_tukeyhsd(endog=subset['avg_error_run_length'],
        #                           groups=subset['error_message_type'],
        #                           alpha=0.05)
        tukey = pairwise_tukeyhsd(endog=subset['avg_error_run_length'],
                                    groups=subset['experience_bucket'],
                                    alpha=0.05)
        # print(f"\nPairwise Tukey HSD results for experience_bucket: {experience_bucket} are:")
        print(f"\nPairwise Tukey HSD results for error_message_type: {official_error_types[error_message_type]} are:")
        print(tukey)

# analyze_hdi_vs_error_message_type_using_regression()
# analyze_hdi_vs_error_message_type_using_tukey()
# analyze_gender_vs_error_message_type_regression()
# analyze_gender_vs_error_message_type_tukey()
# gender_vs_error_message_type()
# graph_experience_vs_error_message_type()
# graph_fluency_vs_error_message_type()
graph_demo_results_side_by_side()
# download_hdi_vs_error_message_type_data()
# analyze_experience_vs_error_message_type_using_regression()
# analyze_experience_vs_error_message_type_using_tukey()