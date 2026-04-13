from pymongo import MongoClient, ASCENDING, DESCENDING
import os
from flask import current_app

_indices_created = False

def get_db():
    global _indices_created
    uri = current_app.config.get('MONGO_URI')
    
    # Extract DB name from URI if possible as fallback
    # Example: mongodb+srv://user:pass@cluster.net/dbname?options
    fallback_db = 'agri_db'
    if uri and '/' in uri.split('://')[-1]:
        parts = uri.split('/')[-1].split('?')[0]
        if parts:
            fallback_db = parts

    client = MongoClient(uri)
    try:
        db = client.get_default_database()
    except Exception:
        db = client[fallback_db]
    
    if not _indices_created:
        try:
            db.predictions.create_index([("user_id", ASCENDING), ("result.timestamp", DESCENDING)])
            _indices_created = True
        except Exception:
            pass
            
    return db
