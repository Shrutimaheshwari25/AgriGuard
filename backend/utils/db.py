from pymongo import MongoClient, ASCENDING, DESCENDING
import os
from flask import current_app

_indices_created = False

def get_db():
    global _indices_created
    client = MongoClient(current_app.config['MONGO_URI'])
    db = client["agri_db"]
    
    if not _indices_created:
        try:
            db.predictions.create_index([("user_id", ASCENDING), ("result.timestamp", DESCENDING)])
            _indices_created = True
        except Exception:
            pass
            
    return db
