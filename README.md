# Music Trends - Music Recommendation System

![MongoDB](https://img.shields.io/badge/MongoDB-%234ea94b.svg?&style=for-the-badge&logo=mongodb&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-%23000000.svg?&style=for-the-badge&logo=flask&logoColor=white)
![Python](https://img.shields.io/badge/Python-%233776AB.svg?&style=for-the-badge&logo=python&logoColor=white)
![HTML](https://img.shields.io/badge/HTML-%23E34F26.svg?&style=for-the-badge&logo=html5&logoColor=white)

## Description

**Music Trends** is a web application designed to explore, search, and discover global music trends. It uses MongoDB for storing and retrieving data about artists, albums, songs, and tags. The application also provides advanced features such as user recommendations and playlist management.

---

## Key Features

### User and Admin Functionalities
- **User Registration and Login:**
  - Users can register with a username and password.
  - Secure login with hashed passwords.
  - Guests can explore the site without registration.

- **Admin Access:**
  - Admins can view if an operation is local or remote.
  - Manage system logs and monitor trends.

### Music Data Retrieval
- **Search for Artists, Albums, and Tags:**
  - Fetch detailed information such as artist biographies, album tracks, and tag summaries.

- **Global Music Trends:**
  - View top 10 tracks, albums, and tags globally or by country.
  - Retrieve artists and tracks based on the number of listens.

### Recommendations and Reviews
- **Personalized Recommendations:**
  - Suggest similar tracks based on user reviews.

- **Submit Reviews:**
  - Users can review tags, albums, and songs with ratings and comments.

- **Review Search:**
  - Fetch reviews for a specific artist, album, or song.

### Playlist Management
- **Create and Manage Playlists:**
  - Add songs and organize personalized playlists.

---

## Technologies Used

- **Backend:** Flask (Python)
- **Database:** MongoDB
- **Frontend:** HTML, CSS, JavaScript

---

## Installation

### Clone the Repository
```bash
git clone https://github.com/sana-rekbi/MusicTrends-Recommendation-MongoDB.git
cd MusicTrends-Recommendation-MongoDB
```

### Setup Virtual Environment
```bash
python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate
pip install -r requirements.txt
```

### Configure MongoDB
1. Ensure MongoDB is installed and running.
2. Create a database called `MusicTrendsDB`.
3. Add the following collections:
   - `GOAOK_artists`, `GOAOK_albums`, `GOAOK_tracks`, `GOAOK_tags`, `GOAOK_trends`, `GOAOK_reviews`, `users`
4. Create a `.env` file with your MongoDB URI:
   ```env
   MONGODB_URI=mongodb+srv://<username>:<password>@<cluster-url>/MusicTrendsDB
   ```

### Populate the Database
```bash
python MongoDB.py
```

### Run the Application
```bash
python main.py
```
Access the application at [http://localhost:5000](http://localhost:5000).

---

## Deployment on Heroku (Optional)

### Install Heroku CLI
```bash
npm install -g heroku
heroku login
```

### Create Heroku Application
```bash
heroku create music-trends
```

### Add MongoDB Atlas
1. Set up a cluster on MongoDB Atlas.
2. Add the URI to Heroku environment variables:
   ```bash
   heroku config:set MONGODB_URI=mongodb+srv://<username>:<password>@<cluster-url>/MusicTrendsDB
   ```

### Deploy to Heroku
```bash
git add .
git commit -m "Deploy Music Trends on Heroku"
git push heroku master
```
Access the app via the Heroku-provided URL.

---

## Project Structure

```plaintext
MusicTrends-Recommendation-MongoDB/
├── src/
│   ├── main.py         # Main application file
│   ├── MongoDB.py      # MongoDB connection and data management
│   ├── templates/      # HTML files
│   └── static/         # CSS and JavaScript files
├── requirements.txt     # Project dependencies
├── README.md            # Documentation
└── .env                 # Environment variables
```

---

## Future Improvements

1. **Enhance User Interface:**
   - Integrate modern frameworks like React or Vue.js.
2. **Expand Recommendations:**
   - Use advanced algorithms for personalized suggestions.
3. **Implement REST API:**
   - Facilitate integration with other applications.
4. **Concurrency Management:**
   - Optimize for simultaneous user queries.

---

## Contributors

- **Sana Rekbi**

---
![image](https://github.com/user-attachments/assets/8435407a-d262-4002-93e0-9249997e1b1a)
![image](https://github.com/user-attachments/assets/48b9b091-6379-4e1d-b130-4ad207ddd5e6)
![image](https://github.com/user-attachments/assets/73fd6ade-b5d8-4537-960c-7234d5578f2e)
![image](https://github.com/user-attachments/assets/34ac3aec-50d1-4ce3-a64c-125755424c5f)
![image](https://github.com/user-attachments/assets/360a1d2d-f811-451e-b216-61c2aa0ff118)
![image](https://github.com/user-attachments/assets/53a4e942-6a9e-4485-87f3-72a50bbdb76c)
![image](https://github.com/user-attachments/assets/63a06912-1134-467c-8d0d-06da3c8dacba)
![image](https://github.com/user-attachments/assets/18eb372f-c14e-42a1-80f4-3ce30b0f31ff)
![image](https://github.com/user-attachments/assets/374fcdcc-d114-479b-8fc4-fd33b33b560f)

