"""
Inference Pipeline for FraudGuard AI Pro

This module implements a high-throughput, low-latency inference pipeline
for real-time fraud detection using the model orchestrator.
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import logging
import time

from model_orchestration import ModelOrchestrator, ModelMetadata, ModelType

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class TransactionFeatures:
    """Features extracted from a transaction for fraud detection."""
    transaction_id: str
    transaction_amount: float
    merchant_id: str
    merchant_category: str
    user_id: str
    user_location: str
    transaction_time: str
    device_fingerprint: str
    ip_address: str
    card_last_four: str
    
    def to_feature_vector(self) -> List[float]:
        """Convert transaction features to a numerical feature vector."""
        # Placeholder: In production, this would implement proper feature engineering
        return [
            self.transaction_amount,
            hash(self.merchant_id) % 1000,
            hash(self.merchant_category) % 100,
            hash(self.user_id) % 10000,
            hash(self.user_location) % 1000,
            hash(self.device_fingerprint) % 10000,
        ]


@dataclass
class FraudDetectionResult:
    """Result of fraud detection inference."""
    transaction_id: str
    fraud_probability: float
    risk_score: float  # 0-100
    is_flagged: bool
    confidence: float
    model_predictions: Dict
    processing_time_ms: float
    timestamp: str
    recommendation: str


class InferencePipeline:
    """
    High-performance inference pipeline for real-time fraud detection.
    
    This pipeline coordinates feature extraction, model inference, and
    risk scoring to provide real-time fraud detection results.
    """

    def __init__(self, fraud_threshold: float = 0.5, risk_score_threshold: float = 70.0):
        """
        Initialize the inference pipeline.
        
        Args:
            fraud_threshold: Probability threshold for flagging as fraud (0-1)
            risk_score_threshold: Risk score threshold for flagging (0-100)
        """
        self.orchestrator = ModelOrchestrator()
        self.fraud_threshold = fraud_threshold
        self.risk_score_threshold = risk_score_threshold
        self.inference_count = 0
        self.total_inference_time = 0.0
        logger.info(f"InferencePipeline initialized with fraud_threshold={fraud_threshold}")

    def setup_models(self) -> None:
        """Initialize and register all fraud detection models."""
        models = [
            ModelMetadata(
                model_id="rf_v1",
                model_type=ModelType.RANDOM_FOREST,
                version="1.0",
                accuracy=0.92,
                precision=0.89,
                recall=0.91,
                f1_score=0.90,
                last_trained="2024-01-15",
                is_active=True,
            ),
            ModelMetadata(
                model_id="gb_v1",
                model_type=ModelType.GRADIENT_BOOSTING,
                version="1.0",
                accuracy=0.94,
                precision=0.92,
                recall=0.93,
                f1_score=0.92,
                last_trained="2024-01-16",
                is_active=True,
            ),
            ModelMetadata(
                model_id="if_v1",
                model_type=ModelType.ISOLATION_FOREST,
                version="1.0",
                accuracy=0.88,
                precision=0.85,
                recall=0.87,
                f1_score=0.86,
                last_trained="2024-01-17",
                is_active=True,
            ),
        ]

        for model in models:
            self.orchestrator.register_model(model, weight=1.0)

        logger.info(f"Registered {len(models)} models for inference")

    def process_transaction(self, features: TransactionFeatures) -> FraudDetectionResult:
        """
        Process a single transaction through the inference pipeline.
        
        Args:
            features: TransactionFeatures object containing transaction data
            
        Returns:
            FraudDetectionResult object with detection results
        """
        start_time = time.time()

        # Extract feature vector
        feature_vector = features.to_feature_vector()

        # Run ensemble inference
        fraud_probability, model_predictions = self.orchestrator.ensemble_predict(feature_vector)

        # Calculate risk score (0-100)
        risk_score = self._calculate_risk_score(fraud_probability, features)

        # Determine if transaction should be flagged
        is_flagged = (
            fraud_probability >= self.fraud_threshold
            or risk_score >= self.risk_score_threshold
        )

        # Generate recommendation
        recommendation = self._generate_recommendation(fraud_probability, risk_score, is_flagged)

        # Calculate processing time
        processing_time_ms = (time.time() - start_time) * 1000

        # Update statistics
        self.inference_count += 1
        self.total_inference_time += processing_time_ms

        result = FraudDetectionResult(
            transaction_id=features.transaction_id,
            fraud_probability=fraud_probability,
            risk_score=risk_score,
            is_flagged=is_flagged,
            confidence=self._calculate_confidence(model_predictions),
            model_predictions=model_predictions,
            processing_time_ms=processing_time_ms,
            timestamp=datetime.utcnow().isoformat(),
            recommendation=recommendation,
        )

        logger.info(
            f"Transaction {features.transaction_id}: "
            f"fraud_prob={fraud_probability:.4f}, "
            f"risk_score={risk_score:.2f}, "
            f"flagged={is_flagged}"
        )

        return result

    def _calculate_risk_score(self, fraud_probability: float, features: TransactionFeatures) -> float:
        """
        Calculate a comprehensive risk score (0-100) for a transaction.
        
        Args:
            fraud_probability: Fraud probability from ensemble model
            features: Transaction features
            
        Returns:
            Risk score between 0 and 100
        """
        # Base score from fraud probability
        base_score = fraud_probability * 100

        # Additional risk factors
        amount_risk = self._assess_amount_risk(features.transaction_amount)
        location_risk = self._assess_location_risk(features.user_location)
        time_risk = self._assess_time_risk(features.transaction_time)

        # Weighted combination
        risk_score = (
            base_score * 0.5
            + amount_risk * 0.2
            + location_risk * 0.2
            + time_risk * 0.1
        )

        return min(100.0, max(0.0, risk_score))

    def _assess_amount_risk(self, amount: float) -> float:
        """Assess risk based on transaction amount."""
        if amount > 10000:
            return 80.0
        elif amount > 5000:
            return 60.0
        elif amount > 1000:
            return 30.0
        else:
            return 10.0

    def _assess_location_risk(self, location: str) -> float:
        """Assess risk based on transaction location."""
        # Placeholder: In production, this would use geolocation data
        return 20.0

    def _assess_time_risk(self, transaction_time: str) -> float:
        """Assess risk based on transaction time."""
        # Placeholder: In production, this would analyze transaction timing patterns
        return 15.0

    def _calculate_confidence(self, model_predictions: Dict) -> float:
        """Calculate overall confidence in the prediction."""
        # Use the number of models and their agreement as confidence metric
        individual_predictions = model_predictions.get("individual_predictions", [])
        if not individual_predictions:
            return 0.0

        # Calculate standard deviation of predictions
        probabilities = [p["fraud_probability"] for p in individual_predictions]
        mean_prob = sum(probabilities) / len(probabilities)
        variance = sum((p - mean_prob) ** 2 for p in probabilities) / len(probabilities)
        std_dev = variance ** 0.5

        # Higher agreement (lower std dev) = higher confidence
        confidence = max(0.0, 1.0 - std_dev)
        return confidence

    def _generate_recommendation(self, fraud_probability: float, risk_score: float, is_flagged: bool) -> str:
        """Generate a recommendation based on detection results."""
        if not is_flagged:
            return "APPROVE"
        elif fraud_probability > 0.8 or risk_score > 90:
            return "BLOCK"
        elif fraud_probability > 0.6 or risk_score > 75:
            return "REVIEW"
        else:
            return "CHALLENGE"

    def get_pipeline_statistics(self) -> Dict:
        """Get statistics about the inference pipeline."""
        avg_inference_time = (
            self.total_inference_time / self.inference_count
            if self.inference_count > 0
            else 0.0
        )

        return {
            "total_inferences": self.inference_count,
            "total_inference_time_ms": self.total_inference_time,
            "average_inference_time_ms": avg_inference_time,
            "throughput_per_second": (
                1000.0 / avg_inference_time if avg_inference_time > 0 else 0.0
            ),
            "active_models": len(self.orchestrator.active_models),
        }


# Example usage
if __name__ == "__main__":
    # Initialize pipeline
    pipeline = InferencePipeline(fraud_threshold=0.5, risk_score_threshold=70.0)
    pipeline.setup_models()

    # Create sample transaction
    sample_transaction = TransactionFeatures(
        transaction_id="txn_12345",
        transaction_amount=1500.00,
        merchant_id="merch_001",
        merchant_category="Electronics",
        user_id="user_001",
        user_location="New York, USA",
        transaction_time="2024-01-20T10:30:00Z",
        device_fingerprint="device_abc123",
        ip_address="192.168.1.1",
        card_last_four="4242",
    )

    # Process transaction
    result = pipeline.process_transaction(sample_transaction)

    print(f"Transaction ID: {result.transaction_id}")
    print(f"Fraud Probability: {result.fraud_probability:.4f}")
    print(f"Risk Score: {result.risk_score:.2f}")
    print(f"Is Flagged: {result.is_flagged}")
    print(f"Recommendation: {result.recommendation}")
    print(f"Processing Time: {result.processing_time_ms:.2f}ms")

    # Print pipeline statistics
    stats = pipeline.get_pipeline_statistics()
    print(f"\nPipeline Statistics: {stats}")
