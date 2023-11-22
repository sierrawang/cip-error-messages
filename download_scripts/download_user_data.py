import pandas as pd
import csv
import ast
from datetime import datetime

import sys
sys.path.insert(1, '../utils')
import util

def get_section_id(user_info):
    return user_info['sections']['cip3'][0].get().id

def get_role(user_info):
    return user_info['roles']['cip3']

def get_age(user_id, users_collection, role):
    user_doc = None
    if role == 'student':
        user_doc = users_collection.document(user_id).collection('cip3').document('studentApplication').get().to_dict()
    elif role == 'sl':
        user_doc = users_collection.document(user_id).collection('cip3').document('sectionLeaderApplication').get().to_dict()
    
    if user_doc:
        try:
            # Calculate age from birthday
            birthday = user_doc['dateOfBirth']
            current_date = datetime.now()
            birth_date = datetime(birthday['year'], birthday['month'], birthday['day'])
            age = current_date.year - birth_date.year - ((current_date.month, current_date.day) < (birth_date.month, birth_date.day))
            return age
        except:
            return -1
    else:
        return -1

def get_gender(user_id, users_collection, role):
    user_doc = None
    if role == 'student':
        user_doc = users_collection.document(user_id).collection('cip3').document('studentApplication').get().to_dict()
    elif role == 'sl':
        user_doc = users_collection.document(user_id).collection('cip3').document('sectionLeaderApplication').get().to_dict()
    
    if user_doc:
        try:
            return user_doc['gender']
        except:
            return None
    else:
        return None

    

def get_country(user_id, users_collection, role):
    user_doc = None
    if role == 'student':
        user_doc = users_collection.document(user_id).collection('cip3').document('studentApplication').get().to_dict()
    elif role == 'sl':
        user_doc = users_collection.document(user_id).collection('cip3').document('sectionLeaderApplication').get().to_dict()
    
    if user_doc:
        try:
            country_info = user_doc['country']
            return country_info['eng_name']
        except:
            return None
    else:
        return None

    

def get_occupation(user_id, users_collection, role):
    user_doc = None
    if role == 'student':
        user_doc = users_collection.document(user_id).collection('cip3').document('studentApplication').get().to_dict()
    elif role == 'sl':
        user_doc = users_collection.document(user_id).collection('cip3').document('sectionLeaderApplication').get().to_dict()
    
    if user_doc:
        try:
            return user_doc['currentOccupation']
        except:
            return None
    else:
        return None

def get_hometown(user_id, users_collection, role):
    user_doc = None
    if role == 'student':
        user_doc = users_collection.document(user_id).collection('cip3').document('studentApplication').get().to_dict()
    elif role == 'sl':
        user_doc = users_collection.document(user_id).collection('cip3').document('sectionLeaderApplication').get().to_dict()
    
    if user_doc:
        try:
            return user_doc['city']
        except:
            return None
    else:
        return None

# Construct a csv file with info on each student and section leader
def download_user_info_for_sections_analysis():
    # Open a csv file to write to
    fieldnames = ["user_id", "role", "gender", "age", "country", "occupation", "section_id", "city"]
    filename = './cip_data_10-31/section_data.csv'
    original_df = pd.read_csv(filename)

    filename2 = './cip_data_10-31/section_data2.csv'
    f = open(filename2, 'w')
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()

    # Get a reference to the users collection to stream the data from
    db = util.setup_db()
    users_collection = db.collection('users')
    users = users_collection.list_documents()

    # Iterate through each user and write their info to our output file
    for user_doc in users:
        # Check if user is in the original csv file
        user_id = user_doc.id
        if user_id in original_df['user_id'].values:
            continue
        
        user_info = user_doc.get().to_dict()

        # Ignore users that don't exits, don't have a section, or don't have a role
        if user_info is None or 'sections' not in user_info or 'roles' not in user_info or 'cip3' not in user_info['sections'] or 'cip3' not in user_info['roles']:
            continue
        
        user_row = { 'user_id': user_doc.id }
        user_row['section_id'] = get_section_id(user_info)
        user_row['role'] = get_role(user_info)

        # Ignore users that aren't students or section leaders
        if user_row['role'] != 'student' and user_row['role'] != 'sl':
            continue

        user_row['age'] = get_age(user_doc.id, users_collection, user_row['role'])
        user_row['gender'] = get_gender(user_doc.id, users_collection, user_row['role'])
        user_row['country'] = get_country(user_doc.id, users_collection, user_row['role'])
        user_row['occupation'] = get_occupation(user_doc.id, users_collection, user_row['role'])
        user_row['city'] = get_hometown(user_doc.id, users_collection, user_row['role'])

        # Write the user's info to the csv file
        writer.writerow(user_row)

def check_sections_data_csv():
    filename = './cip_data_10-23/section_data.csv'
    df = pd.read_csv(filename)

    # Print the number of students
    print('Number of students: ' + str(len(df[df['role'] == 'student'])))

    # Print the number of section leaders
    print('Number of section leaders: ' + str(len(df[df['role'] == 'sl'])))

    # Print the total number of users
    print('Total number of users: ' + str(len(df)), 'should be sum of students and section leaders')

    # Check if every student has a section
    students = df[df['role'] == 'student']
    students_without_section = students[students['section_id'].isna()]
    print('Number of students without a section: ' + str(len(students_without_section)))

    # Check if every section leader has a section
    section_leaders = df[df['role'] == 'sl']
    section_leaders_without_section = section_leaders[section_leaders['section_id'].isna()]
    print('Number of section leaders without a section: ' + str(len(section_leaders_without_section)))

    # Check the number of section ids
    section_ids = df['section_id']
    print('Number of unique section ids: ' + str(len(section_ids.unique())))

    # Check if every age is valid (between 16 and 100)
    ages = df['age']
    min_age = ages.min()
    max_age = ages.max()
    print('Min age: ' + str(min_age))
    print('Max age: ' + str(max_age))

    # Check that there are no null values
    print('Number of null values in each column:')
    print(df.isnull().sum())





download_user_info_for_sections_analysis()
# check_sections_data_csv()