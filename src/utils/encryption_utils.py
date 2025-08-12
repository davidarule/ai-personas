#!/usr/bin/env python3
"""
Encryption utilities for securing sensitive data like API keys
Uses Fernet symmetric encryption from the cryptography library
"""

import os
import base64
import logging
from typing import Optional, Union
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

logger = logging.getLogger(__name__)


class EncryptionError(Exception):
    """Custom exception for encryption-related errors"""
    pass


class EncryptionManager:
    """Manages encryption and decryption of sensitive data"""
    
    def __init__(self, master_key: Optional[str] = None):
        """Initialize the encryption manager
        
        Args:
            master_key: Base64 encoded master key. If not provided, reads from ENCRYPTION_KEY env var
        """
        if master_key:
            self._master_key = master_key
        else:
            self._master_key = os.getenv('ENCRYPTION_KEY')
            
        if not self._master_key:
            raise EncryptionError(
                "No encryption key provided. Set ENCRYPTION_KEY environment variable or pass master_key parameter"
            )
        
        try:
            # Validate the key is valid base64
            base64.b64decode(self._master_key)
        except Exception as e:
            raise EncryptionError(f"Invalid encryption key format: {str(e)}")
        
        # Create Fernet instance
        self._fernet = self._create_fernet_from_master_key(self._master_key)
        
    def _create_fernet_from_master_key(self, master_key: str) -> Fernet:
        """Create a Fernet instance from the master key
        
        Args:
            master_key: Base64 encoded master key
            
        Returns:
            Fernet instance for encryption/decryption
        """
        try:
            # Decode the base64 master key
            master_key_bytes = base64.b64decode(master_key)
            
            # If the key is already 32 bytes (Fernet key size), use it directly
            if len(master_key_bytes) == 32:
                fernet_key = base64.urlsafe_b64encode(master_key_bytes)
                return Fernet(fernet_key)
            
            # Otherwise, derive a key using PBKDF2
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=b'ai-personas-salt',  # Static salt for consistent key derivation
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(master_key_bytes))
            return Fernet(key)
            
        except Exception as e:
            raise EncryptionError(f"Failed to create encryption instance: {str(e)}")
    
    def encrypt(self, plaintext: str) -> str:
        """Encrypt a plaintext string
        
        Args:
            plaintext: The string to encrypt
            
        Returns:
            Base64 encoded encrypted data
        """
        if not plaintext:
            return ""
            
        try:
            # Convert to bytes and encrypt
            plaintext_bytes = plaintext.encode('utf-8')
            encrypted_bytes = self._fernet.encrypt(plaintext_bytes)
            
            # Return as base64 string for easy storage
            return base64.b64encode(encrypted_bytes).decode('utf-8')
            
        except Exception as e:
            logger.error(f"Encryption failed: {str(e)}")
            raise EncryptionError(f"Failed to encrypt data: {str(e)}")
    
    def decrypt(self, ciphertext: str) -> str:
        """Decrypt an encrypted string
        
        Args:
            ciphertext: Base64 encoded encrypted data
            
        Returns:
            Decrypted plaintext string
        """
        if not ciphertext:
            return ""
            
        try:
            # Decode from base64
            encrypted_bytes = base64.b64decode(ciphertext)
            
            # Decrypt
            decrypted_bytes = self._fernet.decrypt(encrypted_bytes)
            
            # Convert back to string
            return decrypted_bytes.decode('utf-8')
            
        except Exception as e:
            logger.error(f"Decryption failed: {str(e)}")
            raise EncryptionError(f"Failed to decrypt data: {str(e)}")
    
    def encrypt_api_key(self, api_key: str, provider_id: str) -> tuple[str, str]:
        """Encrypt an API key and generate a hint
        
        Args:
            api_key: The API key to encrypt
            provider_id: The provider ID (used for additional context)
            
        Returns:
            Tuple of (encrypted_key, key_hint)
        """
        if not api_key:
            return ("", "")
            
        # Generate hint (last 4 characters)
        key_hint = '****' + api_key[-4:] if len(api_key) > 4 else '****'
        
        # Add provider context to make encrypted values unique per provider
        contextualized_key = f"{provider_id}:{api_key}"
        
        # Encrypt the key
        encrypted_key = self.encrypt(contextualized_key)
        
        return (encrypted_key, key_hint)
    
    def decrypt_api_key(self, encrypted_key: str, provider_id: str) -> str:
        """Decrypt an API key
        
        Args:
            encrypted_key: The encrypted API key
            provider_id: The provider ID (used for validation)
            
        Returns:
            Decrypted API key
        """
        if not encrypted_key:
            return ""
            
        # Decrypt the key
        decrypted = self.decrypt(encrypted_key)
        
        # Validate and extract the actual key
        if ':' in decrypted:
            stored_provider, actual_key = decrypted.split(':', 1)
            if stored_provider != provider_id:
                logger.warning(f"Provider mismatch in decrypted key: expected {provider_id}, got {stored_provider}")
            return actual_key
        
        # Fallback for keys without provider context
        return decrypted


# Singleton instance
_encryption_manager: Optional[EncryptionManager] = None


def get_encryption_manager() -> EncryptionManager:
    """Get the singleton encryption manager instance
    
    Returns:
        EncryptionManager instance
    """
    global _encryption_manager
    if _encryption_manager is None:
        _encryption_manager = EncryptionManager()
    return _encryption_manager


def is_encryption_available() -> bool:
    """Check if encryption is available (key is configured)
    
    Returns:
        True if encryption can be used, False otherwise
    """
    return bool(os.getenv('ENCRYPTION_KEY'))


def generate_encryption_key() -> str:
    """Generate a new encryption key
    
    Returns:
        Base64 encoded encryption key suitable for use as ENCRYPTION_KEY
    """
    # Generate a new Fernet key (32 bytes)
    key = Fernet.generate_key()
    # Extract just the key bytes (remove URL-safe base64 encoding)
    key_bytes = base64.urlsafe_b64decode(key)
    # Return as standard base64 for cleaner environment variable
    return base64.b64encode(key_bytes).decode('utf-8')