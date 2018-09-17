#######################################################################################
# Module that is responsible to connect to the Streaming Server and gather the tweets #
#######################################################################################
from utils import db_utils, manage_credentials, read_write, other_utils
from tweepy import StreamListener
import json
from tkinter import messagebox
from pymongo.errors import ServerSelectionTimeoutError, AutoReconnect

LOG_NAME = " (stream_util) : "


# Class that inherits StreamListener and handles the data.
class StdOutListener(StreamListener):
    def __init__(self):
        super(StdOutListener, self).__init__()
        self.flag = False  # this flag indicates if stream must stop or not. As long as it is False, we keep stream open
        self.pause_flag = False  # as long as false, pause is closed
        self.store_counter = None  # this counter, counts how many tweets stored to the DB so far
        read_write.log_message("[INFO]" + LOG_NAME + "StreamListener initialized")

    def on_connect(self):
        global stream_controller
        message_1 = "[SUCCESS]" + LOG_NAME + "Connected to Streaming Server!"
        message_2 = "[INFO]" + LOG_NAME + "#### Gathering tweets for '" + stream_controller.search_keyword \
                    + "' keyword. ####"
        print(message_2)
        read_write.log_message(message_1)
        read_write.log_message(message_2)

        # and save the keyword to the keywords.json file
        keywords_list = [x for x in stream_controller.search_keyword.split(",")]
        for keyword in keywords_list:
            keyword = keyword.lstrip()
            keyword = keyword.rstrip()
            read_write.write_keywords(keyword)

        self.store_counter = 0  # initialize the counter
        self.ignore_counter = 0

    def on_data(self, data):
        if self.flag:  # flag keep track if we want to stop the stream
            read_write.log_message("[INFO]" + LOG_NAME + "Gathered " +
                                   str(self.store_counter) +
                                   " tweets - Ignored " + str(self.ignore_counter) +
                                   " tweets")
            return False  # return False to terminate the loop
        if self.pause_flag:  # pause flag keeps track if we want to pause the stream
            return True  # return True and do nothing with the data. It's a virtual pause.

        data = json.loads(data)  # turn the incoming data into json format

        if data["lang"] != "en":  # we deal only with English language text based tweets
            print("Non English - ignoring tweet.")
            self.ignore_counter += 1
            return True

        # we pass our data into this static method to clean them and keep only the necessary
        our_tweet = other_utils.format_tweet(data, method="stream")
        try:
            # this method try to save our tweet to the active connection to Mongo and returns the outcome
            # If all are OK, returns True, but if it fail, it returns False. With this way, we keep track
            # how many tweets we stored so far
            if db_utils.store_tweet(our_tweet):
                self.store_counter += 1  # increase the counter
                if self.store_counter % 100 == 0:  # and if we reach a multiply of 100, we print the result
                    print("Stored " + str(self.store_counter) + " tweets so far.")
            else:
                self.ignore_counter += 1
        except ServerSelectionTimeoutError as e:
            read_write.log_message("[ERROR]" + LOG_NAME + "ServerSelectionTimeoutError: " + str(e))
            messagebox.showerror("Error", "Lost Connection to the DB")
            return False
        except AutoReconnect as e:
            read_write.log_message("[ERROR]" + LOG_NAME + "AutoReconnect: " + str(e))
            messagebox.showerror("Error", "Lost Connection to the DB")
            return False

        # return True to continue the loop
        return True

    def on_error(self, status):
        # statuses take from here:
        # https://dev.twitter.com/overview/api/response-codes
        if status == 401:
            message = "[HTTP_ERROR]" + LOG_NAME + "401 Unauthorized - Missing or incorrect authentication credentials."
        elif status == 304:
            message = "[HTTP_ERROR]" + LOG_NAME + "304 Not Modified - There was no new data to return."
        elif status == 403:
            message = "[HTTP_ERROR]" + LOG_NAME + "403 Forbidden - The request is understood, " + \
                      "but it has been refused or access is not allowed."
        elif status == 420:
            message = "[HTTP_ERROR]" + LOG_NAME + "420 Enhance Your Calm - Returned when you are being rate limited."
        elif status == 500:
            message = "[HTTP_ERROR]" + LOG_NAME + "500 Internal Server Error - Something is broken."
        elif status == 503:
            message = "[HTTP_ERROR]" + LOG_NAME + "503 Service Unavailable - The Twitter servers are up, " + \
                      "but overloaded with requests. Try again later."
        elif status == 504:
            message = "[HTTP_ERROR]" + LOG_NAME + "504 Gateway timeout - The Twitter servers are up, but " + \
                      "the request couldn’t be serviced due to some failure within our stack. Try again later."
        else:
            message = "[HTTP_ERROR]" + LOG_NAME + status + " Unknown."

        print(message)
        read_write.log_message(message)
        read_write.log_message("[INFO]" + LOG_NAME + "Stopping stream")
        return False  # and stop the stream

    def on_disconnect(self, notice):
        status = json.loads(notice)
        message = "[ERROR] (" + type(self).__name__ + ") : Name=" + status["stream_name"] + \
                  ", Reason=" + status["reason"] + ", Code=" + str(status["code"])
        print(message)
        read_write.log_message(message)
        return False

    def on_exception(self, exception):
        read_write.log_message("[ERROR]" + LOG_NAME + str(exception))
        return False

    # setters for the flags
    def set_flag(self, value):
        self.flag = value

    def set_pause(self, value):
        self.pause_flag = value


# class that is responsible to start or close the threads of the stream
class StreamController(object):
    def __init__(self):
        self.search_keyword = None
        self.listener = StdOutListener()
        read_write.log_message("[INFO]" + LOG_NAME + "StreamController initialized")

    # method that starts the Streaming API
    def combine(self):
        # if not, set the flags to False ( so that we will be able to iterate at the Listener class )
        self.listener.set_flag(False)
        self.listener.set_pause(False)
        # and finally we start the stream
        self.stream()

    def stop(self):
        # setting only this flag to True, means that we break out of the streaming loop
        self.listener.set_flag(True)
        print("Stream stopped successfully.")

    def pause(self):
        self.listener.set_pause(True)

    def unpause(self):
        self.listener.set_pause(False)

    def stream(self):
        stream = manage_credentials.get_stream(listener=self.listener)
        # this is a try-except block, because if there is something wrong in the Listener class,
        # like e.g internet connection failure, it raises the exception inside the active thread
        try:
            # user can give more than one keywords for searching, we just add them to a list
            # he must separate them with commas, so we can split them and remove the whitespace with strip
            search_list = [x.strip() for x in self.search_keyword.split(",")]

            message = "[INFO]" + LOG_NAME + "Trying to connect to the Streaming Server..."
            print(message)
            read_write.log_message(message)
            stream.filter(track=search_list,
                          async=True)  # start the loop, async sets the Streaming in a new Thread
        except AttributeError as e:
            message = "[ERROR]" + LOG_NAME + "AttributeError: " + str(e)
            print(message)
            read_write.log_message(message)
            messagebox.showerror("Fatal error", "No credentials were found. Please close the script, " +
                                 "add the file and try again!")
        except Exception as e:
            message = "[ERROR]" + LOG_NAME + "Exception: " + str(repr(e))
            print(message)
            read_write.log_message(message)
            pass


# this controller, is initialized once the program starts, and we manage to handle the Streaming API
# through his methods
stream_controller = StreamController()


# function to start the Streaming API
def start_stream(frame):
    global stream_controller  # get the instance in hands
    # check if user gave a keyword
    if frame.keyword_entry.get().strip(" ") is not "":
        # change the GUI into more favorable way
        frame.mng_stream_btn.config(text="Stop Stream", command=lambda: stop_stream(frame))
        frame.pause_stream_btn.grid()  # show the pause button
        frame.pause_stream_btn.config(command=lambda: pause_unpause(frame))
        stream_controller.search_keyword = frame.keyword_entry.get()  # and set the keyword into controller,
        stream_controller.combine()  # to start the stream
    else:
        messagebox.showerror("Error", "Enter a keyword")


# function to handle the Pause/Un-pause button events
def pause_unpause(frame):
    global stream_controller
    if stream_controller.listener.pause_flag:  # if flag is True, it means that we already paused the stream
        stream_controller.unpause()  # so un-pause it and change the GUI
        frame.pause_stream_btn.config(text="Pause Stream")
        read_write.log_message("[INFO]" + LOG_NAME + "Continuing stream...")
    else:
        # but if it false, it means we press the Pause Stream button, so set it accordingly
        stream_controller.pause()
        frame.pause_stream_btn.config(text="Continue Stream")
        print("Stream paused...")
        read_write.log_message("[INFO]" + LOG_NAME + "Stream paused...")


# function to close the stream
def stop_stream(frame):
    global stream_controller
    frame.mng_stream_btn.config(text="Start Stream", command=lambda: start_stream(frame))
    frame.pause_stream_btn.grid_remove()
    print("Terminating stream...")
    read_write.log_message("[INFO]" + LOG_NAME + "Terminating stream...")
    stream_controller.stop()  # by calling the stream controller
