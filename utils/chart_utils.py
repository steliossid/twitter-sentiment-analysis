###########################################################################################
# Module that is responsible to show the pie charts of the sentiment analysis results      #
###########################################################################################
from utils import db_utils, read_write
from pymongo.errors import ServerSelectionTimeoutError, AutoReconnect
from tkinter import messagebox
import sys

try:
    import matplotlib.pyplot as plt
except ImportError as e:
    read_write.log_message("[FATAL] (chart_utils) : ImportError: " + str(e))
    sys.exit("[SEVERE] " + str(e) + ". Please install this module to continue")

LOG_NAME = " (chart_utils) : "


def show_textblob_polarity():
    try:
        collection = db_utils.get_collection()
        all_documents = collection.find()
        tweets_sum = all_documents.count()

        number_of_textblob_positive = collection.find({"textblob.polarity": 'pos'}).count()
        number_of_textblob_neutral = collection.find({"textblob.polarity": 'neu'}).count()
        number_of_textblob_negative = collection.find({"textblob.polarity": 'neg'}).count()

        percent_pos = (number_of_textblob_positive / tweets_sum) * 100
        percent_neu = (number_of_textblob_neutral / tweets_sum) * 100
        percent_neg = (number_of_textblob_negative / tweets_sum) * 100

        labels = 'Positive', 'Neutral', 'Negative'
        sizes = [percent_pos, percent_neu, percent_neg]

        fig1, ax1 = plt.subplots()
        ax1.pie(sizes, labels=labels, autopct='%1.1f%%',
                shadow=True, startangle=90)
        ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        plt.title('Textblob Polarity')
        plt.show()
    except ServerSelectionTimeoutError as e:
        read_write.log_message("[ERROR]" + LOG_NAME + "ServerSelectionTimeoutError: " + str(e))
        messagebox.showerror("Error", "Lost Connection to the DB")
        return
    except AutoReconnect as e:
        read_write.log_message("[ERROR]" + LOG_NAME + "AutoReconnect: " + str(e))
        messagebox.showerror("Error", "Lost Connection to the DB")
        return


def show_textblob_subjectivity():
    try:
        collection = db_utils.get_collection()
        all_documents = collection.find()
        tweets_sum = all_documents.count()

        number_of_textblob_subjective = collection.find({"textblob.subjectivity": 'subj'}).count()
        number_of_textblob_objective = collection.find({"textblob.subjectivity": 'obj'}).count()

        percent_subj = (number_of_textblob_subjective / tweets_sum) * 100
        percent_obj = (number_of_textblob_objective / tweets_sum) * 100

        labels = 'Subjective', 'Objective'
        sizes = [percent_subj, percent_obj]

        fig1, ax1 = plt.subplots()
        ax1.pie(sizes, labels=labels, autopct='%1.1f%%',
                shadow=True, startangle=90)
        ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        plt.title('Textblob Subjectivity')
        plt.show()

    except ServerSelectionTimeoutError as e:
        read_write.log_message("[ERROR]" + LOG_NAME + "ServerSelectionTimeoutError: " + str(e))
        messagebox.showerror("Error", "Lost Connection to the DB")
        return
    except AutoReconnect as e:
        read_write.log_message("[ERROR]" + LOG_NAME + "AutoReconnect: " + str(e))
        messagebox.showerror("Error", "Lost Connection to the DB")
        return


def show_vader_polarity():
    try:
        collection = db_utils.get_collection()
        all_documents = collection.find()
        tweets_sum = all_documents.count()

        number_of_vader_positive = collection.find({"vader.polarity": 'pos'}).count()
        number_of_vader_neutral = collection.find({"vader.polarity": 'neu'}).count()
        number_of_vader_negative = collection.find({"vader.polarity": 'neg'}).count()

        percent_pos = (number_of_vader_positive / tweets_sum) * 100
        percent_neu = (number_of_vader_neutral / tweets_sum) * 100
        percent_neg = (number_of_vader_negative / tweets_sum) * 100

        labels = 'Positive', 'Neutral', 'Negative'
        sizes = [percent_pos, percent_neu, percent_neg]

        fig1, ax1 = plt.subplots()
        ax1.pie(sizes, labels=labels, autopct='%1.1f%%',
                shadow=True, startangle=90)
        ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        plt.title('VADER Polarity')
        plt.show()
    except ServerSelectionTimeoutError as e:
        read_write.log_message("[ERROR]" + LOG_NAME + "ServerSelectionTimeoutError: " + str(e))
        messagebox.showerror("Error", "Lost Connection to the DB")
        return
    except AutoReconnect as e:
        read_write.log_message("[ERROR]" + LOG_NAME + "AutoReconnect: " + str(e))
        messagebox.showerror("Error", "Lost Connection to the DB")
        return


def show_training_polarity():
    try:
        collection = db_utils.get_collection()
        all_documents = collection.find()
        tweets_sum = all_documents.count()

        number_of_training_positive = collection.find({"training.polarity": 'pos'}).count()
        number_of_training_negative = collection.find({"training.polarity": 'neg'}).count()

        percent_pos = (number_of_training_positive / tweets_sum) * 100
        percent_neg = (number_of_training_negative / tweets_sum) * 100

        labels = 'Positive', 'Negative'
        sizes = [percent_pos, percent_neg]

        fig1, ax1 = plt.subplots()
        ax1.pie(sizes, labels=labels, autopct='%1.1f%%',
                shadow=True, startangle=90)
        ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        plt.title('NLTK Polarity')
        plt.show()
    except ServerSelectionTimeoutError as e:
        read_write.log_message("[ERROR]" + LOG_NAME + "ServerSelectionTimeoutError: " + str(e))
        messagebox.showerror("Error", "Lost Connection to the DB")
        return
    except AutoReconnect as e:
        read_write.log_message("[ERROR]" + LOG_NAME + "AutoReconnect: " + str(e))
        messagebox.showerror("Error", "Lost Connection to the DB")
        return


def show_training_subjectivity():
    try:
        collection = db_utils.get_collection()
        all_documents = collection.find()
        tweets_sum = all_documents.count()

        number_of_training_subjective = collection.find({"training.subjectivity": 'subj'}).count()
        number_of_training_objective = collection.find({"training.subjectivity": 'obj'}).count()

        percent_subj = (number_of_training_subjective / tweets_sum) * 100
        percent_obj = (number_of_training_objective / tweets_sum) * 100

        labels = 'Subjective', 'Objective'
        sizes = [percent_subj, percent_obj]

        fig1, ax1 = plt.subplots()
        ax1.pie(sizes, labels=labels, autopct='%1.1f%%',
                shadow=True, startangle=90)
        ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        plt.title('NLTK Subjectivity')
        plt.show()

    except ServerSelectionTimeoutError as e:
        read_write.log_message("[ERROR]" + LOG_NAME + "ServerSelectionTimeoutError: " + str(e))
        messagebox.showerror("Error", "Lost Connection to the DB")
        return
    except AutoReconnect as e:
        read_write.log_message("[ERROR]" + LOG_NAME + "AutoReconnect: " + str(e))
        messagebox.showerror("Error", "Lost Connection to the DB")
        return
