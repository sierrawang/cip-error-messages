import re

# NOTE - For some reason, some of the values in the error column look like weird_error_pattern.
# I think it is because it's somehow being incorrectly logged as a chunk of the error message.
# We can still extract the last line of the standard error message from this.



weird_error_pattern = r"^\(Line \d+\) (.+)\x1b$"

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

def normalize_error_message(raw_error):
    return generalize_error_message(get_clean_last_line(raw_error))