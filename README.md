# cip-error-messages
This repo contains the code used in this paper: insert-link-to-paper. error_message_code contains the code used to generate the different error message types. All other folders contain code used in the data analysis. Note that the data for this project lives in the Code in Place 3 firestore, and was not published to github to maintain privacy of the students.

+ error_message_code/ contains the code used to generate the different error message types. 
    + frontend/ has the files were copied directly from the Code in Place React web application code.
    + backend/ has the files directly copied from the firebase repo for creating Forum based error messages.

+ data_files/ contains all of the data files for this project. Note that Sierra did not push most of them for privacy. Contact Sierra if you want access to these files.
    + sl_and_student_data.csv contains the age, gender, city, country, occupation, section_id, country's HDI, longitude, latitude for each student and section leader. Sierra downloaded each user's role (sl or student), gender, age, city, country, occupation, section id from the users/ collection in Code in Place firestore in 2023. She specifically downloaded all users who had section data, and a role that was either ‘sl’ or ‘student’. She performed three manual edits of this data - (1) removed Brahm who was listed as a student, (2) added user YVrXNIB6vTR1GbdNzExVlgYo2D72 as an sl, because they are listed as a ta but also lead a section, and (3) removed Chris Piech Test who was listed as a student. The HDI, latitude, and longitude columns were added programmatically based on each user's location.
    + student_logs/ contains the IDE logs per student. There is one file per student, titled {student_id}.csv. Each row contains the 'code', 'error_message', 'error', 'output', 'assnId', 'type', 'title', 'ogTimestamp', 'serverTimestamp', 'projectId', and 'unitTestResults' for every time the student ran their code. The 'error' is the compiler generated error, while the 'error_message' is the enhanced error that is shown to the student.
    + short_term_data/ contains the parsed data on how students resolve their errors in the short term
    + long_term_data/ contains the parsed data on how students resolve their errors in the long term
    + hdi.xlsx is data on the Human Development Index (HDI) for many countries, downloaded from the United Nations Programme in 2023 (note, that this data is from 2021-22 however)
    + demographics_with_error_data.csv contains demographics information on most of the students (it missing data on 50 students for an unknown reason). This information comes from the files firebase/scripts/admission/accept_adults_original.csv and firebase/scripts/admission/accept_minors.csv. This is used for the experience column.

+ download_scripts/ contains the scripts needed to download data from the Code in Place 2023 firebase. To run these scripts, you must clone the Code in Place firebase repo, then copy and run each script from firebase/scripts/download_data/
    + download_logs_per_student.py downloads one csv per student containing their IDE logs
    + download_user_data.py downloads one csv containing demographic information on each student

+ parsing_scripts/
    + add_hdi.py adds an hdi column to sl_and_student_data.csv
    + add_error_message_type.py adds an error_message_type column to each row of each student log file that says what error message type was used, and each row of sl_and_student_data.csv that says the error message type they used, if they just used one for the whole course.
    + add_experience.py adds an experience column to each row of log file, that says what error message type was used
    + add_avg_error_run_length.py adds an avg_error_run_length column to sl_and_student_data.csv that contains the average error run length of each student for the course.
    + analyze_demographics_results.py analyzes the statsitical significance of the demographics results
    + analyze_long_term_results.py analyzes the statsitical significance of the long term results
    + analyze_short_term_results.py analyzes the statsitical significance of the short term results
    + count_users_and_errors.py counts the number of students that used each error message type, and the number of errors made of each error message type. Sierra used this code to generate table 1 in the paper.
    + graph_demographics_results.py graphs the time to resolve errors for HDI, gender, and programming experience
    + graph_long_term_results.py graphs the long term results for different error message types
    + graph_short_term_results.py graphs the short term results for different error message types
    + parse_long_term_results.py determines how students' rate of error, and time to resolve their error, changes throughout the course
    + parse_short_term_results.py determines the rate that users make the same error in the subsequent run, and the number of runs it takes a user to resolve an error, and writes this information to output files
    + error_message_types.py contains common information about error message types
    + clean_error_message.py contains functions for turning raw errors into more general errors (removes function and variable names, etc)
    + karel_info.py contains information about karel assignments