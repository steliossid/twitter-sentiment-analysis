#######################################################################################################
# Module that is responsible to functionalities like tweet formatting etc.                            #
#######################################################################################################
from utils import sentiment_utils, read_write
import sys
import string
import re
import os

try:
    from nltk.tokenize import word_tokenize
    from nltk.corpus import stopwords
except ImportError as e:
    read_write.log_message("[FATAL] (other_utils) : ImportError: " + str(e))
    sys.exit("[SEVERE] " + str(e) + ". Please install this module to continue")

LOG_NAME = " (other_utils) : "

try:
    stops = stopwords.words('english')
except LookupError as e:
    read_write.log_message("[FATAL] (other_utils) : LookupError: " + str(e))
    instructions = " ****   INSTALLATION INSTRUCTIONS   ****\n\n"
    instructions += "    1) Open a new terminal and type python. This will open a python terminal\n"
    instructions += "    2) Type import ntlk\n    3) Type nltk.download()\n"
    instructions += "    4) This will open a new window. Search in CORPORA for the package named 'Stopwords'\n"
    instructions += "    5) Double click OR click download to install it"
    read_write.log_message(instructions)
    sys.exit(str(e) + "\n" + instructions)

punctuation = list(string.punctuation)
punctuation.append("''")
punctuation.append("``")
punctuation.append("—")
punctuation.append("…")
punctuation.append("...")
punctuation.append("--")
punctuation.append("..")
stops.extend(punctuation)
stops.append("rt")

regexes = [
    re.compile('#.*'),  # finding hashtags
    re.compile('.*http[s]?://.*'),  # finding urls
    re.compile('@.*'),  # finding mentions
]


# function to clear the text of a tweet into two lists, one for text and one for stop_words
def clear_text(text):
    # building the lists or dictionaries that hold our data
    response = {}  # final object of response
    words = []  # this list holds all the meaningful words
    stop_words = []  # this list holds all the stop words
    punctuations = []  # this list holds all the punctuation marks
    entities = []  # this list holds all mentions, hastags and urls

    try:
        # tokenize the text into a list
        text = word_tokenize(text)
    except LookupError as e:
        read_write.log_message("[FATAL] (other_utils) : LookupError: " + str(e))
        instructions = " ****   INSTALLATION INSTRUCTIONS   ****\n\n"
        instructions += "    1) Open a new terminal and type python. This will open a python terminal\n"
        instructions += "    2) Type import ntlk\n    3) Type nltk.download()\n"
        instructions += "    4) This will open a new window. Search in ALL PACKAGES for the package named 'punkt'\n"
        instructions += "    5) Double click OR click download to install it"
        read_write.log_message(instructions)
        print(str(e) + "\n" + instructions)
        os._exit(1)

    # re-build the string because NLTK does not understand mentions or hashtags etc
    text = re_build_text(text)

    counter = 0
    for word in text:
        word = word.lower()
        counter += 1
        # tweets that are more than 140 characters, show … character at the end of the word
        # we choose, not to save these
        if len(word) > 1 and word.endswith("…"):
            continue

        # for some strange reason, "https" or "http" string escapes the clearing, so I excluded it manually
        if word == "https" or word == "http":
            continue

        # and distribute the word into the matching list
        if any(regex.match(word) for regex in regexes):
            entities.append(word)
        else:
            if word not in stops:
                # entry = {"value": word} # this is not needed anymore
                words.append(word)  # we append just the word here
            else:
                if word in punctuation:
                    punctuations.append(word)
                else:
                    stop_words.append(word)

    response["entities"] = entities
    response["punctuation"] = punctuations
    response["words"] = words
    response["stop_words"] = stop_words

    return response


# function that re-builds the tokens list, because some words are not acceptable by word_tokenizer of NLTK
# such as @mentions or #hashtags or https://urls
def re_build_text(text):
    escape_symbols = ["@", "#"]
    counter = 0
    for index in text:
        # building hashtags and mentions into one item
        if index in escape_symbols:
            try:
                index = index + text[counter + 1]
                text.remove(text[counter + 1])

                # if there is a : symbol, it connects with the previous word, that now is -1 indexes behind
                # because we removed the previous one
                if text[counter + 1] is ":":
                    index = index + ":"
                    text.remove(text[counter + 1])
            except IndexError:
                pass
            text[counter] = index  # save the index into the current item, but have the others removed
        # building the urls into one item
        elif index == "http" or index == "https":
            try:
                index += text[counter + 1]
                text.remove(text[counter + 1])
            except IndexError:
                pass
            try:
                index += text[counter + 1]
                text.remove(text[counter + 1])
            except IndexError:
                pass
            text[counter] = index
        # building n't endings, into one item with previous one
        elif index == "n't":
            # if previous word ends with vowel, add the "n" at the end of the word
            if text[counter - 1][-1:] in ["a", "e", "i", "o", "u"]:
                text[counter - 1] = text[counter - 1] + "n"
            text[counter] = "not"
        elif index == "'re":
            text[counter] = "are"

        counter += 1

    return text


def only_useful_words(text):
    response = clear_text(text)
    return " ".join(str(x) for x in response["words"])


def format_tweet(tweet, **kwargs):
    formatted_tweet = {}
    cleared_text = clear_text(tweet["text"])
    useful_words = only_useful_words(tweet["text"])
    if kwargs["method"] is "stream":
        # see "anatomy of a tweet" for more details
        # IMPORTANT: tweepy.api.stream method, returns StreamResult Object
        # we can't parse it like json, but it does the parsing itself for us
        # only thing remaining is to call it's values like that.
        # we again create the dictionary to store the document to MongoDB
        formatted_tweet = {"_id": tweet["id"],  # this will make the tweet's id, ObjectID
                           "whole_text": tweet["text"],
                           "text": cleared_text,
                           "textblob": {
                               "polarity": sentiment_utils.textblob_polarity(useful_words),
                               "subjectivity": sentiment_utils.textblob_subjectivity(useful_words)
                           },
                           "vader": {
                               "polarity": sentiment_utils.vader_polarity(useful_words)
                           },
                           "training": {
                               "polarity": sentiment_utils.sent_result_polarity(useful_words),
                               "subjectivity": sentiment_utils.sent_result_subjectivity(useful_words)
                           }}
    # and we return the results
    return formatted_tweet
