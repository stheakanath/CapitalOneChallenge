import bottle
import webbrowser
import beaker.middleware
import sys
import operator
import io
import csv
import math
from bottle import route, redirect, post, run, request, hook
from instagram import client
from bottle import static_file

def load_sentiments(path="sentiments.csv"):
    """Read the sentiment file and return a dictionary containing the sentiment
    score of each word, a value from -1 to +1.
    """
    with io.open(path, encoding='utf8') as sentiment_file:
        scores = [line.split(',') for line in sentiment_file]
        return {word: float(score.strip()) for word, score in scores}

word_sentiments = load_sentiments()

def sentence_sentiment(str):
    str_split, sentiment, count = str.split(), 0, 0
    for word in str_split:
        if word_sentiments.get(word) != None:
            sentiment += word_sentiments.get(word)
            count += 1
    if count == 0:
        return 0.0
    return sentiment / count

bottle.debug(True)

session_opts = {
    'session.type': 'file',
    'session.data_dir': './session/',
    'session.auto': True,
}

app = beaker.middleware.SessionMiddleware(bottle.app(), session_opts)

CONFIG = {
    'client_id': "5ef9df4d2aa445f19632adfb483fb4c0",
    'client_secret': "92c457fbbdd94ab6947311c8332fcf6c",
    'redirect_uri': 'http://localhost:8515/oauth_callback'
}

unauthenticated_api = client.InstagramAPI(**CONFIG)

@hook('before_request')
def setup_request():
    request.session = request.environ['beaker.session']

@route('/')
def home():
    return static_file('index.html', root='') 

@route('/static/:path#.+#', name='static')
def static(path):
    return static_file(path, root='static')

@route('/oauth_callback')
def on_callback():
    code = request.GET.get("code")
    if not code:
        return 'Missing code'
    try:
        access_token, user_info = unauthenticated_api.exchange_code_for_access_token(code)
        if not access_token:
            return 'Could not get access token'
        api = client.InstagramAPI(access_token=access_token, client_secret=CONFIG['client_secret'])
        request.session['access_token'] = access_token
    except Exception as e:
        print(e)
    #return static_file('loading.html', root='')
    print "Pulling data"
    return get_data(20)
    print "finished getting data"
    return static_file('data.html', root='')
    

def get_data(x):
    r_id = 1
    access_token = request.session['access_token']
    if not access_token:
        return 'Missing Access Token'
    try:
        c = csv.writer(open("static/data.csv", "wb"))
        c.writerow(["user_id", "id", "size", "likes","date","link","group"])
        api = client.InstagramAPI(access_token=access_token, client_secret=CONFIG['client_secret'])
        recent_media, next = api.tag_recent_media(count=x, max_id=1, tag_name="CapitalOne")
        photos = []
        data, userArr = [], []
        senti, visual_senti = "med", "Positive"
        total_positive, total_neutral, total_negative = 0, 0, 0
        for media in recent_media:
            sentiment = sentence_sentiment(media.caption.text.replace("\n", "").replace("#", ""))
            if sentiment > 0:
                total_positive += 1
                senti, visual_senti = "high", "Positive"
            elif sentiment < 0:
                total_negative += 1
                senti, visual_senti = "low", "Negative"
            else:
                total_neutral += 1
                senti, visual_senti = "medium", "None"
            c.writerow([media.user.username, r_id, math.log(media.like_count + 1, 10) * 5 + 10, media.like_count, media.created_time, media.link, senti])
            user_item = api.user(media.user.id).counts
            r_id += 1
            data.append([str(media.id), str(media.created_time), str(media.like_count), visual_senti])
            userArr.append([str(media.id), media.user.username, str(user_item["followed_by"]), str(user_item["follows"])])
        return createHtml(data, userArr, {"Positive": total_positive, "Negative": total_negative, "Neutral":total_neutral})
    except Exception as e:
        print(e)
    
def createHtml(dataArr, userArr, total_details):
	htmlStr = """<!doctype html><head><meta charset="utf-8"><title>Instagram #CapitalOne Sentiment Trends</title><link rel="stylesheet" href="static/reset.css"><link rel="stylesheet" href="http://maxcdn.bootstrapcdn.com/bootstrap/3.3.5/css/bootstrap.min.css"><link rel="stylesheet" href="static/style.css"><script src="static/modernizr-2.0.6.min.js"></script></head><body><div id="container" class="container"><header></br><h1>Instagram #CapitalOne Sentiment Trends</h1><h3>by Kuriakose Sony Theakanath</h3></header><div id="main" role="main"><div id="vis"></div></div><footer><p><b>Hover over bubbles to see details about each Instagram post<b></br>#CapitalOne is currently trending """
	htmlStr += max(total_details.iteritems(), key=operator.itemgetter(1))[0]
	htmlStr += """!</p></footer></br><h2>Instagram Posts of #CapitalOne</h2><table class="table"><thead><tr><th>Instagram Post ID</th><th>Post Date</th><th>Likes</th><th>Sentiment</th></tr></thead><tbody>"""

    # Dynamically create the table
	for elem in dataArr:
		cred = "<tr>"
		for item in elem:
			cred += ("<td>" + item + "</td>")
		cred += "</tr>"
		htmlStr += cred
	htmlStr += """</tbody></table><h2>User Details</h2><table class="table"><thead><tr><th>Instagram Post ID</th><th>Username</th><th>Num of Followers</th><th>Num Following</th></tr></thead><tbody>"""
	for elem in userArr:
		cred = "<tr>"
		for item in elem:
			cred += ("<td>" + item + "</td>")
		cred += "</tr>"
		htmlStr += cred
	htmlStr += ("""</tbody></table><h2>""" + "Positive posts: " + str(total_details["Positive"]) + " | Negative posts: " + str(total_details["Negative"]) + " | Netural posts: " + str(total_details["Neutral"]) + "</h2>")
	htmlStr += """</div><script>window.jQuery || document.write('<script src="static/jquery-1.6.2.min.js"><\/script>')</script><script defer src="static/plugins.js"></script><script defer src="static/script.js"></script><script src="static/CustomTooltip.js"></script><script src="static/coffee-script.js"></script><script src="static/d3.js"></script><script type="text/coffeescript" src="static/vis.coffee"></script><script type="text/javascript">$(document).ready(function() {$(document).ready(function() {$('#view_selection a').click(function() {var view_type = $(this).attr('id');$('#view_selection a').removeClass('active');$(this).toggleClass('active');toggle_view(view_type);return false;});});});</script></body></html> """
	return htmlStr 

# Let's run the whole thing!
bottle.run(app=app, host='localhost', port=8515, reloader=True)
