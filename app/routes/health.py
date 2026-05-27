from flask import Blueprint, jsonify
from app.utils.logger import get_recent_requests

health_bp = Blueprint("health", __name__)


@health_bp.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "message": "FarmSense API is running"
    })


@health_bp.route("/recent-requests", methods=["GET"])
def recent_requests():
    logs = get_recent_requests(limit=10)
    return jsonify({
        "count": len(logs),
        "requests": logs
    })