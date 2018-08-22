#####################################################################################################
# Module that is responsible for the polarity and subjectivity training of the tweets               #
#####################################################################################################
from utils import read_write
import sys
import os.path
import string
from tkinter import messagebox
try:
    from nltk import classify
    from nltk.sentiment.util import *
    from nltk.sentiment import SentimentAnalyzer
    from nltk.classify import NaiveBayesClassifier
except ImportError as e:
    read_write.log_message("[FATAL] (training) : ImportError: " + str(e))
    sys.exit("[SEVERE] " + str(e) + ". Please install this module to continue")

try:
    from nltk.corpus import movie_reviews
    from nltk.corpus import subjectivity
    from nltk.corpus import stopwords
except LookupError as e:
    read_write.log_message("[FATAL] (training) : LookupError: " + str(e))
    instructions = " ****   INSTALLATION INSTRUCTIONS   ****\n\n"
    instructions += "    1) Open a new terminal and type python. This will open a python terminal\n"
    instructions += "    2) Type import ntlk\n    3) Type nltk.download()\n"
    instructions += "    4) This will open a new window. Search in 'All Packages' and install movie_reviews," \
                    " subjectivity and stopwords\n"
    instructions += "    5) Double click OR click download to install it"
    read_write.log_message(instructions)
    sys.exit(str(e) + "\n" + instructions)

LOG_NAME = " (training) : "


def start_training():
    pol_checkfile = os.path.exists('files/sa_polarity.pickle')
    subj_checkfile = os.path.exists('files/sa_subjectivity.pickle')
    if pol_checkfile:
        message1 = "SA Polarity file already exists."
        messagebox.showinfo("File found", message1)
    else:
        message1 = "Cannot find the polarity sentiment analyzer file.\n"
        message1 += "Training a new one using NaiveBayesClassifier.\n"
        message1 += "Be patient. It might take a while."
        messagebox.showinfo("Training", message1)
        train_sentiment_analyzer(NaiveBayesClassifier.train, True, 100, True)
        messagebox.showinfo("Training", "Polarity Training finished.")
    read_write.log_message("[INFO]" + LOG_NAME + message1)
    if subj_checkfile:
        message2 = "SA Subjectivity file already exists."
        messagebox.showinfo("File found", message2)
    else:
        message2 = "Cannot find the subjectivity sentiment analyzer file.\n"
        message2 += "Training a new one using NaiveBayesClassifier.\n"
        message2 += "Be patient. It might take a while."
        messagebox.showinfo("Training", message2)
        train_sentiment_analyzer(NaiveBayesClassifier.train, True, 1500, False)
        messagebox.showinfo("Training", "Subjectivity Training finished.")
    read_write.log_message("[INFO]" + LOG_NAME + message2)


def train_sentiment_analyzer(trainer, save_analyzer=False, n_instances=None, category=None):
    if n_instances is not None:
        n_instances = int(n_instances / 2)

    # NLTK's integrated Movie Reviews dataset for the polarity training
    # and subjectivity dataset for the subj training
    if category:  # True for polarity
        first_docs = [(list(movie_reviews.words(pos_id)), 'pos')
                      for pos_id in movie_reviews.fileids('pos')[:n_instances]]
        second_docs = [(list(movie_reviews.words(neg_id)), 'neg')
                       for neg_id in movie_reviews.fileids('neg')[:n_instances]]
    else:  # False for subjectivity
        first_docs = [(sent, 'subj') for sent in subjectivity.sents(categories='subj')[:n_instances]]
        second_docs = [(sent, 'obj') for sent in subjectivity.sents(categories='obj')[:n_instances]]

    # We separately split positive and negative instances to keep a balanced
    # uniform class distribution in both train and test sets.
    train_first_docs, test_first_docs = split_train_test(first_docs)
    train_second_docs, test_second_docs = split_train_test(second_docs)

    training_docs = train_first_docs + train_second_docs
    testing_docs = test_first_docs + test_second_docs

    sentim_analyzer = SentimentAnalyzer()
    if category:
        all_words = sentim_analyzer.all_words(training_docs)
    else:
        all_words = sentim_analyzer.all_words([mark_negation(doc) for doc in training_docs])

    all_words_clean = []
    stopwords_english = stopwords.words('english')
    for word in all_words:
        if word not in stopwords_english and word not in string.punctuation:
            all_words_clean.append(word)

    # Add simple unigram word features
    unigram_feats = sentim_analyzer.unigram_word_feats(all_words_clean, min_freq=4)
    sentim_analyzer.add_feat_extractor(extract_unigram_feats, unigrams=unigram_feats)

    # Apply features to obtain a feature-value representation of our datasets
    training_set = sentim_analyzer.apply_features(training_docs)
    testing_set = sentim_analyzer.apply_features(testing_docs)

    classifier = sentim_analyzer.train(trainer, training_set)
    try:
        classifier.show_most_informative_features()
    except AttributeError:
        message = "Your classifier does not provide a show_most_informative_features() method."
        print(message)
        read_write.log_message(message)
        sentim_analyzer.evaluate(testing_set)
    classifier_accuracy_percent = (classify.accuracy(classifier, testing_set)) * 100
    message_acc = 'Accuracy of classifier = ' + str(classifier_accuracy_percent) + '%'
    print(message_acc)
    read_write.log_message("[INFO]" + LOG_NAME + message_acc)
    if save_analyzer:
        if category:  # True for polarity
            save_file(sentim_analyzer, 'files/sa_polarity.pickle')
            message = "sa_polarity.pickle file saved."
            print(message)
            read_write.log_message(message)
        else:  # False for subjectivity
            save_file(sentim_analyzer, 'files/sa_subjectivity.pickle')
            message = "sa_subjectivity.pickle file saved."
            print(message)
            read_write.log_message(message)
