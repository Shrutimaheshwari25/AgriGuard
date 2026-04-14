from pymongo import MongoClient, ASCENDING, DESCENDING
import os
from flask import current_app

_client = None
_db = None
_indices_created = False

def get_db():
    global _client, _db, _indices_created
    
    if _db is not None:
        return _db
        
    uri = current_app.config.get('MONGO_URI')
    
    # Extract DB name from URI if possible as fallback
    fallback_db = 'agri_db'
    if uri and '/' in uri.split('://')[-1]:
        parts = uri.split('/')[-1].split('?')[0]
        if parts:
            fallback_db = parts

    _client = MongoClient(uri)
    try:
        _db = _client.get_default_database()
    except Exception:
        _db = _client[fallback_db]
    
    if not _indices_created:
        try:
            _db.predictions.create_index([("user_id", ASCENDING), ("result.timestamp", DESCENDING)])
            _indices_created = True
        except Exception:
            pass
            
    return _db
