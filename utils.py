import os
import sys
import logging
from termcolor import colored

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def clean_dir(path: str) -> None:
    """
    Removes every file in a directory.

    Args:
        path (str): Path to directory.

    Returns:
        None
    """
    try:
        if not os.path.exists(path):
            os.mkdir(path)
            logger.info(f"Created directory: {path}")

        for file in os.listdir(path):
            file_path = os.path.join(path, file)
            os.remove(file_path)
            logger.info(f"Removed file: {file_path}")

        logger.info(colored(f"Cleaned {path} directory", "green"))
    except Exception as e:
        logger.error(f"Error occurred while cleaning directory {path}: {str(e)}")


def check_env_vars() -> None:
    """
    Checks if the necessary environment variables are set.

    Returns:
        None

    Raises:
        SystemExit: If any required environment variables are missing.
    """
    try:
        required_vars = ["PEXELS_API_KEY",]
        missing_vars = [var + os.getenv(var)  for var in required_vars if os.getenv(var) is None or (len(os.getenv(var)) == 0)]  

        if missing_vars:
            missing_vars_str = ", ".join(missing_vars)
            logger.error(colored(f"The following environment variables are missing: {missing_vars_str}", "red"))
            logger.error(colored("Please consult 'EnvironmentVariables.md' for instructions on how to set them.", "yellow"))
            sys.exit(1)  # Aborts the program
    except Exception as e:
        logger.error(f"Error occurred while checking environment variables: {str(e)}")
        sys.exit(1)  # Aborts the program if an unexpected error occurs





def extract_paragraph(json_data):
    try:
        paragraph = ""
        for word_data in json_data["channels"][0]["alternatives"][0]["words"]:
            paragraph += word_data["word"] + " "
        return paragraph.strip()
    except KeyError as e:
        print(f"Error: Missing key in JSON data: {e}")
        return None
    except Exception as e:
        print(f"Error: An unexpected error occurred: {e}")
        return None


def extract_StartTime(json_data, searchWord):
    try:
        prev_start_time = None
        for word_data in json_data["channels"][0]["alternatives"][0]["words"]:
            word = word_data["word"]
            word_start = word_data["start"]
           
            if word == searchWord:
                # If this is the first match or the difference with the previous match is at least 2 seconds
                if prev_start_time is None or (word_start - prev_start_time) >= 2:
                    if prev_start_time is not None:
                       print(f"prev_start_time {prev_start_time} start :{word_start}")
                       prev_start_time = word_start
                    return word_start
        return None    
    except KeyError as e:
        print(f"Error: Missing key in JSON data: {e}")
        return None
    except Exception as e:
        print(f"Error: An unexpected error occurred: {e}")
        return None




def add_start_time(json_data, word_data_list):
    updated_word_data_list = []
    for word_data in word_data_list:
        word = word_data['word']
        start_time = extract_StartTime(json_data, word)
        if start_time is not None:
            word_data['startTime'] = start_time
            updated_word_data_list.append(word_data)
    print(f"before checking duration gap:{updated_word_data_list}")        
    updated_word_data_list=modify_array(updated_word_data_list)        
    return updated_word_data_list



def modify_array(array):
    modified_array = []
    prev_start_time = None

    for element in array:
        current_start_time = element['startTime']

        if prev_start_time is None or (current_start_time - prev_start_time) >= 2:
            modified_array.append(element)
            prev_start_time = current_start_time
            print(f"prev_start_time:{prev_start_time},current_start_time:{current_start_time}")

    return modified_array

def convert_to_seconds(time_str):
    # Split the time string into hours, minutes, and seconds.milliseconds
    h, m, s_ms = time_str.split(':')
    
    # Split the seconds and milliseconds
    s, ms = map(float, s_ms.split('.'))
    
    # Convert everything to seconds
    total_seconds = int(h) * 3600 + int(m) * 60 + s + ms / 1000.0

    return total_seconds


