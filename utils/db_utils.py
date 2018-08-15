######################################################################
# Module that operates and is responsible for the MongoDB connection #
######################################################################
from utils import read_write
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError, ConfigurationError, DuplicateKeyError
import random
import string

LOG_NAME = " (db_utils) : "

collection = None
database = None
client = None


# returns a dictionary having two values "connect": boolean denoting the results and "errors": string showing the errors
# If connection is successful, "host": string and "port": int will be added in the response dictionary
def can_connect(host, port):
    response = {"connect": False, "errors": ""}
    try:
        port = int(port)  # getting the port, if it is not an int, we will have an exception
    except ValueError as e:
        message = "[ERROR]" + LOG_NAME + "ValueError:" + str(e)
        print(message)
        read_write.log_message(message)
        response["errors"] = "Port must be an integer"
        return response

    try:  # try connect to the MongoDB
        connection = MongoClient(host=host, port=port, serverSelectionTimeoutMS=10000, tz_aware=True)
    except ConfigurationError as e:  # if host is not appropriate
        message = "[ERROR]" + LOG_NAME + "ConfigurationError:" + str(e)
        print(message)
        read_write.log_message(message)
        response["errors"] = str(e)
        return response
    except TypeError as e:  # if port result to an error
        message = "[ERROR]" + LOG_NAME + "TypeError:" + str(e)
        print(message)
        read_write.log_message(message)
        response["errors"] = str(e)
        return response

    # to see if we can connect to the MongoDB, we make a test query to see if we can write in it
    # so we create a new database and collection with unique names
    pseudo_random = ''.join(
        random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(16))
    a_db = connection["random_database_" + pseudo_random]
    a_collection = a_db["random_collection_" + pseudo_random]

    try:  # we give the client, 10 seconds to connect
        read_write.log_message("[INFO]" + LOG_NAME + "Trying to connect to MongoDB with host: " +
                               host + " and port: " + str(port))
        a_collection.insert({"test": 1})
    except ServerSelectionTimeoutError as e:
        message = "[ERROR]" + LOG_NAME + "ServerSelectionTimeoutError:" + str(e)
        print(message)
        read_write.log_message(message)
        response["errors"] = "Can't connect"
        return response

    # if all OK, drop the test database
    connection.drop_database(a_db)
    # but make a global variable of the client, because we reference to it many times
    global client
    client = connection
    read_write.log_message("[INFO]" + LOG_NAME + "Successfully connected")
    response["connect"] = True
    response["host"] = host
    response["port"] = port
    return response


def store_tweet(tweet):
    global collection
    try:
        collection.insert(tweet)
        return True
    except DuplicateKeyError as e:
        message = "[ERROR]" + LOG_NAME + "DuplicateKeyError:" + str(e)
        print(message)
        return False


# this function, return the active MongoDB connection client
def get_client():
    global client
    return client


# getters and setters for database and collection
def set_database(name):
    global database
    database = name


def get_database():
    global database
    return database


def set_collection(name):
    global collection
    collection = name


def get_collection():
    global collection
    return collection
