import pandas as pd
import statsmodels.api as sm
from statsmodels.formula.api import ols
from statsmodels.stats.multicomp import pairwise_tukeyhsd

error_message_types = ['default', 'explain', 'messageboard', 'tigerpython', 'superhero', 'gpt']

data_folder = '../data_files/'

# Check the effect of a parameter (demographic or error message type) 
# WITHIN each group (error messge type or demographic)
def analyze_param_within_group(df, test_column, within_column):
    groups = df[within_column].unique()

    for group in groups:
        # Grab the subset of the data for this group
        subset = df[df[within_column] == group]

        print(f'For {test_column} results, # Users {group}: {len(subset)}')

        # See if there is any significant difference in the average error run length within this group
        model = ols(f'avg_error_run_length ~ C({test_column})', data=subset).fit()
        anova_table = sm.stats.anova_lm(model, typ=2)

        # The PR(>F) value is the p-value, and says whether we can reject the null hypothesis that the means are equal
        # or in other words, that the error message type does not affect the average error run length
        print(f"\nFor {group}, ANOVA results are:")
        print(anova_table)
        
        # perform pairwise comparison
        tukey = pairwise_tukeyhsd(endog=subset['avg_error_run_length'],
                                    groups=subset[test_column],
                                    alpha=0.05)
        print(f"\nPairwise Tukey HSD results for {group} are:")
        print(tukey)


def check_effect_of_hdi():
    df = pd.read_csv(f'{data_folder}sl_and_student_data.csv')
    df = df[df['error_message_type'].isin(error_message_types)]
    df = df.dropna(subset=['avg_error_run_length'])
    df = df.dropna(subset=['hdi'])

    # Assuming your DataFrame is df
    bins = [0, 0.54999, 0.69999, 0.79999, 1]
    df['hdi_bin'] = pd.cut(df['hdi'], bins)

    print("Checking effect of HDI on average error run length, within each error message type")
    analyze_param_within_group(df, 'hdi_bin', 'error_message_type')

    # print("Checking effect of error message type on average error run length, within each HDI group")
    # analyze_param_within_group(df, 'error_message_type', 'hdi_bin')

def check_effect_of_gender():
    df = pd.read_csv(f'{data_folder}sl_and_student_data.csv')
    df = df[df['error_message_type'].isin(error_message_types)]
    print(len(df))
    # Print number of students in each gender
    f = len(df[df['gender'] == 'female'])
    m = len(df[df['gender'] == 'male'])
    o = len(df[df['gender'] == 'other'])

    print(f'{m} students identify as male, {f} students identify as female, and {o} students do not identify as either')

    df = df.dropna(subset=['avg_error_run_length'])

    print("Checking effect of gender on average error run length, within each error message type")
    analyze_param_within_group(df, 'gender', 'error_message_type')

    # print("Checking effect of error message type on average error run length, within each gender")
    # analyze_param_within_group(df, 'error_message_type', 'gender')

def check_effect_of_experience():
    df = pd.read_csv(f'{data_folder}sl_and_student_data.csv')
    df = df[df['error_message_type'].isin(error_message_types)]
    df = df.dropna(subset=['avg_error_run_length'])
    df = df.dropna(subset=['experience'])

    # Multiply all values in 'experience' column by -1 because 
    # -18 is the most experienced and 0 is the least experienced
    df['experience'] = df['experience'] * -1

    # Assuming your 'experience' is a continuous variable, we will create buckets using pandas "cut"
    df["experience_bucket"] = pd.cut(df['experience'], bins=5)

    # print("Checking effect of experience on average error run length, within each error message type")
    # analyze_param_within_group(df, 'experience_bucket', 'error_message_type')

    print("Checking effect of error message type on average error run length, within each experience group")
    analyze_param_within_group(df, 'error_message_type', 'experience_bucket')

if __name__ == '__main__':
    # Look at whether gender, hdi, and experience of a user affects the average error run length, 
    # WITHIN each error message type. Also, look WITHIN each group (across each error message type), 
    # to see if the error message type affects the average error run length.

    check_effect_of_hdi()
    check_effect_of_gender()
    # check_effect_of_experience()