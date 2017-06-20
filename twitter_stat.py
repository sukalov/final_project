import json
import tweepy
import datetime
import time
from credentials import *
from flask import Flask
from flask import url_for, render_template, request, redirect
import matplotlib.pyplot as plt
from matplotlib import style
style.use('ggplot')

def init():
	global api
	auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
	auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
	api = tweepy.API(auth)

def limit_handled(cursor):
    while True:
        try:
            yield cursor.next()
        except tweepy.error.TweepError:
            time.sleep(15 * 60)

def twitter_search(word):
        i = 0
        tweetcount = {}
        for tweet in limit_handled(tweepy.Cursor(api.search, q=word).items()):
                if (not tweet.retweeted) and ('RT @' not in tweet.text):
                                if len(str(tweet.created_at.day)) == 1:
                                        day = '0' + str(tweet.created_at.day)
                                else:
                                        day = str(tweet.created_at.day)

                                if len(str(tweet.created_at.month)) == 1:
                                    mon = '0' + str(tweet.created_at.month)
                                else:
                                    mon = str(tweet.created_at.month)
                                    
                                date = day + '.' + mon + '.' + str(tweet.created_at.year)
                                if date in tweetcount:
                                        tweetcount[date] += 1
                                else:
                                        tweetcount[date] = 1
                                i += 1
                                if i >= 10000:
                                        break
        return tweetcount


def mondate(arr):
        mondate = arr[0].split('.')[2] + arr[0].split('.')[1] + arr[0].split('.')[0]
        return mondate

def realdate(strdate):
    realdate = datetime.date(int(strdate.split('.')[2]), int(strdate.split('.')[1]), int(strdate.split('.')[0]))
    return realdate

def strdate(realdate):
    strdate = realdate.strftime("%d.%m.%Y")
    return strdate

def sort_dates(tc):
    sorteddates = []
    for elem in tc:
        element = [elem, tc[elem]]
        sorteddates.append(element)
    sorteddates.sort(key=mondate)
    return sorteddates

def add_empty(tc):
    i = 0
    for date in tc:
        i += 1
        if i == 1:
            mindate = realdate(date)
            maxdate = realdate(date)
        elif realdate(date) < mindate:
            mindate = realdate(date)
        elif realdate(date) > maxdate:
            maxdate = realdate(date)
        
    d = mindate
    delta = datetime.timedelta(days=1)
    tc2 = tc
    
    while d < maxdate:
        d += delta
        if strdate(d) not in tc2:
            tc2[strdate(d)] = 0

    return tc2
       

def plot_draw(sd):
    X = []
    Y = []
    for elem in sd:
        X.append(elem[0])
        Y.append(elem[1])

    plt.plot(Y)
    plt.ylabel('количество упоминаний слова')
    plt.xlabel('дата')
    plt.xticks(range(len(sd)), [n[0] for n in sd], rotation='vertical')
    plt.subplots_adjust(bottom=0.25)
    plt.savefig('static/graph.png', format='png', dpi=100)


app = Flask(__name__)

@app.route('/')
def home():
        global word
        if request.args:
                word = request.args['word']
                return redirect(url_for('result'))
        return render_template ('home.html')


@app.route('/result')
def result():
        init()
        plot_draw(sort_dates(add_empty(twitter_search(word))))
        return render_template ('result.html', word=word)

if __name__ == '__main__':
    app.run()
