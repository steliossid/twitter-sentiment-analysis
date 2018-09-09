#####################################################################################################
# Module that is responsible for the polarity and subjectivity training of the tweets               #
#####################################################################################################
from utils import read_write
import sys
import os.path
import string
from tkinter import messagebox
from random import shuffle
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
        message1 += "Training a new one using Naive Bayes Classifier.\n"
        message1 += "Be patient. It might take a while."
        messagebox.showinfo("Training", message1)
        train_sentiment_analyzer_polarity(1000)
        messagebox.showinfo("Training", "Polarity Training finished.")
    read_write.log_message("[INFO]" + LOG_NAME + message1)
    if subj_checkfile:
        message2 = "SA Subjectivity file already exists."
        messagebox.showinfo("File found", message2)
    else:
        message2 = "Cannot find the subjectivity sentiment analyzer file.\n"
        message2 += "Training a new one using Naive Bayes Classifier.\n"
        message2 += "Be patient. It might take a while."
        messagebox.showinfo("Training", message2)
        train_sentiment_analyzer_subjectivity(5000)
        messagebox.showinfo("Training", "Subjectivity Training finished.")
    read_write.log_message("[INFO]" + LOG_NAME + message2)


def bag_of_words(words):
    stopwords_english = stopwords.words('english')
    punctuation = list(string.punctuation)
    punctuation.append("''")
    punctuation.append("``")
    punctuation.append("—")
    punctuation.append("…")
    punctuation.append("...")
    punctuation.append("--")
    punctuation.append("..")
    stopwords_english.extend(punctuation)
    words_clean = []

    for word in words:
        word = word.lower()
        if word not in stopwords_english and word not in string.digits:
            words_clean.append(word)

    words_dictionary = dict([word, True] for word in words_clean)

    return words_dictionary


def train_sentiment_analyzer_polarity(n_instances=None):

    if n_instances is not None:
        n_instances = int(0.2*n_instances)

    pos_reviews = []
    for fileid in movie_reviews.fileids('pos'):
        words = movie_reviews.words(fileid)
        pos_reviews.append(words)

    neg_reviews = []
    for fileid in movie_reviews.fileids('neg'):
        words = movie_reviews.words(fileid)
        neg_reviews.append(words)

    # positive reviews feature set
    pos_reviews_set = []
    for words in pos_reviews:
        pos_reviews_set.append((bag_of_words(words), 'pos'))

    # negative reviews feature set
    neg_reviews_set = []
    for words in neg_reviews:
        neg_reviews_set.append((bag_of_words(words), 'neg'))

    shuffle(pos_reviews_set)
    shuffle(neg_reviews_set)

    test_set = pos_reviews_set[:n_instances] + neg_reviews_set[:n_instances]
    train_set = pos_reviews_set[n_instances:] + neg_reviews_set[n_instances:]

    print('Training classifier')
    classifier = NaiveBayesClassifier.train(train_set)

    print(classifier.show_most_informative_features(10))

    classifier_accuracy_percent = (classify.accuracy(classifier, test_set)) * 100
    message_acc = 'Accuracy of classifier = ' + str(classifier_accuracy_percent) + '%'
    print(message_acc)
    read_write.log_message("[INFO]" + LOG_NAME + message_acc)

    save_file(classifier, 'files/sa_polarity.pickle')
    message = "sa_polarity.pickle file saved."
    print(message)
    read_write.log_message(message)


def train_sentiment_analyzer_subjectivity(n_instances=None):
    if n_instances is not None:
        n_instances = int(n_instances / 2)

    # NLTK's integrated  and subjectivity dataset for the subj training
    subj_docs = [(sent, 'subj') for sent in subjectivity.sents(categories='subj')[:n_instances]]
    obj_docs = [(sent, 'obj') for sent in subjectivity.sents(categories='obj')[:n_instances]]

    # We separately split positive and negative instances to keep a balanced
    # uniform class distribution in both train and test sets.
    train_subj_docs, test_subj_docs = split_train_test(subj_docs)
    train_obj_docs, test_obj_docs = split_train_test(obj_docs)

    training_docs = train_subj_docs + train_obj_docs
    testing_docs = test_subj_docs + test_obj_docs

    sentim_analyzer = SentimentAnalyzer()

    all_words = sentim_analyzer.all_words([mark_negation(doc) for doc in training_docs])

    stopwords_english = stopwords.words('english')
    punctuation = list(string.punctuation)
    punctuation.append("''")
    punctuation.append("``")
    punctuation.append("—")
    punctuation.append("…")
    punctuation.append("...")
    punctuation.append("--")
    punctuation.append("..")
    stopwords_english.extend(punctuation)
    all_words_clean = []
    for word in all_words:
        if word not in stopwords_english and word not in string.digits:
            all_words_clean.append(word)

    # Add simple unigram word features
    unigram_feats = sentim_analyzer.unigram_word_feats(all_words_clean, min_freq=4)
    sentim_analyzer.add_feat_extractor(extract_unigram_feats, unigrams=unigram_feats)

    # Apply features to obtain a feature-value representation of our datasets
    training_set = sentim_analyzer.apply_features(training_docs)
    testing_set = sentim_analyzer.apply_features(testing_docs)

    trainer = NaiveBayesClassifier.train
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

    save_file(sentim_analyzer, 'files/sa_subjectivity.pickle')
    message = "sa_subjectivity.pickle file saved."
    print(message)
    read_write.log_message(message)
