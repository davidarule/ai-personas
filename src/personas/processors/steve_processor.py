"""
Steve Processor - Security Architect Persona

Actually generates security architecture documents, threat models, and security policies
with Git integration for proper PR workflow
"""

import asyncio
import logging
import os
from typing import Dict, Any, List
from datetime import datetime
from pathlib import Path

from .azure_devops_enabled_processor import AzureDevOpsEnabledProcessor

logger = logging.getLogger(__name__)


class SteveProcessor(AzureDevOpsEnabledProcessor):
    """
    Security Architect processor for Steve
    
    Generates:
    - Security architecture documents
    - Threat models
    - Security policies
    - Risk assessments
    - Compliance mappings
    """
    
    def __init__(self, output_dir: str = "/tmp/ai_factory_outputs"):
        super().__init__(output_dir)
        self.persona_id = "steve"
        self.persona_name = "SteveBot"
        
    async def process_work_item(self, work_item: Any) -> Dict[str, Any]:
        """Process a work item and generate actual security documents with PR workflow"""
        logger.info(f"Steve processing work item #{work_item.id}: {work_item.title}")
        
        outputs = []
        pr_info = None
        
        # Determine what to generate based on work item
        if "system architecture" in work_item.title.lower():
            output = await self._generate_system_architecture()
            outputs.append(output)
        elif "threat model" in work_item.title.lower():
            output = await self._generate_threat_model()
            outputs.append(output)
        elif "security architecture" in work_item.title.lower():
            output = await self._generate_security_architecture()
            outputs.append(output)
        elif "security policy" in work_item.title.lower():
            output = await self._generate_security_policy()
            outputs.append(output)
        elif "risk assessment" in work_item.title.lower():
            output = await self._generate_risk_assessment()
            outputs.append(output)
        else:
            # Generate general security design
            output = await self._generate_security_design()
            outputs.append(output)
        
        # Create Pull Request workflow using Azure DevOps
        repo_config = await self._get_repo_config()
        if repo_config:
            pr_info = await self._create_azure_devops_pr_with_files(work_item, outputs, repo_config)
            
            # If PR was created successfully, assign reviewers and create review tasks
            if pr_info and pr_info.get('status') == 'success':
                await self._assign_reviewers_and_create_tasks(work_item, outputs, pr_info)
            
        return {
            'status': 'completed',
            'outputs': outputs,
            'message': f"Generated {len(outputs)} security documents",
            'pull_request': pr_info,
            'next_steps': self._get_next_steps(outputs, pr_info)
        }
        
    async def _generate_threat_model(self) -> Dict[str, str]:
        """Generate a threat model document"""
        threat_model = """# Trivia By Grok - Threat Model

## Executive Summary
This document provides a comprehensive threat model for the Trivia By Grok application using the STRIDE methodology.

## System Architecture Overview
```
┌─────────────┐     HTTPS/WSS    ┌─────────────┐     TLS      ┌─────────────┐
│   Frontend  │ ◄──────────────► │   Backend   │ ◄───────────► │  Database   │
│  React App  │                  │  FastAPI    │                │ PostgreSQL  │
└─────────────┘                  └─────────────┘                └─────────────┘
      │                                 │                              │
      │                                 │                              │
      ▼                                 ▼                              ▼
┌─────────────┐                  ┌─────────────┐                ┌─────────────┐
│   Browser   │                  │   Auth      │                │   Backup    │
│   Storage   │                  │   Service   │                │   Storage   │
└─────────────┘                  └─────────────┘                └─────────────┘
```

## STRIDE Analysis

### 1. Spoofing
**Threat**: Attackers impersonating legitimate users
- **Risk Level**: High
- **Attack Vectors**:
  - Stolen JWT tokens
  - Session hijacking
  - Credential stuffing
- **Mitigations**:
  - Implement MFA
  - Short token lifetimes (15 min access, 7 day refresh)
  - Device fingerprinting
  - IP allowlisting for admin accounts

### 2. Tampering
**Threat**: Modification of data in transit or at rest
- **Risk Level**: Medium
- **Attack Vectors**:
  - Man-in-the-middle attacks
  - Database compromise
  - API parameter manipulation
- **Mitigations**:
  - TLS 1.3 for all communications
  - Input validation and sanitization
  - Database encryption at rest
  - Integrity checks for critical data

### 3. Repudiation
**Threat**: Users denying actions they performed
- **Risk Level**: Low
- **Attack Vectors**:
  - Insufficient logging
  - Log tampering
- **Mitigations**:
  - Comprehensive audit logging
  - Immutable log storage
  - Digital signatures for critical actions

### 4. Information Disclosure
**Threat**: Unauthorized access to sensitive data
- **Risk Level**: High
- **Attack Vectors**:
  - SQL injection
  - Insecure direct object references
  - Error message information leakage
- **Mitigations**:
  - Parameterized queries
  - Proper access controls
  - Generic error messages
  - Data classification and encryption

### 5. Denial of Service
**Threat**: Making the service unavailable
- **Risk Level**: Medium
- **Attack Vectors**:
  - DDoS attacks
  - Resource exhaustion
  - Algorithmic complexity attacks
- **Mitigations**:
  - Rate limiting
  - CDN with DDoS protection
  - Resource quotas
  - Circuit breakers

### 6. Elevation of Privilege
**Threat**: Gaining unauthorized elevated access
- **Risk Level**: High
- **Attack Vectors**:
  - Privilege escalation bugs
  - Insecure admin interfaces
  - Default credentials
- **Mitigations**:
  - Principle of least privilege
  - Role-based access control
  - Regular security audits
  - No default credentials

## Attack Trees

### User Account Compromise
```
Goal: Compromise User Account
├── Steal Credentials
│   ├── Phishing Attack
│   ├── Keylogger
│   └── Database Breach
├── Session Hijacking
│   ├── XSS Attack
│   ├── Session Fixation
│   └── Token Theft
└── Account Recovery Abuse
    ├── Email Account Compromise
    └── Social Engineering
```

## Security Controls Implementation

### Authentication & Authorization
- OAuth 2.0 + JWT implementation
- RBAC with granular permissions
- MFA via TOTP
- Account lockout policies

### Data Protection
- AES-256 encryption at rest
- TLS 1.3 in transit
- PII tokenization
- Secure key management (HashiCorp Vault)

### Application Security
- OWASP Top 10 mitigations
- Security headers (CSP, HSTS, etc.)
- Input validation framework
- Output encoding

### Infrastructure Security
- Network segmentation
- WAF implementation
- Container security scanning
- Infrastructure as Code security

## Risk Matrix

| Risk | Likelihood | Impact | Mitigation Priority |
|------|------------|--------|-------------------|
| Account Takeover | High | High | Critical |
| Data Breach | Medium | High | Critical |
| DDoS Attack | Medium | Medium | High |
| Insider Threat | Low | High | Medium |
| Supply Chain | Low | Medium | Low |

## Compliance Mapping
- NIST CSF: Covers all 5 functions
- ISO 27001: Addresses 12 of 14 domains
- OWASP ASVS: Level 2 compliance
- PCI DSS: Not applicable (no payment processing)

## Review Schedule
- Quarterly threat model reviews
- Annual penetration testing
- Continuous vulnerability scanning
- Monthly security metrics review
"""

        # Save to file
        import os
        os.makedirs(f"{self.output_directory}/security/threat_models", exist_ok=True)
        
        with open(f"{self.output_directory}/security/threat_models/trivia_threat_model.md", 'w') as f:
            f.write(threat_model)
            
        return {
            'type': 'Threat Model',
            'name': 'trivia_threat_model.md',
            'path': f"{self.output_directory}/security/threat_models/trivia_threat_model.md",
            'content': threat_model,
            'preview': threat_model[:300] + '...',
            'files_created': ['trivia_threat_model.md']
        }
        

    async def _generate_system_architecture(self) -> Dict[str, Any]:
        """Generate comprehensive system architecture document"""
        architecture = """# System Architecture Document - Trivia By Grok

## 1. System Architecture Overview

### Core System Design
- **Architecture Pattern**: Model-View-ViewModel (MVVM) with Repository Pattern
- **Target Platforms**: Android (API 29+) and iOS (14.0+)
- **Backend**: Node.js middleware with PostgreSQL database
- **AI Integration**: Grok AI (grok-3-mini) for question generation

### High-Level Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                    Client Applications                      │
├─────────────────────────────────────────────────────────────┤
│      Android App (Kotlin)    │    iOS App (Swift)         │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │          UI Layer (MVVM)                               │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │ │
│  │  │     UI      │  │ ViewModels  │  │ Navigation  │    │ │
│  │  └─────────────┘  └─────────────┘  └─────────────┘    │ │
│  │          Repository Layer                              │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │ │
│  │  │  Network    │  │   Storage   │  │   Cache     │    │ │
│  │  │  Services   │  │  Services   │  │   Layer     │    │ │
│  │  └─────────────┘  └─────────────┘  └─────────────┘    │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────┬───────────────────────────────────┘
                          │ HTTPS/TLS 1.3
┌─────────────────────────┼───────────────────────────────────┐
│                 Middleware Server                          │
├─────────────────────────────────────────────────────────────┤
│              Node.js + Express.js                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │    API      │  │ Rate Limit  │  │    Auth     │        │
│  │  Gateway    │  │ & Throttle  │  │  Service    │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
│  ┌─────────────────────────────────────────────────────┐   │
│  │               Core Services                         │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────────┐      │   │
│  │  │Question  │  │  Image   │  │Verification  │      │   │
│  │  │Generator │  │ Search   │  │  Service     │      │   │
│  │  └──────────┘  └──────────┘  └──────────────┘      │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │ PostgreSQL  │  │   Grok AI   │  │   Pexels    │        │
│  │  Database   │  │  (xAI API)  │  │     API     │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

## 2. Component Architecture

### Service Boundaries & Interfaces

#### Client Components
- **UI Layer**: Platform-specific presentation (Compose/SwiftUI)
- **ViewModel Layer**: Business logic and state management
- **Repository Layer**: Data access abstraction
- **Network Layer**: API communication (Retrofit/URLSession)
- **Storage Layer**: Local persistence (Room/CoreData)

#### Server Components
- **API Gateway**: Request routing and validation
- **Authentication Service**: Bearer token validation
- **Rate Limiting Service**: Traffic throttling
- **Question Generation Service**: AI integration
- **Image Search Service**: Pexels API integration
- **Verification Service**: Fact checking (optional)
- **Feedback Service**: User feedback management

### Interface Contracts
```typescript
// Question Generation Interface
interface QuestionGenerationService {
  generateQuestions(topic: string, count: number, difficulty: string): Promise<Question[]>
  validateQuestions(questions: Question[]): ValidationResult
}

// Storage Interface
interface StorageService {
  saveQuizHistory(quiz: QuizResult): Promise<void>
  getQuizHistory(): Promise<QuizHistoryItem[]>
  clearHistory(): Promise<void>
}

// Network Interface
interface NetworkService {
  post<T>(endpoint: string, data: any): Promise<T>
  get<T>(endpoint: string): Promise<T>
  handleRetry(request: NetworkRequest): Promise<any>
}
```

## 3. Data Architecture

### Data Models
```typescript
// Core Data Models
interface Question {
  question: string
  options: string[]
  correctAnswer: string
  explanation: string
  imageUrl?: string
  isVisual: boolean
}

interface QuizConfiguration {
  topic: string
  numberOfQuestions: number
  difficulty: 'Novice' | 'Apprentice' | 'Journeyman' | 'Expert' | 'Master'
}

interface QuizResult {
  quizId: string
  configuration: QuizConfiguration
  questions: Question[]
  userAnswers: string[]
  score: number
  percentage: number
  completedAt: Date
}
```

### Storage Architecture
- **Client Storage**: Local-first with platform storage
  - Android: SharedPreferences + Room Database
  - iOS: UserDefaults + CoreData
- **Server Storage**: PostgreSQL for feedback and analytics
- **Caching Strategy**: Multi-level caching (memory, disk, network)

### Data Flow Patterns
```
User Input → Validation → API Request → AI Processing → Response Validation → Local Storage
     ↓              ↓            ↓              ↓                ↓              ↓
  UI State    Business Logic  Network Layer   AI Service      Data Layer   Persistence
```

## 4. API Architecture

### RESTful Design
```yaml
Base URL: https://triviaapp-api.brumbiesoft.org/api/v1

Endpoints:
  GET /health:
    description: Health check
    auth: none
    response: { status, version, timestamp }
  
  POST /questions/generate:
    description: Generate trivia questions
    auth: Bearer token
    request: { topic, count, difficulty }
    response: { questions: Question[] }
    timeout: 450s
  
  POST /images/search:
    description: Search for images
    auth: Bearer token
    request: { query, per_page }
    response: { photos: Photo[] }
  
  POST /feedback:
    description: Submit feedback
    auth: Bearer token
    request: { questionData, feedbackType, description }
    response: { feedbackId }
```

### API Security
- **Authentication**: Bearer token (64-char hex)
- **Rate Limiting**: 100 requests/minute per IP
- **Input Validation**: Server-side validation
- **CORS**: Restricted origins
- **HTTPS**: TLS 1.3 encryption

## 5. Integration Architecture

### Service Communication Patterns
- **Synchronous**: HTTP REST for real-time operations
- **Asynchronous**: Event-driven for background tasks (future)
- **Circuit Breaker**: Fault tolerance for external services
- **Retry Logic**: Exponential backoff for failures

### External Service Integration
```typescript
// Grok AI Integration
interface GrokAIConfig {
  baseURL: 'https://api.x.ai/v1'
  model: 'grok-3-mini'
  temperature: 0.7
  maxTokens: 4000
  timeout: 450000
}

// Pexels Integration
interface PexelsConfig {
  baseURL: 'https://api.pexels.com/v1'
  rateLimit: 200 // per hour
  imageSize: 'medium'
  timeout: 30000
}
```

## 6. Infrastructure Architecture

### Cloud & Deployment
```yaml
Production Environment:
  Server: Ubuntu 22.04 LTS
  Runtime: Node.js 18+
  Process Manager: PM2 (cluster mode, 2 instances)
  Reverse Proxy: Nginx
  SSL/TLS: Let's Encrypt certificates
  Database: PostgreSQL 13+
  Monitoring: PM2 + custom health checks

Deployment Strategy:
  Method: Git-based deployment
  Process: Zero-downtime with PM2 graceful reload
  Database: Automated migrations
  Backup: Daily PostgreSQL dumps
  Logs: PM2 log rotation
```

### DevOps Pipeline
```
Developer → Git Repository → CI/CD Pipeline → Production
    ↓            ↓                ↓               ↓
  Local       Version         Automated       Zero-
  Testing     Control         Testing         Downtime
                              & Build         Deployment
```

## 7. Performance Architecture

### Optimization Strategies
- **Client Optimization**:
  - Local caching of questions and history
  - Lazy loading of images
  - Background prefetching
  - Efficient state management

- **Server Optimization**:
  - Connection pooling
  - Query optimization
  - Response caching
  - Load balancing

### Scaling Strategies
```yaml
Performance Targets:
  API Response: <100ms (health), <60s (generation)
  Concurrent Users: 1000+
  Questions/Hour: 10,000+
  API Requests/Second: 100+

Scaling Approach:
  Horizontal: Load balancer + multiple instances
  Database: Read replicas + connection pooling  
  CDN: Static asset caching
  Cache: Redis for session data (future)
```

## 8. Technology Recommendations

### Frontend Technologies
- **Android**: Kotlin + Jetpack Compose + Material Design 3
- **iOS**: Swift + SwiftUI + iOS Design System
- **Architecture**: MVVM + Repository Pattern
- **DI**: Hilt (Android) / Manual (iOS)
- **Async**: Coroutines (Android) / Combine (iOS)
- **Storage**: Room (Android) / CoreData (iOS)

### Backend Technologies
- **Runtime**: Node.js 18+ with Express.js
- **Database**: PostgreSQL 13+ with JSONB support
- **Process Manager**: PM2 for clustering
- **Reverse Proxy**: Nginx for SSL/load balancing
- **Monitoring**: Custom health checks + PM2 monitoring

### Third-Party Services
- **AI**: Grok AI (xAI) for question generation
- **Images**: Pexels API for visual content
- **SSL**: Let's Encrypt for certificates

## 9. Security Architecture

### Security Layers
```
┌─────────────────────────────────────────────────────────┐
│              Transport Security                         │
│  TLS 1.3, Certificate Pinning, HSTS Headers           │
└─────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────┐
│            Application Security                         │
│  Authentication, Rate Limiting, Input Validation      │
└─────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────┐
│               Data Security                             │
│  Local Storage Only, No PII, Encryption at Rest       │
└─────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────┐
│          Infrastructure Security                        │
│  Firewall, OS Hardening, Access Controls              │
└─────────────────────────────────────────────────────────┘
```

### Security Controls
- **Authentication**: Bearer token API authentication
- **Input Validation**: Server-side validation
- **Transport Security**: HTTPS/TLS 1.3
- **Data Protection**: Local-only storage, no PII collection
- **Rate Limiting**: Request throttling
- **Error Handling**: Secure error messages

## 10. Implementation Roadmap

### Phase 1: Core Architecture (Weeks 1-4)
- [ ] Implement MVVM architecture on both platforms
- [ ] Set up repository pattern and data models
- [ ] Create API service layer
- [ ] Implement local storage

### Phase 2: Service Integration (Weeks 5-8)
- [ ] Integrate Grok AI for question generation
- [ ] Add Pexels image search
- [ ] Implement caching strategy
- [ ] Add error handling and retry logic

### Phase 3: Production Readiness (Weeks 9-12)
- [ ] Deploy server infrastructure
- [ ] Implement monitoring and logging
- [ ] Performance optimization
- [ ] Security hardening

### Phase 4: Scale & Enhance (Weeks 13-16)
- [ ] Add horizontal scaling
- [ ] Implement advanced caching
- [ ] Add analytics and feedback
- [ ] Performance tuning

---

**Architecture Metadata**:
- **Author**: Steve Bot (System Architect)
- **Version**: 1.0
- **Date**: August 4, 2025
- **Classification**: System Architecture Document
- **Review Status**: Ready for Technical Review"""

        # Save to file
        import os
        os.makedirs(f"{self.output_directory}/architecture/system", exist_ok=True)
        
        with open(f"{self.output_directory}/architecture/system/system_architecture.md", 'w') as f:
            f.write(architecture)
            
        return {
            'type': 'System Architecture',
            'name': 'system_architecture.md',
            'path': f"{self.output_directory}/architecture/system/system_architecture.md",
            'content': architecture,
            'preview': architecture[:300] + '...',
            'files_created': ['system_architecture.md']
        }
        
    async def _generate_security_architecture(self) -> Dict[str, str]:
        """Generate security architecture document"""
        architecture = """# Security Architecture Document

## 1. Security Architecture Overview

### Design Principles
1. **Defense in Depth**: Multiple layers of security controls
2. **Zero Trust**: Never trust, always verify
3. **Least Privilege**: Minimal required permissions
4. **Secure by Default**: Security enabled out of the box
5. **Fail Secure**: Secure failure modes

### Security Zones
```
┌─────────────────────────────────────────────────────────────┐
│                        DMZ Zone                              │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    │
│  │    WAF      │───►│  Load       │───►│   Reverse   │    │
│  │            │    │  Balancer   │    │   Proxy     │    │
│  └─────────────┘    └─────────────┘    └─────────────┘    │
└────────────────────────────┬────────────────────────────────┘
                             │
┌────────────────────────────┼────────────────────────────────┐
│                Application Zone                              │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    │
│  │  Frontend   │    │   API       │    │   Auth      │    │
│  │  Servers    │    │  Servers    │    │  Service    │    │
│  └─────────────┘    └─────────────┘    └─────────────┘    │
└────────────────────────────┬────────────────────────────────┘
                             │
┌────────────────────────────┼────────────────────────────────┐
│                    Data Zone                                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    │
│  │  Primary    │    │   Cache     │    │   Backup    │    │
│  │  Database   │    │   Layer     │    │   Storage   │    │
│  └─────────────┘    └─────────────┘    └─────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

## 2. Security Components

### Network Security
- **Firewalls**: Stateful inspection at zone boundaries
- **IDS/IPS**: Network-based intrusion detection
- **VPN**: Site-to-site for admin access
- **Network Segmentation**: VLAN isolation

### Application Security
```yaml
Frontend Security:
  - Content Security Policy (CSP)
  - Subresource Integrity (SRI)
  - XSS Protection
  - CSRF Tokens
  
API Security:
  - OAuth 2.0 / JWT
  - Rate Limiting
  - API Gateway
  - Input Validation
  
Backend Security:
  - Secure Coding Practices
  - Dependency Scanning
  - SAST/DAST Integration
  - Runtime Protection
```

### Data Security
- **Encryption**:
  - At Rest: AES-256-GCM
  - In Transit: TLS 1.3
  - Key Management: HSM-backed
  
- **Access Control**:
  - Row-Level Security
  - Column-Level Encryption
  - Data Masking
  - Audit Logging

## 3. Identity & Access Management

### Authentication Architecture
```
User ──► Frontend ──► Auth Service ──► Identity Provider
                           │
                           ├── Local Auth (PBKDF2)
                           ├── OAuth Providers
                           └── SAML/SSO
```

### Authorization Model
- **RBAC Implementation**:
  - Roles: Admin, Moderator, Player
  - Permissions: Granular action-based
  - Dynamic permission evaluation
  
### Session Management
- JWT with refresh tokens
- Secure session storage
- Session timeout policies
- Concurrent session limits

## 4. Security Monitoring & Logging

### SIEM Integration
```json
{
  "log_sources": [
    "application_logs",
    "access_logs",
    "security_events",
    "authentication_logs",
    "system_logs"
  ],
  "correlation_rules": [
    "failed_login_attempts",
    "privilege_escalation",
    "data_exfiltration",
    "suspicious_api_usage"
  ]
}
```

### Security Metrics
- Authentication success/failure rates
- API abuse detection
- Security incident response times
- Vulnerability remediation SLAs

## 5. Incident Response

### Playbooks
1. **Data Breach Response**
2. **DDoS Mitigation**
3. **Account Compromise**
4. **Malware Detection**

### Recovery Procedures
- Automated backup restoration
- Disaster recovery sites
- Business continuity planning
- Regular DR testing

## 6. Compliance & Governance

### Regulatory Compliance
- GDPR: Privacy by design
- CCPA: Data subject rights
- SOC 2: Security controls
- ISO 27001: ISMS implementation

### Security Policies
1. Information Security Policy
2. Access Control Policy
3. Incident Response Policy
4. Data Classification Policy
5. Acceptable Use Policy

## 7. Security Testing

### Testing Strategy
- **Penetration Testing**: Quarterly
- **Vulnerability Scanning**: Weekly
- **Security Code Review**: Per PR
- **Red Team Exercises**: Annually

## 8. Third-Party Security

### Vendor Assessment
- Security questionnaires
- SOC 2 reports review
- Penetration test results
- Continuous monitoring

### Supply Chain Security
- Dependency scanning
- License compliance
- SBOM generation
- Vulnerability tracking
"""

        # Save to file
        import os
        os.makedirs(f"{self.output_directory}/security/architecture", exist_ok=True)
        
        with open(f"{self.output_directory}/security/architecture/security_architecture.md", 'w') as f:
            f.write(architecture)
            
        return {
            'type': 'Security Architecture',
            'name': 'security_architecture.md',
            'path': f"{self.output_directory}/security/architecture/security_architecture.md",
            'content': architecture,
            'preview': architecture[:300] + '...',
            'files_created': ['security_architecture.md']
        }
        
    async def _generate_security_policy(self) -> Dict[str, str]:
        """Generate security policy document"""
        policy = """# Information Security Policy

## Document Control
- **Version**: 1.0
- **Effective Date**: 2025-01-01
- **Classification**: Internal
- **Owner**: Chief Information Security Officer

## 1. Purpose
This Information Security Policy establishes the security requirements and responsibilities for protecting Trivia By Grok's information assets.

## 2. Scope
This policy applies to all employees, contractors, consultants, and third parties who have access to Trivia By Grok systems and data.

## 3. Policy Statements

### 3.1 Access Control
- **Principle of Least Privilege**: Users shall only be granted the minimum access necessary
- **Segregation of Duties**: Critical functions must be separated across multiple individuals
- **Account Management**: All accounts must be approved, regularly reviewed, and promptly deactivated

### 3.2 Authentication
- **Password Requirements**:
  - Minimum 12 characters
  - Complexity requirements enforced
  - No reuse of last 10 passwords
  - Maximum age: 90 days
  
- **Multi-Factor Authentication**:
  - Required for all administrative access
  - Required for remote access
  - Recommended for all users

### 3.3 Data Protection
- **Classification Levels**:
  - **Confidential**: Requires encryption at rest and in transit
  - **Internal**: Requires access controls
  - **Public**: No special requirements
  
- **Encryption Standards**:
  - AES-256 for data at rest
  - TLS 1.2+ for data in transit
  - Key rotation every 12 months

### 3.4 Network Security
- **Firewall Requirements**: All systems must be protected by firewalls
- **Network Segmentation**: Production and development environments must be separated
- **Remote Access**: VPN required for all remote connections

### 3.5 Application Security
- **Secure Development**:
  - Security training for all developers
  - Code reviews required
  - SAST/DAST tools in CI/CD
  
- **Vulnerability Management**:
  - Critical patches: 24 hours
  - High patches: 7 days
  - Medium patches: 30 days
  - Low patches: 90 days

### 3.6 Physical Security
- **Data Center Requirements**:
  - 24/7 monitoring
  - Biometric access controls
  - Environmental controls
  
- **Endpoint Security**:
  - Full disk encryption
  - Auto-lock after 10 minutes
  - Remote wipe capability

### 3.7 Incident Response
- **Reporting**: All security incidents must be reported within 1 hour
- **Response Team**: Dedicated incident response team on-call 24/7
- **Communication**: Defined escalation procedures

### 3.8 Business Continuity
- **Backup Requirements**:
  - Daily incremental backups
  - Weekly full backups
  - Off-site storage
  - Quarterly restore testing
  
- **Recovery Objectives**:
  - RTO: 4 hours
  - RPO: 1 hour

### 3.9 Compliance
- **Regulatory Requirements**: Compliance with GDPR, CCPA, and applicable laws
- **Auditing**: Annual security audits required
- **Training**: Annual security awareness training mandatory

### 3.10 Third-Party Security
- **Vendor Assessment**: Security review required for all vendors
- **Contractual Requirements**: Security clauses in all contracts
- **Monitoring**: Continuous monitoring of critical vendors

## 4. Responsibilities

### 4.1 All Personnel
- Comply with this policy
- Report security incidents
- Protect credentials
- Complete security training

### 4.2 Management
- Enforce policy compliance
- Provide necessary resources
- Support security initiatives
- Lead by example

### 4.3 Information Security Team
- Maintain this policy
- Provide security guidance
- Monitor compliance
- Respond to incidents

### 4.4 IT Operations
- Implement security controls
- Maintain secure configurations
- Apply security patches
- Monitor security events

## 5. Enforcement
- Violations may result in disciplinary action up to and including termination
- Legal action may be taken for criminal violations
- Contractors may have contracts terminated

## 6. Exceptions
- Exceptions must be approved by the CISO
- Documented with business justification
- Time-limited with expiration date
- Reviewed quarterly

## 7. Review
This policy shall be reviewed annually and updated as needed.

## 8. Definitions
- **Information Asset**: Any data, system, or resource of value
- **Security Incident**: Any event that compromises security
- **User**: Any person with authorized access

## 9. Related Documents
- Acceptable Use Policy
- Incident Response Plan
- Business Continuity Plan
- Data Classification Standard
"""

        # Save to file
        import os
        os.makedirs(f"{self.output_directory}/security/policies", exist_ok=True)
        
        with open(f"{self.output_directory}/security/policies/information_security_policy.md", 'w') as f:
            f.write(policy)
            
        return {
            'type': 'Security Policy',
            'name': 'information_security_policy.md',
            'path': f"{self.output_directory}/security/policies/information_security_policy.md",
            'content': policy,
            'preview': policy[:300] + '...',
            'files_created': ['information_security_policy.md']
        }
        
    async def _generate_risk_assessment(self) -> Dict[str, str]:
        """Generate risk assessment document"""
        risk_assessment = """# Risk Assessment - Trivia By Grok

## Executive Summary
This risk assessment identifies and evaluates security risks for the Trivia By Grok application.

## Risk Assessment Methodology
- **Framework**: NIST RMF / ISO 27005
- **Risk Score**: Likelihood × Impact (1-5 scale)
- **Risk Levels**: Low (1-5), Medium (6-12), High (13-20), Critical (21-25)

## Identified Risks

### 1. Account Takeover
- **Description**: Attackers gaining unauthorized access to user accounts
- **Likelihood**: 4 (High)
- **Impact**: 4 (High)
- **Risk Score**: 16 (High)
- **Existing Controls**:
  - Password complexity requirements
  - Account lockout policies
- **Recommended Controls**:
  - Implement MFA
  - Add anomaly detection
  - Device fingerprinting

### 2. SQL Injection
- **Description**: Malicious SQL queries compromising database
- **Likelihood**: 2 (Low)
- **Impact**: 5 (Critical)
- **Risk Score**: 10 (Medium)
- **Existing Controls**:
  - Parameterized queries
  - Input validation
- **Recommended Controls**:
  - WAF implementation
  - Database activity monitoring

### 3. DDoS Attack
- **Description**: Service availability compromise through traffic flooding
- **Likelihood**: 3 (Medium)
- **Impact**: 3 (Medium)
- **Risk Score**: 9 (Medium)
- **Existing Controls**:
  - Basic rate limiting
- **Recommended Controls**:
  - CDN with DDoS protection
  - Advanced rate limiting
  - Traffic analysis

### 4. Data Breach
- **Description**: Unauthorized access to sensitive user data
- **Likelihood**: 2 (Low)
- **Impact**: 5 (Critical)
- **Risk Score**: 10 (Medium)
- **Existing Controls**:
  - Encryption at rest
  - Access controls
- **Recommended Controls**:
  - Data loss prevention (DLP)
  - Enhanced monitoring
  - Tokenization of PII

### 5. Insider Threat
- **Description**: Malicious actions by authorized users
- **Likelihood**: 2 (Low)
- **Impact**: 4 (High)
- **Risk Score**: 8 (Medium)
- **Existing Controls**:
  - Access logging
- **Recommended Controls**:
  - User behavior analytics
  - Privileged access management
  - Data access monitoring

### 6. Third-Party Compromise
- **Description**: Security breach through vendor/supplier
- **Likelihood**: 3 (Medium)
- **Impact**: 3 (Medium)
- **Risk Score**: 9 (Medium)
- **Existing Controls**:
  - Vendor assessments
- **Recommended Controls**:
  - Continuous vendor monitoring
  - Security requirements in contracts
  - Regular audits

### 7. API Abuse
- **Description**: Excessive or malicious API usage
- **Likelihood**: 4 (High)
- **Impact**: 2 (Low)
- **Risk Score**: 8 (Medium)
- **Existing Controls**:
  - Basic rate limiting
- **Recommended Controls**:
  - API gateway
  - Advanced rate limiting
  - API key management

### 8. XSS Attacks
- **Description**: Cross-site scripting compromising user sessions
- **Likelihood**: 3 (Medium)
- **Impact**: 3 (Medium)
- **Risk Score**: 9 (Medium)
- **Existing Controls**:
  - Output encoding
  - CSP headers
- **Recommended Controls**:
  - Enhanced CSP policies
  - Regular security scanning
  - Input sanitization library

## Risk Matrix

```
Impact ↑
5 |  M  |  H  |  H  |  C  |  C  |
4 |  L  |  M  |  H  |  H  |  C  |
3 |  L  |  M  |  M  |  H  |  H  |
2 |  L  |  L  |  M  |  M  |  H  |
1 |  L  |  L  |  L  |  M  |  M  |
  +-----+-----+-----+-----+-----+
    1     2     3     4     5   → Likelihood
```

## Risk Treatment Plan

### Priority 1 (Critical/High Risks)
1. **Account Takeover**
   - Implement MFA by Q1 2025
   - Deploy anomaly detection by Q2 2025
   - Budget: $50,000

2. **Data Breach**
   - Implement DLP solution by Q1 2025
   - Enhance monitoring capabilities
   - Budget: $75,000

### Priority 2 (Medium Risks)
1. **SQL Injection**
   - Deploy WAF by Q2 2025
   - Implement database monitoring
   - Budget: $40,000

2. **DDoS Attack**
   - Implement CDN solution by Q2 2025
   - Enhance rate limiting
   - Budget: $30,000

### Priority 3 (Low Risks)
- Monitor and reassess quarterly
- Implement as budget allows

## Residual Risk Analysis

After implementing recommended controls:
- Critical Risks: 0
- High Risks: 0
- Medium Risks: 3
- Low Risks: 5

## Risk Acceptance

The following residual risks are accepted by management:
- Low-impact API abuse (after controls)
- Minimal insider threat risk (with monitoring)
- Supply chain risks (with vendor management)

## Review and Monitoring

- Quarterly risk reviews
- Annual comprehensive assessment
- Continuous threat intelligence monitoring
- KRI dashboard implementation

## Appendices

### A. Risk Scoring Methodology
### B. Control Effectiveness Ratings
### C. Threat Intelligence Sources
### D. Historical Incident Data
"""

        # Save to file
        import os
        os.makedirs(f"{self.output_directory}/security/risk_assessments", exist_ok=True)
        
        with open(f"{self.output_directory}/security/risk_assessments/risk_assessment_2025.md", 'w') as f:
            f.write(risk_assessment)
            
        return {
            'type': 'Risk Assessment',
            'name': 'risk_assessment_2025.md',
            'path': f"{self.output_directory}/security/risk_assessments/risk_assessment_2025.md",
            'content': risk_assessment,
            'preview': risk_assessment[:300] + '...',
            'files_created': ['risk_assessment_2025.md']
        }
        
    async def _generate_security_design(self) -> Dict[str, str]:
        """Generate general security design document"""
        design = """# Security Design Document

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
"""

        # Save to file
        import os
        os.makedirs(f"{self.output_directory}/security/design", exist_ok=True)
        
        with open(f"{self.output_directory}/security/design/security_design.md", 'w') as f:
            f.write(design)
            
        return {
            'type': 'Security Design',
            'name': 'security_design.md',
            'path': f"{self.output_directory}/security/design/security_design.md",
            'content': design,
            'preview': design[:300] + '...',
            'files_created': ['security_design.md']
        }
    
    async def _get_repo_config(self) -> Dict[str, str]:
        """Get Azure DevOps repository configuration for PR creation"""
        return {
            'organization': os.environ.get('AZURE_DEVOPS_ORG', 'data6').replace('https://dev.azure.com/', ''),
            'project': os.environ.get('AZURE_DEVOPS_PROJECT', 'AI-Personas-Test-Sandbox-2'),
            'repository': os.environ.get('AZURE_DEVOPS_REPO', 'AI-Personas-Test-Sandbox-2'),
            'base_branch': None  # Auto-detect from repository default branch
        }
    
    def _get_next_steps(self, outputs: List[Dict], pr_info: Dict = None) -> List[str]:
        """Generate next steps based on outputs and PR status"""
        steps = []
        
        if pr_info and pr_info.get('status') == 'success':
            steps.extend([
                f"📋 Pull Request created: {pr_info.get('pr_url', 'N/A')}",
                f"👥 Reviewers assigned: {', '.join(pr_info.get('reviewers', []))}",
                "⏳ Awaiting security architecture review",
                "🔄 Address review feedback when received",
                "✅ Merge after all approvals"
            ])
        else:
            steps.extend([
                "📝 Security documents generated successfully",
                "⚠️ Manual PR creation required (Azure DevOps integration pending)",
                "👥 Request review from security team",
                "📋 Share documents for architecture approval"
            ])
        
        # Add implementation next steps
        steps.extend([
            "🛠️ Break down security requirements into development tasks",
            "🧪 Plan security testing and validation",
            "📊 Set up security monitoring and alerting",
            "📚 Update team security training materials"
        ])
        
        return steps
    
    async def _create_azure_devops_pr_with_files(self, work_item: Any, outputs: List[Dict], 
                                                 repo_config: Dict[str, str]) -> Dict[str, Any]:
        """Create a pull request with files actually committed to the branch"""
        if not self.azure_client:
            return {
                'status': 'error', 
                'message': 'Azure DevOps client not initialized'
            }
        
        try:
            # Generate branch name
            branch_name = self._generate_branch_name(work_item.id, self.persona_name.lower())
            
            # Get repository by name to get the ID
            repositories = await self.azure_client.git.get_repositories()
            repo_id = None
            for repo in repositories:
                if repo['name'] == repo_config['repository']:
                    repo_id = repo['id']
                    break
                    
            if not repo_id:
                return {
                    'status': 'error',
                    'message': f"Repository '{repo_config['repository']}' not found"
                }
            
            # Create branch using the existing API method with auto-detection
            branch_result = await self.azure_client.git.create_branch(
                repo_id, 
                branch_name, 
                None  # Let the API auto-detect the default branch
            )
            
            if not branch_result:
                return {
                    'status': 'error',
                    'message': f"Failed to create branch '{branch_name}'"
                }
            
            # Commit files to the branch
            commit_success = await self._commit_outputs_to_branch(outputs, branch_name, work_item)
            
            if not commit_success:
                return {
                    'status': 'error',
                    'message': f"Failed to commit files to branch '{branch_name}'"
                }
            
            # Create PR description
            pr_title = f"[WI-{work_item.id}] {work_item.title}"
            pr_description = self._generate_pr_description(work_item, outputs)
            
            # Get suggested reviewers
            reviewers = self._get_suggested_reviewers(work_item, outputs)
            
            # Get the actual default branch for PR target
            default_branch = await self.azure_client.git.get_default_branch(repo_id)
            
            # Create pull request using the existing API method
            pr_result = await self.azure_client.git.create_pull_request(
                repo_id,
                source_branch=branch_name,
                target_branch=default_branch,
                title=pr_title,
                description=pr_description,
                reviewers=reviewers,
                draft=False
            )
            
            if pr_result:
                pr_url = f"https://dev.azure.com/{repo_config['organization']}/{repo_config['project']}/_git/{repo_config['repository']}/pullrequest/{pr_result['pullRequestId']}"
                
                return {
                    'status': 'success',
                    'branch': branch_name,
                    'pr_id': pr_result['pullRequestId'],
                    'pr_url': pr_url,
                    'reviewers': reviewers,
                    'files_committed': [output.get('name', 'unknown') for output in outputs],
                    'message': f'Pull request created with {len(outputs)} files: {pr_url}'
                }
            else:
                return {
                    'status': 'error',
                    'message': 'Failed to create pull request'
                }
                
        except Exception as e:
            logger.error(f"Error creating Azure DevOps PR with files: {e}")
            return {
                'status': 'error',
                'message': f'PR creation failed: {str(e)}'
            }
    
    async def _commit_outputs_to_branch(self, outputs: List[Dict], branch_name: str, work_item: Any) -> bool:
        """Commit generated output files to the PR branch"""
        try:
            import subprocess
            import shutil
            
            # Switch to PR branch
            result = subprocess.run(['git', 'checkout', branch_name], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                logger.error(f"Failed to checkout branch {branch_name}: {result.stderr}")
                return False
            
            # Configure git identity as Steve Bot
            subprocess.run(['git', 'config', 'user.name', 'Steve Bot'])
            subprocess.run(['git', 'config', 'user.email', 'steve.bot@insitec.com.au'])
            
            files_added = []
            
            # Copy and commit each output file
            for output in outputs:
                source_path = output.get('path')
                if source_path and os.path.exists(source_path):
                    # Determine target location in repo
                    target_path = self._get_repo_target_path(output)
                    full_target_path = os.path.join(os.getcwd(), target_path.lstrip('/'))
                    
                    # Create target directory
                    os.makedirs(os.path.dirname(full_target_path), exist_ok=True)
                    
                    # Copy file
                    shutil.copy2(source_path, full_target_path)
                    
                    # Add to git
                    git_path = target_path.lstrip('/')
                    result = subprocess.run(['git', 'add', git_path], 
                                          capture_output=True, text=True)
                    if result.returncode == 0:
                        files_added.append(git_path)
                        logger.info(f"Added file to git: {git_path}")
                    else:
                        logger.error(f"Failed to add file {git_path}: {result.stderr}")
            
            if not files_added:
                logger.error("No files were successfully added to git")
                return False
            
            # Commit files
            commit_msg = f"""Add {work_item.title} artifacts

Generated files:
{chr(10).join(f'- {f}' for f in files_added)}

Generated by Steve Bot (System Architect)
🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>"""
            
            result = subprocess.run(['git', 'commit', '-m', commit_msg], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                logger.error(f"Failed to commit: {result.stderr}")
                return False
            
            # Push to remote
            result = subprocess.run(['git', 'push', 'origin', branch_name], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                logger.error(f"Failed to push: {result.stderr}")
                return False
            
            logger.info(f"Successfully committed {len(files_added)} files to branch {branch_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to commit files to branch: {e}")
            return False
    
    def _get_repo_target_path(self, output: Dict) -> str:
        """Get the target path in the repository for an output file"""
        output_type = output.get('type', '').lower()
        filename = output.get('name', 'document.md')
        
        if 'system architecture' in output_type:
            return f"docs/architecture/system/{filename}"
        elif 'security' in output_type:
            if 'architecture' in output_type:
                return f"docs/security/architecture/{filename}"
            elif 'policy' in output_type:
                return f"docs/security/policies/{filename}"
            elif 'threat' in output_type:
                return f"docs/security/threat_models/{filename}"
            elif 'risk' in output_type:
                return f"docs/security/risk_assessments/{filename}"
            else:
                return f"docs/security/{filename}"
        elif 'architecture' in output_type:
            return f"docs/architecture/{filename}"
        else:
            return f"docs/{filename}"
    
    async def _assign_reviewers_and_create_tasks(self, work_item: Any, outputs: List[Dict], pr_info: Dict):
        """Assign reviewers to PR and create review tasks for personas"""
        logger.info(f"Steve Bot assigning reviewers and creating review tasks for PR #{pr_info.get('pr_id')}")
        
        # Define reviewers based on work item type and outputs
        reviewers = self._get_architecture_reviewers(work_item, outputs)
        
        # Try to assign reviewers to the actual PR in Azure DevOps
        pr_reviewers_assigned = await self._assign_pr_reviewers(reviewers, pr_info)
        
        # Create review tasks for each persona
        tasks_created = []
        for reviewer in reviewers:
            task_result = await self._create_review_task_for_persona(
                reviewer, work_item, pr_info, outputs
            )
            if task_result:
                tasks_created.append(task_result)
                logger.info(f"Created review task for {reviewer['name']}: {task_result['task_id']}")
        
        logger.info(f"Steve Bot completed reviewer assignment: {len(tasks_created)} review tasks created, {len(pr_reviewers_assigned)} PR reviewers assigned")
        
        return {
            'reviewers_assigned': len(reviewers),
            'tasks_created': len(tasks_created),
            'review_tasks': tasks_created
        }
    
    def _get_architecture_reviewers(self, work_item: Any, outputs: List[Dict]) -> List[Dict]:
        """Get appropriate reviewers for architecture work items with PR identity mappings"""
        
        # Define personas with their Azure DevOps identities and PR identity mappings
        # PR Identity IDs are discovered through manual testing and differ from Graph API Origin IDs
        available_personas = [
            {
                'name': 'Kav Bot',
                'email': 'kav.bot@insitec.com.au',
                'role': 'Test Engineer (Security Testing)',
                'expertise': ['security', 'testing', 'vulnerabilities', 'compliance'],
                'focus': 'Security architecture and testing review',
                'required': True,  # Security review is always required
                'pr_identity_id': '5d101cce-1cdd-624b-9853-b391d8185c92',  # Confirmed working
                'origin_id': 'eb61c9a5-9ebe-48da-be0e-56c608603dfb'
            },
            {
                'name': 'Lachlan Bot',
                'email': 'lachlan.bot@insitec.com.au', 
                'role': 'DevSecOps Engineer',
                'expertise': ['infrastructure', 'deployment', 'devops', 'cloud', 'devsecops'],
                'focus': 'Infrastructure and deployment architecture review',
                'required': True,  # Infrastructure review is required for architecture
                'pr_identity_id': None,  # Need to discover through manual testing
                'origin_id': '51f491b1-9c2d-4e4a-946e-982e33a35375'
            },
            {
                'name': 'Moby Bot',
                'email': 'moby.bot@insitec.com.au',
                'role': 'Mobile Developer',
                'expertise': ['mobile', 'android', 'ios', 'apps'],
                'focus': 'Mobile architecture and platform review',
                'required': False,  # Optional for mobile-specific reviews
                'pr_identity_id': None,  # Need to discover
                'origin_id': '7b12fdd0-7e40-4f8b-8a85-acdb3e55b7e3'
            },
            {
                'name': 'Shaun Bot',
                'email': 'shaun.bot@insitec.com.au',
                'role': 'UI/UX Designer',
                'expertise': ['ui', 'ux', 'design', 'user', 'interface'],
                'focus': 'User experience and interface architecture review',
                'required': False,  # Optional for UX reviews
                'pr_identity_id': None,  # Need to discover
                'origin_id': '47dad174-cbe4-4cc4-abbd-b90a0cb0d187'
            }
        ]
        
        # Filter to actual available reviewers (not the author)
        all_personas = [p for p in available_personas if p['name'] != 'Steve Bot']
        
        # For system architecture, assign all relevant reviewers
        if "system architecture" in work_item.title.lower():
            # System architecture needs comprehensive review from all domains
            return all_personas
        
        # For other work items, select based on keywords
        work_item_text = f"{work_item.title} {work_item.description}".lower()
        selected_reviewers = []
        
        for persona in all_personas:
            # Check if persona's expertise matches work item content
            if any(expertise in work_item_text for expertise in persona['expertise']):
                selected_reviewers.append(persona)
        
        # Always include at least security review for any architecture work
        kav_assigned = any(r['name'] == 'Kav Bot' for r in selected_reviewers)
        if not kav_assigned:
            selected_reviewers.append(all_personas[0])  # Kav Bot
        
        return selected_reviewers
    
    async def _create_review_task_for_persona(self, reviewer: Dict, work_item: Any, 
                                            pr_info: Dict, outputs: List[Dict]) -> Dict:
        """Create a review task for a specific persona"""
        
        task_id = f"review-pr-{pr_info.get('pr_id')}-{reviewer['name'].lower().replace(' ', '-')}"
        
        # Create detailed review task description
        task_description = self._generate_review_task_description(
            reviewer, work_item, pr_info, outputs
        )
        
        # Save task to file system for the persona to pick up
        task_file_path = await self._save_review_task_file(
            task_id, reviewer, task_description, pr_info
        )
        
        # Log the task creation
        logger.info(f"Steve Bot created review task: {task_id} for {reviewer['name']}")
        
        return {
            'task_id': task_id,
            'reviewer_name': reviewer['name'],
            'reviewer_email': reviewer['email'],
            'task_file': task_file_path,
            'pr_id': pr_info.get('pr_id'),
            'focus_area': reviewer['focus']
        }
    
    def _generate_review_task_description(self, reviewer: Dict, work_item: Any, 
                                        pr_info: Dict, outputs: List[Dict]) -> str:
        """Generate detailed review task description for persona"""
        
        pr_url = pr_info.get('pr_url', 'N/A')
        pr_id = pr_info.get('pr_id', 'N/A')
        
        # Get output file details
        output_files = []
        for output in outputs:
            output_files.append(f"- `{output.get('name', 'unknown')}` ({output.get('type', 'unknown')})")
        
        files_list = '\n'.join(output_files) if output_files else '- No files specified'
        
        return f"""# PR Review Task: {reviewer['name']}

## Assignment Details
- **PR ID:** #{pr_id}
- **PR URL:** {pr_url}
- **Work Item:** #{work_item.id} - {work_item.title}
- **Assigned To:** {reviewer['name']} ({reviewer['role']})
- **Review Focus:** {reviewer['focus']}
- **Created By:** Steve Bot (System Architect)
- **Created At:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Review Scope
As the **{reviewer['role']}**, please review the architecture document with specific focus on your area of expertise:

**Your Focus Areas:**
{self._get_persona_specific_review_items(reviewer)}

## Files to Review
{files_list}

## Architecture Overview
{work_item.description or 'System architecture for Trivia By Grok mobile application'}

## Review Requirements
1. **Technical Accuracy:** Verify technical correctness and feasibility
2. **Best Practices:** Ensure adherence to industry best practices in your domain
3. **Implementation Feasibility:** Assess if the architecture can be implemented as designed
4. **Risk Assessment:** Identify potential risks or concerns
5. **Recommendations:** Provide specific improvement suggestions

## Expected Deliverables
1. **Review Report:** Technical findings and recommendations
2. **Approval Decision:** Approve or request changes with detailed reasoning
3. **Action Items:** Specific issues that need resolution (if any)

## Process
1. Access PR at: {pr_url}
2. Review the architecture document thoroughly
3. Generate your technical review report
4. Submit feedback through your normal review process
5. Set PR status based on your findings

**Priority:** High
**Deadline:** Within 24 hours

---
*This review task was automatically generated by Steve Bot as part of the architecture review process.*
"""
    
    def _get_persona_specific_review_items(self, reviewer: Dict) -> str:
        """Get specific review items based on persona expertise"""
        
        focus_items = {
            'Kav Bot': """
- Security architecture completeness and effectiveness
- Authentication and authorization mechanisms  
- Data protection and privacy compliance
- API security patterns and best practices
- Threat model coverage and risk assessment
- Security testing integration points
- Vulnerability assessment opportunities
- Security controls implementation feasibility""",
            
            'Lachlan Bot': """
- Infrastructure architecture scalability and reliability
- Deployment pipeline and automation capabilities
- Cloud infrastructure and configuration management
- DevSecOps integration and security automation
- Monitoring, logging, and observability
- CI/CD pipeline security and efficiency
- Infrastructure as Code best practices
- Production deployment readiness""",
            
            'Moby Bot': """
- Mobile platform architecture appropriateness
- Android and iOS platform compatibility and best practices
- MVVM implementation patterns and mobile app architecture
- Mobile-specific performance and memory considerations
- Platform-specific security implementations
- Mobile app lifecycle and state management
- Cross-platform development considerations
- Mobile user experience technical requirements""",
            
            'Shaun Bot': """
- User experience architecture alignment
- Interface design system compatibility and integration
- User workflow and navigation pattern support
- Accessibility considerations in technical architecture
- Design system integration capabilities
- User interaction patterns technical feasibility
- Responsive design architecture support
- Usability testing and feedback integration points"""
        }
        
        return focus_items.get(reviewer['name'], "- General architecture review and best practices assessment")
    
    async def _save_review_task_file(self, task_id: str, reviewer: Dict, 
                                   description: str, pr_info: Dict) -> str:
        """Save review task to file system for persona to pick up"""
        
        # Create tasks directory if it doesn't exist
        tasks_dir = Path("tasks/reviews")
        tasks_dir.mkdir(parents=True, exist_ok=True)
        
        # Create task file
        task_file = tasks_dir / f"{task_id}.md"
        
        try:
            with open(task_file, 'w', encoding='utf-8') as f:
                f.write(description)
            
            logger.info(f"Steve Bot saved review task file: {task_file}")
            return str(task_file)
            
        except Exception as e:
            logger.error(f"Failed to save review task file: {e}")
            return None
    
    async def _assign_pr_reviewers(self, reviewers: List[Dict], pr_info: Dict) -> List[Dict]:
        """Assign reviewers to PR using hybrid approach: API attempts + review task fallback"""
        
        pr_id = pr_info.get('pr_id')
        if not pr_id:
            logger.warning("No PR ID available for reviewer assignment")
            return []
        
        logger.info(f"Steve Bot attempting to assign {len(reviewers)} reviewers to PR #{pr_id}")
        
        try:
            # Get repository ID (hardcoded for our test project)
            repo_id = '8b0982ac-cda2-437e-bf69-b7f7efe2d5f6'  # AI-Personas-Test-Sandbox-2
            
            api_success_count = 0
            assigned_reviewers = []
            
            # Attempt API assignment for reviewers with known PR identity IDs
            for reviewer in reviewers:
                reviewer_name = reviewer.get('name', 'Unknown')
                reviewer_email = reviewer.get('email', '')
                is_required = reviewer.get('required', False)
                pr_identity_id = reviewer.get('pr_identity_id')
                
                # Try API assignment if we have the PR identity ID
                api_success = await self._add_pr_reviewer(
                    repo_id, pr_id, reviewer_email, is_required, pr_identity_id
                )
                
                if api_success:
                    api_success_count += 1
                    assigned_reviewers.append({
                        'name': reviewer_name,
                        'email': reviewer_email,
                        'required': is_required,
                        'status': 'assigned_via_api'
                    })
                    logger.info(f"✅ Successfully assigned {reviewer_name} via API")
                else:
                    logger.info(f"⚠️  API assignment failed for {reviewer_name} - will use review task system")
                    
            # Always create review tasks as backup (this system already works reliably)
            tasks_created = []
            for reviewer in reviewers:
                try:
                    task_result = await self._create_review_task_for_persona(
                        reviewer, pr_info.get('work_item'), pr_info, []
                    )
                    if task_result:
                        tasks_created.append(task_result)
                        assigned_reviewers.append({
                            'name': reviewer.get('name', 'Unknown'),
                            'email': reviewer.get('email', ''),
                            'required': reviewer.get('required', False),
                            'status': 'review_task_created'
                        })
                except Exception as e:
                    logger.error(f"Error creating review task for {reviewer.get('name')}: {e}")
            
            # Log comprehensive summary
            logger.info(f"Steve Bot reviewer assignment summary for PR #{pr_id}:")
            logger.info(f"  - API assignments successful: {api_success_count}/{len(reviewers)}")
            logger.info(f"  - Review tasks created: {len(tasks_created)}/{len(reviewers)}")
            logger.info(f"  - Total reviewers engaged: {len(assigned_reviewers)}")
            logger.info(f"  - Overall success: {'Yes' if len(assigned_reviewers) > 0 else 'No'}")
            
            return assigned_reviewers
            
        except Exception as e:
            logger.error(f"Error in hybrid PR reviewer assignment: {e}")
            return []
    
    async def _add_pr_reviewer(self, repo_id: str, pr_id: int, reviewer_email: str, is_required: bool, pr_identity_id: str = None) -> bool:
        """Add a single reviewer to the PR using the correct Azure DevOps REST API"""
        
        import requests
        import base64
        
        try:
            # Only attempt API assignment if we have the PR identity ID
            if not pr_identity_id:
                logger.info(f"No PR identity ID for {reviewer_email} - will rely on review task system")
                return False
                
            # Get PAT token and create auth header
            pat_token = os.environ.get('AZURE_DEVOPS_PAT')
            if not pat_token:
                logger.warning("No AZURE_DEVOPS_PAT environment variable - cannot assign reviewer via API")
                return False
                
            auth_string = f":{pat_token}"
            auth_bytes = auth_string.encode('ascii')
            auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
            headers = {
                'Authorization': f'Basic {auth_b64}',
                'Content-Type': 'application/json'
            }
            
            # Use the confirmed working API pattern
            reviewer_url = f"https://dev.azure.com/data6/AI-Personas-Test-Sandbox-2/_apis/git/repositories/{repo_id}/pullrequests/{pr_id}/reviewers/{pr_identity_id}?api-version=7.1"
            
            reviewer_data = {
                'vote': 0,
                'isRequired': is_required,
                'isFlagged': False
            }
            
            logger.info(f"Steve Bot assigning {reviewer_email} via API using PR identity {pr_identity_id}")
            
            response = requests.put(reviewer_url, headers=headers, json=reviewer_data)
            
            if response.status_code == 200:
                logger.info(f"✅ Successfully assigned {reviewer_email} as {'required' if is_required else 'optional'} reviewer via API")
                return True
            else:
                logger.warning(f"❌ API assignment failed for {reviewer_email}: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error adding PR reviewer {reviewer_email} via API: {e}")
            return False
