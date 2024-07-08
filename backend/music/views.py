from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth import admin
from django.contrib.auth.models import User 
from django.contrib.auth import authenticate ,login,logout
from django.contrib.auth.decorators import login_required
import requests
import base64
from dotenv import load_dotenv
load_dotenv()
import os
import urllib.parse

headers = {
            "x-rapidapi-key": "d14d415cd1mshc0efe0756b39d9ap1a83fejsn8508998dfdac",
            "x-rapidapi-host": "spotify-scraper.p.rapidapi.com"
        } 
@login_required(login_url='login')
def index(request):
    top_artists_list = top_artists()
    top_trackss_list = top_tracks()
    first_tracks = top_trackss_list[:6]
    second_tracks = top_trackss_list[6:12]
    third_tracks = top_trackss_list[12:]

    return render(request, 'index.html', {'artists':top_artists_list,
                                          'track1':first_tracks,
                                          'track2':second_tracks,
                                          'track3':third_tracks,
                                          })

def login_user(req):
    if req.method == 'POST':
        username = req.POST['username']
        password = req.POST['password']
        
        auth_user = authenticate(username=username, password=password)
        if auth_user is not None:
            user = User.get_full_name(User)
            
            login(req, auth_user)
             
            return redirect('/',{'user':user})     
        
        else:
            messages.info(req, "User Does not exist.")
            return redirect('login')
        
        
    return render(req, 'login.html')

def register(req):
    if req.method == 'POST':
        email = req.POST['email']
        username = req.POST['username']
        password = req.POST['password']
        password2 = req.POST['password2']
        
        if password != password2:
             messages.info(req,'Password does not match') 
             return redirect('register')
        else:
            if User.objects.filter(email=email).exists():
                messages.info(req, 'Email Already exist')
                return redirect('register')
            
            elif User.objects.filter(username=username).exists():
                 messages.info(req, 'Username Already exist')
                 return redirect('register')
             
            else:
                user = User.objects.create_user(username=username,email=email,password=password)
                user.save()
                
                auth_user = authenticate(username=username, password=password)
             
                login(req, auth_user)
                return redirect('/')                 
                
                
    else:
        return render(req,'signup.html')
    
@login_required(login_url='login')
def logout_user(req):
    logout(req)
    return redirect('login')

def top_artists():
    url = "https://api.spotify.com/v1/search/?q=pop&type=artist&limit=7"
    response_data = get_spotify_data(url)
    artists_info =[]
    
    if 'artists' in response_data:
        for artist in response_data['artists']['items']:
            name = artist['name'] if artist['name'] else None
            avatar_url = artist['images'][0]['url'] if artist['images'] else None
            artist_id = artist['id']
            
            artists_info.append((name, avatar_url, artist_id))
    return artists_info


def artist_profile(req,pk):
    url = "https://spotify-scraper.p.rapidapi.com/v1/artist/overview"

    querystring = {"artistId": pk}

    headers = {
        "x-rapidapi-key": "d14d415cd1mshc0efe0756b39d9ap1a83fejsn8508998dfdac",
        "x-rapidapi-host": "spotify-scraper.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)
    if response.status_code == 200:
        response_data = response.json()
        
        name = response_data['name']
        is_verified = response_data['verified']
        monthly_listeners = response_data['stats']['monthlyListeners']
        header_image = response_data['visuals']['header'][0]['url']
        
        track_info = []
        # track_info = []
        for track in response_data['discography']['topTracks']:
            track_id = track['id']
            track_name = track['name']
            duration = track['durationText']
            play_counts = track['playCount']
            image = track['album']['cover'][0]['url']
            
            artists = []
            for artist in track['artists']:
                artists.append(artist['name'])

            track_info.append({
                'track_id':track_id,
                'track_cover':image,
                'track_name':track_name,
                'duration':duration,
                'play_counts': play_counts,
                'artists':artists
            })
        
        artist_data = {
            'name':name,
            'monthly_listeners':monthly_listeners,
            'header_image':header_image,
            'is_verified': is_verified,
            'track_info': track_info
        }
    else:
       artist_data={}
       print('Error getting data.')    
    return render(req, 'profile.html', artist_data)

def top_tracks():
    query = "naija"
    query_encoded = urllib.parse.quote(query)
    url = f"https://api.spotify.com/v1/search?q={query_encoded}&type=track&limit=18"
    response_data = get_spotify_data(url)
    tracks_info =[]
    if 'tracks' in response_data:
        for track in response_data['tracks']['items']:
            track_id = track['id']
            track_name = track['name']
            artist_name = track['artists'][0]['name'] if track['artists'] else None
            avatar_url = track['album']['images'][0]['url'] if track['album'] else None
            
            tracks_info.append({'name':artist_name,'track_name':track_name, 'avatar_url':avatar_url, 'track_id':track_id})
    return tracks_info

def search(req,):
    if req.method == "POST":
        search_query = req.POST['search_query']
        
        url = "https://spotify-scraper.p.rapidapi.com/v1/search"

        querystring = {"term":search_query,"type":"all"}
        response = requests.get(url, headers=headers, params=querystring)

        if response.status_code == 200:
            response_data = response.json()
            
            if 'tracks' in response_data:
                total_count = response_data['tracks']['totalCount']
                tracks = response_data['tracks']['items']
                
                track_list =[]
                for track in tracks:
                    track_id = track['id']
                    duration = track['durationText']
                    name = track['name']
                    artist_name = track['artists'][0]['name']
                    
                    track_list.append({
                        'track_id': track_id,
                        'duration': duration,
                        'name': name,
                        'artist_name': artist_name
                    })
            context ={
                'total_count':total_count,
                'track_list':track_list
            }
            return render(req, 'search.html',context)
            
        
    else:
        return render(req, 'search.html')

def music(req,pk):
    url = f"https://api.spotify.com/v1/tracks/{pk}"
    response_data = get_spotify_data(url)
    
    if "album" in response_data:
        track_name = response_data['album']['name']
        artist_name = response_data['album']['artists'][0]['name'] if response_data['album']['artists'] else "No altist"
        cover = response_data['album']['images'][0]['url']
        audio_query = track_name + artist_name
        audio_details = get_audio_details(audio_query)
        audio_url = audio_details[0]
        duration_text = audio_details[1]
    return render(req, 'music.html',{'track_name':track_name,'artist_name':artist_name,'cover':cover,"audio_url":audio_url,"duration_text":duration_text})
    
def get_audio_details(query):
    
    url = "https://spotify-scraper.p.rapidapi.com/v1/track/download"

    querystring = {"track": query}

    response = requests.get(url, headers=headers, params=querystring)
    audio_details = []

    if response.status_code == 200:
        response_data = response.json()

        if 'youtubeVideo' in response_data and 'audio' in response_data['youtubeVideo']:
            audio_list = response_data['youtubeVideo']['audio']
            if audio_list:
                first_audio_url = audio_list[0]['url']
                duration_text = audio_list[0]['durationText']

                audio_details.append(first_audio_url)
                audio_details.append(duration_text)
            else:
                print("No audio data availble")
        else:
            print("No 'youtubeVideo' or 'audio' key found")
    else:
        print("Failed to fetch data")

    return audio_details

def get_spotify_access_token():
    client_id = os.environ.get('SPOTIFY_CLIENT_ID')
    client_secret = os.environ.get('SPOTIFY_CLIENT_SECRET')

    # Spotify token URL
    token_url = 'https://accounts.spotify.com/api/token'

    # Encode the client ID and client secret
    client_creds = f"{client_id}:{client_secret}"
    client_creds_b64 = base64.b64encode(client_creds.encode()).decode()

    # Set the headers and data for the request
    headers = {
        'Authorization': f'Basic {client_creds_b64}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {
        'grant_type': 'client_credentials'
    }

    # Make the request to get the access token
    response = requests.post(token_url, headers=headers, data=data)
    response_data = response.json()

    # Extract the access token from the response
    access_token = response_data['access_token']

    return access_token

def get_spotify_data(endpoint):
    access_token = get_spotify_access_token()
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.get(endpoint, headers=headers)
    response.raise_for_status()
    return response.json()