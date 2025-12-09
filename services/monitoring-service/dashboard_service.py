"""
Real-time Monitoring Dashboard Service for FraudGuard AI Pro

This module provides real-time monitoring, analytics, and dashboard data
for fraud detection metrics and system performance.
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict
import logging
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class MetricSnapshot:
    """A snapshot of metrics at a specific point in time."""
    timestamp: str
    total_transactions: int
    fraudulent_transactions: int
    fraud_rate: float
    average_risk_score: float
    blocked_transactions: int
    reviewed_transactions: int
    approved_transactions: int


@dataclass
class DashboardMetrics:
    """Comprehensive dashboard metrics."""
    current_snapshot: MetricSnapshot
    hourly_metrics: List[MetricSnapshot] = field(default_factory=list)
    daily_metrics: List[MetricSnapshot] = field(default_factory=list)
    top_merchants: List[Tuple[str, int]] = field(default_factory=list)
    top_fraud_categories: List[Tuple[str, int]] = field(default_factory=list)
    geographic_distribution: Dict[str, int] = field(default_factory=dict)
    model_performance: Dict[str, float] = field(default_factory=dict)


class DashboardService:
    """
    Service for managing real-time monitoring dashboards and analytics.
    
    This service tracks fraud detection metrics, maintains historical data,
    and provides insights for dashboard visualization.
    """

    def __init__(self, retention_hours: int = 24):
        """
        Initialize the dashboard service.
        
        Args:
            retention_hours: Number of hours to retain historical metrics
        """
        self.retention_hours = retention_hours
        self.metrics_history: List[MetricSnapshot] = []
        self.transaction_log: List[Dict] = []
        self.merchant_fraud_count: defaultdict = defaultdict(int)
        self.category_fraud_count: defaultdict = defaultdict(int)
        self.geographic_fraud_count: defaultdict = defaultdict(int)
        self.model_scores: Dict[str, List[float]] = defaultdict(list)
        
        # Current session metrics
        self.total_transactions = 0
        self.fraudulent_transactions = 0
        self.blocked_count = 0
        self.reviewed_count = 0
        self.approved_count = 0
        self.total_risk_score = 0.0
        
        logger.info(f"DashboardService initialized with {retention_hours}h retention")

    def record_transaction(
        self,
        transaction_id: str,
        fraud_probability: float,
        risk_score: float,
        is_flagged: bool,
        recommendation: str,
        merchant_id: str,
        merchant_category: str,
        user_location: str,
        model_predictions: Dict,
    ) -> None:
        """
        Record a transaction for monitoring and analytics.
        
        Args:
            transaction_id: Unique transaction identifier
            fraud_probability: Probability of fraud (0-1)
            risk_score: Risk score (0-100)
            is_flagged: Whether transaction was flagged
            recommendation: Recommendation (APPROVE, BLOCK, REVIEW, CHALLENGE)
            merchant_id: Merchant identifier
            merchant_category: Merchant category
            user_location: User's geographic location
            model_predictions: Predictions from individual models
        """
        # Update counters
        self.total_transactions += 1
        self.total_risk_score += risk_score

        if is_flagged:
            self.fraudulent_transactions += 1

        if recommendation == "BLOCK":
            self.blocked_count += 1
        elif recommendation == "REVIEW":
            self.reviewed_count += 1
        elif recommendation == "APPROVE":
            self.approved_count += 1

        # Track by merchant
        self.merchant_fraud_count[merchant_id] += (1 if is_flagged else 0)

        # Track by category
        self.category_fraud_count[merchant_category] += (1 if is_flagged else 0)

        # Track by location
        self.geographic_fraud_count[user_location] += (1 if is_flagged else 0)

        # Record model scores
        for pred in model_predictions.get("individual_predictions", []):
            model_id = pred["model_id"]
            self.model_scores[model_id].append(pred["fraud_probability"])

        # Log transaction
        self.transaction_log.append({
            "transaction_id": transaction_id,
            "timestamp": datetime.utcnow().isoformat(),
            "fraud_probability": fraud_probability,
            "risk_score": risk_score,
            "is_flagged": is_flagged,
            "recommendation": recommendation,
            "merchant_id": merchant_id,
            "merchant_category": merchant_category,
            "user_location": user_location,
        })

        logger.debug(f"Recorded transaction {transaction_id}")

    def get_current_metrics(self) -> MetricSnapshot:
        """
        Get current session metrics.
        
        Returns:
            MetricSnapshot with current metrics
        """
        fraud_rate = (
            self.fraudulent_transactions / self.total_transactions
            if self.total_transactions > 0
            else 0.0
        )

        avg_risk_score = (
            self.total_risk_score / self.total_transactions
            if self.total_transactions > 0
            else 0.0
        )

        return MetricSnapshot(
            timestamp=datetime.utcnow().isoformat(),
            total_transactions=self.total_transactions,
            fraudulent_transactions=self.fraudulent_transactions,
            fraud_rate=fraud_rate,
            average_risk_score=avg_risk_score,
            blocked_transactions=self.blocked_count,
            reviewed_transactions=self.reviewed_count,
            approved_transactions=self.approved_count,
        )

    def get_dashboard_metrics(self) -> DashboardMetrics:
        """
        Get comprehensive dashboard metrics.
        
        Returns:
            DashboardMetrics object with all relevant metrics
        """
        current = self.get_current_metrics()

        # Get top merchants by fraud count
        top_merchants = sorted(
            self.merchant_fraud_count.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]

        # Get top fraud categories
        top_categories = sorted(
            self.category_fraud_count.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]

        # Get geographic distribution
        geo_distribution = dict(self.geographic_fraud_count)

        # Calculate model performance
        model_performance = {}
        for model_id, scores in self.model_scores.items():
            if scores:
                model_performance[model_id] = {
                    "average_fraud_probability": sum(scores) / len(scores),
                    "predictions_count": len(scores),
                    "max_probability": max(scores),
                    "min_probability": min(scores),
                }

        return DashboardMetrics(
            current_snapshot=current,
            hourly_metrics=self.metrics_history[-24:],  # Last 24 hours
            daily_metrics=self.metrics_history[-7:],    # Last 7 days
            top_merchants=top_merchants,
            top_fraud_categories=top_categories,
            geographic_distribution=geo_distribution,
            model_performance=model_performance,
        )

    def get_fraud_timeline(self, hours: int = 24) -> List[Dict]:
        """
        Get fraud detection timeline for the specified period.
        
        Args:
            hours: Number of hours to look back
            
        Returns:
            List of fraud events with timestamps
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        fraud_events = [
            txn for txn in self.transaction_log
            if txn["is_flagged"]
            and datetime.fromisoformat(txn["timestamp"]) > cutoff_time
        ]

        return sorted(fraud_events, key=lambda x: x["timestamp"], reverse=True)

    def get_merchant_risk_profile(self, merchant_id: str) -> Dict:
        """
        Get risk profile for a specific merchant.
        
        Args:
            merchant_id: Merchant identifier
            
        Returns:
            Dictionary with merchant risk metrics
        """
        merchant_transactions = [
            txn for txn in self.transaction_log
            if txn["merchant_id"] == merchant_id
        ]

        if not merchant_transactions:
            return {"error": "No transactions found for merchant"}

        fraud_count = sum(1 for txn in merchant_transactions if txn["is_flagged"])
        avg_risk = sum(txn["risk_score"] for txn in merchant_transactions) / len(merchant_transactions)

        return {
            "merchant_id": merchant_id,
            "total_transactions": len(merchant_transactions),
            "fraud_count": fraud_count,
            "fraud_rate": fraud_count / len(merchant_transactions),
            "average_risk_score": avg_risk,
            "risk_level": self._classify_risk_level(fraud_count / len(merchant_transactions)),
        }

    def get_geographic_insights(self) -> Dict:
        """
        Get geographic fraud distribution insights.
        
        Returns:
            Dictionary with geographic fraud data
        """
        total_fraud = sum(self.geographic_fraud_count.values())
        
        return {
            "total_locations": len(self.geographic_fraud_count),
            "total_fraud_by_location": dict(self.geographic_fraud_count),
            "fraud_percentage_by_location": {
                location: (count / total_fraud * 100) if total_fraud > 0 else 0
                for location, count in self.geographic_fraud_count.items()
            },
            "highest_risk_location": max(
                self.geographic_fraud_count.items(),
                key=lambda x: x[1],
                default=(None, 0)
            )[0],
        }

    def get_model_comparison(self) -> Dict:
        """
        Get comparison of model performance.
        
        Returns:
            Dictionary with model performance comparison
        """
        comparison = {}
        
        for model_id, scores in self.model_scores.items():
            if scores:
                comparison[model_id] = {
                    "total_predictions": len(scores),
                    "average_fraud_probability": sum(scores) / len(scores),
                    "fraud_detection_rate": sum(1 for s in scores if s > 0.5) / len(scores),
                    "high_confidence_predictions": sum(1 for s in scores if s > 0.8) / len(scores),
                }

        return comparison

    def export_metrics_json(self) -> str:
        """
        Export all metrics as JSON.
        
        Returns:
            JSON string with all dashboard metrics
        """
        metrics = self.get_dashboard_metrics()
        
        return json.dumps({
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
        }, indent=2)

    @staticmethod
    def _classify_risk_level(fraud_rate: float) -> str:
        """Classify risk level based on fraud rate."""
        if fraud_rate > 0.1:
            return "CRITICAL"
        elif fraud_rate > 0.05:
            return "HIGH"
        elif fraud_rate > 0.02:
            return "MEDIUM"
        else:
            return "LOW"


# Example usage
if __name__ == "__main__":
    # Initialize dashboard service
    dashboard = DashboardService()

    # Simulate recording transactions
    for i in range(100):
        dashboard.record_transaction(
            transaction_id=f"txn_{i:05d}",
            fraud_probability=0.3 + (i % 70) / 100,
            risk_score=20 + (i % 80),
            is_flagged=(i % 10) < 2,
            recommendation=["APPROVE", "BLOCK", "REVIEW"][i % 3],
            merchant_id=f"merchant_{i % 10}",
            merchant_category=["Electronics", "Retail", "Food"][i % 3],
            user_location=["New York", "Los Angeles", "Chicago"][i % 3],
            model_predictions={
                "individual_predictions": [
                    {"model_id": "rf_v1", "fraud_probability": 0.3 + (i % 70) / 100},
                    {"model_id": "gb_v1", "fraud_probability": 0.25 + (i % 75) / 100},
                ]
            },
        )

    # Get metrics
    metrics = dashboard.get_dashboard_metrics()
    print(f"Total Transactions: {metrics.current_snapshot.total_transactions}")
    print(f"Fraud Rate: {metrics.current_snapshot.fraud_rate:.2%}")
    print(f"Average Risk Score: {metrics.current_snapshot.average_risk_score:.2f}")
    print(f"\nTop Merchants: {metrics.top_merchants}")
    print(f"Top Categories: {metrics.top_fraud_categories}")

    # Export metrics
    print(f"\nMetrics JSON:\n{dashboard.export_metrics_json()}")
