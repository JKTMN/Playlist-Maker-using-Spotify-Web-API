import base64
from datetime import datetime, timedelta
import json
from flask import Flask, jsonify, redirect, render_template, request, session, url_for
import requests
import os
from urllib.parse import urlencode
from dotenv import load_dotenv
import urllib.parse

load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
REDIRECT_URI = os.getenv('REDIRECT_URI')
AUTH_URL = "https://accounts.spotify.com/authorize"
TOKEN_URL = "https://accounts.spotify.com/api/token"
API_BASE_URL = "https://api.spotify.com/v1/"

@app.route('/')
def home():
    return "Welcome to my Spotify App <a href='/login'>Login with Spotify</a>"

@app.route('/login')
def login():
    scope = 'user-read-private user-read-email playlist-modify-private playlist-modify-public'

    params = {
        'client_id': CLIENT_ID,
        'response_type': 'code',
        'scope': scope,
        'redirect_uri': REDIRECT_URI,
        'show_dialog': True
    }

    auth_url = f"{AUTH_URL}?{urllib.parse.urlencode(params)}"

    return redirect(auth_url)


@app.route('/callback')
def callback():
    req_body = {
        'code': request.args['code'],
        'grant_type': 'authorization_code',
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }

    response = requests.post(TOKEN_URL, data=req_body)
    token_info = response.json()

    session['access_token'] = token_info['access_token']
    session['refresh_token'] = token_info['refresh_token']
    session['expires_at'] = datetime.now().timestamp() + token_info['expires_in']

    return redirect('/get-user-id')

@app.route('/refresh-token')
def refresh_token():
    if 'refresh_token' not in session:
        return redirect('/login')
    
    if datetime.now().timestamp() > session['expires_at']:
        req_body = {
            'grant_type': 'refresh_token',
            'refresh_token': session['refresh_token'],
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET
        }

        response = requests.post(TOKEN_URL, data=req_body)
        new_token_info = response.json

        session['access_token'] = new_token_info['access_token']
        session['expires_at'] = datetime.now().timestamp() + new_token_info['expires_in']

    return redirect('/search-for-artist')


@app.route('/get-access-token', methods=['POST'])
def get_access_token():
    auth_string = CLIENT_ID + ":" + CLIENT_SECRET
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    result = requests.post(url, headers=headers, data=data)
    json_result = json.loads(result.content)
    session['access_token'] = json_result["access_token"]
    return session['access_token']


@app.route('/get-auth-header')
def get_auth_header():
    return {"Authorization": "Bearer " + {session['access_token']}}


@app.route('/get-user-id', methods=['GET'])
def get_user_id():
    if 'access_token' not in session:
        return redirect('/login')

    if datetime.now().timestamp() > session['expires_at']:
        return redirect('/refresh-token')

    url = "https://api.spotify.com/v1/me"
    headers = {
        "Authorization": f"Bearer {session['access_token']}"
    }

    result = requests.get(url, headers=headers)

    json_result = result.json()
    user_id = json_result.get('id')
    session['user_id'] = user_id
    print(f"user id: {user_id}")

    return render_template("make_playlist.html")

@app.route('/submit', methods=['POST'])
def submit():
    session['artist'] = request.form.get('artist-name')
    return redirect('/search-for-artist')

@app.route('/search-for-artist', methods=['GET'])
def search_for_artist():
    if 'access_token' not in session or 'artist' not in session:
        return redirect('/login')

    url = "https://api.spotify.com/v1/search"
    headers = {
        "Authorization": f"Bearer {session['access_token']}"
    }

    query = {
        'q': session['artist'],
        'type': 'artist',
        'limit': 1
    }

    result = requests.get(url, headers=headers, params=query)
    json_result = result.json()
    artist_items = json_result.get('artists', {}).get('items', [])
    session['artists_id'] = artist_items[0].get('id', None)
    print("artist id: " + session['artists_id'])
    return redirect('/get-related-artists')

@app.route('/get-related-artists', methods=['GET'])
def get_related_artists():
    if 'access_token' not in session or 'artists_id' not in session:
        return redirect('/login')
    url=f"https://api.spotify.com/v1/artists/{session['artists_id']}/related-artists"
    headers = {
        "Authorization": f"Bearer {session['access_token']}"
    }

    response = requests.get(url, headers=headers)
    json_result = response.json()
    artists_items = json_result.get('artists', [])
    artist_ids = [artist.get('id', None) for artist in artists_items[:4]]

    session['artist_ids'] = artist_ids
    print(session['artist_ids'])
    return redirect('/get-recommendations')

@app.route('/get-recommendations', methods=['GET'])
def get_recommendations():
    if 'artists_id' not in session or 'artist_ids' not in session or 'access_token' not in session:
        return "Artist ID or related artist IDs missing", 400
    
    seed_artists = [session['artists_id']] + session['artist_ids']

    seed_artists = seed_artists[:5]

    url="https://api.spotify.com/v1/recommendations"
    headers = {
        "Authorization": f"Bearer {session['access_token']}"
    }

    query = {
        'seed_artists': ','.join(seed_artists),
        'limit': 30
    }

    response = requests.get(url, headers=headers, params=query)
    recomendations = response.json()
    track_uris = [track['uri'] for track in recomendations.get('tracks', [])]
    session['track_uris'] = track_uris
    print(f"track uri: {track_uris}")
    return redirect('/create-playlist-form')

@app.route('/create-playlist-form')
def create_playlist_form():
    return render_template('create_playlist.html')
    

@app.route('/create-playlist', methods=['POST'])
def create_playlist():
    if 'access_token' not in session or 'user_id' not in session:
        return redirect('/login')

    url = f"https://api.spotify.com/v1/users/{session['user_id']}/playlists"
    
    headers = {
        "Authorization": f"Bearer {session['access_token']}",
        "Content-Type": "application/json"
    }

    body = {
        "name": "User Generated Playlist",
        "description": "A playlist generated from a Spotify Web API app",
        "public": False
    }

    response = requests.post(url, headers=headers, json=body)
    result = response.json()
    
    playlist_id = result.get('id')
    session['playlist_id'] = playlist_id
    
    return jsonify({"message": "Playlist created successfully", "playlist_id": playlist_id, "redirect": "/add-to-playlist-form"}), 200

@app.route('/add-to-playlist-form')
def add_to_playlist_form():
    return render_template('add_to_playlist.html')

@app.route('/add-songs-to-playlist', methods=['POST'])
def add_songs_to_playlist():
    if 'access_token' not in session or 'playlist_id' not in session or 'track_uris' not in session:
        return redirect('/login')
    url = f"https://api.spotify.com/v1/playlists/{session['playlist_id']}/tracks"
    headers = {
        "Authorization": f"Bearer {session['access_token']}",
        "Content-Type": "application/json"
    }

    body = {
        "uris": session['track_uris']
    }

    print(body)

    response = requests.post(url, headers=headers, json=body)

    result = response.json()
    snapshot_id = result.get('snapshot_id')

    return render_template('playlist_successful.html')


    

#get genres
#get songs
#make playlist
#add songs to playlist



if __name__ == '__main__':
    app.run(debug=True)
