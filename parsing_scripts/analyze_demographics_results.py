import pandas as pd
import statsmodels.api as sm
from statsmodels.formula.api import ols
from statsmodels.stats.multicomp import pairwise_tukeyhsd
from error_message_types import official_error_types

error_message_types = ['default', 'explain', 'messageboard', 'tigerpython', 'superhero', 'gpt']


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

if __name__ == '__main__':
    analyze_hdi_vs_error_message_type_using_regression()
    analyze_hdi_vs_error_message_type_using_tukey()
    
    analyze_gender_vs_error_message_type_regression()
    analyze_gender_vs_error_message_type_tukey()
    
    analyze_experience_vs_error_message_type_using_regression()
    analyze_experience_vs_error_message_type_using_tukey()