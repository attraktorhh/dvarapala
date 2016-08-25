from sys import exc_info
import logging

import tweepy

from config import (TWITTER_CONSUMER_SECRET, TWITTER_CONSUMER_KEY,
                    TWITTER_ACCESS_TOKEN_KEY, TWITTER_ACCESS_TOKEN_SECRET,
                    TWITTER_MESSAGE, TWITTER_ENABLE, TWITTER_TIME_FORMAT,
                    TIME_ZONE)

logger = logging.getLogger(__name__)


def publish(is_open, open_detail, message, last_change_time):
    """
    @param last_change_time: arrow.Arrow
    """
    if not TWITTER_ENABLE:
        return True
    logger.info("publishing to twitter")

    twitter_message = TWITTER_MESSAGE.format(
        time=last_change_time.to(TIME_ZONE).format(TWITTER_TIME_FORMAT),
        message=message)

    try:
        auth = tweepy.OAuthHandler(TWITTER_CONSUMER_KEY,
                                   TWITTER_CONSUMER_SECRET)
        auth.set_access_token(TWITTER_ACCESS_TOKEN_KEY,
                              TWITTER_ACCESS_TOKEN_SECRET)

        twitter_api = tweepy.API(auth)
        status = twitter_api.update_status(twitter_message)

        if status is not None:
            logger.info("OK")
        else:
            logger.error("response is None")
    except tweepy.TweepError as e:
        logger.error(e)
        return False
    except:
        logger.error(exc_info()[0])
        return False

    return True
