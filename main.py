#!/usr/bin/env python3
"""
Simple Movie Recommendation System using a third party API
"""

import os
import random
import requests
from dotenv import load_dotenv
from flask import Flask, jsonify
from service import RecommendationService

# Load environment variables
load_dotenv()

app = Flask(__name__)


class MovieRecommender:
    def __init__(self):
        self.base_url = os.getenv("API_URI")
        self.api_key = os.getenv("API_KEY")

        if not self.api_key or not self.base_url:
            raise ValueError("API_URI or API_KEY not found in environment variables")

    def search_movies(self, query, page=1):
        """Search for movies using the given API"""
        params = {"apikey": self.api_key, "s": query, "page": page, "type": "movie"}

        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()

            if data.get("Response") == "True":
                return data.get("Search", [])
            else:
                print(f"Error: {data.get('Error', 'Unknown error')}")
                return []

        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")
            return []

    def get_movie_details(self, imdb_id):
        """Get detailed information about a specific movie"""
        params = {"apikey": self.api_key, "i": imdb_id, "plot": "full"}

        try:
            print(f"Retrieving movie details...")
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()

            if data.get("Response") == "True":
                return data
            else:
                print(f"Error: {data.get('Error', 'Unknown error')}")
                return None

        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")
            return None

    def get_random_movie(self):
        """Get a random movie recommendation using popular search terms"""
        # Popular movie search terms for variety
        search_terms = [
            "action",
            "comedy",
            "drama",
            "thriller",
            "horror",
            "sci-fi",
            "romance",
            "adventure",
            "fantasy",
            "mystery",
            "crime",
            "war",
            "superhero",
            "animation",
            "documentary",
            "classic",
            "blockbuster",
        ]

        # Try multiple search terms to find movies
        while search_terms:
            random_term = random.choice(search_terms)
            print("Searching for movies with term:", random_term)
            movies = self.search_movies(random_term, 1)
            print("Found ", len(movies), " movies on page 1")
            if movies:
                # Get a random movie from the results
                random_movie = random.choice(movies)
                print("Getting detailed information for movie: ", random_movie["Title"])
                # Get detailed information
                movie_details = self.get_movie_details(random_movie["imdbID"])
                if movie_details:
                    return movie_details

        return None

    def recommend_movie(self):
        """Main recommendation function"""

        movie = self.get_random_movie()

        if movie:
            return {
                "title": movie.get("Title", "Unknown"),
                "year": movie.get("Year", "Unknown"),
                "genre": movie.get("Genre", "Unknown"),
                "plot": movie.get("Plot", "No plot available"),
                "director": movie.get("Director", "Unknown"),
                "actors": movie.get("Actors", "Unknown"),
                "rating": movie.get("imdbRating", "N/A"),
                "poster": movie.get("Poster", ""),
                "imdb_id": movie.get("imdbID", ""),
                "recommendation_reason": "Random recommendation",
            }
        else:
            return {
                "error": "Unable to find a movie recommendation at this time. Please try again later."
            }


# Initialize the recommender
recommender = MovieRecommender()
recommendation_service = RecommendationService()


@app.route("/")
def home():
    """Home endpoint with basic information"""
    return jsonify(
        {
            "message": "Movie Recommendation API",
            "endpoints": {
                "/recommend": "GET - Get a random movie recommendation",
                "/recommendations": "GET - Get recent recommendations from database",
            },
            "example": "/recommend",
        }
    )


@app.route("/recommend")
def recommend_random():
    """Get a random movie recommendation"""
    recommendation = recommender.recommend_movie()

    # Save to MongoDB if recommendation is successful
    if "error" not in recommendation:
        save_result = recommendation_service.save_recommendation(recommendation)
        recommendation["saved_to_db"] = save_result["success"]
        if not save_result["success"]:
            recommendation["db_error"] = save_result["error"]

    return jsonify(recommendation)


@app.route("/recommendations")
def get_recommendations():
    """Get recent recommendations from MongoDB"""
    result = recommendation_service.get_recommendations()
    return jsonify(result)


if __name__ == "__main__":
    # For GCP deployment, use 0.0.0.0 to bind to all interfaces
    app.run(host="0.0.0.0", port=8080, debug=False)
