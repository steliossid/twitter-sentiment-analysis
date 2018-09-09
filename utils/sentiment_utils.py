#####################################################################################################
# Module that is responsible for the sentiment analysis of the tweets                               #
#####################################################################################################
from utils import read_write, training
import sys
try:
    from textblob import TextBlob
    from nltk.sentiment.util import *
    from nltk.tokenize import regexp, word_tokenize
except ImportError as e:
    read_write.log_message("[FATAL] (sentiment_utils) : ImportError: " + str(e))
    sys.exit("[SEVERE] " + str(e) + ". Please install this module to continue")

try:
    from nltk.sentiment.vader import SentimentIntensityAnalyzer
except LookupError as e:
    read_write.log_message("[FATAL] (sentiment_utils) : LookupError: " + str(e))
    instructions = " ****   INSTALLATION INSTRUCTIONS   ****\n\n"
    instructions += "    1) Open a new terminal and type python. This will open a python terminal\n"
    instructions += "    2) Type import ntlk\n    3) Type nltk.download()\n"
    instructions += "    4) This will open a new window. Search in 'All Packages' and install vader_lexicon.\n"
    instructions += "    5) Double click OR click download to install it"
    read_write.log_message(instructions)
    sys.exit(str(e) + "\n" + instructions)

LOG_NAME = " (sentiment_utils) : "


def textblob_polarity(text):
    # Textblob polarity values: negative vs. positive   (-1.0 => +1.0)
    #                                                   Zero value is neutral
    testimonial = TextBlob(text)
    polarity_value = testimonial.sentiment.polarity
    if polarity_value > 0:
        label = "pos"
    elif polarity_value == 0:
        label = "neu"
    else:
        label = "neg"

    return label


def textblob_subjectivity(text):
    # Textblob  subjectivity values: objective vs. subjective (+0.0 => +1.0)
    testimonial = TextBlob(text)
    subjectivity_value = testimonial.sentiment.subjectivity
    if subjectivity_value >= 0.5:
        label = "subj"
    else:
        label = "obj"

    return label


def vader_polarity(text):
    # VADER polarity values: negative vs. positive   (-1.0 => 1.0)
    #                                                (-0.2,0.2) values are neutral
    analyzer = SentimentIntensityAnalyzer()
    scores = analyzer.polarity_scores(text)

    # compound value is chosen because we want multidimensional measures of sentiment just like Textblob
    # We will consider posts with a compound value greater than 0.2 as positive and less than -0.2 as negative.
    # There's some testing and experimentation that goes with choosing these ranges,
    # and there is a trade-off to be made here.
    # If we choose a higher value, we might get more compact results
    # (less false positives and false negatives),  but the size of the results will decrease significantly.

    if scores["compound"] > 0.2:
        label = "pos"
    elif scores["compound"] < -0.2:
        label = "neg"
    else:
        label = "neu"

    return label


def sent_result_polarity(text):
    # Classify a single sentence as positive/negative using a stored custom classifier.
    tokens = word_tokenize(text)
    custom_set = training.bag_of_words(tokens)
    classifier = load('files/sa_polarity.pickle')
    label = classifier.classify(custom_set)

    return label


def sent_result_subjectivity(text):
    # Classify a single sentence as subjective/objective using a stored custom classifier.
    word_tokenizer = regexp.WhitespaceTokenizer()
    # Tokenize and convert to lower case
    tokenized_text = [word.lower() for word in word_tokenizer.tokenize(text)]
    sentim_analyzer = load('files/sa_subjectivity.pickle')
    label = sentim_analyzer.classify(tokenized_text)

    return label


