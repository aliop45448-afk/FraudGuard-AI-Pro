"""
API Gateway for FraudGuard AI Pro

This module implements the main API gateway that routes requests to appropriate
microservices and provides OpenAPI documentation.
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime
import logging
import os
from functools import wraps

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Service endpoints mapping
SERVICE_ENDPOINTS = {
    "auth": os.getenv("AUTH_SERVICE_URL", "http://localhost:5001"),
    "monitoring": os.getenv("MONITORING_SERVICE_URL", "http://localhost:5002"),
    "inference": os.getenv("INFERENCE_SERVICE_URL", "http://localhost:5003"),
    "api": os.getenv("API_SERVICE_URL", "http://localhost:5004"),
}


# ============================================================================
# Middleware and Decorators
# ============================================================================

def require_auth(f):
    """Decorator to require authentication token."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not token:
            return jsonify({"error": "Missing authorization token"}), 401
        
        # In production, validate token with auth service
        request.user_id = "user_from_token"
        return f(*args, **kwargs)
    
    return decorated_function


def log_request(f):
    """Decorator to log incoming requests."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        logger.info(f"{request.method} {request.path} from {request.remote_addr}")
        return f(*args, **kwargs)
    
    return decorated_function


# ============================================================================
# Health and Info Endpoints
# ============================================================================

@app.route('/health', methods=['GET'])
@log_request
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "service": "api-gateway",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
    }), 200


@app.route('/api/v1/info', methods=['GET'])
@log_request
def api_info():
    """Get API information and available endpoints."""
    return jsonify({
        "service": "FraudGuard AI Pro API Gateway",
        "version": "1.0.0",
        "description": "Enterprise-grade fraud detection platform",
        "timestamp": datetime.utcnow().isoformat(),
        "endpoints": {
            "authentication": "/api/v1/auth",
            "transactions": "/api/v1/transactions",
            "dashboards": "/api/v1/dashboards",
            "merchants": "/api/v1/merchants",
            "reports": "/api/v1/reports",
            "webhooks": "/api/v1/webhooks",
        },
    }), 200


# ============================================================================
# Authentication Endpoints
# ============================================================================

@app.route('/api/v1/auth/register', methods=['POST'])
@log_request
def register():
    """Register a new user."""
    return jsonify({
        "message": "Register endpoint - forward to auth service",
        "endpoint": f"{SERVICE_ENDPOINTS['auth']}/api/auth/register",
    }), 200


@app.route('/api/v1/auth/login', methods=['POST'])
@log_request
def login():
    """Authenticate user."""
    return jsonify({
        "message": "Login endpoint - forward to auth service",
        "endpoint": f"{SERVICE_ENDPOINTS['auth']}/api/auth/login",
    }), 200


@app.route('/api/v1/auth/logout', methods=['POST'])
@log_request
@require_auth
def logout():
    """Logout user."""
    return jsonify({
        "status": "logged_out",
        "message": "User successfully logged out",
    }), 200


# ============================================================================
# Transaction Processing Endpoints
# ============================================================================

@app.route('/api/v1/transactions/detect', methods=['POST'])
@log_request
@require_auth
def detect_fraud():
    """
    Process a transaction for fraud detection.
    
    Request body:
    {
        "transaction_id": "txn_123",
        "transaction_amount": 1500.00,
        "merchant_id": "merchant_001",
        "merchant_category": "Electronics",
        "user_id": "user_001",
        "user_location": "New York, USA",
        "transaction_time": "2024-01-20T10:30:00Z",
        "device_fingerprint": "device_abc123",
        "ip_address": "192.168.1.1",
        "card_last_four": "4242"
    }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = [
            'transaction_id', 'transaction_amount', 'merchant_id',
            'merchant_category', 'user_id', 'user_location'
        ]
        
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # In production, forward to inference service
        return jsonify({
            "transaction_id": data['transaction_id'],
            "fraud_probability": 0.35,
            "risk_score": 45.2,
            "is_flagged": False,
            "recommendation": "APPROVE",
            "processing_time_ms": 125.5,
            "timestamp": datetime.utcnow().isoformat(),
        }), 200
    
    except Exception as e:
        logger.error(f"Fraud detection error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/v1/transactions/<transaction_id>', methods=['GET'])
@log_request
@require_auth
def get_transaction(transaction_id):
    """Get transaction details."""
    return jsonify({
        "transaction_id": transaction_id,
        "status": "retrieved",
        "message": "Transaction details would be returned from database",
    }), 200


@app.route('/api/v1/transactions', methods=['GET'])
@log_request
@require_auth
def list_transactions():
    """List transactions with filters."""
    limit = request.args.get('limit', 100, type=int)
    offset = request.args.get('offset', 0, type=int)
    
    return jsonify({
        "limit": limit,
        "offset": offset,
        "total": 0,
        "transactions": [],
    }), 200


# ============================================================================
# Dashboard and Monitoring Endpoints
# ============================================================================

@app.route('/api/v1/dashboards/metrics', methods=['GET'])
@log_request
@require_auth
def get_dashboard_metrics():
    """Get dashboard metrics."""
    return jsonify({
        "endpoint": f"{SERVICE_ENDPOINTS['monitoring']}/api/metrics/dashboard",
        "message": "Dashboard metrics would be retrieved from monitoring service",
    }), 200


@app.route('/api/v1/dashboards/fraud-timeline', methods=['GET'])
@log_request
@require_auth
def get_fraud_timeline():
    """Get fraud detection timeline."""
    hours = request.args.get('hours', 24, type=int)
    
    return jsonify({
        "period_hours": hours,
        "endpoint": f"{SERVICE_ENDPOINTS['monitoring']}/api/fraud/timeline",
        "message": "Fraud timeline would be retrieved from monitoring service",
    }), 200


# ============================================================================
# Merchant Management Endpoints
# ============================================================================

@app.route('/api/v1/merchants/<merchant_id>/risk-profile', methods=['GET'])
@log_request
@require_auth
def get_merchant_risk_profile(merchant_id):
    """Get merchant risk profile."""
    return jsonify({
        "merchant_id": merchant_id,
        "endpoint": f"{SERVICE_ENDPOINTS['monitoring']}/api/merchants/{merchant_id}/risk-profile",
        "message": "Merchant risk profile would be retrieved",
    }), 200


@app.route('/api/v1/merchants/<merchant_id>/transactions', methods=['GET'])
@log_request
@require_auth
def get_merchant_transactions(merchant_id):
    """Get transactions for a merchant."""
    limit = request.args.get('limit', 100, type=int)
    
    return jsonify({
        "merchant_id": merchant_id,
        "limit": limit,
        "transactions": [],
    }), 200


# ============================================================================
# Reporting Endpoints
# ============================================================================

@app.route('/api/v1/reports/fraud-summary', methods=['GET'])
@log_request
@require_auth
def get_fraud_summary():
    """Get fraud summary report."""
    period = request.args.get('period', 'daily')  # daily, weekly, monthly
    
    return jsonify({
        "period": period,
        "report_type": "fraud_summary",
        "generated_at": datetime.utcnow().isoformat(),
        "message": "Fraud summary report would be generated",
    }), 200


@app.route('/api/v1/reports/export', methods=['POST'])
@log_request
@require_auth
def export_report():
    """Export report in specified format."""
    data = request.get_json()
    format_type = data.get('format', 'pdf')  # pdf, csv, json
    
    return jsonify({
        "format": format_type,
        "status": "processing",
        "message": "Report export would be processed",
    }), 202


# ============================================================================
# Webhook Endpoints
# ============================================================================

@app.route('/api/v1/webhooks', methods=['POST'])
@log_request
@require_auth
def create_webhook():
    """Create a webhook subscription."""
    data = request.get_json()
    
    required_fields = ['event_type', 'url']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400
    
    return jsonify({
        "webhook_id": "webhook_123",
        "event_type": data['event_type'],
        "url": data['url'],
        "status": "active",
        "created_at": datetime.utcnow().isoformat(),
    }), 201


@app.route('/api/v1/webhooks/<webhook_id>', methods=['DELETE'])
@log_request
@require_auth
def delete_webhook(webhook_id):
    """Delete a webhook subscription."""
    return jsonify({
        "webhook_id": webhook_id,
        "status": "deleted",
    }), 200


# ============================================================================
# Model Management Endpoints
# ============================================================================

@app.route('/api/v1/models', methods=['GET'])
@log_request
@require_auth
def list_models():
    """List available fraud detection models."""
    return jsonify({
        "models": [
            {
                "model_id": "rf_v1",
                "model_type": "random_forest",
                "version": "1.0",
                "accuracy": 0.92,
                "status": "active",
            },
            {
                "model_id": "gb_v1",
                "model_type": "gradient_boosting",
                "version": "1.0",
                "accuracy": 0.94,
                "status": "active",
            },
        ],
    }), 200


@app.route('/api/v1/models/<model_id>/performance', methods=['GET'])
@log_request
@require_auth
def get_model_performance(model_id):
    """Get model performance metrics."""
    return jsonify({
        "model_id": model_id,
        "accuracy": 0.92,
        "precision": 0.89,
        "recall": 0.91,
        "f1_score": 0.90,
        "last_updated": datetime.utcnow().isoformat(),
    }), 200


# ============================================================================
# Error Handlers
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({
        "error": "Endpoint not found",
        "path": request.path,
        "method": request.method,
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({"error": "Internal server error"}), 500


# ============================================================================
# OpenAPI/Swagger Documentation
# ============================================================================

@app.route('/api/v1/docs', methods=['GET'])
@log_request
def get_api_docs():
    """Get OpenAPI documentation."""
    return jsonify({
        "openapi": "3.0.0",
        "info": {
            "title": "FraudGuard AI Pro API",
            "version": "1.0.0",
            "description": "Enterprise-grade fraud detection platform API",
        },
        "servers": [
            {"url": "/api/v1", "description": "Production API"},
        ],
        "paths": {
            "/transactions/detect": {
                "post": {
                    "summary": "Detect fraud in a transaction",
                    "tags": ["Transactions"],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "transaction_id": {"type": "string"},
                                        "transaction_amount": {"type": "number"},
                                        "merchant_id": {"type": "string"},
                                    },
                                }
                            }
                        },
                    },
                    "responses": {
                        "200": {"description": "Fraud detection result"},
                    },
                }
            },
        },
    }), 200


if __name__ == '__main__':
    logger.info("Starting API Gateway")
    app.run(host='0.0.0.0', port=5000, debug=True)
