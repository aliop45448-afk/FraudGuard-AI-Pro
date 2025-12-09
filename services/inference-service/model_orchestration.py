"""
Model Orchestration Module for FraudGuard AI Pro

This module implements multi-model orchestration for fraud detection,
supporting Random Forest, Gradient Boosting, Neural Networks, Isolation Forest, and LSTM models.
"""

from typing import Dict, List, Tuple, Optional
import numpy as np
from dataclasses import dataclass
from enum import Enum
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ModelType(Enum):
    """Enumeration of supported model types."""
    RANDOM_FOREST = "random_forest"
    GRADIENT_BOOSTING = "gradient_boosting"
    NEURAL_NETWORK = "neural_network"
    ISOLATION_FOREST = "isolation_forest"
    LSTM = "lstm"


@dataclass
class ModelMetadata:
    """Metadata for a fraud detection model."""
    model_id: str
    model_type: ModelType
    version: str
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    last_trained: str
    is_active: bool


@dataclass
class PredictionResult:
    """Result of a single model prediction."""
    model_id: str
    model_type: ModelType
    fraud_probability: float
    confidence_score: float
    explanation: Dict[str, any]


class ModelOrchestrator:
    """
    Orchestrates multiple fraud detection models for ensemble predictions.
    
    This class manages the lifecycle of multiple ML models, handles their
    predictions, and combines results using weighted ensemble methods.
    """

    def __init__(self):
        """Initialize the model orchestrator."""
        self.models: Dict[str, ModelMetadata] = {}
        self.model_weights: Dict[str, float] = {}
        self.active_models: List[str] = []
        logger.info("ModelOrchestrator initialized")

    def register_model(self, metadata: ModelMetadata, weight: float = 1.0) -> None:
        """
        Register a new model with the orchestrator.
        
        Args:
            metadata: ModelMetadata object containing model information
            weight: Weight for ensemble prediction (default: 1.0)
        """
        self.models[metadata.model_id] = metadata
        self.model_weights[metadata.model_id] = weight
        
        if metadata.is_active:
            self.active_models.append(metadata.model_id)
        
        logger.info(f"Model {metadata.model_id} registered with weight {weight}")

    def get_model_metadata(self, model_id: str) -> Optional[ModelMetadata]:
        """
        Retrieve metadata for a specific model.
        
        Args:
            model_id: ID of the model to retrieve
            
        Returns:
            ModelMetadata object or None if model not found
        """
        return self.models.get(model_id)

    def list_active_models(self) -> List[ModelMetadata]:
        """
        Get a list of all active models.
        
        Returns:
            List of active ModelMetadata objects
        """
        return [self.models[mid] for mid in self.active_models]

    def ensemble_predict(self, features: np.ndarray) -> Tuple[float, Dict]:
        """
        Generate ensemble prediction from all active models.
        
        This method combines predictions from multiple models using weighted averaging.
        
        Args:
            features: Input feature vector for prediction
            
        Returns:
            Tuple of (ensemble_fraud_probability, detailed_results_dict)
        """
        if not self.active_models:
            raise ValueError("No active models available for prediction")

        predictions: List[PredictionResult] = []
        weighted_sum = 0.0
        total_weight = 0.0

        for model_id in self.active_models:
            # Simulate model prediction (in production, call actual model)
            prediction = self._predict_with_model(model_id, features)
            predictions.append(prediction)
            
            weight = self.model_weights[model_id]
            weighted_sum += prediction.fraud_probability * weight
            total_weight += weight

        ensemble_probability = weighted_sum / total_weight if total_weight > 0 else 0.0

        return ensemble_probability, {
            "ensemble_fraud_probability": ensemble_probability,
            "individual_predictions": [
                {
                    "model_id": p.model_id,
                    "model_type": p.model_type.value,
                    "fraud_probability": p.fraud_probability,
                    "confidence_score": p.confidence_score,
                }
                for p in predictions
            ],
            "model_count": len(predictions),
        }

    def _predict_with_model(self, model_id: str, features: np.ndarray) -> PredictionResult:
        """
        Generate prediction from a specific model.
        
        Args:
            model_id: ID of the model to use for prediction
            features: Input feature vector
            
        Returns:
            PredictionResult object
        """
        metadata = self.models[model_id]
        
        # Placeholder: In production, this would call the actual model
        # For now, we simulate a prediction based on model metadata
        fraud_probability = np.random.random()
        confidence_score = metadata.accuracy
        
        explanation = {
            "model_type": metadata.model_type.value,
            "feature_importance": {
                "transaction_amount": 0.25,
                "merchant_category": 0.20,
                "geographic_anomaly": 0.15,
                "time_anomaly": 0.15,
                "user_behavior": 0.15,
                "device_fingerprint": 0.10,
            },
        }
        
        return PredictionResult(
            model_id=model_id,
            model_type=metadata.model_type,
            fraud_probability=fraud_probability,
            confidence_score=confidence_score,
            explanation=explanation,
        )

    def update_model_weights(self, weights: Dict[str, float]) -> None:
        """
        Update the weights for ensemble prediction.
        
        Args:
            weights: Dictionary mapping model IDs to their new weights
        """
        for model_id, weight in weights.items():
            if model_id in self.models:
                self.model_weights[model_id] = weight
                logger.info(f"Updated weight for model {model_id} to {weight}")
            else:
                logger.warning(f"Model {model_id} not found")

    def deactivate_model(self, model_id: str) -> None:
        """
        Deactivate a model from ensemble predictions.
        
        Args:
            model_id: ID of the model to deactivate
        """
        if model_id in self.active_models:
            self.active_models.remove(model_id)
            self.models[model_id].is_active = False
            logger.info(f"Model {model_id} deactivated")

    def activate_model(self, model_id: str) -> None:
        """
        Activate a model for ensemble predictions.
        
        Args:
            model_id: ID of the model to activate
        """
        if model_id in self.models and model_id not in self.active_models:
            self.active_models.append(model_id)
            self.models[model_id].is_active = True
            logger.info(f"Model {model_id} activated")

    def export_configuration(self) -> Dict:
        """
        Export the current orchestrator configuration.
        
        Returns:
            Dictionary containing all model metadata and weights
        """
        return {
            "models": {
                mid: {
                    "metadata": {
                        "model_id": m.model_id,
                        "model_type": m.model_type.value,
                        "version": m.version,
                        "accuracy": m.accuracy,
                        "precision": m.precision,
                        "recall": m.recall,
                        "f1_score": m.f1_score,
                        "last_trained": m.last_trained,
                        "is_active": m.is_active,
                    },
                    "weight": self.model_weights[mid],
                }
                for mid, m in self.models.items()
            },
            "active_models": self.active_models,
        }


# Example usage
if __name__ == "__main__":
    # Create orchestrator
    orchestrator = ModelOrchestrator()

    # Register models
    models_to_register = [
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
            model_id="nn_v1",
            model_type=ModelType.NEURAL_NETWORK,
            version="1.0",
            accuracy=0.91,
            precision=0.88,
            recall=0.90,
            f1_score=0.89,
            last_trained="2024-01-17",
            is_active=True,
        ),
    ]

    for model in models_to_register:
        orchestrator.register_model(model, weight=1.0)

    # Generate ensemble prediction
    sample_features = np.random.randn(10)
    fraud_prob, results = orchestrator.ensemble_predict(sample_features)

    print(f"Ensemble Fraud Probability: {fraud_prob:.4f}")
    print(f"Detailed Results: {json.dumps(results, indent=2)}")
