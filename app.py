from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
from dotenv import load_dotenv
from requests import post, get
import spotipy


app = Flask(__name__, static_folder="static", template_folder="templates")

load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

API_ENDPOINT = "https://api.spotify.com/v1"

def create_spotify_oauth():
    return spotipy.oauth2.SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=url_for("callback", _external=True),
        scope="user-read-private user-read-email user-read-playback-state user-modify-playback-state user-read-currently-playing user-top-read"
    )

def get_currently_playing():
    access_token = request.args.get("access_token")
    sp = spotipy.Spotify(auth=access_token)
    current_track = sp.current_user_playing_track()
    top_10_artists = sp.current_user_top_artists(limit=10)["items"]
    if current_track == None:
        return ["Nothing is currently playing", "https://i.kym-cdn.com/photos/images/original/002/139/758/0c4.jpg"]
    else:
        current_track_name = current_track["item"]["name"]
        current_track_image = current_track["item"]["album"]["images"][0]["url"]
        return [current_track_name, current_track_image, top_10_artists]

@app.route("/")
def login():
    sp_oauth = create_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route("/callback")
def callback():
    sp_oauth = create_spotify_oauth()
    code = request.args.get("code")
    token_info = sp_oauth.get_access_token(code)
    access_token = token_info["access_token"]
    return redirect(url_for("index", access_token=access_token))

@app.route("/index")
def index():
    access_token = request.args.get("access_token")
    sp = spotipy.Spotify(auth=access_token)
    user = sp.current_user()
    display_name = user["display_name"]
    display_image = user["images"][0]["url"]
    display_currently_playing = get_currently_playing()[0]
    display_currently_playing_image = get_currently_playing()[1]
    display_top_10_artists = get_currently_playing()[2]
    return render_template("index.html", 
    display_name=display_name, 
    display_image=display_image, 
    display_currently_playing=display_currently_playing,
    display_currently_playing_image=display_currently_playing_image,
    display_top_10_artists=display_top_10_artists)


if __name__ == "__main__":
    app.run(debug=True)