"""
Monitoring Service API for FraudGuard AI Pro

Flask-based REST API for real-time monitoring, dashboards, and analytics.
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime
import logging

from dashboard_service import DashboardService

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize dashboard service
dashboard_service = DashboardService()


# ============================================================================
# Health Check Endpoints
# ============================================================================

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "service": "monitoring-service",
        "timestamp": datetime.utcnow().isoformat(),
    }), 200


# ============================================================================
# Dashboard Metrics Endpoints
# ============================================================================

@app.route('/api/metrics/current', methods=['GET'])
def get_current_metrics():
    """Get current session metrics."""
    metrics = dashboard_service.get_current_metrics()
    return jsonify({
        "timestamp": metrics.timestamp,
        "total_transactions": metrics.total_transactions,
        "fraudulent_transactions": metrics.fraudulent_transactions,
        "fraud_rate": metrics.fraud_rate,
        "average_risk_score": metrics.average_risk_score,
        "blocked_transactions": metrics.blocked_transactions,
        "reviewed_transactions": metrics.reviewed_transactions,
        "approved_transactions": metrics.approved_transactions,
    }), 200


@app.route('/api/metrics/dashboard', methods=['GET'])
def get_dashboard_metrics():
    """Get comprehensive dashboard metrics."""
    metrics = dashboard_service.get_dashboard_metrics()
    return jsonify({
        "current_snapshot": {
            "timestamp": metrics.current_snapshot.timestamp,
            "total_transactions": metrics.current_snapshot.total_transactions,
            "fraudulent_transactions": metrics.current_snapshot.fraudulent_transactions,
            "fraud_rate": metrics.current_snapshot.fraud_rate,
            "average_risk_score": metrics.current_snapshot.average_risk_score,
            "blocked_transactions": metrics.current_snapshot.blocked_transactions,
            "reviewed_transactions": metrics.current_snapshot.reviewed_transactions,
            "approved_transactions": metrics.current_snapshot.approved_transactions,
        },
        "top_merchants": metrics.top_merchants,
        "top_fraud_categories": metrics.top_fraud_categories,
        "geographic_distribution": metrics.geographic_distribution,
        "model_performance": metrics.model_performance,
    }), 200


# ============================================================================
# Fraud Timeline and Analysis Endpoints
# ============================================================================

@app.route('/api/fraud/timeline', methods=['GET'])
def get_fraud_timeline():
    """Get fraud detection timeline."""
    hours = request.args.get('hours', 24, type=int)
    timeline = dashboard_service.get_fraud_timeline(hours)
    return jsonify({
        "period_hours": hours,
        "fraud_events": timeline,
        "total_events": len(timeline),
    }), 200


@app.route('/api/fraud/geographic', methods=['GET'])
def get_geographic_insights():
    """Get geographic fraud distribution insights."""
    insights = dashboard_service.get_geographic_insights()
    return jsonify(insights), 200


# ============================================================================
# Merchant Analysis Endpoints
# ============================================================================

@app.route('/api/merchants/<merchant_id>/risk-profile', methods=['GET'])
def get_merchant_risk_profile(merchant_id):
    """Get risk profile for a specific merchant."""
    profile = dashboard_service.get_merchant_risk_profile(merchant_id)
    return jsonify(profile), 200


# ============================================================================
# Model Performance Endpoints
# ============================================================================

@app.route('/api/models/comparison', methods=['GET'])
def get_model_comparison():
    """Get comparison of model performance."""
    comparison = dashboard_service.get_model_comparison()
    return jsonify(comparison), 200


# ============================================================================
# Transaction Recording Endpoint
# ============================================================================

@app.route('/api/transactions/record', methods=['POST'])
def record_transaction():
    """Record a transaction for monitoring and analytics."""
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = [
            'transaction_id', 'fraud_probability', 'risk_score',
            'is_flagged', 'recommendation', 'merchant_id',
            'merchant_category', 'user_location', 'model_predictions'
        ]

        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        # Record transaction
        dashboard_service.record_transaction(
            transaction_id=data['transaction_id'],
            fraud_probability=data['fraud_probability'],
            risk_score=data['risk_score'],
            is_flagged=data['is_flagged'],
            recommendation=data['recommendation'],
            merchant_id=data['merchant_id'],
            merchant_category=data['merchant_category'],
            user_location=data['user_location'],
            model_predictions=data['model_predictions'],
        )

        return jsonify({
            "status": "recorded",
            "transaction_id": data['transaction_id'],
        }), 201

    except Exception as e:
        logger.error(f"Error recording transaction: {str(e)}")
        return jsonify({"error": str(e)}), 500


# ============================================================================
# Export Endpoints
# ============================================================================

@app.route('/api/metrics/export/json', methods=['GET'])
def export_metrics_json():
    """Export all metrics as JSON."""
    import json
    metrics_json = dashboard_service.export_metrics_json()
    return app.response_class(
        response=metrics_json,
        status=200,
        mimetype='application/json'
    )


# ============================================================================
# Error Handlers
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({"error": "Internal server error"}), 500


if __name__ == '__main__':
    logger.info("Starting Monitoring Service API")
    app.run(host='0.0.0.0', port=5002, debug=True)
