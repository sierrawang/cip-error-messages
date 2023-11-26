import pandas as pd

def add_experience():
    # Load the data
    sl_and_student_data = pd.read_csv('../data_files/sl_and_student_data.csv')

    # Add a column for the error message type
    sl_and_student_data['experience'] = None

    demographics_data = pd.read_csv('../data_files/demographics_with_error_data.csv')

    # For each row
    students_only = sl_and_student_data[sl_and_student_data['role'] == 'student']
    count = 0
    for i, row in students_only.iterrows():
        try:
            # Add the average error run length to the dataframe
            sl_and_student_data.at[i, 'experience'] = demographics_data[demographics_data['uid'] == row['user_id']]['experience'].values[0]
        except:
            print(row['user_id'])
            count += 1

    # Missing data for 50 students, I have no idea why
    print(count)

    # Save the dataframe
    sl_and_student_data.to_csv('../data_files/sl_and_student_data.csv', index=False)

if __name__ == '__main__':
    add_experience()
    