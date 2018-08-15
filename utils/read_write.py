###############################################################
# Module that is responsible to write or read data from files #
###############################################################
import json
import os
from datetime import datetime

LOG_NAME = " (read_write) : "

file_path = os.path.abspath("files")


# function that returns the current datetime. I do it here, because this is needed in
def get_timestamp():
    now = datetime.now()
    now = now.replace(microsecond=0)
    return now


# we initialize a log_file, every time the program starts
log_file = str(get_timestamp()).replace(' ', '_').replace(':', '-') + ".log"
log_path = os.path.abspath("logs/" + log_file)
print("[INFO] Log file path set: " + str(log_path))


# function that returns the data in json format from mongo.json file
def read_mongo():
    try:
        with open(os.path.abspath(file_path + "/mongo.json")) as datafile:
            data = json.load(datafile)
    except FileNotFoundError as fe:
        message = "[ERROR]" + LOG_NAME + "FileNotFoundError: " + str(fe)
        print(message)
        log_message(message)
        data = []
    return data


# function that returns the data in json format from last.json file
def read_last():
    try:
        with open(os.path.abspath(file_path + "/last.json")) as datafile:
            data = json.load(datafile)
    except FileNotFoundError as fe:
        message = "[ERROR]" + LOG_NAME + "FileNotFoundError: " + str(fe)
        print(message)
        log_message(message)
        data = {}
    return data


# function that reads and returns the data from keywords.json file
def read_keywords():
    try:
        with open(os.path.abspath(file_path + "/keywords.json")) as datafile:
            data = json.load(datafile)
    except FileNotFoundError as fe:
        message = "[ERROR]" + LOG_NAME + "FileNotFoundError: " + str(fe)
        print(message)
        log_message(message)
        data = []
    return data


# function that read credentials from credentials.json
def read_credentials():
    try:
        with open(os.path.abspath(file_path + "/credentials.json")) as datafile:
            credentials = json.load(datafile)
    except FileNotFoundError as fe:
        message = "[ERROR]" + LOG_NAME + "FileNotFoundError: " + str(fe)
        print(message)
        log_message(message)
        credentials = {}
    return credentials


# function that writes the data in mongo.json file
def write_mongo(data):
    with open(os.path.abspath(file_path + "/mongo.json"), "w") as outfile:
        json.dump(data, outfile, sort_keys=True, indent=2)


# function that writes the data in last.json file
def write_last(data):
    with open(os.path.abspath(file_path + "/last.json"), "w") as outfile:
        json.dump(data, outfile, sort_keys=True, indent=2)


# function that writes the data in keywords.json file
# Unlike the other functions, this counts the length of the list, because we store only the 10 last keywords
def write_keywords(data):
    keywords = read_keywords()
    if data in keywords:  # if the keyword is already in the file
        return

    # we use a while loop, to catch if user enter manually some keywords in the json file
    while len(keywords) >= 10:  # if we have 10 keywords stored
        keywords.pop()  # pop the last out
    keywords.insert(0, data)  # and insert in the first position the new one
    with open(os.path.abspath(file_path + "/keywords.json"), "w") as outfile:
        json.dump(keywords, outfile, sort_keys=False, indent=2)


# function that opens the log file and appends the new message
def log_message(message):
    with open(log_path, "a") as logging:
        try:
            logging.write(str(get_timestamp()) + " >> " + message + "\n")
        except UnicodeEncodeError as e:
            message = str(get_timestamp()) + "[WARN]" + LOG_NAME + "UnicodeEncodeError: " + str(e) + "\n"
            logging.write(message)


# function that gets as argument a window and sets a favicon to it
def set_favicon(root):
    root.iconbitmap(os.path.abspath("files/favicon.ico"))
