#%%

import requests
import time
import json
from datetime import datetime, timedelta
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd

API_KEY = '26f21ff2e4773c9c6581ae2cd5ed55a0'
BASE_URL = 'http://ws.audioscrobbler.com/2.0/'
REQUEST_DELAY = 4  
VALIDITY_PERIOD_HOURS = 72


# MongoDB setup
client = MongoClient('localhost', 27017)
db = client['SD2024_projet']

collections = ['GOAOK_artists', 'GOAOK_albums', 'GOAOK_tracks', 'GOAOK_tags', 'GOAOK_trends', 'GOAOK_reviews']
for collection in collections:
    if collection not in db.list_collection_names():
        db.create_collection(collection)

artists_collection = db['GOAOK_artists']
albums_collection = db['GOAOK_albums']
tracks_collection = db['GOAOK_tracks']
tags_collection = db['GOAOK_tags']
trends_collection = db['GOAOK_trends']
reviews_collection = db['GOAOK_reviews']  
users_collection = db['GOAOK_users']  

def recommend_similar_tracks_based_on_reviews(username):
    # Extraire les avis de la collection
    reviews = list(reviews_collection.find({}, {"_id": 0, "artist": 1, "song": 1, "review": 1}))
    if not reviews:
        print("No reviews found in the database.")
        return []

    # Créer un DataFrame et vérifier les champs nécessaires
    df = pd.DataFrame(reviews)
    if "review" not in df.columns or "song" not in df.columns or "artist" not in df.columns:
        print("Required columns missing in DataFrame.")
        return []

    # Nettoyer les données
    df = df.dropna(subset=["review", "song", "artist"])

    # Avis utilisateur
    user_reviews = list(reviews_collection.find({"username": username}, {"_id": 0, "review": 1}))
    if not user_reviews:
        print(f"No reviews found for user: {username}")
        return []

    # Texte des avis utilisateur
    user_review_text = " ".join([review["review"] for review in user_reviews])
    df = pd.concat([df, pd.DataFrame([{"review": user_review_text}])], ignore_index=True)

    # TF-IDF et Similarité Cosine
    tfidf = TfidfVectorizer(stop_words="english")
    tfidf_matrix = tfidf.fit_transform(df["review"].fillna(""))
    cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

    # Trouver les indices similaires
    user_idx = len(df) - 1
    similar_indices = cosine_sim[user_idx].argsort()[-10:-1][::-1]

    # Générer des recommandations tout en évitant les doublons
    recommendations = []
    seen = set()  # Utiliser un ensemble pour vérifier les doublons
    for idx in similar_indices:
        track_info = df.iloc[idx]
        song = track_info["song"]
        artist = track_info["artist"]
        if (song, artist) not in seen and pd.notna(song) and pd.notna(artist):
            recommendations.append({
                "song": song,
                "artist": artist
            })
            seen.add((song, artist))  # Ajouter la combinaison à l'ensemble

    return recommendations




def is_data_outdated(last_updated, validity_period=VALIDITY_PERIOD_HOURS):
    return datetime.now() - last_updated > timedelta(hours=validity_period)



def create_user(username, password, is_admin=False):
    hashed_password = generate_password_hash(password)
    user = {'username': username, 'password': hashed_password, 'is_admin': is_admin}
    users_collection.insert_one(user)

def get_user(username):
    user = users_collection.find_one({'username': username})
    if user and 'is_admin' not in user:
        user['is_admin'] = False  # Default to False if the field is missing
    return user

def verify_password(username, password):
    user = get_user(username)
    if user and check_password_hash(user['password'], password):
        return True
    return False



# Local Query Functions


#### 1
def get_tag_info(tag):
    params = {
        'method': 'tag.getinfo',
        'tag': tag,
        'api_key': API_KEY,
        'format': 'json'
    }
    response = requests.get(BASE_URL, params=params)
    time.sleep(REQUEST_DELAY) #delay of 4 secs
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print(f"Error fetching tag info for {tag}: {response.status_code}")
        return None


def get_album_info(artist, album):
    params = {
        'method': 'album.getinfo',
        'artist': artist,
        'album': album,
        'autocorrect':1,
        'api_key': API_KEY,
        'format': 'json'
    }
    response = requests.get(BASE_URL, params=params)
    time.sleep(REQUEST_DELAY)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print(f"Error fetching album info for {artist} - {album}: {response.status_code}")
        return None


def get_artist_info(artist):
    params = {
        'method': 'artist.getinfo',
        'artist': artist,
        'autocorrect':1,
        'api_key': API_KEY,
        'format': 'json'
    }
    response = requests.get(BASE_URL, params=params)
    time.sleep(REQUEST_DELAY)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print(f"Error fetching artist info for {artist}: {response.status_code}")
        return None

#  2
def get_top_tracks():
    params = {
        'method': 'chart.gettoptracks',
        'api_key': API_KEY,
        'format': 'json',
        'limit': 10
    }
    response = requests.get(BASE_URL, params=params)
    time.sleep(REQUEST_DELAY)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print(f"Error fetching top tracks: {response.status_code}")
        return None



def get_top_artists():
    params = {
        'method': 'chart.gettopartists',
        'api_key': API_KEY,
        'format': 'json',
        'limit': 10
    }
    response = requests.get(BASE_URL, params=params)
    time.sleep(REQUEST_DELAY)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print(f"Error fetching top artists: {response.status_code}")
        return None


def get_top_tags():
    params = {
        'method': 'chart.gettoptags',
        'api_key': API_KEY,
        'format': 'json',
        'limit': 10
    }
    response = requests.get(BASE_URL, params=params)
    time.sleep(REQUEST_DELAY)

    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print(f"Error fetching top tags: {response.status_code}")
        return None

def get_top_tracks_by_country(country):
    params = {
        'method': 'geo.gettoptracks',
        'country': country,
        'api_key': API_KEY,
        'format': 'json',
        'limit': 10
    }
    response = requests.get(BASE_URL, params=params)
    time.sleep(REQUEST_DELAY)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print(f"Error fetching top tracks: {response.status_code}")
        return None


def get_top_artists_by_country(country):
    params = {
        'method': 'geo.gettopartists',
        'country': country,
        'api_key': API_KEY,
        'format': 'json',
        'limit': 10
    }
    response = requests.get(BASE_URL, params=params)
    time.sleep(REQUEST_DELAY)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print(f"Error fetching top artists: {response.status_code}")
        return None

# 3 in store data section
# 3
def store_top_tracks(top_tracks):
    top_tracks['last_updated'] = datetime.now()
    trends_collection.update_one({'type': 'top_tracks'}, {'$set': top_tracks}, upsert=True)

def store_top_artists(top_artists):
    top_artists['last_updated'] = datetime.now()
    trends_collection.update_one({'type': 'top_artists'}, {'$set': top_artists}, upsert=True)

def store_top_tags(top_tags):
    top_tags['last_updated'] = datetime.now()
    trends_collection.update_one({'type': 'top_tags'}, {'$set': top_tags}, upsert=True)

def log_trend_query(trend_type, trend_data):
    log_entry = {
        'last_updated': datetime.now(),
        'type': trend_type,
        '$set': trend_data
    }
    trends_collection.insert_one(log_entry)

def get_trend_logs():
    logs = trends_collection.find({'type': {'$in': ['top_tracks', 'top_artists', 'top_tags']}}).sort('last_updated', -1)
    return list(logs)

# 4
def get_similar_artists(artist):
    params = {
        'method': 'artist.getsimilar',
        'artist': artist,
        'autocorrect':1,
        'api_key': API_KEY,
        'format': 'json',
        'limit': 3
    }
    response = requests.get(BASE_URL, params=params)
    time.sleep(REQUEST_DELAY)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print(f"Error fetching similar artists for {artist}: {response.status_code}")
        return None
    
def get_similar_tracks(track, artist):
    params = {
        'method': 'track.getsimilar',
        'track' : track,
        'artist': artist,
        'autocorrect':1,
        'api_key': API_KEY,
        'format': 'json',
        'limit': 3
    }
    response = requests.get(BASE_URL, params=params)
    time.sleep(REQUEST_DELAY)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print(f"Error fetching similar tracks for {track} - {artist}: {response.status_code}")
        return None

def get_artist_top_albums(artist):
    params = {
        'method': 'artist.gettopalbums',
        'artist': artist,
        'autocorrect':1,
        'api_key': API_KEY,
        'format': 'json',
        'limit': 3
    }
    response = requests.get(BASE_URL, params=params)
    time.sleep(REQUEST_DELAY)
    return response.json()

def get_artist_top_tracks(artist):
    params = {
        'method': 'artist.gettoptracks',
        'artist': artist,
        'autocorrect':1,
        'api_key': API_KEY,
        'format': 'json',
        'limit': 3
    }
    response = requests.get(BASE_URL, params=params)
    time.sleep(REQUEST_DELAY)
    return response.json()

def search_similar_albums_songs(artist):
    similar_artists = get_similar_artists(artist)
    similar_albums_songs = []
    
    for similar_artist in similar_artists['similarartists']['artist']:
        artist_name = similar_artist['name']
        top_albums = get_artist_top_albums(artist_name)
        top_tracks = get_artist_top_tracks(artist_name)
        
        similar_albums_songs.append({
            'artist': artist_name,
            'top_albums': top_albums['topalbums']['album'],
            'top_tracks': top_tracks['toptracks']['track']
        })
    
    return similar_albums_songs

# similar_albums_songs = search_similar_albums_songs('Radiohead')
# print(similar_albums_songs)

# 5


def search_artists_by_listens(operator, threshold):
    if operator not in ['greater', 'less']:
        raise ValueError("Operator must be 'greater' or 'less'")
    query = {'artist.stats.playcount': {'$gt' if operator == 'greater' else '$lt': threshold}}
    results = list(artists_collection.find(query))
    for result in results:
        last_updated = result.get('last_updated')
        if last_updated and is_data_outdated(last_updated):
            print(f"Data for artist {result['artist']['name']} is outdated.")
            new_data = fetch_new_artist_data(result['artist']['name'])
            if new_data:
                artists_collection.update_one({'_id': result['_id']}, {'$set': new_data})

            
    
    return results

def search_albums_by_listens(operator, threshold):
    if operator not in ['greater', 'less']:
        raise ValueError("Operator must be 'greater' or 'less'")
    query = {'album.playcount': {'$gt' if operator == 'greater' else '$lt': threshold}}
    results = list(albums_collection.find(query))
    
    for result in results:
        last_updated = result.get('last_updated')
        if last_updated and is_data_outdated(last_updated):
            print(f"Data for album {result['album']['name']} is outdated.")
            new_data = fetch_new_album_data(result['album']['artist'], result['album']['name'])
            if new_data:
                albums_collection.update_one({'_id': result['_id']}, {'$set': new_data})
    
    return results

def search_tracks_by_listens(operator, threshold):
    if operator not in ['greater', 'less']:
        raise ValueError("Operator must be 'greater' or 'less'")
    query = {'track.playcount': {'$gt' if operator == 'greater' else '$lt': threshold}}
    results = list(tracks_collection.find(query))
    
    for result in results:
        last_updated = result.get('last_updated')
        if last_updated and is_data_outdated(last_updated):
            print(f"Data for song {result['track']['name']} is outdated.")
            new_data = fetch_new_track_data(result['track']['artist']['name'], result['track']['name'])
            if new_data:
                tracks_collection.update_one({'_id': result['_id']}, {'$set': new_data})
    
    return results


def fetch_new_artist_data(artist_name):
    params = {
        'method': 'artist.getinfo',
        'artist': artist_name,
        'api_key': API_KEY,
        'format': 'json'
    }
    response = requests.get(BASE_URL, params=params)
    time.sleep(REQUEST_DELAY)
    if response.status_code == 200:
        data = response.json()
        artist_info = {
            'artist.name': data['artist']['name'],
            'artist.stats.playcount': data['artist']['stats']['playcount'],
            'last_updated': datetime.now()
        }
        return artist_info
    else:
        print(f"Error fetching new data for artist {artist_name}: {response.status_code}")
        return None

def fetch_new_album_data(artist_name, album_name):
    params = {
        'method': 'album.getinfo',
        'artist': artist_name,
        'album': album_name,
        'api_key': API_KEY,
        'format': 'json'
    }
    response = requests.get(BASE_URL, params=params)
    time.sleep(REQUEST_DELAY)
    if response.status_code == 200:
        data = response.json()
        album_info = {
            'album.artist': data['album']['artist'],
            'album.name': data['album']['name'],
            'album.playcount': data['album']['playcount'],
            'last_updated': datetime.now()
        }
        return album_info
    else:
        print(f"Error fetching new data for album {album_name} by {artist_name}: {response.status_code}")
        return None

def fetch_new_track_data(artist_name, song_title):
    params = {
        'method': 'track.getinfo',
        'artist': artist_name,
        'track': song_title,
        'api_key': API_KEY,
        'format': 'json'
    }
    response = requests.get(BASE_URL, params=params)
    time.sleep(REQUEST_DELAY)
    if response.status_code == 200:
        data = response.json()
        song_info = {
            'track.artist.name': data['track']['artist']['name'],
            'track.name': data['track']['name'],
            'track.playcount': data['track']['playcount'],
            'last_updated': datetime.now()
        }
        return song_info
    else:
        print(f"Error fetching new data for song {song_title} by {artist_name}: {response.status_code}")
        return None

# Example usage
# artists_with_high_listens = search_by_listens(artists_collection, min_listens=10000)
# print(artists_with_high_listens)

# 6

def search_reviews_for_artist(artist_name):
    query = {'artist': artist_name}
    results = list(reviews_collection.find(query, {'_id': 0}))
    return results

def search_reviews_for_album(artist_name, album_name):
    query = {'artist': artist_name, 'album': album_name}
    results = list(reviews_collection.find(query, { '_id': 0}))
    return results

def search_reviews_for_song(artist_name, song_title):
    query = {'artist': artist_name, 'song': song_title}
    results = list(reviews_collection.find(query, {'_id': 0}))
    return results

# c
# functions to submitt rew]views
def submit_tag_review(username, tag, review_text, rating):
    if rating < 0 or rating > 5:
        return False, "Rating must be between 0 and 5"
    review = {
        "username": username,
        "tag": tag,
        "review": review_text,
        "rating": rating,
        "date": datetime.now()
    }
    reviews_collection.insert_one(review)
    return True, "Tag review submitted successfully"

def submit_album_review(username, artist, album, review_text, rating):
    if rating < 0 or rating > 5:
        return False, "Rating must be between 0 and 5"
    review = {
        "username": username,
        "artist": artist,
        "album": album,
        "review": review_text,
        "rating": rating,
        "date": datetime.now()
    }
    reviews_collection.insert_one(review)
    return True, "Album review submitted successfully"

def submit_song_review(username, artist, song, review_text, rating):
    if rating < 0 or rating > 5:
        return False, "Rating must be between 0 and 5"
    review = {
        "username": username,
        "artist": artist,
        "song": song,
        "review": review_text,
        "rating": rating,
        "date": datetime.now()
    }
    reviews_collection.insert_one(review)
    return True, "Song review submitted successfully"



# Access Static Information from MongoDB
def get_local_tag_info(tag):
    return tags_collection.find_one({'tag.name': tag})

def get_local_album_info(artist, album):
    return albums_collection.find_one({'album.artist': artist, 'album.name': album})


def get_local_artist_info(artist):
    return artists_collection.find_one({'artist.name': artist})

def get_local_top_tracks():
    return trends_collection.find_one({'type': 'top_tracks'})

def get_local_top_artists():
    return trends_collection.find_one({'type': 'top_artists'})

def get_local_top_tags():
    return trends_collection.find_one({'type': 'top_tags'})

# #####################################################################################################
# Storing Data Locally in MongoDB



def store_tag_info(tag_info):
    if tag_info and 'tag' in tag_info:
        tag_name = tag_info['tag'].get('name', 'Unknown Tag')
        tag_info['last_updated'] = datetime.now()
        tags_collection.update_one({'tag.name': tag_name}, {'$set': tag_info}, upsert=True)
    else:
        print(f"Invalid tag info: {tag_info}")


def store_album_info(album_info):
    if album_info and 'album' in album_info:
        album = album_info['album']
        artist_name = album.get('artist', 'Unknown Artist')
        album_title = album.get('name', 'Unknown Album')
        album_info['last_updated'] = datetime.now()
        albums_collection.update_one({'album.artist': artist_name, 'album.name': album_title}, {'$set': album_info}, upsert=True)
    else:
        print(f"Invalid album info: {album_info}")

def store_artist_info(artist_info):
    if artist_info and 'artist' in artist_info:
        artist_name = artist_info['artist'].get('name', 'Unknown Artist')
        artist_info['last_updated'] = datetime.now()
        artists_collection.update_one({'artist.name': artist_name}, {'$set': artist_info}, upsert=True)
    else:
        print(f"Invalid artist info: {artist_info}")


#############


########################################################################
# Remote Query

    
# Function to perform the query
def query(query_type, **kwargs):
    if query_type == 'tag_info':
        local_data = get_local_tag_info(kwargs['tag'])
        if local_data:
            last_updated = local_data.get('last_updated')
            if last_updated and not is_data_outdated(last_updated):
                return local_data, 'local'
        remote_data = get_tag_info(kwargs['tag'])
        if remote_data:
            store_tag_info(remote_data)
            return remote_data, 'remote'
        else:
            return None, 'error'

    elif query_type == 'album_info':
        local_data = get_local_album_info(kwargs['artist'], kwargs['album'])
        if local_data:
            last_updated = local_data.get('last_updated')
            if last_updated and not is_data_outdated(last_updated):
                return local_data, 'local'
        remote_data = get_album_info(kwargs['artist'], kwargs['album'])
        if remote_data:
            store_album_info(remote_data)
            return remote_data, 'remote'
        else:
            return None, 'error'

    elif query_type == 'artist_info':
        local_data = get_local_artist_info(kwargs['artist'])
        if local_data:
            last_updated = local_data.get('last_updated')
            if last_updated and not is_data_outdated(last_updated):
                return local_data, 'local'
        remote_data = get_artist_info(kwargs['artist'])
        if remote_data:
            store_artist_info(remote_data)
            return remote_data, 'remote'
        else:
            return None, 'error'

    elif query_type == 'top_tracks':
        
        remote_data = get_top_tracks()
        if remote_data:
            log_trend_query('top_tracks',remote_data)
            return remote_data, 'remote'
        else:
            return None, 'error'

    elif query_type == 'top_tags':
        
        remote_data = get_top_tags()
        if remote_data:
            log_trend_query('top_tags',remote_data)
            return remote_data, 'remote'
        else:
            return None, 'error'

    elif query_type == 'top_artists':
    
        remote_data = get_top_artists()
        if remote_data:
            log_trend_query('top_artists',remote_data)
            return remote_data, 'remote'
        else:
            return None, 'error'

    elif query_type == 'top_tracks_by_country':
        remote_data = get_top_tracks_by_country(kwargs['country'])
        if remote_data:
            return remote_data, 'remote'
        else:
            return None, 'error'
    
    elif query_type == 'top_artists_by_country':
        remote_data = get_top_artists_by_country(kwargs['country'])
        if remote_data:
            return remote_data, 'remote'
        else:
            return None, 'error'
            
    elif query_type == 'trend_logs':
        return get_trend_logs(), 'local'

    elif query_type == 'similar_albums_songs':
        remote_data = search_similar_albums_songs(kwargs['artist'])
        if remote_data:
            return remote_data, 'remote'
        else:
            return None, 'error'
    
    elif query_type == 'similar_artists':
        remote_data = get_similar_artists(kwargs['artist'])
        if remote_data:
            return remote_data, 'remote'
        else:
            return None, 'error'
    
    elif query_type == 'search_artists_by_listens':
        return search_artists_by_listens(kwargs['operator'], kwargs['threshold']), 'local'

    elif query_type == 'search_albums_by_listens':
        return search_albums_by_listens(kwargs['operator'], kwargs['threshold']), 'local'

    elif query_type == 'search_songs_by_listens':
        return search_tracks_by_listens(kwargs['operator'], kwargs['threshold']), 'local'
    
    elif query_type == 'search_reviews_for_artist':
        return search_reviews_for_artist(kwargs['artist']), 'local'

    elif query_type == 'search_reviews_for_album':
        return search_reviews_for_album(kwargs['artist'], kwargs['album']), 'local'

    elif query_type == 'search_reviews_for_song':
        return search_reviews_for_song(kwargs['artist'], kwargs['song']), 'local'
    
    elif query_type == 'submit_tag_review':
        return submit_tag_review(kwargs['username'], kwargs['tag'], kwargs['review_text'], kwargs['rating'])

    elif query_type == 'submit_album_review':
        return submit_album_review(kwargs['username'], kwargs['artist'], kwargs['album'], kwargs['review_text'], kwargs['rating'])

    elif query_type == 'submit_song_review':
        return submit_song_review(kwargs['username'], kwargs['artist'], kwargs['song'], kwargs['review_text'], kwargs['rating'])
    
    else:
        return None, 'not_found'

    

# Example usage
# if __name__ == '__main__':

#     # Example of registering and logging in a user
#     username = "test_user2"
#     password = "password1234"
    
#     # Register user
#     success, message = register_user(username, password)
#     print(message)
    
#     # Authenticate user
#     success, message = authenticate_user(username, password)
#     print(message)
    
#     if success:
#         # Submit a tag review
#         tag = "rock"
#         review_text = "Rock music is very energetic and diverse."
#         rating = 5
#         success, message = query('submit_tag_review', username=username, tag=tag, review_text=review_text, rating=rating)
#         print(message)

#         # Submit an album review
#         artist = "Radiohead"
#         album = "OK Computer"
#         review_text = "An amazing album with deep lyrics and captivating melodies."
#         rating = 5
#         success, message = query('submit_album_review', username=username, artist=artist, album=album, review_text=review_text, rating=rating)
#         print(message)

#         # Submit a song review
#         artist = "Radiohead"
#         song = "Karma Police"
#         review_text = "A hauntingly beautiful song with powerful lyrics."
#         rating = 5
#         success, message = query('submit_song_review', username=username, artist=artist, song=song, review_text=review_text, rating=rating)
#         print(message)

#     # Query for tag information
#     tag_name = 'rock'
#     tag_data, tag_source = query('tag_info', tag=tag_name)
#     print(f"Tag Data: {tag_data}, Source: {tag_source}")

#     # Query for album information
#     artist_name = 'Radiohead'
#     album_name = 'OK Computer'
#     album_data, album_source = query('album_info', artist=artist_name, album=album_name)
#     print(f"Album Data: {album_data}, Source: {album_source}")

#     # Query for artist information
#     artist_name = 'Radiohead'
#     artist_data, artist_source = query('artist_info', artist=artist_name)
#     print(f"Artist Data: {artist_data}, Source: {artist_source}")

#     # Query for top tracks
#     top_tracks_data, top_tracks_source = query('top_tracks')
#     print(f"Top Tracks Data: {top_tracks_data}, Source: {top_tracks_source}")

#     # Query for top tags
#     top_tags_data, top_tags_source = query('top_tags')
#     print(f"Top Tags Data: {top_tags_data}, Source: {top_tags_source}")

#     # Query for top albums
#     top_artists_data, top_artists_source = query('top_artists')
#     print(f"Top Artists Data: {top_artists_data}, Source: {top_artists_source}")

#     # Query for top tracks by country
#     country_name = 'United States'
#     top_tracks_by_country_data, top_tracks_by_country_source = query('top_tracks_by_country', country=country_name)
#     print(f"Top Tracks by Country Data: {top_tracks_by_country_data}, Source: {top_tracks_by_country_source}")

#     # Query for top artists by country
#     top_artists_by_country_data, top_artists_by_country_source = query('top_artists_by_country', country=country_name)
#     print(f"Top Artists by Country Data: {top_artists_by_country_data}, Source: {top_artists_by_country_source}")

#     # Get trend logs
#     trend_logs_data, trend_logs_source = query('trend_logs')
#     print(f"Trend Log Data: {trend_logs_data}, Source: {trend_logs_source}")
    
#     # Query for similar artists
#     artist_name = 'Radiohead'
#     similar_artist_data, similar_artist_source = query('similar_artists', artist=artist_name)
#     print(f"Similar Artists Data: {similar_artist_data}, Source: {similar_artist_source}")


#     # Query for similar albums and songs
#     artist_name = 'Radiohead'
#     similar_albums_songs_data, similar_albums_songs_source = query('similar_albums_songs', artist=artist_name)
#     print(f"Similar Albums and Songs Data: {similar_albums_songs_data}, Source: {similar_albums_songs_source}")

#     listens_threshold = "9999999"
#     search_results, search_source = query('search_artists_by_listens', operator='less', threshold=listens_threshold)
#     print(f"Search Results for Artists: {search_results}, Source: {search_source}")

#     # Search for albums with listens greater than a threshold
#     search_results, search_source = query('search_albums_by_listens', operator='greater', threshold=listens_threshold)
#     print(f"Search Results for Albums: {search_results}, Source: {search_source}")

#     # Search for songs with listens greater than a threshold
#     search_results, search_source = query('search_songs_by_listens', operator='less', threshold=listens_threshold)
#     print(f"Search Results for Songs: {search_results}, Source: {search_source}")

#     # Search for reviews for an artist
#     artist_name = 'Radiohead'
#     reviews_data, reviews_source = query('search_reviews_for_artist', artist=artist_name)
#     print(f"Reviews for Artist: {reviews_data}, Source: {reviews_source}")

#     # Search for reviews for an album
#     artist_name = 'Radiohead'
#     album_name = 'OK Computer'
#     reviews_data, reviews_source = query('search_reviews_for_album', artist=artist_name, album=album_name)
#     print(f"Reviews for Album: {reviews_data}, Source: {reviews_source}")

#     # Search for reviews for a song
#     artist_name = 'Radiohead'
#     song_title = 'Karma Police'
#     reviews_data, reviews_source = query('search_reviews_for_song', artist=artist_name, song=song_title)
#     print(f"Reviews for Song: {reviews_data}, Source: {reviews_source}")
# %%


sample_reviews = [
    {
        "artist": "Radiohead",
        "album": "OK Computer",
        "song": "Karma Police",
        "reviewer": "John Doe",
        "review": "An amazing song with deep lyrics and captivating melody.",
        "rating": 5,
        "date": datetime(2022, 5, 17)
    },
    {
        "artist": "Radiohead",
        "album": "OK Computer",
        "reviewer": "Jane Smith",
        "review": "A revolutionary album that changed the course of rock music.",
        "rating": 5,
        "date": datetime(2022, 5, 18)
    },
    {
        "artist": "Radiohead",
        "song": "No Surprises",
        "reviewer": "Alice Johnson",
        "review": "A hauntingly beautiful song with a calm and soothing vibe.",
        "rating": 4,
        "date": datetime(2022, 5, 19)
    },
    {
        "artist": "The Beatles",
        "album": "Abbey Road",
        "song": "Come Together",
        "reviewer": "Bob Brown",
        "review": "A classic track with an unforgettable groove.",
        "rating": 5,
        "date": datetime(2022, 5, 20)
    },
    {
        "artist": "The Beatles",
        "album": "Abbey Road",
        "reviewer": "Carol White",
        "review": "An iconic album with timeless songs.",
        "rating": 5,
        "date": datetime(2022, 5, 21)
    },
    {
        "artist": "Pink Floyd",
        "album": "The Dark Side of the Moon",
        "reviewer": "Dave Green",
        "review": "A masterpiece that takes you on a sonic journey.",
        "rating": 5,
        "date": datetime(2022, 5, 22)
    },
    {
        "artist": "Pink Floyd",
        "song": "Money",
        "reviewer": "Eve Black",
        "review": "A powerful song with a catchy riff and deep message.",
        "rating": 4,
        "date": datetime(2022, 5, 23)
    },
    {
        "artist": "Nirvana",
        "album": "Nevermind",
        "song": "Smells Like Teen Spirit",
        "reviewer": "Frank Blue",
        "review": "An anthem of a generation with raw energy.",
        "rating": 5,
        "date": datetime(2022, 5, 24)
    },
    {
        "artist": "Nirvana",
        "album": "Nevermind",
        "reviewer": "Grace Yellow",
        "review": "A groundbreaking album that redefined rock music.",
        "rating": 5,
        "date": datetime(2022, 5, 25)
    },
    {
        "artist": "Queen",
        "album": "A Night at the Opera",
        "song": "Bohemian Rhapsody",
        "reviewer": "Henry Purple",
        "review": "A theatrical masterpiece with unparalleled creativity.",
        "rating": 5,
        "date": datetime(2022, 5, 26)
    }
]

# Insert sample reviews into the collection
# reviews_collection.insert_many(sample_reviews)

# print("Sample reviews added to the collection.")

