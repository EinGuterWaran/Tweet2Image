from credentials import client_key, client_secret, access_token, access_token_secret
import tweepy
import pandas as pd
import numpy as np
import GetOldTweets3 as Got
from datetime import datetime
import pytz
import os


tz = pytz.timezone('Europe/Berlin')


def get_profile_image(username):
    api = connect_to_twitter()
    cursor = tweepy.Cursor(api.user_timeline,
                           id=username,
                           tweet_mode='extended').items(1)
    for x in cursor:
        image_url = x.user.profile_image_url
    image_url = image_url.replace("_normal", "")
    return image_url


def get_name(username):
    api = connect_to_twitter()
    cursor = tweepy.Cursor(api.user_timeline,
                           id=username,
                           tweet_mode='extended').items(1)
    for x in cursor:
        name = x.user.name
    return name


def is_retweet(x):
    if x.retweeted or "RT @" in x.full_text:
        return True
    return False


def is_comment(x):
    if x.full_text[0] == "@":
        return True
    return False


def connect_to_twitter():
    auth = tweepy.OAuthHandler(client_key, client_secret)
    auth.set_access_token(access_token, access_token_secret)
    return tweepy.API(auth)


def most_liked_tweets(username, how_many, min_likes):
    api = connect_to_twitter()
    cursor = tweepy.Cursor(api.user_timeline,
                           id=username,
                           tweet_mode='extended').items(how_many)
    tweets = []
    for x in cursor:
        media_url = []
        if not is_retweet(x) and not is_comment(
                x) and x.favorite_count >= min_likes:
            if 'media' in x.entities:
                for media in x.extended_entities['media']:
                    media_url.append(media['media_url'])
            favs = x.favorite_count
            retweets = x.retweet_count
            the_id = x.id
            when = x.created_at
            tweets.append([x.full_text, favs, retweets, the_id, when, media_url])
            print("Tweet "+str(the_id)+": "+x.full_text+" added.")
    tweet_df = pd.DataFrame(
        np.array(tweets),
        columns=['tweet', 'favs', 'retweets', 'id', 'date', 'media_url'])
    tweet_df.favs = tweet_df.favs.astype(int)
    tweet_df.retweets = tweet_df.retweets.astype(int)
    tweet_df = tweet_df.sort_values('favs',
                                    ascending=False).reset_index(drop=True)
    return tweet_df


def most_liked_tweets2(username, how_many, min_likes):
    # Creation of query object
    tweetCriteria = Got.manager.TweetCriteria().setUsername(
        username).setMaxTweets(how_many)
    # Creation of list that contains all tweets
    thetweets = Got.manager.TweetManager.getTweets(tweetCriteria)
    # Creating list of chosen tweet data
    tweets = []
    for x in thetweets:
        if not is_retweet(x) and not is_comment(
                x) and x.favorite_count >= min_likes:
            favs = x.favorite_count
            retweets = x.retweet_count
            the_id = x.id
            when = x.created_at
            tweets.append([x.full_text, favs, retweets, the_id, when])
    tweet_df = pd.DataFrame(
        np.array(tweets), columns=['tweet', 'favs', 'retweets', 'id', 'date'])
    tweet_df.favs = tweet_df.favs.astype(float)
    tweet_df.retweet = tweet_df.retweets.astype(float)
    tweet_df = tweet_df.sort_values('favs',
                                    ascending=False).reset_index(drop=True)
    return tweet_df


def tweets_to_csv(username, last_x_tweets, min_favs):
    my_best_tweets = most_liked_tweets(username, last_x_tweets, min_favs)
    timestamp_now = datetime.now(tz).strftime("%Y-%m-%d_%H-%M-%S")
    if not os.path.exists('tweet_lists/'+username):
        os.makedirs('tweet_lists/'+username)
    filename = 'tweet_lists/'+username+'/tweets_' + username + "_" + str(last_x_tweets) + "_" + str(min_favs) + "_" + \
               str(timestamp_now) + '.csv'
    my_best_tweets.to_csv(filename, index=False)

    print(filename+" saved.")
    return filename
