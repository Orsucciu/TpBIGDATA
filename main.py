import tweepy
import argparse
from textblob import *
import json
import numpy
import matplotlib
import seaborn
import matplotlib.pyplot as plt
import pandas
import warnings
import time


# warnings.simplefilter("error") # uncomment this for extra info (not recommended when you have no problems)

matplotlib.use("TkAgg")


class Chjurchjulimu:
    polarity = 0
    url = ""
    reactions = 0  # flawed, as it doesn't count replies (only likes and rts)
    text = ""

    def __init__(self, polarity=0, url="null", react=0, text="Empty"):
        self.polarity = polarity
        self.url = url
        self.reactions = react
        self.text = text

    def to_string(self):
        return "Polarity : " + str(self.polarity) + "\n Reactions : " + str(self.reactions) + "\n Text : " + self.text + "\n Url : " + "https://twitter.com/statuses/"+self.url


with open('logins.json') as f:
    data = json.load(f)

consumer_key = data["consumer_key"]
consumer_secret = data["consumer_secret"]
access_token = data["access_token"]
access_token_secret = data["access_token_secret"]

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)

""" tp1
public_tweets = api.home_timeline()
for tweet in public_tweets:
    print(tweet.text)
    print(tweet.created_at)
    print(tweet.author)

wanted_tweets = api.user_timeline(screen_name="seofim", count=20)
for tweet in wanted_tweets:
    print(tweet.created_at)
    print(tweet.text)

searched_tweets = api.search(q="okay", count=20, lang="en")
for tweet in searched_tweets:
    print(tweet.created_at)
    print(tweet.text)
"""

parser = argparse.ArgumentParser(prog="tweet-analysis", description="Analysis Tweets")
parser.add_argument("-user", type=str, help="twitter's username", required=False)
parser.add_argument("-term", type=str, required=False)
parser.add_argument("-language", type=str, required=False)
parser.add_argument("-qtty", type=int, required=False)
args = parser.parse_args()

# analyzed_tweets = api.user_timeline(screen_name=args.user, count=100)
# for tweet in analyzed_tweets:
#   print(tweet.text)
#   print(TextBlob(tweet.text).sentiment)

analyzed_search = api.search(q="tumblr", count=200, lang="en")
average_polarity = 0
average_subjectivity = 0
for tweet in analyzed_search:
    average_polarity += TextBlob(tweet.text).polarity
    average_subjectivity += TextBlob(tweet.text).subjectivity
average_polarity = average_polarity / 100
average_subjectivity = average_subjectivity / 100
print("Polarity : " + str(average_polarity) + ' Subjectivity : ' + str(average_subjectivity))

positive = 0
negative = 0
neutral = 0
worst_tweet = Chjurchjulimu()
best_tweet = Chjurchjulimu()

chjurchjulime = []

for raw_tweet in tweepy.Cursor(api.search, q=args.term, lang=args.language, tweet_mode="extended").items(args.qtty):
    tweet = TextBlob(raw_tweet.full_text).correct()
    reactions = int(raw_tweet.favorite_count) + int(raw_tweet.retweet_count)
    chjurchjulime.append([raw_tweet.full_text, str(raw_tweet.created_at)[:10], "https://twitter.com/statuses/" + str(raw_tweet.id_str), tweet.polarity, reactions])
    if tweet.polarity >= 0.15:
        positive += 1
        if reactions > best_tweet.reactions:
            best_tweet.reactions = (raw_tweet.favorite_count + raw_tweet.retweet_count)
            best_tweet.polarity = tweet.polarity
            best_tweet.text = raw_tweet.full_text
            best_tweet.url = raw_tweet.id_str

    if tweet.polarity <= -0.15:
        negative += 1
        if reactions > worst_tweet.reactions:
            worst_tweet.reactions = (raw_tweet.favorite_count + raw_tweet.retweet_count)
            worst_tweet.polarity = tweet.polarity
            worst_tweet.text = raw_tweet.full_text
            worst_tweet.url = raw_tweet.id_str
    else:
        neutral += 1

data = pandas.DataFrame(chjurchjulime, columns=['Text', 'Date', 'Url', 'Polarity', 'Reactions'])

print("Keyword : " + args.term)
print("Language : " + args.language)
print("Positive tweets : " + str((positive/args.qtty)*100) + "%")
print("Negative tweets : " + str((negative/args.qtty)*100) + "%")
print("Neutral tweets :| " + str((neutral/args.qtty)*100) + "%")
print("Quantity of tweets : " + str(args.qtty))
print("")
print("\nBest tweet : ")
print(best_tweet.to_string())
print("\nWorst tweet : ")
print(worst_tweet.to_string())

seaborn.set(style="darkgrid")

fig, ax = plt.subplots(1, 2)

seaborn.lineplot(x="Polarity", y="Reactions", data=data, ax=ax[0])
seaborn.barplot(x=data["Date"], y=data["Date"].value_counts(), data=data, ax=ax[1])
plt.show()
