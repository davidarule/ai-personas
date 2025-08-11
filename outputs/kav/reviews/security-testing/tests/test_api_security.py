import pytest
import requests
import time
from typing import Dict, Any

class TestAPISecuritye:
    """Comprehensive API security test suite"""
    
    @pytest.fixture
    def auth_headers(self, base_url):
        """Get authenticated headers"""
        response = requests.post(
            f"{base_url}/api/auth/login",
            json={"email": "test@example.com", "password": "TestPassword123!"}
        )
        token = response.json().get("access_token")
        return {"Authorization": f"Bearer {token}"}
    
    def test_sql_injection_protection(self, base_url):
        """Test SQL injection protection"""
        sql_payloads = [
            "' OR '1'='1",
            "1' OR '1' = '1",
            "'; DROP TABLE users; --"
        ]
        
        for payload in sql_payloads:
            response = requests.post(
                f"{base_url}/api/auth/login",
                json={"email": payload, "password": "test"}
            )
            
            assert response.status_code in [400, 401]
            assert "error" in response.json()
            # Ensure no SQL error messages leak
            assert "sql" not in response.text.lower()
            assert "syntax" not in response.text.lower()
    
    def test_xss_protection(self, base_url, auth_headers):
        """Test XSS protection"""
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "javascript:alert('XSS')"
        ]
        
        for payload in xss_payloads:
            response = requests.put(
                f"{base_url}/api/user/profile",
                headers=auth_headers,
                json={"bio": payload}
            )
            
            # Get profile to check if payload is escaped
            profile = requests.get(
                f"{base_url}/api/user/profile",
                headers=auth_headers
            )
            
            profile_data = profile.json()
            # Ensure payload is escaped
            assert payload not in profile_data.get("bio", "")
            assert "&lt;script&gt;" in profile_data.get("bio", "") or profile_data.get("bio", "") != payload
    
    def test_authentication_security(self, base_url):
        """Test authentication security features"""
        # Test password complexity
        weak_passwords = ["123456", "password", "qwerty123"]
        
        for pwd in weak_passwords:
            response = requests.post(
                f"{base_url}/api/auth/register",
                json={
                    "email": f"test{time.time()}@example.com",
                    "password": pwd,
                    "username": f"test{int(time.time())}"
                }
            )
            
            assert response.status_code == 400
            assert "password" in response.json().get("error", "").lower()
    
    def test_rate_limiting(self, base_url):
        """Test rate limiting is enforced"""
        endpoint = f"{base_url}/api/auth/login"
        
        # Make rapid requests
        responses = []
        for _ in range(150):
            response = requests.post(
                endpoint,
                json={"email": "test@test.com", "password": "wrong"}
            )
            responses.append(response.status_code)
            
            if response.status_code == 429:
                break
        
        # Ensure rate limiting kicked in
        assert 429 in responses, "Rate limiting not enforced"
    
    def test_authorization_idor(self, base_url):
        """Test for IDOR vulnerabilities"""
        # Create two users and test cross-access
        user1 = self._create_test_user(base_url, "user1")
        user2 = self._create_test_user(base_url, "user2")
        
        # Try to access user2's data with user1's token
        response = requests.get(
            f"{base_url}/api/users/{user2['id']}/private",
            headers={"Authorization": f"Bearer {user1['token']}"}
        )
        
        assert response.status_code in [403, 404]
    
    def test_jwt_security(self, base_url, auth_headers):
        """Test JWT implementation security"""
        # Get a valid token
        token = auth_headers["Authorization"].split(" ")[1]
        
        # Test with modified token
        modified_token = token[:-10] + "tampered123"
        
        response = requests.get(
            f"{base_url}/api/user/profile",
            headers={"Authorization": f"Bearer {modified_token}"}
        )
        
        assert response.status_code == 401
    
    def test_security_headers(self, base_url):
        """Test security headers are present"""
        response = requests.get(f"{base_url}/api/health")
        
        required_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": ["DENY", "SAMEORIGIN"],
            "Strict-Transport-Security": "max-age=",
            "X-XSS-Protection": "1"
        }
        
        for header, expected in required_headers.items():
            assert header in response.headers
            
            if isinstance(expected, list):
                assert any(exp in response.headers[header] for exp in expected)
            else:
                assert expected in response.headers[header]
    
    def test_cors_configuration(self, base_url):
        """Test CORS is properly configured"""
        # Test with evil origin
        response = requests.get(
            f"{base_url}/api/health",
            headers={"Origin": "https://evil.com"}
        )
        
        acao = response.headers.get("Access-Control-Allow-Origin")
        
        # Should not allow all origins
        assert acao != "*"
        assert acao != "https://evil.com"
    
    def _create_test_user(self, base_url: str, username: str) -> Dict[str, Any]:
        """Helper to create a test user"""
        user_data = {
            "email": f"{username}_{time.time()}@example.com",
            "password": "TestPassword123!",
            "username": f"{username}_{int(time.time())}"
        }
        
        # Register
        requests.post(f"{base_url}/api/auth/register", json=user_data)
        
        # Login
        response = requests.post(
            f"{base_url}/api/auth/login",
            json={"email": user_data["email"], "password": user_data["password"]}
        )
        
        data = response.json()
        return {
            "id": data.get("user_id"),
            "token": data.get("access_token"),
            "email": user_data["email"]
        }
