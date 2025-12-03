import os
import random
import requests
from flask import Flask, jsonify, request

# Try to import the service, but handle the case where the file/db isn't there yet
try:
    from service import RecommendationService

    service_available = True
except ImportError:
    print("Warning: service.py not found. Database features disabled.")
    service_available = False

app = Flask(__name__)

# --- CONFIGURATION ---
# In Cloud Functions, set these as "Runtime Environment Variables"
API_URI = os.environ.get("API_URI", "http://www.omdbapi.com/")
API_KEY = os.environ.get("API_KEY")


class MovieRecommender:
    def __init__(self):
        if not API_KEY:
            # We don't raise an error immediately to allow the function to load,
            # but API calls will fail if not set.
            print("CRITICAL: API_KEY environment variable not set.")

    def search_movies(self, query, page=1):
        if not API_KEY:
            return []
        params = {"apikey": API_KEY, "s": query, "page": page, "type": "movie"}
        try:
            response = requests.get(API_URI, params=params)
            response.raise_for_status()
            data = response.json()
            if data.get("Response") == "True":
                return data.get("Search", [])
            return []
        except Exception as e:
            print(f"Request error: {e}")
            return []

    def get_movie_details(self, imdb_id):
        if not API_KEY:
            return None
        params = {"apikey": API_KEY, "i": imdb_id, "plot": "full"}
        try:
            response = requests.get(API_URI, params=params)
            response.raise_for_status()
            data = response.json()
            if data.get("Response") == "True":
                return data
            return None
        except Exception as e:
            print(f"Request error: {e}")
            return None

    def get_random_movie(self):
        search_terms = [
            "action",
            "comedy",
            "drama",
            "thriller",
            "sci-fi",
            "adventure",
            "fantasy",
            "mystery",
            "crime",
        ]

        # Limit attempts to prevent timeout in Cloud Function
        for _ in range(3):
            random_term = random.choice(search_terms)
            movies = self.search_movies(random_term, 1)
            if movies:
                random_movie = random.choice(movies)
                return self.get_movie_details(random_movie["imdbID"])
        return None

    def recommend_movie(self):
        movie = self.get_random_movie()
        if movie:
            return {
                "title": movie.get("Title", "Unknown"),
                "year": movie.get("Year", "Unknown"),
                "genre": movie.get("Genre", "Unknown"),
                "plot": movie.get("Plot", "No plot available"),
                "poster": movie.get("Poster", ""),
                "imdb_id": movie.get("imdbID", ""),
            }
        return {"error": "Unable to find a movie recommendation."}


# Initialize classes
recommender = MovieRecommender()
if service_available:
    try:
        recommendation_service = RecommendationService()
    except:
        service_available = False

# --- ROUTES ---


@app.route("/", methods=["GET"])
def home():
    return jsonify(
        {
            "message": "Movie Recommendation API",
            "endpoints": ["/recommend", "/recommendations"],
        }
    )


@app.route("/recommend", methods=["GET"])
def recommend_random():
    recommendation = recommender.recommend_movie()

    # Save to DB if service is available and no error
    if service_available and "error" not in recommendation:
        try:
            # Assumes recommendation_service is instantiated correctly
            recommendation_service.save_recommendation(recommendation)
            recommendation["saved_to_db"] = True
        except Exception as e:
            recommendation["saved_to_db"] = False
            recommendation["db_error"] = str(e)

    return jsonify(recommendation)


@app.route("/recommendations", methods=["GET"])
def get_recommendations():
    if not service_available:
        return jsonify({"error": "Database service not configured"}), 503

    try:
        result = recommendation_service.get_recommendations()
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# NOTE: No app.run() here. The GCF runtime acts as the server.
