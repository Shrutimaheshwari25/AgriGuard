from flask import Blueprint, jsonify, request, Response
import csv
import io
from utils.auth_utils import token_required
from utils.db import get_db

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/history', methods=['GET'])
@token_required
def get_history(current_user_id):
    db = get_db()
    from bson.objectid import ObjectId
    
    query = {"user_id": ObjectId(current_user_id)}
    
    crop = request.args.get('crop')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    if crop:
        query["result.crop"] = {"$regex": f"^{crop}$", "$options": "i"}
        
    date_filter = {}
    if start_date:
        date_filter["$gte"] = start_date
    if end_date:
        # e.g., 2030-01-01T23:59:59
        date_filter["$lte"] = end_date + "T23:59:59Z" if 'T' not in end_date else end_date
    if date_filter:
        query["result.timestamp"] = date_filter
    
    cursor = db.predictions.find(query).sort("result.timestamp", -1).limit(50)
    history = []
    
    for doc in cursor:
        doc['_id'] = str(doc['_id'])
        doc['user_id'] = str(doc['user_id'])
        history.append(doc)
        
    return jsonify({"history": history}), 200

@dashboard_bp.route('/stats', methods=['GET'])
@token_required
def get_stats(current_user_id):
    # This route is used for Recharts in the frontend
    db = get_db()
    from bson.objectid import ObjectId
    
    # We aggregate what crops the user predicted most
    pipeline = [
        {"$match": {"user_id": ObjectId(current_user_id)}},
        {"$group": {"_id": "$result.crop", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    
    crop_stats = list(db.predictions.aggregate(pipeline))
    
    formatted_stats = [{"name": stat["_id"], "value": stat["count"]} for stat in crop_stats]
    
    return jsonify({"crop_stats": formatted_stats}), 200

@dashboard_bp.route('/export', methods=['GET'])
@token_required
def export_csv(current_user_id):
    db = get_db()
    from bson.objectid import ObjectId
    
    cursor = db.predictions.find({"user_id": ObjectId(current_user_id)}).sort("result.timestamp", -1)
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Timestamp", "Predicted Crop", "Confidence (%)", "Selected Model", "N", "P", "K", "pH", "Temp", "Humidity", "Rainfall"])
    
    for doc in cursor:
        r = doc.get("result", {})
        i = doc.get("inputs", {})
        writer.writerow([
            r.get("timestamp", ""),
            r.get("crop", ""),
            r.get("confidence", ""),
            r.get("selected_model", "XGBoost"),
            i.get("N", ""), i.get("P", ""), i.get("K", ""), i.get("ph", ""),
            i.get("temperature", ""), i.get("humidity", ""), i.get("rainfall", "")
        ])
        
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=predictions_export.csv"}
    )
