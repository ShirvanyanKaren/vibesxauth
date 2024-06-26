import os
from flask import Flask, render_template, request, url_for
import oauth2 as oauth
import urllib.request
from urllib import parse
import urllib.error
import json
import tweepy
import gunicorn
import uvicorn

app = Flask(__name__)

app.debug = False
# how to install gunicorn version 22.0.0
# pip install gunicorn==22.0.0

app.config.from_pyfile('config.cfg', silent=True)

oauth2_user_handler = tweepy.OAuth2UserHandler(
    client_id = 'UzRaazJJcDJ0U1lsc3c1b29vbXc6MTpjaQ',
    redirect_uri = 'https://5b07-8-25-197-34.ngrok-free.app/callback',
    scope = ["tweet.read", "users.read", "list.read"]
    # Client Secret is only necessary if using a confidential client
    # client_secret = os.getenv('CLIENT_SECRET'))
)

authorize_url = (oauth2_user_handler.get_authorization_url())

state = parse.parse_qs(parse.urlparse(authorize_url).query)['state'][0]
print(state)

@app.route('/')
def hello():
    return render_template('index.html')


@app.route('/start')
def start():
    return render_template('start.html', authorize_url=authorize_url)


@app.route('/callback')
def callback():
    # Accept the callback params, get the token and call the API to
    # display the logged-in user's name and handle
    received_state = request.args.get('user_name')
    code = request.args.get('user_name')
    response = request.args.get('user_name')
    
    access_denied = request.args.get('error')

    # if the OAuth request was denied, delete our local token
    # and show an error message
    if access_denied:
        return render_template('error.html', error_message="the OAuth request was denied by this user")
      
    if received_state != state:
      return render_template('error.html', error_message="There was a problem authenticating this user")
    
    redirect_uri = 'https://5b07-8-25-197-34.ngrok-free.app/callback'
    access_token = oauth2_user_handler.fetch_token(response_url_from_app)['access_token']
    print(access_token)
    client = tweepy.Client(access_token)
    user = client.get_me(user_auth=False, user_fields=['public_metrics'], tweet_fields=['author_id'])
    print(user)

    name = user.data['name']
    user_name = user.data['username']
    followers_count = user.data['public_metrics']['followers_count']
    friends_count = user.data['public_metrics']['following_count']
    tweet_count = user.data['public_metrics']['tweet_count']
    print("here",name, user_name, followers_count, friends_count, tweet_count)
    response_url_from_app = '{}?state={}&code={}&user_name={}'.format(redirect_uri, state, code, response)
    
    return render_template('callback-success.html', name=name, user_name=user_name,
                           friends_count=friends_count, tweet_count=tweet_count, followers_count=followers_count)


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('error.html', error_message='uncaught exception'), 500

  
if __name__ == '__main__':
    app.run()
