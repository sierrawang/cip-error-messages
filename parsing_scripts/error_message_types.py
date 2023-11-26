import ast

official_error_types = {
    'default': "Standard",
    'explain': "Long Explanation",
    'messageboard': "Forum",
    'tigerpython': "Simple Explanation",
    'superhero': "GPT - Superhero",
    'gpt': "GPT - Default",
}

# Get the error message types that this user used
def get_error_message_type_for_df(df):
    # Count the number of distinct error message types
    error_message_types = df['error_message_type'].unique()

    result = []
    for error_message_type in error_message_types:
        if error_message_type in official_error_types:
            result.append(error_message_type)

    return result

def valid_error_message_type(row):
    return row['error_message_type'] in official_error_types

def get_raw_errors(row):
    try:
        raw_errors = ast.literal_eval(row['error'])
        raw_error_messages = ast.literal_eval(row['error_message'])
        assert(len(raw_errors) == 0 or len(raw_error_messages) > 0) # Assert that the user actually saw an error message
        return raw_errors
    except:
        print('get_raw_errors') #, row['error'], row['error_message'])
        return []