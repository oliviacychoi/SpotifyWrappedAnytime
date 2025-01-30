from flask import Flask, request, url_for, session, redirect, render_template
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time 
from credentials import CLIENT_ID, CLIENT_SECRET, SECRET_KEY
import os

TOKEN_INFO = "token_info"
SHORT_TERM = "short_term"
MEDIUM_TERM = "medium_term"
LONG_TERM = "long_term"

def create_spotify_oauth():
    return SpotifyOAuth(
        client_id = CLIENT_ID,
        client_secret = CLIENT_SECRET,
        redirect_uri = url_for('redirectPage', _external=True),
        scope = 'user-top-read user-library-read')
     

app = Flask(__name__)
app.secret_key = SECRET_KEY
app.config['SESSION_COOKIE_NAME'] = 'Spotify Cookie'


@app.route("/")
def mainPage():
    return render_template('mainPage.html')

@app.route("/login")
def login():
    sp_oauth = create_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)
    

@app.route("/redirectPage")
def redirectPage():
    sp_oauth = create_spotify_oauth()
    session.clear()
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session[TOKEN_INFO] = token_info
    return redirect(url_for("results", _external=True))

def get_token():
    token_info = session.get(TOKEN_INFO,None)
    if not token_info:
        raise 'exception'
    now = int(time.time())
    is_expired = token_info['expires_at'] - now < 60 
    if (is_expired): 
        sp_oauth = create_spotify_oauth()
        token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
    return token_info 

@app.route("/results")
def results():
    user_token = get_token()
    sp = spotipy.Spotify(
        auth=user_token['access_token']
    )
    if os.path.exists(".cache"): 
        os.remove(".cache")
    current_user_name = sp.current_user()['display_name']
    short_term = sp.current_user_top_tracks(limit=10,offset=0,time_range=SHORT_TERM)
    medium_term = sp.current_user_top_tracks(limit=10,offset=0,time_range=MEDIUM_TERM)
    long_term = sp.current_user_top_tracks(limit=10,offset=0,time_range=LONG_TERM)

    return render_template(
        'results.html', 
        user_display_name=current_user_name, 
        short_term=short_term, 
        medium_term=medium_term, 
        long_term=long_term)

if __name__ == '__main__':
    app.run()