import os
from datetime import datetime, timezone
from pymongo import MongoClient


class RecommendationService:
    """Recommendation storage and retrieval"""

    def __init__(self):
        # We fetch the variable directly.
        # In Cloud Functions, this is set in the Deployment Configuration.
        connection_string = os.getenv("MONGODB_CONNECTION_STRING")

        if not connection_string:
            # We print a warning instead of crashing, so the Function doesn't 500 error
            # if the DB is temporarily misconfigured.
            print(
                "WARNING: MONGODB_CONNECTION_STRING not set. Database features will fail."
            )
            self.client = None
            self.db = None
            self.collection = None
        else:
            # connectTimeoutMS=2000 prevents the function from hanging if DB is down
            self.client = MongoClient(connection_string, connectTimeoutMS=2000)
            self.db = self.client["movie_recommendations"]
            self.collection = self.db["recommendations"]

    def save_recommendation(self, recommendation_data):
        if self.collection is None:
            return {"success": False, "error": "Database not configured"}

        try:
            data_to_save = recommendation_data.copy()
            # Use timezone-aware UTC (Best practice)
            data_to_save["created_at"] = datetime.now(timezone.utc)

            result = self.collection.insert_one(data_to_save)
            return {"success": True, "id": str(result.inserted_id)}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_recommendations(self, limit=10):
        if self.collection is None:
            return {"success": False, "error": "Database not configured"}

        try:
            cursor = self.collection.find().sort("created_at", -1).limit(limit)
            recommendations = list(cursor)

            for rec in recommendations:
                if "created_at" in rec and rec["created_at"]:
                    rec["created_at"] = rec["created_at"].isoformat()
                if "_id" in rec:
                    rec["id"] = str(rec["_id"])
                    del rec["_id"]

            return {"success": True, "recommendations": recommendations}
        except Exception as e:
            return {"success": False, "error": str(e)}
