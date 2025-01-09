from flask import Flask, request, render_template, redirect, url_for, session, flash
import MongoDB  
from flask import jsonify
from pymongo import MongoClient

# Connexion à MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['SD2024_projet']  
albums_collection = db['GOAOK_albums']  

app = Flask(__name__)

app.secret_key = 'supersecretkey'  

# Mock admin credentials
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'password'


@app.route('/search', methods=['POST'])
def search():
    search_type = request.form['search_type']
    results = None
    if search_type == 'tag':
        keyword = request.form['keyword']
        results, source = MongoDB.query('tag_info', tag=keyword)
    elif search_type == 'album':
        artist = request.form['album_artist']
        album = request.form['album']
        results, source = MongoDB.query('album_info', artist=artist, album=album)
        if results and 'album' in results:
            tracks = results['album'].get('tracks', {}).get('track', [])
            results['album']['num_tracks'] = len(tracks)
            results['album']['total_duration'] = sum(int(track.get('duration', 0)) for track in tracks)
    elif search_type == 'artist':
        artist = request.form['artist']
        results, source = MongoDB.query('artist_info', artist=artist)
        if results and 'artist' in results:
            bio_content = results['artist'].get('bio', {}).get('content', '')
            albums_section = bio_content.split("Studio albums")[1] if "Studio albums" in bio_content else ''
            albums = [line.strip() for line in albums_section.split("\n") if line.strip()]
            results['artist']['albums'] = albums
    elif search_type == 'artist_by_listens':        
        operator = request.form['operator']
        threshold = str(request.form['threshold'])        
        results, source = MongoDB.query('search_artists_by_listens', operator=operator, threshold=threshold)
    elif search_type == 'album_by_listens':
        operator = request.form['operator']        
        threshold = str(request.form['threshold'])
        results, source = MongoDB.query('search_albums_by_listens', operator=operator, threshold=threshold)        
    elif search_type == 'song_by_listens':        
        operator = request.form['operator']
        threshold = str(request.form['threshold'])        
        results, source = MongoDB.query('search_songs_by_listens', operator=operator, threshold=threshold)
    else:
        results = {'error': 'Invalid search type'}
        print(f"Error: {results}") 

    return render_template('home.html', results=results, source=source)

@app.route('/trends', methods=['GET', 'POST'])
def trends():
    results = None
    logs = None
    if request.method == 'POST':
        search_type = request.form['search_type']
        if search_type == 'top_tracks':
            results, source = MongoDB.query('top_tracks')
        elif search_type == 'top_tags':
            results, source = MongoDB.query('top_tags')
        elif search_type == 'top_artists':
            results, source = MongoDB.query('top_artists')
        elif search_type == 'top_tracks_by_country':
            country = request.form['country']
            results, source = MongoDB.query('top_tracks_by_country', country=country)
        elif search_type == 'top_artists_by_country':
            country = request.form['country']
            results, source = MongoDB.query('top_artists_by_country', country=country)
    
        if results:
            MongoDB.log_trend_query(search_type, results)
        
        return render_template('trends.html', results=results, source=source)
    return render_template('trends.html')


@app.route('/find_similar', methods=['GET', 'POST'])
def find_similar():
    results = None
    if request.method == 'POST':
        artist = request.form['artist']
        results, source = MongoDB.query('similar_albums_songs', artist=artist)
        return render_template('find_similar.html', results=results, source=source)
    return render_template('find_similar.html')


@app.route('/trend_logs')
def trend_logs():
    logs, source = MongoDB.query('trend_logs')
    return render_template('trend_logs.html', logs=logs, source=source)


@app.route('/reviews', methods=['GET', 'POST'])
def reviews():
    if request.method == 'POST':
        search_type = request.form['search_type']
        artist = request.form['artist']
        album = request.form.get('album')
        song = request.form.get('song')
        if search_type == 'artist':
            reviews, source = MongoDB.query('search_reviews_for_artist', artist=artist)
        elif search_type == 'album' and album:
            reviews, source = MongoDB.query('search_reviews_for_album', artist=artist, album=album)
        elif search_type == 'song' and song:
            reviews, source = MongoDB.query('search_reviews_for_song', artist=artist, song=song)
        else:
            reviews = None
            source = 'Invalid review type'
        return render_template('reviews.html', reviews=reviews, source=source)
    return render_template('reviews.html', reviews=None)

@app.route('/submit_reviews', methods=['GET', 'POST'])
def submit_reviews():
    if request.method == 'POST':
        review_type = request.form['review_type']
        artist = request.form['artist']
        album = request.form.get('album')
        song = request.form.get('song')
        tag = request.form.get('tag')
        review_text = request.form['review_text']
        rating = int(request.form['rating'])
        username = session.get('username', 'Guest')

        if review_type == 'tag':
            success, message = MongoDB.submit_tag_review(username, tag, review_text, rating)
        elif review_type == 'album':
            success, message = MongoDB.submit_album_review(username, artist, album, review_text, rating)
        elif review_type == 'song':
            success, message = MongoDB.submit_song_review(username, artist, song, review_text, rating)
        else:
            success, message = False, "Invalid review type"

        if success:
            flash(message)
            return redirect(url_for('home'))
        else:
            return render_template('submit_reviews.html', message=message)

    return render_template('submit_reviews.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if MongoDB.get_user(username):
            return render_template('register.html', error='User already exists')
        MongoDB.create_user(username, password, is_admin=False)
        flash('Registration successful! Please login.')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = MongoDB.get_user(username)
        if user and MongoDB.verify_password(username, password):
            session['username'] = username
            session['role'] = 'admin' if user.get('is_admin', False) else 'user'
            flash(f'Logged in as {session["role"]}')
            return redirect(url_for('home'))
        else:
            return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.')
    return redirect(url_for('home'))
@app.route('/')
def home():
    recommendations = []
    if 'username' in session:
        username = session['username']
        recommendations = MongoDB.recommend_similar_tracks_based_on_reviews(username)
    return render_template('home.html', recommendations=recommendations)
@app.route('/popular_albums', methods=['GET'])
def popular_albums():
    # Requête pour récupérer les albums triés par popularité (ou autre critère pertinent)
    albums = list(albums_collection.find({}, {"_id": 0, "album_name": 1, "artist": 1, "popularity": 1}).sort("popularity", -1).limit(10))

    if not albums:
        return jsonify({"error": "No albums found"}), 404

    return jsonify({"albums": albums})
@app.route('/create_playlist', methods=['POST'])
def create_playlist():
    try:
        username = session.get('username')
        if not username or username == 'Guest':
            flash("You must be logged in to create playlists.", "warning")  # Flash a warning message
            return redirect(url_for('home'))  # Redirect to home page

        playlist_name = request.form['playlist_name']
        playlists_collection = db['playlists']
        playlists_collection.insert_one({
            "username": username,
            "playlist_name": playlist_name,
            "songs": []
        })

        flash("Playlist created successfully!", "success")  # Flash a success message
        return redirect(url_for('home'))
    except Exception as e:
        flash(f"An error occurred: {str(e)}", "danger")  # Flash an error message
        return redirect(url_for('home'))



@app.route('/add_to_playlist', methods=['POST'])
def add_to_playlist():
    playlist_name = request.form['playlist_name']
    song = request.form['song']
    artist = request.form['artist']

    playlists_collection = db['playlists']
    playlists_collection.update_one(
        {"playlist_name": playlist_name},
        {"$push": {"songs": {"song": song, "artist": artist}}}
    )

    return jsonify({"success": True})



if __name__ == "__main__":
    app.run(debug=True)

