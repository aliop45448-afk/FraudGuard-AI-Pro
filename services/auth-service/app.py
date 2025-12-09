"""
Authentication Service API for FraudGuard AI Pro

Flask-based REST API for user authentication, authorization, and security management.
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime
import logging
import os

from security_manager import (
    AES256Encryptor,
    PasswordManager,
    JWTManager,
    MFAManager,
    ComplianceManager,
    MFAMethod,
)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize security components
encryptor = AES256Encryptor()
password_manager = PasswordManager()
jwt_manager = JWTManager(secret_key=os.getenv("JWT_SECRET_KEY", "your-secret-key-here"))
mfa_manager = MFAManager()
compliance = ComplianceManager()

# In-memory user store (replace with database in production)
users_db = {}
sessions_db = {}


# ============================================================================
# Health Check Endpoints
# ============================================================================

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "service": "auth-service",
        "timestamp": datetime.utcnow().isoformat(),
    }), 200


# ============================================================================
# User Registration and Login Endpoints
# ============================================================================

@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register a new user."""
    try:
        data = request.get_json()

        # Validate required fields
        if not data.get('username') or not data.get('password') or not data.get('email'):
            return jsonify({"error": "Missing required fields"}), 400

        username = data['username']
        password = data['password']
        email = data['email']

        # Check if user already exists
        if username in users_db:
            return jsonify({"error": "User already exists"}), 409

        # Hash password
        hashed_password, salt = password_manager.hash_password(password)

        # Store user
        users_db[username] = {
            "username": username,
            "email": email,
            "password_hash": hashed_password,
            "password_salt": salt,
            "created_at": datetime.utcnow().isoformat(),
            "mfa_enabled": False,
            "mfa_method": None,
        }

        logger.info(f"User registered: {username}")

        return jsonify({
            "status": "registered",
            "username": username,
            "email": compliance.mask_email(email),
        }), 201

    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/auth/login', methods=['POST'])
def login():
    """Authenticate user and return access token."""
    try:
        data = request.get_json()

        # Validate required fields
        if not data.get('username') or not data.get('password'):
            return jsonify({"error": "Missing credentials"}), 400

        username = data['username']
        password = data['password']

        # Check if user exists
        if username not in users_db:
            return jsonify({"error": "Invalid credentials"}), 401

        user = users_db[username]

        # Verify password
        if not password_manager.verify_password(
            password,
            user['password_hash'],
            user['password_salt']
        ):
            return jsonify({"error": "Invalid credentials"}), 401

        # Check if MFA is enabled
        if user.get('mfa_enabled'):
            # Create MFA challenge
            challenge = mfa_manager.create_challenge(
                user_id=username,
                method=MFAMethod[user.get('mfa_method', 'TOTP')]
            )
            return jsonify({
                "status": "mfa_required",
                "challenge_id": challenge.challenge_id,
                "mfa_method": challenge.method.value,
            }), 202

        # Create tokens
        access_token = jwt_manager.create_token(
            user_id=username,
            token_type="access",
            expires_in_hours=1,
            scopes=["read", "write"]
        )

        refresh_token = jwt_manager.create_token(
            user_id=username,
            token_type="refresh",
            expires_in_hours=24,
        )

        logger.info(f"User logged in: {username}")

        return jsonify({
            "status": "authenticated",
            "access_token": access_token.token,
            "refresh_token": refresh_token.token,
            "token_type": "Bearer",
            "expires_in": 3600,
        }), 200

    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({"error": str(e)}), 500


# ============================================================================
# MFA Endpoints
# ============================================================================

@app.route('/api/auth/mfa/verify', methods=['POST'])
def verify_mfa():
    """Verify MFA challenge."""
    try:
        data = request.get_json()

        if not data.get('challenge_id') or not data.get('code'):
            return jsonify({"error": "Missing challenge_id or code"}), 400

        challenge_id = data['challenge_id']
        code = data['code']

        # Verify challenge
        if not mfa_manager.verify_challenge(challenge_id, code):
            return jsonify({"error": "Invalid MFA code"}), 401

        challenge = mfa_manager.get_challenge(challenge_id)

        # Create tokens
        access_token = jwt_manager.create_token(
            user_id=challenge.user_id,
            token_type="access",
            expires_in_hours=1,
            scopes=["read", "write"]
        )

        refresh_token = jwt_manager.create_token(
            user_id=challenge.user_id,
            token_type="refresh",
            expires_in_hours=24,
        )

        logger.info(f"MFA verified for user: {challenge.user_id}")

        return jsonify({
            "status": "authenticated",
            "access_token": access_token.token,
            "refresh_token": refresh_token.token,
            "token_type": "Bearer",
            "expires_in": 3600,
        }), 200

    except Exception as e:
        logger.error(f"MFA verification error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/auth/mfa/enable', methods=['POST'])
def enable_mfa():
    """Enable MFA for user."""
    try:
        data = request.get_json()
        token = request.headers.get('Authorization', '').replace('Bearer ', '')

        if not token:
            return jsonify({"error": "Missing authorization token"}), 401

        payload = jwt_manager.verify_token(token)
        if not payload:
            return jsonify({"error": "Invalid token"}), 401

        user_id = payload['user_id']
        mfa_method = data.get('method', 'TOTP')

        if user_id not in users_db:
            return jsonify({"error": "User not found"}), 404

        users_db[user_id]['mfa_enabled'] = True
        users_db[user_id]['mfa_method'] = mfa_method

        logger.info(f"MFA enabled for user: {user_id}")

        return jsonify({
            "status": "mfa_enabled",
            "mfa_method": mfa_method,
        }), 200

    except Exception as e:
        logger.error(f"MFA enable error: {str(e)}")
        return jsonify({"error": str(e)}), 500


# ============================================================================
# Token Management Endpoints
# ============================================================================

@app.route('/api/auth/token/refresh', methods=['POST'])
def refresh_access_token():
    """Refresh access token using refresh token."""
    try:
        data = request.get_json()

        if not data.get('refresh_token'):
            return jsonify({"error": "Missing refresh_token"}), 400

        refresh_token = data['refresh_token']

        # Verify refresh token
        new_token = jwt_manager.refresh_token(refresh_token, expires_in_hours=1)

        if not new_token:
            return jsonify({"error": "Invalid refresh token"}), 401

        logger.info(f"Token refreshed for user: {new_token.user_id}")

        return jsonify({
            "access_token": new_token.token,
            "token_type": "Bearer",
            "expires_in": 3600,
        }), 200

    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/auth/token/validate', methods=['POST'])
def validate_token():
    """Validate an access token."""
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')

        if not token:
            return jsonify({"error": "Missing authorization token"}), 401

        payload = jwt_manager.verify_token(token)

        if not payload:
            return jsonify({
                "valid": False,
                "error": "Invalid token"
            }), 401

        return jsonify({
            "valid": True,
            "user_id": payload['user_id'],
            "token_type": payload.get('token_type'),
            "scopes": payload.get('scopes', []),
        }), 200

    except Exception as e:
        logger.error(f"Token validation error: {str(e)}")
        return jsonify({"error": str(e)}), 500


# ============================================================================
# Encryption Endpoints
# ============================================================================

@app.route('/api/security/encrypt', methods=['POST'])
def encrypt_data():
    """Encrypt sensitive data."""
    try:
        data = request.get_json()

        if not data.get('plaintext'):
            return jsonify({"error": "Missing plaintext"}), 400

        plaintext = data['plaintext']
        encrypted = encryptor.encrypt(plaintext)

        return jsonify({
            "encrypted": encrypted,
        }), 200

    except Exception as e:
        logger.error(f"Encryption error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/security/decrypt', methods=['POST'])
def decrypt_data():
    """Decrypt sensitive data."""
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')

        if not token:
            return jsonify({"error": "Missing authorization token"}), 401

        payload = jwt_manager.verify_token(token)
        if not payload:
            return jsonify({"error": "Invalid token"}), 401

        data = request.get_json()

        if not data.get('ciphertext'):
            return jsonify({"error": "Missing ciphertext"}), 400

        ciphertext = data['ciphertext']
        decrypted = encryptor.decrypt(ciphertext)

        logger.info(f"Data decrypted by user: {payload['user_id']}")

        return jsonify({
            "decrypted": decrypted,
        }), 200

    except Exception as e:
        logger.error(f"Decryption error: {str(e)}")
        return jsonify({"error": str(e)}), 500


# ============================================================================
# Audit and Compliance Endpoints
# ============================================================================

@app.route('/api/audit/log', methods=['POST'])
def create_audit_log():
    """Create an audit log entry."""
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')

        if not token:
            return jsonify({"error": "Missing authorization token"}), 401

        payload = jwt_manager.verify_token(token)
        if not payload:
            return jsonify({"error": "Invalid token"}), 401

        data = request.get_json()

        audit_log = compliance.generate_audit_log(
            action=data.get('action'),
            user_id=payload['user_id'],
            resource=data.get('resource'),
            details=data.get('details', {}),
        )

        logger.info(f"Audit log created: {audit_log['audit_id']}")

        return jsonify(audit_log), 201

    except Exception as e:
        logger.error(f"Audit log error: {str(e)}")
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
    logger.info("Starting Authentication Service API")
    app.run(host='0.0.0.0', port=5001, debug=True)
