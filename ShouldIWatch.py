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


parser = argparse.ArgumentParser(prog="tweet-analysis", description="Analysis Tweets")
parser.add_argument("-term", type=str, required=False)
parser.add_argument("-language", type=str, required=False)
parser.add_argument("-qtty", type=int, required=False)
args = parser.parse_args()


positive = 0
negative = 0
neutral = 0
worst_tweet = Chjurchjulimu()
best_tweet = Chjurchjulimu()

chjurchjulime = []
t = 0
for raw_tweet in tweepy.Cursor(api.search, q=args.term, lang=args.language, tweet_mode="extended").items(args.qtty):
    t += 1
    print("Tweet " + str(t) + "/" + str(args.qtty))
    tweet = TextBlob(raw_tweet.full_text).correct()
    reactions = int(raw_tweet.favorite_count) + int(raw_tweet.retweet_count)
    chjurchjulime.append([raw_tweet.full_text, str(raw_tweet.created_at)[:10], "https://twitter.com/statuses/" + str(raw_tweet.id_str), tweet.polarity, reactions, raw_tweet.user.id_str])
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

data = pandas.DataFrame(chjurchjulime, columns=['Text', 'Date', 'Url', 'Polarity', 'Reactions', 'Users'])

print("Keyword : " + args.term)
print("Language : " + args.language)
print("Positive tweets : " + str((positive/args.qtty)*100) + "%")
print("Negative tweets : " + str((negative/args.qtty)*100) + "%")
print("Neutral tweets :| " + str((neutral/args.qtty)*100) + "%")
print("Quantity of tweets : " + str(args.qtty))
print("Number of Different posters : " + str(data["Users"].nunique()))
print("Number of days for all these tweets to be posted : " + str(data["Date"].value_counts()))
print("")
print("\nBest tweet : ")
print(best_tweet.to_string())
print("\nWorst tweet : ")
print(worst_tweet.to_string())

seaborn.set(style="darkgrid")

fig, ax = plt.subplots(1, 2)

seaborn.lineplot(x="Polarity", y="Reactions", data=data, ax=ax[0])
seaborn.barplot(x=data["Date"], y=data["Date"].nunique(), data=data, ax=ax[1])
plt.show()
