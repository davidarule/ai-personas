#!/usr/bin/env python3
"""Test encryption availability"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

from utils.encryption_utils import is_encryption_available, get_encryption_manager

print(f"Encryption available: {is_encryption_available()}")
print(f"ENCRYPTION_KEY env var: {'Set' if os.environ.get('ENCRYPTION_KEY') else 'Not set'}")

if is_encryption_available():
    try:
        manager = get_encryption_manager()
        print("Encryption manager created successfully")
        
        # Test encryption
        test_key = "sk-test123456789"
        encrypted, hint = manager.encrypt_api_key(test_key, "test_provider")
        print(f"Encryption test successful")
        print(f"Encrypted length: {len(encrypted)}")
        print(f"Hint: {hint}")
        
        # Test decryption
        decrypted = manager.decrypt_api_key(encrypted, "test_provider")
        print(f"Decryption test successful: {decrypted == test_key}")
    except Exception as e:
        print(f"Error: {str(e)}")
else:
    print("Encryption is not available")