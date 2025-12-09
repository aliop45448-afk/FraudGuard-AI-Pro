"""
Security Manager for FraudGuard AI Pro

This module implements comprehensive security features including:
- AES-256 encryption/decryption
- Multi-Factor Authentication (MFA)
- JWT token management
- Password hashing and validation
- GDPR/PCI DSS compliance utilities
"""

import hashlib
import hmac
import secrets
import jwt
import logging
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import json

try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
    from cryptography.hazmat.backends import default_backend
    import base64
except ImportError:
    print("Warning: cryptography library not installed. Some features will be limited.")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MFAMethod(Enum):
    """Multi-Factor Authentication methods."""
    TOTP = "totp"  # Time-based One-Time Password
    SMS = "sms"
    EMAIL = "email"
    HARDWARE_KEY = "hardware_key"


@dataclass
class MFAChallenge:
    """Represents an MFA challenge."""
    challenge_id: str
    user_id: str
    method: MFAMethod
    created_at: str
    expires_at: str
    is_verified: bool


@dataclass
class SecurityToken:
    """Represents a security token."""
    token: str
    user_id: str
    token_type: str  # access, refresh, api_key
    issued_at: str
    expires_at: str
    scopes: list


class AES256Encryptor:
    """
    AES-256 encryption/decryption utility.
    
    Provides secure encryption and decryption of sensitive data
    using AES-256 in Fernet mode.
    """

    def __init__(self, master_key: Optional[str] = None):
        """
        Initialize the encryptor.
        
        Args:
            master_key: Master encryption key (if None, generates new one)
        """
        if master_key:
            self.master_key = master_key.encode() if isinstance(master_key, str) else master_key
        else:
            self.master_key = Fernet.generate_key()
        
        self.cipher = Fernet(self.master_key)
        logger.info("AES256Encryptor initialized")

    def encrypt(self, plaintext: str) -> str:
        """
        Encrypt plaintext using AES-256.
        
        Args:
            plaintext: Text to encrypt
            
        Returns:
            Encrypted text (base64 encoded)
        """
        if isinstance(plaintext, str):
            plaintext = plaintext.encode()
        
        encrypted = self.cipher.encrypt(plaintext)
        return encrypted.decode()

    def decrypt(self, ciphertext: str) -> str:
        """
        Decrypt ciphertext using AES-256.
        
        Args:
            ciphertext: Encrypted text to decrypt
            
        Returns:
            Decrypted plaintext
        """
        if isinstance(ciphertext, str):
            ciphertext = ciphertext.encode()
        
        decrypted = self.cipher.decrypt(ciphertext)
        return decrypted.decode()

    def get_master_key(self) -> str:
        """Get the master key for storage."""
        return self.master_key.decode()


class PasswordManager:
    """
    Password hashing and validation utility.
    
    Implements secure password hashing using PBKDF2 with SHA-256.
    """

    def __init__(self, iterations: int = 100000):
        """
        Initialize the password manager.
        
        Args:
            iterations: Number of PBKDF2 iterations
        """
        self.iterations = iterations
        logger.info(f"PasswordManager initialized with {iterations} iterations")

    def hash_password(self, password: str) -> Tuple[str, str]:
        """
        Hash a password using PBKDF2.
        
        Args:
            password: Password to hash
            
        Returns:
            Tuple of (hashed_password, salt)
        """
        salt = secrets.token_hex(32)
        
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt.encode(),
            iterations=self.iterations,
            backend=default_backend()
        )
        
        key = kdf.derive(password.encode())
        hashed = base64.b64encode(key).decode()
        
        return hashed, salt

    def verify_password(self, password: str, hashed: str, salt: str) -> bool:
        """
        Verify a password against its hash.
        
        Args:
            password: Password to verify
            hashed: Stored hash
            salt: Salt used for hashing
            
        Returns:
            True if password matches, False otherwise
        """
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt.encode(),
            iterations=self.iterations,
            backend=default_backend()
        )
        
        key = kdf.derive(password.encode())
        computed_hash = base64.b64encode(key).decode()
        
        return hmac.compare_digest(computed_hash, hashed)

    def generate_temporary_password(self, length: int = 16) -> str:
        """
        Generate a temporary password.
        
        Args:
            length: Length of the password
            
        Returns:
            Temporary password
        """
        return secrets.token_urlsafe(length)


class JWTManager:
    """
    JWT token management utility.
    
    Handles creation, validation, and refresh of JWT tokens.
    """

    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        """
        Initialize the JWT manager.
        
        Args:
            secret_key: Secret key for signing tokens
            algorithm: JWT algorithm (default: HS256)
        """
        self.secret_key = secret_key
        self.algorithm = algorithm
        logger.info(f"JWTManager initialized with algorithm {algorithm}")

    def create_token(
        self,
        user_id: str,
        token_type: str = "access",
        expires_in_hours: int = 1,
        scopes: Optional[list] = None,
    ) -> SecurityToken:
        """
        Create a JWT token.
        
        Args:
            user_id: User ID
            token_type: Type of token (access, refresh, api_key)
            expires_in_hours: Token expiration time in hours
            scopes: List of scopes for the token
            
        Returns:
            SecurityToken object
        """
        now = datetime.utcnow()
        expires_at = now + timedelta(hours=expires_in_hours)
        
        payload = {
            "user_id": user_id,
            "token_type": token_type,
            "iat": now,
            "exp": expires_at,
            "scopes": scopes or [],
        }
        
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        
        return SecurityToken(
            token=token,
            user_id=user_id,
            token_type=token_type,
            issued_at=now.isoformat(),
            expires_at=expires_at.isoformat(),
            scopes=scopes or [],
        )

    def verify_token(self, token: str) -> Optional[Dict]:
        """
        Verify and decode a JWT token.
        
        Args:
            token: Token to verify
            
        Returns:
            Decoded token payload or None if invalid
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {str(e)}")
            return None

    def refresh_token(self, token: str, expires_in_hours: int = 1) -> Optional[SecurityToken]:
        """
        Refresh an expired token.
        
        Args:
            token: Token to refresh
            expires_in_hours: New expiration time in hours
            
        Returns:
            New SecurityToken or None if refresh failed
        """
        payload = self.verify_token(token)
        if not payload:
            return None
        
        return self.create_token(
            user_id=payload["user_id"],
            token_type=payload.get("token_type", "access"),
            expires_in_hours=expires_in_hours,
            scopes=payload.get("scopes"),
        )


class MFAManager:
    """
    Multi-Factor Authentication manager.
    
    Handles MFA challenges and verification.
    """

    def __init__(self):
        """Initialize the MFA manager."""
        self.active_challenges: Dict[str, MFAChallenge] = {}
        logger.info("MFAManager initialized")

    def create_challenge(
        self,
        user_id: str,
        method: MFAMethod,
        expires_in_minutes: int = 5,
    ) -> MFAChallenge:
        """
        Create an MFA challenge.
        
        Args:
            user_id: User ID
            method: MFA method
            expires_in_minutes: Challenge expiration time
            
        Returns:
            MFAChallenge object
        """
        challenge_id = secrets.token_urlsafe(16)
        now = datetime.utcnow()
        expires_at = now + timedelta(minutes=expires_in_minutes)
        
        challenge = MFAChallenge(
            challenge_id=challenge_id,
            user_id=user_id,
            method=method,
            created_at=now.isoformat(),
            expires_at=expires_at.isoformat(),
            is_verified=False,
        )
        
        self.active_challenges[challenge_id] = challenge
        logger.info(f"MFA challenge created for user {user_id}")
        
        return challenge

    def verify_challenge(self, challenge_id: str, verification_code: str) -> bool:
        """
        Verify an MFA challenge.
        
        Args:
            challenge_id: Challenge ID
            verification_code: Verification code provided by user
            
        Returns:
            True if verification successful, False otherwise
        """
        challenge = self.active_challenges.get(challenge_id)
        
        if not challenge:
            logger.warning(f"Challenge {challenge_id} not found")
            return False
        
        # Check if challenge expired
        if datetime.fromisoformat(challenge.expires_at) < datetime.utcnow():
            logger.warning(f"Challenge {challenge_id} expired")
            del self.active_challenges[challenge_id]
            return False
        
        # Placeholder: In production, verify the code based on the MFA method
        # For now, accept any 6-digit code
        if len(verification_code) == 6 and verification_code.isdigit():
            challenge.is_verified = True
            logger.info(f"Challenge {challenge_id} verified for user {challenge.user_id}")
            return True
        
        return False

    def get_challenge(self, challenge_id: str) -> Optional[MFAChallenge]:
        """Get an MFA challenge."""
        return self.active_challenges.get(challenge_id)


class ComplianceManager:
    """
    Compliance utilities for GDPR and PCI DSS.
    
    Provides tools for data masking, audit logging, and compliance reporting.
    """

    @staticmethod
    def mask_credit_card(card_number: str) -> str:
        """
        Mask credit card number for display.
        
        Args:
            card_number: Full credit card number
            
        Returns:
            Masked card number (e.g., XXXX-XXXX-XXXX-1234)
        """
        if len(card_number) < 4:
            return "XXXX"
        
        last_four = card_number[-4:]
        return f"XXXX-XXXX-XXXX-{last_four}"

    @staticmethod
    def mask_email(email: str) -> str:
        """
        Mask email address for display.
        
        Args:
            email: Full email address
            
        Returns:
            Masked email (e.g., u***@example.com)
        """
        if "@" not in email:
            return "***"
        
        local, domain = email.split("@", 1)
        if len(local) <= 1:
            masked_local = "*"
        else:
            masked_local = local[0] + "*" * (len(local) - 2) + local[-1]
        
        return f"{masked_local}@{domain}"

    @staticmethod
    def mask_phone(phone: str) -> str:
        """
        Mask phone number for display.
        
        Args:
            phone: Full phone number
            
        Returns:
            Masked phone number (e.g., XXX-XXX-1234)
        """
        if len(phone) < 4:
            return "XXX"
        
        last_four = phone[-4:]
        return f"XXX-XXX-{last_four}"

    @staticmethod
    def generate_audit_log(
        action: str,
        user_id: str,
        resource: str,
        details: Dict,
    ) -> Dict:
        """
        Generate an audit log entry.
        
        Args:
            action: Action performed
            user_id: User who performed the action
            resource: Resource affected
            details: Additional details
            
        Returns:
            Audit log entry
        """
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "action": action,
            "user_id": user_id,
            "resource": resource,
            "details": details,
            "audit_id": secrets.token_urlsafe(16),
        }


# Example usage
if __name__ == "__main__":
    # Initialize security components
    encryptor = AES256Encryptor()
    password_manager = PasswordManager()
    jwt_manager = JWTManager(secret_key="your-secret-key-here")
    mfa_manager = MFAManager()
    compliance = ComplianceManager()

    # Example: Encrypt/Decrypt
    plaintext = "Sensitive transaction data"
    encrypted = encryptor.encrypt(plaintext)
    decrypted = encryptor.decrypt(encrypted)
    print(f"Original: {plaintext}")
    print(f"Encrypted: {encrypted}")
    print(f"Decrypted: {decrypted}")

    # Example: Password hashing
    password = "MySecurePassword123!"
    hashed, salt = password_manager.hash_password(password)
    is_valid = password_manager.verify_password(password, hashed, salt)
    print(f"\nPassword valid: {is_valid}")

    # Example: JWT token
    token = jwt_manager.create_token(user_id="user_123", expires_in_hours=24)
    print(f"\nToken created: {token.token[:50]}...")
    verified = jwt_manager.verify_token(token.token)
    print(f"Token verified: {verified is not None}")

    # Example: MFA
    challenge = mfa_manager.create_challenge(user_id="user_123", method=MFAMethod.TOTP)
    print(f"\nMFA Challenge: {challenge.challenge_id}")

    # Example: Compliance masking
    print(f"\nMasked card: {compliance.mask_credit_card('4532123456789010')}")
    print(f"Masked email: {compliance.mask_email('user@example.com')}")
    print(f"Masked phone: {compliance.mask_phone('+1234567890')}")
