#!/usr/bin/env python3
"""
Generate a new encryption key for the AI Personas application
This key should be stored securely as the ENCRYPTION_KEY environment variable
"""

import sys
import os
import base64

# Add the src directory to the path to import encryption_utils
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

from utils.encryption_utils import generate_encryption_key, EncryptionManager


def main():
    """Generate and display a new encryption key with instructions"""
    
    print("AI Personas Encryption Key Generator")
    print("=" * 40)
    print()
    
    # Generate a new key
    new_key = generate_encryption_key()
    
    print("Generated Encryption Key:")
    print(new_key)
    print()
    print("Key Length:", len(new_key), "characters")
    print()
    
    # Test the key
    try:
        manager = EncryptionManager(master_key=new_key)
        test_string = "test_api_key_12345"
        encrypted = manager.encrypt(test_string)
        decrypted = manager.decrypt(encrypted)
        
        if decrypted == test_string:
            print("✓ Key validation successful - encryption/decryption working correctly")
        else:
            print("✗ Key validation failed - encryption/decryption not working")
            sys.exit(1)
            
    except Exception as e:
        print(f"✗ Key validation failed: {str(e)}")
        sys.exit(1)
    
    print()
    print("IMPORTANT: Store this key securely!")
    print("=" * 40)
    print()
    print("To use this key, set it as an environment variable:")
    print()
    print("  Linux/Mac:")
    print(f'    export ENCRYPTION_KEY="{new_key}"')
    print()
    print("  Windows:")
    print(f'    set ENCRYPTION_KEY={new_key}')
    print()
    print("  Or add to your .env file:")
    print(f'    ENCRYPTION_KEY={new_key}')
    print()
    print("SECURITY NOTES:")
    print("- Never commit this key to version control")
    print("- Store it in a secure secrets management system")
    print("- Rotate keys periodically for better security")
    print("- Keep a secure backup of this key - losing it means losing access to encrypted data")
    print()


if __name__ == "__main__":
    main()