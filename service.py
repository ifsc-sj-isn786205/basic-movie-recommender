import os
from datetime import datetime
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class RecommendationService:
    """Recommendation storage and retrieval"""

    def __init__(self):
        connection_string = os.getenv("MONGODB_CONNECTION_STRING")
        if not connection_string:
            raise ValueError(
                "MONGODB_CONNECTION_STRING not found in environment variables"
            )

        # Connect to MongoDB
        self.client = MongoClient(connection_string)
        self.db = self.client["movie_recommendations"]
        self.collection = self.db["recommendations"]

    def save_recommendation(self, recommendation_data):
        """Save a recommendation"""
        try:
            # Create a copy to avoid modifying the original data
            data_to_save = recommendation_data.copy()
            data_to_save["created_at"] = datetime.utcnow()

            # Insert document
            result = self.collection.insert_one(data_to_save)
            return {"success": True, "id": str(result.inserted_id)}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_recommendations(self, limit=10):
        """Get recent recommendations from MongoDB"""
        try:
            cursor = self.collection.find().sort("created_at", -1).limit(limit)
            recommendations = list(cursor)

            # Convert datetime objects to strings for JSON serialization
            for rec in recommendations:
                if "created_at" in rec and rec["created_at"]:
                    rec["created_at"] = rec["created_at"].isoformat()
                # Remove _id field which is not JSON serializable
                if "_id" in rec:
                    rec["id"] = str(rec["_id"])
                    del rec["_id"]

            return {"success": True, "recommendations": recommendations}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def close_connection(self):
        """Close MongoDB connection"""
        self.client.close()
