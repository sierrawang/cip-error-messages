# This is a script to download a csv of the logs for each student from the database.
# This will run in the firebase repo, in firebase/scripts/download_data
# Sierra - 7/13/23

import csv
from concurrent.futures import ThreadPoolExecutor
import pandas as pd

import sys
sys.path.insert(1, '../utils')
import util

def process_user_doc(user_doc, student_id):
    fieldnames = ['code', 'error_message', 'error', 'output', 'assnId', 'type', 'title', 'ogTimestamp', 'serverTimestamp', 'projectId', 'unitTestResults']

    user_id = user_doc.id
    assert user_id == student_id
    file_name = f'./logs_11-21/{user_id}.csv'
    writer = csv.DictWriter(open(file_name, 'w'), fieldnames=fieldnames)
    writer.writeheader()

    logs_collection = user_doc.collection('logs')
    logs_stream = logs_collection.stream() 

    for logs_doc in logs_stream:
        log = logs_doc.to_dict()

        projectData = log.get('projectData', {})
        assnId = projectData.get('assnId')
        type_ = projectData.get('type')
        title = projectData.get('title')
        projectId = projectData.get('uid')

        code = log.get('code')
        codeRunResults = log.get('codeRunResults', {})
        error_message = codeRunResults.get('error_message')
        error = codeRunResults.get('error')
        output = codeRunResults.get('output')
        ogTimestamp = logs_doc.id
        serverTimestamp = log.get('serverTimestamp')

        unitTestResults = log.get('unitTestResults', [])
        utResults = []
        for unitTestResult in unitTestResults:
            utResults.append(unitTestResult.get('state'))


        writer.writerow({'code': code,
                         'error_message': error_message,
                         'error': error,
                         'output': output,
                         'assnId': assnId,
                         'type': type_,
                         'title': title,
                         'ogTimestamp': ogTimestamp,
                         'serverTimestamp': serverTimestamp,
                         'projectId': projectId,
                         'unitTestResults': utResults})

def main_parallel():
    db = util.setup_db()
    collection_ref = db.collection('ide_logs_v2')
    user_docs = collection_ref.list_documents()
    
    futures = []
    with ThreadPoolExecutor() as executor:
        count = 0
        for user_doc in user_docs:
            futures.append(executor.submit(process_user_doc, user_doc))
            count += 1
            if count % 100 == 0:
                print(f"Processed {count} users")

def main_sequential():
    db = util.setup_db()
    collection_ref = db.collection('ide_logs_v2')
    
    sl_and_students = pd.read_csv('sl_and_student_data.csv')
    students_only = sl_and_students[sl_and_students['role'] == 'student']['user_id']
    print("Number of students", len(students_only))

    count = 0
    for student in students_only:
        user_doc = collection_ref.document(student)

        try:
            process_user_doc(user_doc, student)
        except Exception as e:
            print(f"Error processing {student}: {e}")
            continue

        count += 1
        if count % 100 == 0:
            print(f"Processed {count} users")

if __name__ == '__main__':
    # main_parallel()
    main_sequential()