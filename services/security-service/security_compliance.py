"""
Security & Compliance Service for FraudGuard AI Pro

Implements encryption, audit logging, GDPR compliance, and PCI DSS requirements.
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
import json
import hashlib
import hmac
import uuid
from dataclasses import dataclass, asdict
from cryptography.fernet import Fernet
import base64

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class AuditLog:
    """Audit log entry."""
    log_id: str
    user_id: str
    action: str
    resource_type: str
    resource_id: str
    timestamp: str
    ip_address: str
    status: str
    details: Dict


@dataclass
class EncryptionKey:
    """Encryption key management."""
    key_id: str
    algorithm: str
    created_at: str
    is_active: bool
    rotation_date: Optional[str] = None


class EncryptionManager:
    """Manages data encryption and decryption."""

    def __init__(self):
        """Initialize encryption manager."""
        self.keys: Dict[str, EncryptionKey] = {}
        self.current_key_id = None
        self._initialize_keys()
        logger.info("EncryptionManager initialized")

    def _initialize_keys(self):
        """Initialize default encryption keys."""
        # Generate initial key
        key = Fernet.generate_key()
        key_id = f"key_{uuid.uuid4().hex[:12]}"

        self.keys[key_id] = EncryptionKey(
            key_id=key_id,
            algorithm="AES-256-Fernet",
            created_at=datetime.utcnow().isoformat(),
            is_active=True,
        )

        self.current_key_id = key_id
        self._cipher = Fernet(key)

    def encrypt_data(self, data: str) -> str:
        """
        Encrypt sensitive data.

        Args:
            data: Data to encrypt

        Returns:
            Encrypted data as base64 string
        """
        try:
            encrypted = self._cipher.encrypt(data.encode())
            return base64.b64encode(encrypted).decode()
        except Exception as e:
            logger.error(f"Encryption error: {str(e)}")
            raise

    def decrypt_data(self, encrypted_data: str) -> str:
        """
        Decrypt sensitive data.

        Args:
            encrypted_data: Encrypted data as base64 string

        Returns:
            Decrypted data
        """
        try:
            encrypted = base64.b64decode(encrypted_data.encode())
            decrypted = self._cipher.decrypt(encrypted)
            return decrypted.decode()
        except Exception as e:
            logger.error(f"Decryption error: {str(e)}")
            raise

    def rotate_keys(self) -> str:
        """
        Rotate encryption keys.

        Returns:
            New key ID
        """
        # Deactivate current key
        if self.current_key_id:
            self.keys[self.current_key_id].is_active = False

        # Generate new key
        key = Fernet.generate_key()
        key_id = f"key_{uuid.uuid4().hex[:12]}"

        self.keys[key_id] = EncryptionKey(
            key_id=key_id,
            algorithm="AES-256-Fernet",
            created_at=datetime.utcnow().isoformat(),
            is_active=True,
        )

        self.current_key_id = key_id
        self._cipher = Fernet(key)

        logger.info(f"Keys rotated: {key_id}")
        return key_id


class AuditLogger:
    """Manages audit logging for compliance."""

    def __init__(self):
        """Initialize audit logger."""
        self.logs: List[AuditLog] = []
        logger.info("AuditLogger initialized")

    def log_action(
        self,
        user_id: str,
        action: str,
        resource_type: str,
        resource_id: str,
        ip_address: str,
        status: str = "success",
        details: Optional[Dict] = None,
    ) -> AuditLog:
        """
        Log an action for audit trail.

        Args:
            user_id: User performing the action
            action: Action performed (CREATE, READ, UPDATE, DELETE)
            resource_type: Type of resource
            resource_id: ID of the resource
            ip_address: IP address of the request
            status: Status of the action
            details: Additional details

        Returns:
            AuditLog entry
        """
        log_id = f"audit_{uuid.uuid4().hex[:12]}"

        log = AuditLog(
            log_id=log_id,
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            timestamp=datetime.utcnow().isoformat(),
            ip_address=ip_address,
            status=status,
            details=details or {},
        )

        self.logs.append(log)
        logger.info(f"Action logged: {action} on {resource_type} {resource_id}")

        return log

    def get_audit_trail(
        self,
        user_id: Optional[str] = None,
        resource_type: Optional[str] = None,
        days: int = 30,
    ) -> List[AuditLog]:
        """
        Get audit trail for specified criteria.

        Args:
            user_id: Filter by user
            resource_type: Filter by resource type
            days: Number of days to look back

        Returns:
            List of audit logs
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        logs = [
            log for log in self.logs
            if datetime.fromisoformat(log.timestamp) > cutoff_date
        ]

        if user_id:
            logs = [log for log in logs if log.user_id == user_id]

        if resource_type:
            logs = [log for log in logs if log.resource_type == resource_type]

        return logs


class GDPRCompliance:
    """Implements GDPR compliance features."""

    @staticmethod
    def mask_pii(data: Dict) -> Dict:
        """
        Mask personally identifiable information.

        Args:
            data: Data to mask

        Returns:
            Masked data
        """
        masked = data.copy()

        # Mask email
        if 'email' in masked:
            email = masked['email']
            parts = email.split('@')
            masked['email'] = f"{parts[0][:2]}***@{parts[1]}"

        # Mask phone
        if 'phone' in masked:
            phone = masked['phone']
            masked['phone'] = f"***{phone[-4:]}"

        # Mask credit card
        if 'card_number' in masked:
            card = masked['card_number']
            masked['card_number'] = f"****{card[-4:]}"

        # Mask SSN
        if 'ssn' in masked:
            masked['ssn'] = "***-**-****"

        # Mask address
        if 'address' in masked:
            masked['address'] = "***"

        return masked

    @staticmethod
    def anonymize_data(data: Dict) -> Dict:
        """
        Anonymize data for analytics.

        Args:
            data: Data to anonymize

        Returns:
            Anonymized data
        """
        anonymized = {}

        for key, value in data.items():
            if key in ['user_id', 'email', 'phone', 'name']:
                # Hash sensitive fields
                anonymized[key] = hashlib.sha256(
                    str(value).encode()
                ).hexdigest()[:16]
            else:
                anonymized[key] = value

        return anonymized

    @staticmethod
    def get_data_export(user_id: str) -> Dict:
        """
        Export user's personal data (GDPR right to data portability).

        Args:
            user_id: User ID

        Returns:
            User's personal data
        """
        # Mock data export
        return {
            "user_id": user_id,
            "export_date": datetime.utcnow().isoformat(),
            "data": {
                "profile": {"name": "User Name", "email": "user@example.com"},
                "transactions": [],
                "preferences": {},
            },
        }


class PCIDSSCompliance:
    """Implements PCI DSS compliance features."""

    @staticmethod
    def validate_card_number(card_number: str) -> bool:
        """
        Validate credit card number using Luhn algorithm.

        Args:
            card_number: Credit card number

        Returns:
            True if valid, False otherwise
        """
        # Remove spaces and dashes
        card_number = card_number.replace(" ", "").replace("-", "")

        if not card_number.isdigit() or len(card_number) < 13:
            return False

        # Luhn algorithm
        digits = [int(d) for d in card_number]
        checksum = 0

        for i, digit in enumerate(reversed(digits)):
            if i % 2 == 1:
                digit *= 2
                if digit > 9:
                    digit -= 9
            checksum += digit

        return checksum % 10 == 0

    @staticmethod
    def mask_card_number(card_number: str) -> str:
        """
        Mask credit card number for display.

        Args:
            card_number: Credit card number

        Returns:
            Masked card number
        """
        card_number = card_number.replace(" ", "").replace("-", "")
        return f"****-****-****-{card_number[-4:]}"

    @staticmethod
    def generate_security_headers() -> Dict[str, str]:
        """
        Generate security headers for PCI DSS compliance.

        Returns:
            Security headers
        """
        return {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": "default-src 'self'",
            "Referrer-Policy": "strict-origin-when-cross-origin",
        }


# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize managers
encryption_manager = EncryptionManager()
audit_logger = AuditLogger()
gdpr_compliance = GDPRCompliance()
pci_compliance = PCIDSSCompliance()


# ============================================================================
# Health Check
# ============================================================================

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "service": "security-service",
        "timestamp": datetime.utcnow().isoformat(),
    }), 200


# ============================================================================
# Encryption Endpoints
# ============================================================================

@app.route('/api/encryption/encrypt', methods=['POST'])
def encrypt_endpoint():
    """Encrypt data."""
    try:
        data = request.get_json()

        if 'data' not in data:
            return jsonify({"error": "Missing data field"}), 400

        encrypted = encryption_manager.encrypt_data(data['data'])

        return jsonify({
            "encrypted": encrypted,
            "key_id": encryption_manager.current_key_id,
            "algorithm": "AES-256-Fernet",
        }), 200

    except Exception as e:
        logger.error(f"Encryption error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/encryption/decrypt', methods=['POST'])
def decrypt_endpoint():
    """Decrypt data."""
    try:
        data = request.get_json()

        if 'encrypted' not in data:
            return jsonify({"error": "Missing encrypted field"}), 400

        decrypted = encryption_manager.decrypt_data(data['encrypted'])

        return jsonify({
            "decrypted": decrypted,
            "timestamp": datetime.utcnow().isoformat(),
        }), 200

    except Exception as e:
        logger.error(f"Decryption error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/encryption/rotate-keys', methods=['POST'])
def rotate_keys():
    """Rotate encryption keys."""
    try:
        new_key_id = encryption_manager.rotate_keys()

        return jsonify({
            "status": "keys_rotated",
            "new_key_id": new_key_id,
            "timestamp": datetime.utcnow().isoformat(),
        }), 200

    except Exception as e:
        logger.error(f"Key rotation error: {str(e)}")
        return jsonify({"error": str(e)}), 500


# ============================================================================
# Audit Logging Endpoints
# ============================================================================

@app.route('/api/audit/log', methods=['POST'])
def log_action():
    """Log an action for audit trail."""
    try:
        data = request.get_json()

        required_fields = ['user_id', 'action', 'resource_type', 'resource_id']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing field: {field}"}), 400

        ip_address = request.remote_addr

        log = audit_logger.log_action(
            user_id=data['user_id'],
            action=data['action'],
            resource_type=data['resource_type'],
            resource_id=data['resource_id'],
            ip_address=ip_address,
            status=data.get('status', 'success'),
            details=data.get('details'),
        )

        return jsonify(asdict(log)), 201

    except Exception as e:
        logger.error(f"Audit logging error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/audit/trail', methods=['GET'])
def get_audit_trail():
    """Get audit trail."""
    try:
        user_id = request.args.get('user_id')
        resource_type = request.args.get('resource_type')
        days = int(request.args.get('days', 30))

        logs = audit_logger.get_audit_trail(
            user_id=user_id,
            resource_type=resource_type,
            days=days,
        )

        return jsonify({
            "total": len(logs),
            "logs": [asdict(log) for log in logs],
        }), 200

    except Exception as e:
        logger.error(f"Audit trail retrieval error: {str(e)}")
        return jsonify({"error": str(e)}), 500


# ============================================================================
# GDPR Compliance Endpoints
# ============================================================================

@app.route('/api/gdpr/mask-pii', methods=['POST'])
def mask_pii():
    """Mask personally identifiable information."""
    try:
        data = request.get_json()

        if 'data' not in data:
            return jsonify({"error": "Missing data field"}), 400

        masked = gdpr_compliance.mask_pii(data['data'])

        return jsonify({
            "masked_data": masked,
            "timestamp": datetime.utcnow().isoformat(),
        }), 200

    except Exception as e:
        logger.error(f"PII masking error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/gdpr/anonymize', methods=['POST'])
def anonymize():
    """Anonymize data for analytics."""
    try:
        data = request.get_json()

        if 'data' not in data:
            return jsonify({"error": "Missing data field"}), 400

        anonymized = gdpr_compliance.anonymize_data(data['data'])

        return jsonify({
            "anonymized_data": anonymized,
            "timestamp": datetime.utcnow().isoformat(),
        }), 200

    except Exception as e:
        logger.error(f"Data anonymization error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/gdpr/export/<user_id>', methods=['GET'])
def export_user_data(user_id):
    """Export user's personal data."""
    try:
        export = gdpr_compliance.get_data_export(user_id)

        return jsonify(export), 200

    except Exception as e:
        logger.error(f"Data export error: {str(e)}")
        return jsonify({"error": str(e)}), 500


# ============================================================================
# PCI DSS Compliance Endpoints
# ============================================================================

@app.route('/api/pci/validate-card', methods=['POST'])
def validate_card():
    """Validate credit card number."""
    try:
        data = request.get_json()

        if 'card_number' not in data:
            return jsonify({"error": "Missing card_number field"}), 400

        is_valid = pci_compliance.validate_card_number(data['card_number'])

        return jsonify({
            "card_number": pci_compliance.mask_card_number(data['card_number']),
            "is_valid": is_valid,
            "timestamp": datetime.utcnow().isoformat(),
        }), 200

    except Exception as e:
        logger.error(f"Card validation error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/pci/security-headers', methods=['GET'])
def get_security_headers():
    """Get PCI DSS security headers."""
    try:
        headers = pci_compliance.generate_security_headers()

        return jsonify({
            "headers": headers,
            "timestamp": datetime.utcnow().isoformat(),
        }), 200

    except Exception as e:
        logger.error(f"Security headers error: {str(e)}")
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
    logger.info("Starting Security & Compliance Service")
    app.run(host='0.0.0.0', port=5005, debug=True)
