"""
Integrations Service for FraudGuard AI Pro

Manages integrations with external systems (SIEM, KYC, Slack, Teams, etc.)
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime
from typing import Dict, List, Optional
import logging
import json
import uuid
import requests
from dataclasses import dataclass, asdict
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IntegrationType(str, Enum):
    """Integration types."""
    SIEM = "siem"
    KYC = "kyc"
    SLACK = "slack"
    TEAMS = "teams"
    EMAIL = "email"
    WEBHOOK = "webhook"
    DATABASE = "database"


class IntegrationStatus(str, Enum):
    """Integration status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    PENDING = "pending"


@dataclass
class Integration:
    """Integration configuration."""
    integration_id: str
    name: str
    integration_type: str
    status: str
    config: Dict
    created_at: str
    last_sync: Optional[str] = None
    error_message: Optional[str] = None


@dataclass
class IntegrationLog:
    """Integration activity log."""
    log_id: str
    integration_id: str
    action: str
    status: str
    message: str
    timestamp: str


class SIEMIntegration:
    """SIEM (Security Information and Event Management) integration."""

    def __init__(self):
        """Initialize SIEM integration."""
        self.siem_endpoint = None
        logger.info("SIEMIntegration initialized")

    def configure(self, endpoint: str, api_key: str) -> bool:
        """Configure SIEM integration."""
        try:
            self.siem_endpoint = endpoint
            self.api_key = api_key
            logger.info("SIEM configured successfully")
            return True
        except Exception as e:
            logger.error(f"SIEM configuration error: {str(e)}")
            return False

    def send_alert(self, alert_data: Dict) -> bool:
        """Send fraud alert to SIEM."""
        try:
            if not self.siem_endpoint:
                logger.error("SIEM not configured")
                return False

            response = requests.post(
                f"{self.siem_endpoint}/api/alerts",
                json=alert_data,
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=10,
            )

            if response.status_code == 200:
                logger.info("Alert sent to SIEM successfully")
                return True
            else:
                logger.error(f"SIEM alert failed: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"SIEM alert error: {str(e)}")
            return False


class KYCIntegration:
    """KYC (Know Your Customer) integration."""

    def __init__(self):
        """Initialize KYC integration."""
        self.kyc_endpoint = None
        logger.info("KYCIntegration initialized")

    def configure(self, endpoint: str, api_key: str) -> bool:
        """Configure KYC integration."""
        try:
            self.kyc_endpoint = endpoint
            self.api_key = api_key
            logger.info("KYC configured successfully")
            return True
        except Exception as e:
            logger.error(f"KYC configuration error: {str(e)}")
            return False

    def verify_customer(self, customer_data: Dict) -> Dict:
        """Verify customer against KYC database."""
        try:
            if not self.kyc_endpoint:
                return {"verified": False, "error": "KYC not configured"}

            response = requests.post(
                f"{self.kyc_endpoint}/api/verify",
                json=customer_data,
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=10,
            )

            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"KYC verification failed: {response.status_code}")
                return {"verified": False, "error": "Verification failed"}

        except Exception as e:
            logger.error(f"KYC verification error: {str(e)}")
            return {"verified": False, "error": str(e)}


class SlackIntegration:
    """Slack notification integration."""

    def __init__(self):
        """Initialize Slack integration."""
        self.webhook_url = None
        logger.info("SlackIntegration initialized")

    def configure(self, webhook_url: str) -> bool:
        """Configure Slack integration."""
        try:
            self.webhook_url = webhook_url
            logger.info("Slack configured successfully")
            return True
        except Exception as e:
            logger.error(f"Slack configuration error: {str(e)}")
            return False

    def send_notification(self, message: str, channel: Optional[str] = None) -> bool:
        """Send notification to Slack."""
        try:
            if not self.webhook_url:
                logger.error("Slack not configured")
                return False

            payload = {
                "text": message,
                "channel": channel or "#fraud-alerts",
            }

            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=10,
            )

            if response.status_code == 200:
                logger.info("Slack notification sent successfully")
                return True
            else:
                logger.error(f"Slack notification failed: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"Slack notification error: {str(e)}")
            return False


class TeamsIntegration:
    """Microsoft Teams notification integration."""

    def __init__(self):
        """Initialize Teams integration."""
        self.webhook_url = None
        logger.info("TeamsIntegration initialized")

    def configure(self, webhook_url: str) -> bool:
        """Configure Teams integration."""
        try:
            self.webhook_url = webhook_url
            logger.info("Teams configured successfully")
            return True
        except Exception as e:
            logger.error(f"Teams configuration error: {str(e)}")
            return False

    def send_notification(self, title: str, message: str, color: str = "0078D4") -> bool:
        """Send notification to Teams."""
        try:
            if not self.webhook_url:
                logger.error("Teams not configured")
                return False

            payload = {
                "@type": "MessageCard",
                "@context": "https://schema.org/extensions",
                "summary": title,
                "themeColor": color,
                "sections": [
                    {
                        "activityTitle": title,
                        "text": message,
                    }
                ],
            }

            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=10,
            )

            if response.status_code == 200:
                logger.info("Teams notification sent successfully")
                return True
            else:
                logger.error(f"Teams notification failed: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"Teams notification error: {str(e)}")
            return False


class IntegrationManager:
    """Manages all integrations."""

    def __init__(self):
        """Initialize integration manager."""
        self.integrations: Dict[str, Integration] = {}
        self.logs: List[IntegrationLog] = []
        self.siem = SIEMIntegration()
        self.kyc = KYCIntegration()
        self.slack = SlackIntegration()
        self.teams = TeamsIntegration()
        logger.info("IntegrationManager initialized")

    def add_integration(
        self,
        name: str,
        integration_type: str,
        config: Dict,
    ) -> Integration:
        """Add a new integration."""
        integration_id = f"int_{uuid.uuid4().hex[:12]}"

        integration = Integration(
            integration_id=integration_id,
            name=name,
            integration_type=integration_type,
            status=IntegrationStatus.PENDING.value,
            config=config,
            created_at=datetime.utcnow().isoformat(),
        )

        self.integrations[integration_id] = integration

        # Configure the integration
        if integration_type == IntegrationType.SIEM.value:
            if self.siem.configure(config.get('endpoint'), config.get('api_key')):
                integration.status = IntegrationStatus.ACTIVE.value
        elif integration_type == IntegrationType.KYC.value:
            if self.kyc.configure(config.get('endpoint'), config.get('api_key')):
                integration.status = IntegrationStatus.ACTIVE.value
        elif integration_type == IntegrationType.SLACK.value:
            if self.slack.configure(config.get('webhook_url')):
                integration.status = IntegrationStatus.ACTIVE.value
        elif integration_type == IntegrationType.TEAMS.value:
            if self.teams.configure(config.get('webhook_url')):
                integration.status = IntegrationStatus.ACTIVE.value

        self._log_action(integration_id, "created", "success", f"Integration {name} created")
        logger.info(f"Integration added: {integration_id}")

        return integration

    def get_integration(self, integration_id: str) -> Optional[Integration]:
        """Get integration by ID."""
        return self.integrations.get(integration_id)

    def list_integrations(self) -> List[Integration]:
        """List all integrations."""
        return list(self.integrations.values())

    def delete_integration(self, integration_id: str) -> bool:
        """Delete an integration."""
        if integration_id in self.integrations:
            del self.integrations[integration_id]
            self._log_action(integration_id, "deleted", "success", "Integration deleted")
            logger.info(f"Integration deleted: {integration_id}")
            return True
        return False

    def _log_action(
        self,
        integration_id: str,
        action: str,
        status: str,
        message: str,
    ) -> IntegrationLog:
        """Log integration action."""
        log_id = f"log_{uuid.uuid4().hex[:12]}"

        log = IntegrationLog(
            log_id=log_id,
            integration_id=integration_id,
            action=action,
            status=status,
            message=message,
            timestamp=datetime.utcnow().isoformat(),
        )

        self.logs.append(log)
        return log

    def get_logs(self, integration_id: Optional[str] = None) -> List[IntegrationLog]:
        """Get integration logs."""
        if integration_id:
            return [log for log in self.logs if log.integration_id == integration_id]
        return self.logs


# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize integration manager
integration_manager = IntegrationManager()


# ============================================================================
# Health Check
# ============================================================================

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "service": "integrations-service",
        "timestamp": datetime.utcnow().isoformat(),
    }), 200


# ============================================================================
# Integration Management Endpoints
# ============================================================================

@app.route('/api/integrations', methods=['POST'])
def add_integration():
    """Add a new integration."""
    try:
        data = request.get_json()

        required_fields = ['name', 'type', 'config']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing field: {field}"}), 400

        integration = integration_manager.add_integration(
            name=data['name'],
            integration_type=data['type'],
            config=data['config'],
        )

        return jsonify(asdict(integration)), 201

    except Exception as e:
        logger.error(f"Integration creation error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/integrations', methods=['GET'])
def list_integrations():
    """List all integrations."""
    try:
        integrations = integration_manager.list_integrations()

        return jsonify({
            "total": len(integrations),
            "integrations": [asdict(i) for i in integrations],
        }), 200

    except Exception as e:
        logger.error(f"Integration list error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/integrations/<integration_id>', methods=['GET'])
def get_integration(integration_id):
    """Get integration details."""
    try:
        integration = integration_manager.get_integration(integration_id)

        if not integration:
            return jsonify({"error": "Integration not found"}), 404

        return jsonify(asdict(integration)), 200

    except Exception as e:
        logger.error(f"Integration retrieval error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/integrations/<integration_id>', methods=['DELETE'])
def delete_integration(integration_id):
    """Delete an integration."""
    try:
        if integration_manager.delete_integration(integration_id):
            return jsonify({
                "integration_id": integration_id,
                "status": "deleted",
            }), 200
        else:
            return jsonify({"error": "Integration not found"}), 404

    except Exception as e:
        logger.error(f"Integration deletion error: {str(e)}")
        return jsonify({"error": str(e)}), 500


# ============================================================================
# Integration Logs Endpoints
# ============================================================================

@app.route('/api/integrations/logs', methods=['GET'])
def get_integration_logs():
    """Get integration logs."""
    try:
        integration_id = request.args.get('integration_id')
        logs = integration_manager.get_logs(integration_id)

        return jsonify({
            "total": len(logs),
            "logs": [asdict(log) for log in logs],
        }), 200

    except Exception as e:
        logger.error(f"Logs retrieval error: {str(e)}")
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
    logger.info("Starting Integrations Service")
    app.run(host='0.0.0.0', port=5008, debug=True)
