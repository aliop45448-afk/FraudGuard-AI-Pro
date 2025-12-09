"""
Inference Service API for FraudGuard AI Pro

Flask-based REST API for real-time fraud detection using the inference pipeline.
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime
import logging
import numpy as np

from model_orchestration import ModelOrchestrator, ModelMetadata, ModelType
from inference_pipeline import InferencePipeline, TransactionFeatures

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize inference pipeline
inference_pipeline = InferencePipeline(fraud_threshold=0.5, risk_score_threshold=70.0)
inference_pipeline.setup_models()


# ============================================================================
# Health Check Endpoints
# ============================================================================

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "service": "inference-service",
        "timestamp": datetime.utcnow().isoformat(),
        "models_active": len(inference_pipeline.orchestrator.active_models),
    }), 200


# ============================================================================
# Fraud Detection Endpoints
# ============================================================================

@app.route('/api/detect', methods=['POST'])
def detect_fraud():
    """
    Detect fraud in a transaction.
    
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
            'merchant_category', 'user_id', 'user_location',
            'transaction_time', 'device_fingerprint', 'ip_address', 'card_last_four'
        ]

        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        # Create transaction features
        features = TransactionFeatures(
            transaction_id=data['transaction_id'],
            transaction_amount=data['transaction_amount'],
            merchant_id=data['merchant_id'],
            merchant_category=data['merchant_category'],
            user_id=data['user_id'],
            user_location=data['user_location'],
            transaction_time=data['transaction_time'],
            device_fingerprint=data['device_fingerprint'],
            ip_address=data['ip_address'],
            card_last_four=data['card_last_four'],
        )

        # Process transaction
        result = inference_pipeline.process_transaction(features)

        return jsonify({
            "transaction_id": result.transaction_id,
            "fraud_probability": result.fraud_probability,
            "risk_score": result.risk_score,
            "is_flagged": result.is_flagged,
            "confidence": result.confidence,
            "recommendation": result.recommendation,
            "processing_time_ms": result.processing_time_ms,
            "timestamp": result.timestamp,
            "model_predictions": result.model_predictions,
        }), 200

    except Exception as e:
        logger.error(f"Fraud detection error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/batch-detect', methods=['POST'])
def batch_detect_fraud():
    """
    Detect fraud in multiple transactions (batch processing).
    
    Request body:
    {
        "transactions": [
            { transaction data },
            { transaction data },
            ...
        ]
    }
    """
    try:
        data = request.get_json()

        if 'transactions' not in data or not isinstance(data['transactions'], list):
            return jsonify({"error": "Invalid request format"}), 400

        results = []
        for txn_data in data['transactions']:
            try:
                features = TransactionFeatures(
                    transaction_id=txn_data['transaction_id'],
                    transaction_amount=txn_data['transaction_amount'],
                    merchant_id=txn_data['merchant_id'],
                    merchant_category=txn_data['merchant_category'],
                    user_id=txn_data['user_id'],
                    user_location=txn_data['user_location'],
                    transaction_time=txn_data['transaction_time'],
                    device_fingerprint=txn_data['device_fingerprint'],
                    ip_address=txn_data['ip_address'],
                    card_last_four=txn_data['card_last_four'],
                )

                result = inference_pipeline.process_transaction(features)
                results.append({
                    "transaction_id": result.transaction_id,
                    "fraud_probability": result.fraud_probability,
                    "risk_score": result.risk_score,
                    "is_flagged": result.is_flagged,
                    "recommendation": result.recommendation,
                })
            except Exception as e:
                logger.error(f"Error processing transaction: {str(e)}")
                results.append({
                    "transaction_id": txn_data.get('transaction_id'),
                    "error": str(e),
                })

        return jsonify({
            "total_transactions": len(data['transactions']),
            "processed": len(results),
            "results": results,
        }), 200

    except Exception as e:
        logger.error(f"Batch detection error: {str(e)}")
        return jsonify({"error": str(e)}), 500


# ============================================================================
# Model Management Endpoints
# ============================================================================

@app.route('/api/models', methods=['GET'])
def list_models():
    """List all registered models."""
    models = inference_pipeline.orchestrator.list_active_models()
    
    return jsonify({
        "total_models": len(models),
        "models": [
            {
                "model_id": m.model_id,
                "model_type": m.model_type.value,
                "version": m.version,
                "accuracy": m.accuracy,
                "precision": m.precision,
                "recall": m.recall,
                "f1_score": m.f1_score,
                "is_active": m.is_active,
                "last_trained": m.last_trained,
            }
            for m in models
        ],
    }), 200


@app.route('/api/models/<model_id>', methods=['GET'])
def get_model(model_id):
    """Get details of a specific model."""
    model = inference_pipeline.orchestrator.get_model_metadata(model_id)
    
    if not model:
        return jsonify({"error": "Model not found"}), 404
    
    return jsonify({
        "model_id": model.model_id,
        "model_type": model.model_type.value,
        "version": model.version,
        "accuracy": model.accuracy,
        "precision": model.precision,
        "recall": model.recall,
        "f1_score": model.f1_score,
        "is_active": model.is_active,
        "last_trained": model.last_trained,
    }), 200


@app.route('/api/models/<model_id>/activate', methods=['POST'])
def activate_model(model_id):
    """Activate a model."""
    inference_pipeline.orchestrator.activate_model(model_id)
    
    return jsonify({
        "model_id": model_id,
        "status": "activated",
    }), 200


@app.route('/api/models/<model_id>/deactivate', methods=['POST'])
def deactivate_model(model_id):
    """Deactivate a model."""
    inference_pipeline.orchestrator.deactivate_model(model_id)
    
    return jsonify({
        "model_id": model_id,
        "status": "deactivated",
    }), 200


@app.route('/api/models/weights', methods=['POST'])
def update_model_weights():
    """Update model weights for ensemble."""
    data = request.get_json()
    
    if 'weights' not in data:
        return jsonify({"error": "Missing weights"}), 400
    
    inference_pipeline.orchestrator.update_model_weights(data['weights'])
    
    return jsonify({
        "status": "weights_updated",
        "weights": data['weights'],
    }), 200


# ============================================================================
# Statistics and Performance Endpoints
# ============================================================================

@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """Get pipeline statistics."""
    stats = inference_pipeline.get_pipeline_statistics()
    
    return jsonify(stats), 200


@app.route('/api/configuration', methods=['GET'])
def get_configuration():
    """Get orchestrator configuration."""
    config = inference_pipeline.orchestrator.export_configuration()
    
    return jsonify(config), 200


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
    logger.info("Starting Inference Service API")
    app.run(host='0.0.0.0', port=5003, debug=True)
