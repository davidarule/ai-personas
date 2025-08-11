# Security Design Document

## Application Security Design

### Authentication Flow
```python
# Secure authentication implementation
from fastapi import HTTPException, Depends
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta

class AuthenticationService:
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.SECRET_KEY = os.environ.get("SECRET_KEY")
        self.ALGORITHM = "HS256"
        self.ACCESS_TOKEN_EXPIRE = timedelta(minutes=15)
        self.REFRESH_TOKEN_EXPIRE = timedelta(days=7)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        return self.pwd_context.hash(password)
    
    def create_access_token(self, data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + self.ACCESS_TOKEN_EXPIRE
        to_encode.update({"exp": expire, "type": "access"})
        return jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
```

### Input Validation Framework
```python
# Comprehensive input validation
from pydantic import BaseModel, validator, constr, EmailStr
from typing import Optional
import re

class SecureUserInput(BaseModel):
    username: constr(min_length=3, max_length=50, regex="^[a-zA-Z0-9_-]+$")
    email: EmailStr
    password: constr(min_length=12, max_length=128)
    
    @validator('password')
    def validate_password_strength(cls, v):
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain lowercase letter')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain digit')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain special character')
        return v
    
    @validator('username')
    def validate_username_blacklist(cls, v):
        blacklist = ['admin', 'root', 'administrator', 'system']
        if v.lower() in blacklist:
            raise ValueError('Username not allowed')
        return v
```

### Security Headers Implementation
```python
# Security headers middleware
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self'; "
            "connect-src 'self' wss: https:;"
        )
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        return response
```

### Secure Session Management
```typescript
// Frontend secure session handling
import { createContext, useContext, useEffect, useState } from 'react';
import axios from 'axios';

interface SecureSession {
    accessToken: string | null;
    refreshToken: string | null;
    expiresAt: number | null;
}

class SessionManager {
    private static instance: SessionManager;
    private refreshPromise: Promise<string> | null = null;
    
    static getInstance(): SessionManager {
        if (!SessionManager.instance) {
            SessionManager.instance = new SessionManager();
        }
        return SessionManager.instance;
    }
    
    async getValidToken(): Promise<string> {
        const session = this.getSession();
        
        if (!session.accessToken || !session.expiresAt) {
            throw new Error('No valid session');
        }
        
        // Check if token is expired or about to expire (5 min buffer)
        if (Date.now() >= session.expiresAt - 300000) {
            return this.refreshAccessToken();
        }
        
        return session.accessToken;
    }
    
    private async refreshAccessToken(): Promise<string> {
        // Prevent multiple simultaneous refresh attempts
        if (this.refreshPromise) {
            return this.refreshPromise;
        }
        
        this.refreshPromise = this.doRefresh();
        const newToken = await this.refreshPromise;
        this.refreshPromise = null;
        
        return newToken;
    }
    
    private getSession(): SecureSession {
        // Use secure storage mechanism
        const encrypted = sessionStorage.getItem('secure_session');
        if (!encrypted) {
            return { accessToken: null, refreshToken: null, expiresAt: null };
        }
        
        // Decrypt session data
        return this.decrypt(encrypted);
    }
}
```

### API Security Implementation
```python
# Rate limiting and API security
from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from collections import defaultdict
import time

class RateLimiter:
    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.requests = defaultdict(list)
    
    async def check_rate_limit(self, request: Request):
        client_ip = request.client.host
        now = time.time()
        minute_ago = now - 60
        
        # Clean old requests
        self.requests[client_ip] = [
            req_time for req_time in self.requests[client_ip] 
            if req_time > minute_ago
        ]
        
        # Check rate limit
        if len(self.requests[client_ip]) >= self.requests_per_minute:
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded"
            )
        
        # Record new request
        self.requests[client_ip].append(now)

class APIKeyValidator:
    def __init__(self):
        self.security = HTTPBearer()
    
    async def validate_api_key(
        self, 
        credentials: HTTPAuthorizationCredentials = Depends(security)
    ):
        api_key = credentials.credentials
        
        # Validate API key format
        if not self._is_valid_format(api_key):
            raise HTTPException(
                status_code=401,
                detail="Invalid API key format"
            )
        
        # Check key in database
        key_data = await self._get_api_key_data(api_key)
        if not key_data:
            raise HTTPException(
                status_code=401,
                detail="Invalid API key"
            )
        
        # Check key permissions
        if not key_data.is_active:
            raise HTTPException(
                status_code=403,
                detail="API key is inactive"
            )
        
        return key_data
```

### Encryption Service
```python
# Data encryption service
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os

class EncryptionService:
    def __init__(self):
        self.master_key = self._derive_key_from_password()
        self.fernet = Fernet(self.master_key)
    
    def _derive_key_from_password(self) -> bytes:
        password = os.environ.get("ENCRYPTION_PASSWORD").encode()
        salt = os.environ.get("ENCRYPTION_SALT").encode()
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        
        key = base64.urlsafe_b64encode(kdf.derive(password))
        return key
    
    def encrypt_sensitive_data(self, data: str) -> str:
        '''Encrypt sensitive data like PII'''
        return self.fernet.encrypt(data.encode()).decode()
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        '''Decrypt sensitive data'''
        return self.fernet.decrypt(encrypted_data.encode()).decode()
    
    def hash_data(self, data: str) -> str:
        '''One-way hash for data like email addresses'''
        import hashlib
        return hashlib.sha256(data.encode()).hexdigest()
```

## Security Testing Integration

### SAST Pipeline
```yaml
# GitLab CI/CD security scanning
security_scan:
  stage: test
  script:
    - semgrep --config=auto .
    - bandit -r src/
    - safety check
    - npm audit
    - trivy fs .
  artifacts:
    reports:
      sast: gl-sast-report.json
```

### DAST Configuration
```yaml
# OWASP ZAP configuration
zap_scan:
  stage: security
  image: owasp/zap2docker-stable
  script:
    - zap-baseline.py -t $TARGET_URL -r zap_report.html
    - zap-api-scan.py -t $API_SPEC_URL -f openapi -r api_report.html
  artifacts:
    paths:
      - zap_report.html
      - api_report.html
```

## Security Monitoring

### Log Aggregation
```python
# Structured security logging
import structlog
from datetime import datetime

logger = structlog.get_logger()

class SecurityLogger:
    @staticmethod
    def log_authentication_attempt(
        username: str, 
        success: bool, 
        ip_address: str,
        user_agent: str
    ):
        logger.info(
            "authentication_attempt",
            username=username,
            success=success,
            ip_address=ip_address,
            user_agent=user_agent,
            timestamp=datetime.utcnow().isoformat()
        )
    
    @staticmethod
    def log_authorization_failure(
        user_id: str,
        resource: str,
        action: str,
        reason: str
    ):
        logger.warning(
            "authorization_failure",
            user_id=user_id,
            resource=resource,
            action=action,
            reason=reason,
            timestamp=datetime.utcnow().isoformat()
        )
    
    @staticmethod
    def log_security_event(
        event_type: str,
        severity: str,
        details: dict
    ):
        logger.info(
            "security_event",
            event_type=event_type,
            severity=severity,
            details=details,
            timestamp=datetime.utcnow().isoformat()
        )
```

This comprehensive security design ensures defense-in-depth protection for the Trivia By Grok application.
