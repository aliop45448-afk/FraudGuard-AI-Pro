"""
Comprehensive API Service for FraudGuard AI Pro

This module implements the full API suite with transaction processing,
webhooks, banking integration, and data export functionality.
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
import json
import uuid
import requests
from dataclasses import dataclass, asdict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class WebhookSubscription:
    """Webhook subscription data structure."""
    webhook_id: str
    user_id: str
    event_type: str
    url: str
    is_active: bool
    created_at: str
    last_triggered: Optional[str] = None
    retry_count: int = 0


@dataclass
class BankingIntegration:
    """Banking integration configuration."""
    integration_id: str
    bank_name: str
    api_key: str
    endpoint: str
    is_active: bool
    last_sync: Optional[str] = None
    sync_frequency: str = "hourly"


class WebhookManager:
    """Manages webhook subscriptions and delivery."""

    def __init__(self):
        """Initialize webhook manager."""
        self.subscriptions: Dict[str, WebhookSubscription] = {}
        self.event_queue: List[Dict] = []
        logger.info("WebhookManager initialized")

    def subscribe(
        self,
        user_id: str,
        event_type: str,
        url: str,
    ) -> WebhookSubscription:
        """
        Create a webhook subscription.

        Args:
            user_id: User ID
            event_type: Type of event to subscribe to
            url: Webhook URL to call

        Returns:
            WebhookSubscription object
        """
        webhook_id = f"webhook_{uuid.uuid4().hex[:12]}"

        subscription = WebhookSubscription(
            webhook_id=webhook_id,
            user_id=user_id,
            event_type=event_type,
            url=url,
            is_active=True,
            created_at=datetime.utcnow().isoformat(),
        )

        self.subscriptions[webhook_id] = subscription
        logger.info(f"Webhook subscription created: {webhook_id}")

        return subscription

    def unsubscribe(self, webhook_id: str) -> bool:
        """
        Remove a webhook subscription.

        Args:
            webhook_id: Webhook ID to remove

        Returns:
            True if successful, False otherwise
        """
        if webhook_id in self.subscriptions:
            del self.subscriptions[webhook_id]
            logger.info(f"Webhook subscription removed: {webhook_id}")
            return True
        return False

    def trigger_event(self, event_type: str, data: Dict) -> None:
        """
        Trigger a webhook event.

        Args:
            event_type: Type of event
            data: Event data
        """
        event = {
            "event_id": f"evt_{uuid.uuid4().hex[:12]}",
            "event_type": event_type,
            "timestamp": datetime.utcnow().isoformat(),
            "data": data,
        }

        # Find subscriptions for this event type
        for webhook_id, subscription in self.subscriptions.items():
            if subscription.event_type == event_type and subscription.is_active:
                self._deliver_webhook(subscription, event)

    def _deliver_webhook(self, subscription: WebhookSubscription, event: Dict) -> None:
        """
        Deliver webhook to subscriber.

        Args:
            subscription: Webhook subscription
            event: Event to deliver
        """
        try:
            response = requests.post(
                subscription.url,
                json=event,
                timeout=10,
                headers={"Content-Type": "application/json"},
            )

            if response.status_code == 200:
                subscription.last_triggered = datetime.utcnow().isoformat()
                subscription.retry_count = 0
                logger.info(f"Webhook delivered: {subscription.webhook_id}")
            else:
                subscription.retry_count += 1
                logger.warning(f"Webhook delivery failed: {subscription.webhook_id}")

        except Exception as e:
            subscription.retry_count += 1
            logger.error(f"Webhook delivery error: {str(e)}")

    def get_subscriptions(self, user_id: str) -> List[WebhookSubscription]:
        """Get all subscriptions for a user."""
        return [
            sub for sub in self.subscriptions.values()
            if sub.user_id == user_id
        ]


class BankingIntegrationManager:
    """Manages banking integrations."""

    def __init__(self):
        """Initialize banking integration manager."""
        self.integrations: Dict[str, BankingIntegration] = {}
        logger.info("BankingIntegrationManager initialized")

    def add_integration(
        self,
        bank_name: str,
        api_key: str,
        endpoint: str,
    ) -> BankingIntegration:
        """
        Add a banking integration.

        Args:
            bank_name: Name of the bank
            api_key: API key for authentication
            endpoint: API endpoint URL

        Returns:
            BankingIntegration object
        """
        integration_id = f"bank_{uuid.uuid4().hex[:12]}"

        integration = BankingIntegration(
            integration_id=integration_id,
            bank_name=bank_name,
            api_key=api_key,
            endpoint=endpoint,
            is_active=True,
        )

        self.integrations[integration_id] = integration
        logger.info(f"Banking integration added: {integration_id}")

        return integration

    def sync_transactions(self, integration_id: str) -> Dict:
        """
        Sync transactions from banking integration.

        Args:
            integration_id: Integration ID

        Returns:
            Sync result
        """
        if integration_id not in self.integrations:
            return {"error": "Integration not found"}

        integration = self.integrations[integration_id]

        try:
            # Call banking API
            response = requests.get(
                f"{integration.endpoint}/transactions",
                headers={"Authorization": f"Bearer {integration.api_key}"},
                timeout=30,
            )

            if response.status_code == 200:
                integration.last_sync = datetime.utcnow().isoformat()
                transactions = response.json()

                logger.info(
                    f"Synced {len(transactions)} transactions from {integration.bank_name}"
                )

                return {
                    "status": "success",
                    "bank": integration.bank_name,
                    "transactions_synced": len(transactions),
                    "last_sync": integration.last_sync,
                }
            else:
                logger.error(f"Banking API error: {response.status_code}")
                return {
                    "status": "error",
                    "message": "Failed to sync transactions",
                }

        except Exception as e:
            logger.error(f"Banking sync error: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
            }

    def get_integrations(self) -> List[BankingIntegration]:
        """Get all active integrations."""
        return list(self.integrations.values())


class DataExportManager:
    """Manages data export functionality."""

    @staticmethod
    def export_transactions(
        transactions: List[Dict],
        format_type: str = "json",
    ) -> Optional[str]:
        """
        Export transactions in specified format.

        Args:
            transactions: List of transactions
            format_type: Export format (json, csv, xml)

        Returns:
            Exported data as string
        """
        if format_type == "json":
            return json.dumps(transactions, indent=2)

        elif format_type == "csv":
            import csv
            from io import StringIO

            output = StringIO()
            if not transactions:
                return ""

            writer = csv.DictWriter(output, fieldnames=transactions[0].keys())
            writer.writeheader()
            writer.writerows(transactions)

            return output.getvalue()

        elif format_type == "xml":
            import xml.etree.ElementTree as ET

            root = ET.Element("transactions")
            for txn in transactions:
                txn_elem = ET.SubElement(root, "transaction")
                for key, value in txn.items():
                    elem = ET.SubElement(txn_elem, key)
                    elem.text = str(value)

            return ET.tostring(root, encoding="unicode")

        return None

    @staticmethod
    def export_report(
        report_data: Dict,
        format_type: str = "json",
    ) -> Optional[str]:
        """
        Export report in specified format.

        Args:
            report_data: Report data
            format_type: Export format (json, pdf, html)

        Returns:
            Exported report as string
        """
        if format_type == "json":
            return json.dumps(report_data, indent=2)

        elif format_type == "html":
            html = f"""
            <html>
            <head>
                <title>Fraud Detection Report</title>
                <style>
                    body {{ font-family: Arial, sans-serif; }}
                    table {{ border-collapse: collapse; width: 100%; }}
                    th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                    th {{ background-color: #4CAF50; color: white; }}
                </style>
            </head>
            <body>
                <h1>Fraud Detection Report</h1>
                <p>Generated: {datetime.utcnow().isoformat()}</p>
                <pre>{json.dumps(report_data, indent=2)}</pre>
            </body>
            </html>
            """
            return html

        return None


# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize managers
webhook_manager = WebhookManager()
banking_manager = BankingIntegrationManager()
export_manager = DataExportManager()


# ============================================================================
# Health Check
# ============================================================================

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "service": "api-service",
        "timestamp": datetime.utcnow().isoformat(),
    }), 200


# ============================================================================
# Webhook Endpoints
# ============================================================================

@app.route('/api/webhooks', methods=['POST'])
def create_webhook():
    """Create a webhook subscription."""
    try:
        data = request.get_json()

        if not data.get('event_type') or not data.get('url'):
            return jsonify({"error": "Missing required fields"}), 400

        user_id = request.headers.get('X-User-ID', 'user_default')

        subscription = webhook_manager.subscribe(
            user_id=user_id,
            event_type=data['event_type'],
            url=data['url'],
        )

        return jsonify({
            "webhook_id": subscription.webhook_id,
            "event_type": subscription.event_type,
            "url": subscription.url,
            "status": "active",
            "created_at": subscription.created_at,
        }), 201

    except Exception as e:
        logger.error(f"Webhook creation error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/webhooks', methods=['GET'])
def list_webhooks():
    """List user's webhooks."""
    try:
        user_id = request.headers.get('X-User-ID', 'user_default')
        subscriptions = webhook_manager.get_subscriptions(user_id)

        return jsonify({
            "total": len(subscriptions),
            "webhooks": [asdict(sub) for sub in subscriptions],
        }), 200

    except Exception as e:
        logger.error(f"Webhook list error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/webhooks/<webhook_id>', methods=['DELETE'])
def delete_webhook(webhook_id):
    """Delete a webhook subscription."""
    try:
        if webhook_manager.unsubscribe(webhook_id):
            return jsonify({
                "webhook_id": webhook_id,
                "status": "deleted",
            }), 200
        else:
            return jsonify({"error": "Webhook not found"}), 404

    except Exception as e:
        logger.error(f"Webhook deletion error: {str(e)}")
        return jsonify({"error": str(e)}), 500


# ============================================================================
# Banking Integration Endpoints
# ============================================================================

@app.route('/api/banking/integrations', methods=['POST'])
def add_banking_integration():
    """Add a banking integration."""
    try:
        data = request.get_json()

        required_fields = ['bank_name', 'api_key', 'endpoint']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing field: {field}"}), 400

        integration = banking_manager.add_integration(
            bank_name=data['bank_name'],
            api_key=data['api_key'],
            endpoint=data['endpoint'],
        )

        return jsonify({
            "integration_id": integration.integration_id,
            "bank_name": integration.bank_name,
            "status": "active",
        }), 201

    except Exception as e:
        logger.error(f"Banking integration error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/banking/integrations', methods=['GET'])
def list_banking_integrations():
    """List all banking integrations."""
    try:
        integrations = banking_manager.get_integrations()

        return jsonify({
            "total": len(integrations),
            "integrations": [
                {
                    "integration_id": i.integration_id,
                    "bank_name": i.bank_name,
                    "is_active": i.is_active,
                    "last_sync": i.last_sync,
                }
                for i in integrations
            ],
        }), 200

    except Exception as e:
        logger.error(f"Banking integration list error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/banking/integrations/<integration_id>/sync', methods=['POST'])
def sync_banking_transactions(integration_id):
    """Sync transactions from banking integration."""
    try:
        result = banking_manager.sync_transactions(integration_id)
        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Banking sync error: {str(e)}")
        return jsonify({"error": str(e)}), 500


# ============================================================================
# Data Export Endpoints
# ============================================================================

@app.route('/api/export/transactions', methods=['POST'])
def export_transactions():
    """Export transactions in specified format."""
    try:
        data = request.get_json()
        format_type = data.get('format', 'json')

        # Mock transaction data
        transactions = [
            {
                "transaction_id": f"TXN_{i:05d}",
                "amount": 100 + i * 10,
                "merchant": f"Merchant {i}",
                "fraud_probability": 0.2 + (i % 10) * 0.05,
                "timestamp": datetime.utcnow().isoformat(),
            }
            for i in range(10)
        ]

        exported = export_manager.export_transactions(transactions, format_type)

        if not exported:
            return jsonify({"error": "Unsupported format"}), 400

        return jsonify({
            "format": format_type,
            "data": exported,
            "count": len(transactions),
        }), 200

    except Exception as e:
        logger.error(f"Export error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/export/report', methods=['POST'])
def export_report():
    """Export report in specified format."""
    try:
        data = request.get_json()
        format_type = data.get('format', 'json')
        period = data.get('period', 'daily')

        # Mock report data
        report_data = {
            "period": period,
            "generated_at": datetime.utcnow().isoformat(),
            "total_transactions": 1000,
            "fraudulent_transactions": 50,
            "fraud_rate": 0.05,
            "average_risk_score": 35.5,
            "blocked_transactions": 25,
            "reviewed_transactions": 15,
            "approved_transactions": 960,
        }

        exported = export_manager.export_report(report_data, format_type)

        if not exported:
            return jsonify({"error": "Unsupported format"}), 400

        return jsonify({
            "format": format_type,
            "data": exported,
        }), 200

    except Exception as e:
        logger.error(f"Report export error: {str(e)}")
        return jsonify({"error": str(e)}), 500


# ============================================================================
# Batch Processing Endpoints
# ============================================================================

@app.route('/api/batch/process', methods=['POST'])
def process_batch():
    """Process batch of transactions."""
    try:
        data = request.get_json()

        if 'transactions' not in data:
            return jsonify({"error": "Missing transactions"}), 400

        transactions = data['transactions']
        batch_id = f"batch_{uuid.uuid4().hex[:12]}"

        # Process transactions
        results = []
        for txn in transactions:
            results.append({
                "transaction_id": txn.get('transaction_id'),
                "status": "processed",
                "fraud_probability": 0.35,
                "recommendation": "APPROVE",
            })

        # Trigger webhook event
        webhook_manager.trigger_event("batch_processed", {
            "batch_id": batch_id,
            "count": len(results),
            "timestamp": datetime.utcnow().isoformat(),
        })

        return jsonify({
            "batch_id": batch_id,
            "total": len(transactions),
            "processed": len(results),
            "results": results,
        }), 200

    except Exception as e:
        logger.error(f"Batch processing error: {str(e)}")
        return jsonify({"error": str(e)}), 500


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
    logger.info("Starting API Service")
    app.run(host='0.0.0.0', port=5004, debug=True)
