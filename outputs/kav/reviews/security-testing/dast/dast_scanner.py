#!/usr/bin/env python3
"""
Custom DAST Scanner for Trivia Application
Focuses on API endpoints and modern web app vulnerabilities
"""

import asyncio
import aiohttp
import json
import time
from typing import List, Dict, Any
import ssl
import certifi

class TriviaAppDASTScanner:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.findings = []
        self.session = None
        self.auth_token = None
        
    async def setup(self):
        """Setup async session"""
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        self.session = aiohttp.ClientSession(connector=connector)
        
    async def cleanup(self):
        """Cleanup session"""
        if self.session:
            await self.session.close()
            
    async def authenticate(self):
        """Authenticate and get token"""
        try:
            async with self.session.post(
                f"{self.base_url}/api/auth/login",
                json={"email": "test@example.com", "password": "TestPassword123!"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    self.auth_token = data.get("access_token")
                    return True
        except:
            pass
        return False
        
    async def scan_cors(self):
        """Test CORS configuration"""
        print("[*] Testing CORS configuration...")
        
        origins = [
            "https://evil.com",
            "null",
            "file://",
            "https://localhost"
        ]
        
        for origin in origins:
            headers = {"Origin": origin}
            
            try:
                async with self.session.get(
                    f"{self.base_url}/api/health",
                    headers=headers
                ) as response:
                    acao = response.headers.get("Access-Control-Allow-Origin")
                    acac = response.headers.get("Access-Control-Allow-Credentials")
                    
                    if acao == origin or acao == "*":
                        self.findings.append({
                            "type": "CORS Misconfiguration",
                            "severity": "Medium",
                            "endpoint": "/api/health",
                            "details": f"Accepts origin: {origin}",
                            "credentials": acac == "true"
                        })
            except:
                pass
                
    async def scan_rate_limiting(self):
        """Test rate limiting"""
        print("[*] Testing rate limiting...")
        
        endpoint = f"{self.base_url}/api/auth/login"
        start_time = time.time()
        request_count = 0
        
        for i in range(200):
            try:
                async with self.session.post(
                    endpoint,
                    json={"email": "test@test.com", "password": "wrong"},
                    timeout=aiohttp.ClientTimeout(total=2)
                ) as response:
                    request_count += 1
                    
                    if response.status == 429:
                        print(f"[+] Rate limiting detected after {request_count} requests")
                        return
            except:
                pass
                
        elapsed = time.time() - start_time
        
        if request_count >= 150:
            self.findings.append({
                "type": "Missing Rate Limiting",
                "severity": "Medium",
                "endpoint": endpoint,
                "details": f"Sent {request_count} requests in {elapsed:.2f}s without rate limiting"
            })
            
    async def scan_api_versioning(self):
        """Test API versioning vulnerabilities"""
        print("[*] Testing API versioning...")
        
        versions = ["v1", "v2", "v0", "beta", "internal", "admin"]
        endpoints = ["/users", "/admin", "/debug", "/config"]
        
        for version in versions:
            for endpoint in endpoints:
                url = f"{self.base_url}/api/{version}{endpoint}"
                
                try:
                    async with self.session.get(url) as response:
                        if response.status in [200, 401, 403]:
                            self.findings.append({
                                "type": "Hidden API Version",
                                "severity": "Low",
                                "endpoint": f"/api/{version}{endpoint}",
                                "status": response.status
                            })
                except:
                    pass
                    
    async def scan_graphql(self):
        """Test for GraphQL endpoints"""
        print("[*] Testing for GraphQL endpoints...")
        
        graphql_endpoints = [
            "/graphql",
            "/api/graphql",
            "/v1/graphql",
            "/query",
            "/api/query"
        ]
        
        introspection_query = {
            "query": "{__schema{queryType{name}}}"
        }
        
        for endpoint in graphql_endpoints:
            try:
                async with self.session.post(
                    f"{self.base_url}{endpoint}",
                    json=introspection_query
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        if "__schema" in str(data):
                            self.findings.append({
                                "type": "GraphQL Introspection Enabled",
                                "severity": "Medium",
                                "endpoint": endpoint,
                                "details": "GraphQL introspection is enabled"
                            })
            except:
                pass
                
    async def scan_websocket(self):
        """Test WebSocket security"""
        print("[*] Testing WebSocket endpoints...")
        
        ws_endpoints = [
            "/ws",
            "/socket.io",
            "/websocket",
            "/api/ws",
            "/notifications"
        ]
        
        for endpoint in ws_endpoints:
            try:
                ws_url = f"ws{'s' if 'https' in self.base_url else ''}://{self.base_url.replace('http://', '').replace('https://', '')}{endpoint}"
                
                async with self.session.ws_connect(
                    ws_url,
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as ws:
                    # Try to send unauthorized message
                    await ws.send_str('{"type": "admin_command", "action": "get_all_users"}')
                    
                    msg = await ws.receive(timeout=2)
                    if msg.type == aiohttp.WSMsgType.TEXT:
                        self.findings.append({
                            "type": "WebSocket Security",
                            "severity": "Medium",
                            "endpoint": endpoint,
                            "details": "WebSocket accepts unauthorized messages"
                        })
                    await ws.close()
            except:
                pass
                
    async def scan_cache_poisoning(self):
        """Test for cache poisoning vulnerabilities"""
        print("[*] Testing cache poisoning...")
        
        headers_to_test = [
            ("X-Forwarded-Host", "evil.com"),
            ("X-Forwarded-Port", "1337"),
            ("X-Forwarded-Prefix", "/admin"),
            ("X-Original-URL", "/admin"),
            ("X-Rewrite-URL", "/admin")
        ]
        
        for header, value in headers_to_test:
            try:
                # First request with poisoned header
                async with self.session.get(
                    f"{self.base_url}/api/public/info",
                    headers={header: value}
                ) as response1:
                    body1 = await response1.text()
                    
                # Second request without header
                async with self.session.get(
                    f"{self.base_url}/api/public/info"
                ) as response2:
                    body2 = await response2.text()
                    
                if value in body2:
                    self.findings.append({
                        "type": "Cache Poisoning",
                        "severity": "High",
                        "endpoint": "/api/public/info",
                        "header": header,
                        "details": f"Cache poisoned with {header}: {value}"
                    })
            except:
                pass
                
    async def scan_jwt_vulnerabilities(self):
        """Test JWT implementation"""
        print("[*] Testing JWT vulnerabilities...")
        
        if not self.auth_token:
            await self.authenticate()
            
        if self.auth_token:
            # Test none algorithm
            parts = self.auth_token.split('.')
            if len(parts) == 3:
                # Modify to use none algorithm
                header = json.loads(base64.urlsafe_b64decode(parts[0] + '=='))
                header['alg'] = 'none'
                new_header = base64.urlsafe_b64encode(json.dumps(header).encode()).decode().rstrip('=')
                none_token = f"{new_header}.{parts[1]}."
                
                try:
                    async with self.session.get(
                        f"{self.base_url}/api/user/profile",
                        headers={"Authorization": f"Bearer {none_token}"}
                    ) as response:
                        if response.status == 200:
                            self.findings.append({
                                "type": "JWT None Algorithm",
                                "severity": "Critical",
                                "endpoint": "/api/user/profile",
                                "details": "JWT accepts 'none' algorithm"
                            })
                except:
                    pass
                    
    async def generate_report(self):
        """Generate DAST report"""
        report = {
            "scan_date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "target": self.base_url,
            "total_findings": len(self.findings),
            "severity_breakdown": {
                "Critical": len([f for f in self.findings if f['severity'] == 'Critical']),
                "High": len([f for f in self.findings if f['severity'] == 'High']),
                "Medium": len([f for f in self.findings if f['severity'] == 'Medium']),
                "Low": len([f for f in self.findings if f['severity'] == 'Low'])
            },
            "findings": self.findings
        }
        
        with open("dast_report.json", "w") as f:
            json.dump(report, f, indent=2)
            
        print(f"\n[+] DAST scan completed. Found {len(self.findings)} issues.")
        return report
        
    async def run_scan(self):
        """Run all DAST tests"""
        await self.setup()
        
        scan_tasks = [
            self.scan_cors(),
            self.scan_rate_limiting(),
            self.scan_api_versioning(),
            self.scan_graphql(),
            self.scan_websocket(),
            self.scan_cache_poisoning(),
            self.scan_jwt_vulnerabilities()
        ]
        
        await asyncio.gather(*scan_tasks)
        await self.generate_report()
        await self.cleanup()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python dast_scanner.py <base_url>")
        sys.exit(1)
        
    scanner = TriviaAppDASTScanner(sys.argv[1])
    asyncio.run(scanner.run_scan())
