#######################################################################################################
# Module that is responsible to functionalities like tweet formatting etc.                            #
#######################################################################################################
from utils import sentiment_utils


def format_tweet(tweet, **kwargs):
    formatted_tweet = {}
    if kwargs["method"] is "stream":
        # see "anatomy of a tweet" for more details
        # IMPORTANT: tweepy.api.stream method, returns StreamResult Object
        # we can't parse it like json, but it does the parsing itself for us
        # only thing remaining is to call it's values like that.
        # we again create the dictionary to store the document to MongoDB
        formatted_tweet = {"_id": tweet["id"],  # this will make the tweet's id, ObjectID
                           "whole_text": tweet["text"],
                           "textblob": {
                               "polarity": sentiment_utils.textblob_polarity(tweet["text"]),
                               "subjectivity": sentiment_utils.textblob_subjectivity(tweet["text"])
                           },
                           "vader": {
                               "polarity": sentiment_utils.vader_polarity(tweet["text"])
                           },
                           "training": {
                               "polarity": sentiment_utils.sent_result(tweet["text"], True),      # True for polarity
                               "subjectivity": sentiment_utils.sent_result(tweet["text"], False)  # False for subj
                           }}
    # and we return the results
    return formatted_tweet
