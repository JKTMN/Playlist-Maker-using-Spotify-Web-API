import os
from dotenv import load_dotenv
import base64
from requests import post, get
import json


load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_Secret = os.getenv("CLIENT_SECRET")

def get_token():
    auth_string = client_id + ":" + client_Secret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    result = post(url, headers=headers, data=data)
    json_result = json.loads(result.content)
    token = json_result["access_token"]
    return token


def get_auth_header(token):
    return {"Authorization": "Bearer " + token}

def search_for_artist(token, artist_name):
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    query = f"?q={artist_name}&type=artist&limit=1"
    
    query_uurl = url + query
    result = get(query_uurl, headers=headers)
    json_result = json.loads(result.content)["artists"]["items"]
    if len(json_result) == 0:
        print("No artist found")
        return None
    return json_result[0]

def search_for_artists(token, artists):
    artist_ids = ",".join(artists)
    url=f"https://api.spotify.com/v1/artists?ids={artist_ids}"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    json_result = json.loads(result.content)
    genres = []
    for artist in json_result["artists"]:
        genres.extend(artist["genres"])
    genres = list(set(genres))
    return genres

def get_songs_by_genres(token, genres):
    all_tracks = []
    for genre in genres:
        url = "https://api.spotify.com/v1/search"
        headers = get_auth_header(token)
        query = f"?q=genre:{genre}&type=track&limit=5"
        query_url = url + query
        result = get(query_url, headers=headers)
        json_result = json.loads(result.content)
        tracks = json_result.get("tracks", {}).get("items", [])
        if tracks:
            all_tracks.extend(track["name"] for track in tracks)
        else:
            print(f"No tracks found for genre: {genre}")
    return all_tracks
    


artists=["2p1fiYHYiXz9qi0JJyxBzN",
"4IZLJdhHCqAvT4pjn8TLH5",
"1AKNroq6zJX4DlJaA0dcKw",
"7k9T7lZlHjRAM1bb0r9Rm3",
"3S0tlB4fE7ChxI2pWz8Xip"]
token = get_token()
print(search_for_artists(token, artists))
genres = search_for_artists(token, artists)

songs = get_songs_by_genres(token, genres)
print(songs)