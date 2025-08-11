"""
Steve Processor - System Architect Persona (Enhanced)

Comprehensive system architect who designs all aspects of system architecture:
- System architecture and design patterns
- Component and service architecture  
- Data architecture and modeling
- Integration architecture
- Infrastructure architecture
- Security architecture (as one aspect)
- Performance and scalability design
- Technology stack decisions
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
    System Architect processor for Steve
    
    Generates comprehensive architectural artifacts including:
    - System architecture documents
    - Component designs
    - Data models and schemas
    - API specifications
    - Integration patterns
    - Infrastructure designs
    - Security architecture (when needed)
    - Performance optimization plans
    - Technology recommendations
    """
    
    def __init__(self, output_dir: str = "/tmp/ai_factory_outputs"):
        super().__init__(output_dir)
        self.persona_id = "steve"
        self.persona_name = "SteveBot"
        
    async def process_work_item(self, work_item: Any) -> Dict[str, Any]:
        """Process a work item and generate appropriate architectural documents"""
        logger.info(f"Steve processing work item #{work_item.id}: {work_item.title}")
        
        outputs = []
        pr_info = None
        
        # Analyze work item to determine what architecture documents to generate
        work_item_lower = work_item.title.lower()
        description_lower = work_item.fields.get('System.Description', '').lower()
        
        # System Architecture (most common)
        if any(term in work_item_lower for term in ["system architecture", "architecture", "design", "technical design"]):
            if "security" in work_item_lower:
                # Security-focused architecture
                output = await self._generate_security_architecture()
                outputs.append(output)
            else:
                # Comprehensive system architecture
                output = await self._generate_system_architecture()
                outputs.append(output)
                
        # Component/Service Architecture
        elif any(term in work_item_lower for term in ["component", "service", "microservice", "module"]):
            output = await self._generate_component_architecture()
            outputs.append(output)
            
        # Data Architecture
        elif any(term in work_item_lower for term in ["data model", "database", "schema", "data architecture"]):
            output = await self._generate_data_architecture()
            outputs.append(output)
            
        # API Architecture
        elif any(term in work_item_lower for term in ["api", "rest", "graphql", "interface"]):
            output = await self._generate_api_architecture()
            outputs.append(output)
            
        # Integration Architecture
        elif any(term in work_item_lower for term in ["integration", "messaging", "event", "workflow"]):
            output = await self._generate_integration_architecture()
            outputs.append(output)
            
        # Infrastructure Architecture
        elif any(term in work_item_lower for term in ["infrastructure", "deployment", "cloud", "devops"]):
            output = await self._generate_infrastructure_architecture()
            outputs.append(output)
            
        # Performance Architecture
        elif any(term in work_item_lower for term in ["performance", "scalability", "optimization"]):
            output = await self._generate_performance_architecture()
            outputs.append(output)
            
        # Technology Stack
        elif any(term in work_item_lower for term in ["technology", "tech stack", "framework"]):
            output = await self._generate_technology_recommendations()
            outputs.append(output)
            
        # Security-specific items
        elif any(term in work_item_lower for term in ["threat model", "security policy", "risk assessment"]):
            if "threat model" in work_item_lower:
                output = await self._generate_threat_model()
            elif "security policy" in work_item_lower:
                output = await self._generate_security_policy()
            elif "risk assessment" in work_item_lower:
                output = await self._generate_risk_assessment()
            outputs.append(output)
            
        else:
            # Default: Generate comprehensive system architecture
            output = await self._generate_system_architecture()
            outputs.append(output)
        
        # Create Pull Request workflow using Azure DevOps
        repo_config = await self._get_repo_config()
        if repo_config:
            pr_info = await self._create_azure_devops_pr(work_item, outputs, repo_config)
            
        return {
            'status': 'completed',
            'outputs': outputs,
            'message': f"Generated {len(outputs)} architectural documents",
            'pull_request': pr_info,
            'next_steps': self._get_next_steps(outputs, pr_info)
        }
    
    async def _generate_system_architecture(self) -> Dict[str, str]:
        """Generate comprehensive system architecture document"""
        architecture_doc = """# System Architecture Document

## 1. Executive Summary

This document provides a comprehensive architectural design for the Trivia Game application, covering all aspects of the system including components, data flow, infrastructure, and operational considerations.

## 2. System Overview

### 2.1 Purpose
The Trivia Game application is a real-time, multiplayer trivia platform that supports various game modes, user progression, and social features.

### 2.2 Key Architectural Principles
- **Scalability**: Horizontal scaling capability for all components
- **Reliability**: 99.9% uptime SLA with fault tolerance
- **Performance**: Sub-100ms response times for game actions
- **Security**: Defense-in-depth with zero-trust principles
- **Maintainability**: Modular architecture with clear boundaries
- **Extensibility**: Plugin architecture for new game types

## 3. High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           Client Applications                            │
├─────────────────┬─────────────────┬─────────────────┬─────────────────┤
│   Web App       │   Mobile iOS    │  Mobile Android │   Admin Portal  │
│   (React)       │   (Swift)       │   (Kotlin)      │   (React)       │
└────────┬────────┴────────┬────────┴────────┬────────┴────────┬────────┘
         │                 │                 │                 │
         └─────────────────┴─────────────────┴─────────────────┘
                                    │
                            ┌───────▼────────┐
                            │  API Gateway   │
                            │  (Kong/AWS)    │
                            └───────┬────────┘
                                    │
┌───────────────────────────────────┴─────────────────────────────────────┐
│                          Backend Services Layer                          │
├─────────────┬─────────────┬─────────────┬─────────────┬────────────────┤
│   Auth      │   Game      │   User      │  Analytics  │  Notification  │
│  Service    │  Service    │  Service    │  Service    │   Service      │
│ (FastAPI)   │ (FastAPI)   │ (FastAPI)   │ (FastAPI)   │  (FastAPI)     │
└──────┬──────┴──────┬──────┴──────┬──────┴──────┬──────┴──────┬─────────┘
       │             │             │             │             │
       └─────────────┴─────────────┴─────────────┴─────────────┘
                                    │
                         ┌──────────┴──────────┐
                         │   Message Broker    │
                         │   (RabbitMQ/Kafka)  │
                         └──────────┬──────────┘
                                    │
┌───────────────────────────────────┴─────────────────────────────────────┐
│                            Data Layer                                    │
├─────────────┬─────────────┬─────────────┬─────────────┬────────────────┤
│ PostgreSQL  │   Redis     │ Elasticsearch│   S3/Blob   │  TimescaleDB   │
│  (Primary)  │   (Cache)   │   (Search)   │  (Storage)  │  (Analytics)   │
└─────────────┴─────────────┴─────────────┴─────────────┴────────────────┘
```

## 4. Component Architecture

### 4.1 Frontend Components

#### Web Application (React)
- **Framework**: React 18 with TypeScript
- **State Management**: Redux Toolkit + RTK Query
- **UI Framework**: Material-UI v5
- **Real-time**: Socket.io client
- **Build**: Vite with code splitting

```typescript
// Component Structure
src/
├── components/
│   ├── common/        // Shared components
│   ├── game/          // Game-specific components
│   ├── user/          // User-related components
│   └── admin/         // Admin components
├── features/          // Feature-based modules
│   ├── auth/
│   ├── gameplay/
│   ├── leaderboard/
│   └── social/
├── services/          // API and external services
├── store/             // Redux store configuration
└── utils/             // Utility functions
```

#### Mobile Applications
- **iOS**: SwiftUI with Combine framework
- **Android**: Jetpack Compose with Kotlin Coroutines
- **Shared Logic**: Kotlin Multiplatform Mobile (KMM)

### 4.2 Backend Services

#### Authentication Service
```python
# Service responsibilities
- User registration and login
- JWT token generation and validation
- OAuth2 integration (Google, Facebook)
- Password reset and account recovery
- Session management
- MFA implementation
```

#### Game Service
```python
# Core game engine
- Game session management
- Real-time gameplay coordination
- Score calculation and validation
- Game state persistence
- Matchmaking algorithms
- Tournament management
```

#### User Service
```python
# User management
- Profile management
- Friend connections
- Achievement tracking
- Statistics aggregation
- Preference storage
- Notification settings
```

### 4.3 Infrastructure Components

#### API Gateway
- **Request routing** and load balancing
- **Authentication** enforcement
- **Rate limiting** per client/endpoint
- **Request/response transformation**
- **API versioning** support
- **Monitoring** and analytics

#### Message Broker
- **Event-driven** communication
- **Pub/sub** for real-time updates
- **Task queues** for background jobs
- **Dead letter queues** for error handling
- **Message persistence** and replay

## 5. Data Architecture

### 5.1 Data Models

#### User Model
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT true,
    email_verified BOOLEAN DEFAULT false,
    profile JSONB DEFAULT '{}'::jsonb
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
```

#### Game Session Model
```sql
CREATE TABLE game_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    room_code VARCHAR(10) UNIQUE NOT NULL,
    host_id UUID REFERENCES users(id),
    game_type VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL,
    max_players INTEGER DEFAULT 8,
    current_players INTEGER DEFAULT 0,
    settings JSONB DEFAULT '{}'::jsonb,
    started_at TIMESTAMP WITH TIME ZONE,
    ended_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_game_sessions_status ON game_sessions(status);
CREATE INDEX idx_game_sessions_room_code ON game_sessions(room_code);
```

### 5.2 Caching Strategy

#### Redis Cache Layers
1. **Session Cache**: Active game sessions (TTL: 2 hours)
2. **User Cache**: User profiles and preferences (TTL: 30 minutes)
3. **Leaderboard Cache**: Top scores per category (TTL: 5 minutes)
4. **Question Cache**: Frequently accessed questions (TTL: 1 hour)

```python
# Cache key patterns
SESSION:{session_id}          # Game session data
USER:{user_id}               # User profile cache
LEADERBOARD:{type}:{period}  # Leaderboard data
QUESTION:{category}:{id}     # Question cache
```

### 5.3 Data Partitioning

- **Game Sessions**: Partitioned by date (monthly)
- **User Activity**: Partitioned by user_id hash
- **Analytics**: Time-series partitioning in TimescaleDB
- **Archives**: Moved to cold storage after 90 days

## 6. API Architecture

### 6.1 RESTful API Design

```yaml
# API Structure
/api/v1/
  /auth/
    POST   /register     # User registration
    POST   /login        # User login
    POST   /logout       # User logout
    POST   /refresh      # Token refresh
    
  /users/
    GET    /profile      # Get user profile
    PUT    /profile      # Update profile
    GET    /stats        # User statistics
    
  /games/
    POST   /create       # Create game session
    POST   /join         # Join game session
    GET    /active       # List active games
    POST   /start        # Start game
    
  /gameplay/
    POST   /answer       # Submit answer
    GET    /question     # Get current question
    GET    /scores       # Get current scores
```

### 6.2 WebSocket Events

```javascript
// Client -> Server Events
socket.emit('JOIN_GAME', { roomCode, userId });
socket.emit('SUBMIT_ANSWER', { questionId, answer });
socket.emit('REQUEST_HINT', { questionId });

// Server -> Client Events
socket.on('GAME_STATE_UPDATE', (state) => {});
socket.on('NEW_QUESTION', (question) => {});
socket.on('SCORES_UPDATE', (scores) => {});
socket.on('GAME_ENDED', (results) => {});
```

### 6.3 GraphQL Schema (Future)

```graphql
type User {
  id: ID!
  username: String!
  email: String!
  profile: UserProfile!
  stats: UserStats!
  friends: [User!]!
}

type Game {
  id: ID!
  roomCode: String!
  host: User!
  players: [Player!]!
  status: GameStatus!
  currentQuestion: Question
}

type Query {
  user(id: ID!): User
  game(roomCode: String!): Game
  leaderboard(type: LeaderboardType!): [LeaderboardEntry!]!
}

type Mutation {
  createGame(input: CreateGameInput!): Game!
  joinGame(roomCode: String!): GameJoinResult!
  submitAnswer(input: AnswerInput!): AnswerResult!
}

type Subscription {
  gameUpdates(roomCode: String!): GameUpdate!
}
```

## 7. Integration Architecture

### 7.1 External Integrations

#### Payment Processing
- **Provider**: Stripe
- **Integration**: Webhooks + API
- **Features**: Subscriptions, one-time purchases
- **Security**: PCI compliance through tokenization

#### Social Media
- **Platforms**: Facebook, Twitter, Discord
- **Features**: Login, share scores, invite friends
- **Implementation**: OAuth2 + Platform SDKs

#### Analytics
- **Tools**: Google Analytics, Mixpanel
- **Custom**: Internal analytics service
- **Data Pipeline**: Kafka -> Spark -> BigQuery

### 7.2 Internal Service Communication

```yaml
# Service Mesh Configuration
communication_patterns:
  synchronous:
    - HTTP/REST for request-response
    - gRPC for high-performance internal calls
    
  asynchronous:
    - RabbitMQ for task queues
    - Kafka for event streaming
    - Redis Pub/Sub for real-time updates
    
  service_discovery:
    - Consul for service registration
    - Health checks every 10s
    - Circuit breakers with Hystrix patterns
```

## 8. Infrastructure Architecture

### 8.1 Cloud Architecture (AWS)

```yaml
# Multi-Region Deployment
regions:
  primary: us-east-1
  secondary: eu-west-1
  
components:
  compute:
    - EKS clusters for services
    - Fargate for serverless tasks
    - Lambda for event processing
    
  storage:
    - RDS Multi-AZ for PostgreSQL
    - ElastiCache for Redis
    - S3 for static assets
    - EFS for shared storage
    
  networking:
    - VPC with public/private subnets
    - ALB for load balancing
    - CloudFront CDN
    - Route53 for DNS
    
  security:
    - WAF for application protection
    - Secrets Manager for credentials
    - KMS for encryption keys
```

### 8.2 Kubernetes Architecture

```yaml
# K8s Deployment Structure
namespaces:
  - production
  - staging
  - monitoring
  
workloads:
  deployments:
    - auth-service (3 replicas)
    - game-service (5 replicas)
    - user-service (3 replicas)
    
  statefulsets:
    - redis-cluster (3 nodes)
    - rabbitmq (3 nodes)
    
  cronjobs:
    - daily-analytics
    - cleanup-old-sessions
    - backup-databases
```

### 8.3 CI/CD Pipeline

```yaml
pipeline:
  source:
    - GitHub repositories
    - Branch protection rules
    
  build:
    - GitHub Actions
    - Docker multi-stage builds
    - Security scanning (Trivy)
    
  test:
    - Unit tests (Jest, pytest)
    - Integration tests
    - E2E tests (Cypress)
    
  deploy:
    - ArgoCD for GitOps
    - Blue-green deployments
    - Automated rollbacks
```

## 9. Performance Architecture

### 9.1 Performance Targets

- **API Response Time**: p99 < 100ms
- **WebSocket Latency**: < 50ms
- **Page Load Time**: < 2 seconds
- **Concurrent Users**: 100,000+
- **Questions per Second**: 50,000+

### 9.2 Optimization Strategies

#### Frontend Optimization
- Code splitting and lazy loading
- Image optimization with WebP
- Service Worker for offline mode
- CDN for static assets
- Bundle size < 200KB

#### Backend Optimization
- Connection pooling
- Query optimization with indexes
- Batch processing for bulk operations
- Caching at multiple levels
- Horizontal scaling with load balancing

#### Database Optimization
- Read replicas for queries
- Materialized views for aggregations
- Partition pruning
- Query plan analysis
- Connection multiplexing

### 9.3 Monitoring and Observability

```yaml
monitoring_stack:
  metrics:
    - Prometheus for metrics collection
    - Grafana for visualization
    - Custom dashboards per service
    
  logging:
    - ELK stack (Elasticsearch, Logstash, Kibana)
    - Structured logging with correlation IDs
    - Log aggregation and analysis
    
  tracing:
    - Jaeger for distributed tracing
    - OpenTelemetry instrumentation
    - Request flow visualization
    
  alerting:
    - PagerDuty integration
    - Slack notifications
    - Automated incident response
```

## 10. Security Architecture

### 10.1 Security Layers

1. **Network Security**
   - AWS WAF rules
   - DDoS protection
   - Private subnets for services
   - VPN for admin access

2. **Application Security**
   - Input validation
   - SQL injection prevention
   - XSS protection
   - CSRF tokens

3. **Data Security**
   - Encryption at rest (AES-256)
   - Encryption in transit (TLS 1.3)
   - Field-level encryption for PII
   - Key rotation every 90 days

4. **Access Control**
   - JWT with short expiration
   - Role-based permissions
   - API rate limiting
   - IP allowlisting for admin

### 10.2 Compliance

- **GDPR**: Data privacy and right to deletion
- **CCPA**: California privacy requirements
- **SOC 2**: Security controls audit
- **PCI DSS**: Payment card security

## 11. Disaster Recovery

### 11.1 Backup Strategy

- **Database**: Daily snapshots, point-in-time recovery
- **File Storage**: Cross-region replication
- **Configuration**: Version controlled in Git
- **Secrets**: Backed up in separate vault

### 11.2 Recovery Objectives

- **RTO** (Recovery Time Objective): 1 hour
- **RPO** (Recovery Point Objective): 15 minutes
- **Failover**: Automated with health checks
- **Testing**: Monthly DR drills

## 12. Future Considerations

### 12.1 Scalability Path

1. **Phase 1** (Current): Single region, 100K users
2. **Phase 2**: Multi-region, 1M users
3. **Phase 3**: Global edge deployment, 10M+ users

### 12.2 Technology Evolution

- Migrate to **GraphQL** for flexible queries
- Implement **WebAssembly** for client performance
- Add **AI/ML** for personalized questions
- Explore **Blockchain** for tournament integrity

## 13. Architecture Decision Records (ADRs)

### ADR-001: Microservices Architecture
- **Status**: Accepted
- **Context**: Need for independent scaling and deployment
- **Decision**: Adopt microservices with clear boundaries
- **Consequences**: Higher operational complexity, better scalability

### ADR-002: PostgreSQL as Primary Database
- **Status**: Accepted
- **Context**: Need for ACID compliance and complex queries
- **Decision**: Use PostgreSQL with read replicas
- **Consequences**: Proven reliability, may need sharding later

### ADR-003: React for Web Frontend
- **Status**: Accepted
- **Context**: Need for responsive, maintainable UI
- **Decision**: React with TypeScript and Material-UI
- **Consequences**: Large ecosystem, good developer experience

## 14. Conclusion

This architecture provides a solid foundation for building a scalable, reliable, and maintainable trivia game platform. The modular design allows for independent evolution of components while maintaining system coherence.

Key success factors:
- Clear service boundaries
- Comprehensive monitoring
- Automated testing and deployment
- Performance optimization at all layers
- Security-first design approach

The architecture is designed to grow with the business, supporting both immediate needs and future expansion."""

        # Save the architecture document
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"system_architecture_{timestamp}.md"
        filepath = os.path.join(self.output_dir, "architecture", filename)
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w') as f:
            f.write(architecture_doc)
            
        return {
            'type': 'System Architecture',
            'name': filename,
            'path': filepath,
            'preview': architecture_doc[:500] + '...'
        }
    
    async def _generate_component_architecture(self) -> Dict[str, str]:
        """Generate component/service architecture document"""
        component_doc = """# Component Architecture Document

## 1. Overview

This document details the component architecture for the Trivia Game application, defining service boundaries, interfaces, and interactions.

## 2. Component Principles

- **Single Responsibility**: Each component has one clear purpose
- **Loose Coupling**: Minimal dependencies between components
- **High Cohesion**: Related functionality grouped together
- **Interface Segregation**: Focused, specific interfaces
- **Dependency Inversion**: Depend on abstractions, not implementations

## 3. Core Components

### 3.1 Authentication Component

```typescript
interface IAuthenticationService {
  register(userData: UserRegistration): Promise<User>
  login(credentials: LoginCredentials): Promise<AuthToken>
  logout(token: string): Promise<void>
  refreshToken(refreshToken: string): Promise<AuthToken>
  validateToken(token: string): Promise<TokenValidation>
  resetPassword(email: string): Promise<void>
  verifyEmail(token: string): Promise<void>
}

// Implementation details
class AuthenticationService implements IAuthenticationService {
  private userRepository: IUserRepository
  private tokenService: ITokenService
  private emailService: IEmailService
  private cryptoService: ICryptoService
  
  // Dependency injection
  constructor(dependencies: AuthServiceDependencies) {
    this.userRepository = dependencies.userRepository
    this.tokenService = dependencies.tokenService
    this.emailService = dependencies.emailService
    this.cryptoService = dependencies.cryptoService
  }
  
  async register(userData: UserRegistration): Promise<User> {
    // Validate input
    const validation = await this.validateRegistration(userData)
    if (!validation.isValid) {
      throw new ValidationError(validation.errors)
    }
    
    // Hash password
    const hashedPassword = await this.cryptoService.hashPassword(userData.password)
    
    // Create user
    const user = await this.userRepository.create({
      ...userData,
      password: hashedPassword
    })
    
    // Send verification email
    await this.emailService.sendVerificationEmail(user)
    
    return user
  }
}
```

### 3.2 Game Engine Component

```python
class GameEngine:
    """Core game logic and state management"""
    
    def __init__(self, game_config: GameConfig):
        self.config = game_config
        self.state_manager = GameStateManager()
        self.rule_engine = RuleEngine()
        self.scoring_engine = ScoringEngine()
        
    async def create_session(self, host_id: str, settings: GameSettings) -> GameSession:
        """Create a new game session"""
        session = GameSession(
            id=generate_uuid(),
            host_id=host_id,
            settings=settings,
            state=GameState.WAITING
        )
        
        await self.state_manager.save_session(session)
        return session
        
    async def process_answer(self, session_id: str, player_id: str, answer: Answer) -> AnswerResult:
        """Process a player's answer"""
        session = await self.state_manager.get_session(session_id)
        current_question = session.current_question
        
        # Validate answer timing
        if not self.rule_engine.is_answer_valid_timing(session, answer):
            return AnswerResult(correct=False, reason="Time expired")
            
        # Check answer correctness
        is_correct = self.rule_engine.check_answer(current_question, answer)
        
        # Calculate score
        score = self.scoring_engine.calculate_score(
            is_correct=is_correct,
            time_taken=answer.time_taken,
            streak=session.players[player_id].streak
        )
        
        # Update state
        await self.state_manager.update_player_score(session_id, player_id, score)
        
        return AnswerResult(
            correct=is_correct,
            score=score,
            new_total=session.players[player_id].total_score
        )
```

### 3.3 Real-time Communication Component

```javascript
class RealtimeService {
  constructor(io) {
    this.io = io
    this.rooms = new Map()
    this.setupEventHandlers()
  }
  
  setupEventHandlers() {
    this.io.on('connection', (socket) => {
      socket.on('JOIN_ROOM', (data) => this.handleJoinRoom(socket, data))
      socket.on('LEAVE_ROOM', (data) => this.handleLeaveRoom(socket, data))
      socket.on('GAME_ACTION', (data) => this.handleGameAction(socket, data))
      socket.on('disconnect', () => this.handleDisconnect(socket))
    })
  }
  
  async handleJoinRoom(socket, { roomId, userId }) {
    // Validate user and room
    const validation = await this.validateJoinRequest(roomId, userId)
    if (!validation.success) {
      socket.emit('JOIN_ERROR', validation.error)
      return
    }
    
    // Join socket room
    socket.join(roomId)
    socket.userId = userId
    socket.roomId = roomId
    
    // Update room state
    if (!this.rooms.has(roomId)) {
      this.rooms.set(roomId, new Set())
    }
    this.rooms.get(roomId).add(userId)
    
    // Notify others
    socket.to(roomId).emit('PLAYER_JOINED', {
      userId,
      timestamp: Date.now()
    })
    
    // Send current state to joiner
    const currentState = await this.gameService.getRoomState(roomId)
    socket.emit('ROOM_STATE', currentState)
  }
  
  broadcastToRoom(roomId, event, data) {
    this.io.to(roomId).emit(event, data)
  }
}
```

### 3.4 Analytics Component

```python
class AnalyticsEngine:
    """Collects and processes game analytics"""
    
    def __init__(self):
        self.event_processor = EventProcessor()
        self.aggregator = MetricsAggregator()
        self.storage = AnalyticsStorage()
        
    async def track_event(self, event: AnalyticsEvent):
        """Track a single analytics event"""
        # Enrich event with metadata
        enriched_event = self.event_processor.enrich(event)
        
        # Store raw event
        await self.storage.store_event(enriched_event)
        
        # Update aggregations
        await self.aggregator.update_metrics(enriched_event)
        
        # Trigger real-time dashboards
        await self.publish_to_dashboard(enriched_event)
        
    async def get_player_analytics(self, player_id: str) -> PlayerAnalytics:
        """Get comprehensive analytics for a player"""
        return PlayerAnalytics(
            total_games=await self.storage.count_player_games(player_id),
            win_rate=await self.calculate_win_rate(player_id),
            favorite_categories=await self.get_favorite_categories(player_id),
            peak_performance_time=await self.analyze_performance_by_time(player_id),
            improvement_trend=await self.calculate_improvement_trend(player_id)
        )
```

## 4. Component Interactions

### 4.1 Sequence Diagram: Game Creation

```mermaid
sequenceDiagram
    participant Client
    participant Gateway
    participant AuthService
    participant GameService
    participant RealtimeService
    participant Database
    
    Client->>Gateway: POST /games/create
    Gateway->>AuthService: Validate token
    AuthService-->>Gateway: User validated
    Gateway->>GameService: Create game session
    GameService->>Database: Save session
    Database-->>GameService: Session saved
    GameService->>RealtimeService: Setup room
    RealtimeService-->>GameService: Room ready
    GameService-->>Gateway: Game created
    Gateway-->>Client: { gameId, roomCode }
```

### 4.2 Event Flow: Answer Submission

```mermaid
graph LR
    A[Player Submits Answer] --> B[WebSocket Server]
    B --> C[Validate Answer]
    C --> D[Game Engine]
    D --> E[Calculate Score]
    E --> F[Update State]
    F --> G[Broadcast Update]
    G --> H[All Players]
    F --> I[Analytics]
    I --> J[Store Event]
```

## 5. Component Configuration

### 5.1 Service Registry

```yaml
services:
  auth-service:
    name: authentication
    version: 1.0.0
    port: 8001
    health_check: /health
    dependencies:
      - postgresql
      - redis
      
  game-service:
    name: game-engine
    version: 1.0.0
    port: 8002
    health_check: /health
    dependencies:
      - postgresql
      - redis
      - rabbitmq
      
  realtime-service:
    name: websocket-server
    version: 1.0.0
    port: 8003
    health_check: /health
    dependencies:
      - redis
      - game-service
```

### 5.2 Component Communication Patterns

```typescript
// Event-driven communication
interface EventBus {
  publish(event: DomainEvent): Promise<void>
  subscribe(eventType: string, handler: EventHandler): void
}

// Request-response communication
interface ServiceClient {
  get<T>(path: string, params?: any): Promise<T>
  post<T>(path: string, data: any): Promise<T>
  put<T>(path: string, data: any): Promise<T>
  delete(path: string): Promise<void>
}

// Circuit breaker pattern
class CircuitBreaker {
  private failures = 0
  private lastFailTime: number
  private state: 'CLOSED' | 'OPEN' | 'HALF_OPEN' = 'CLOSED'
  
  async execute<T>(operation: () => Promise<T>): Promise<T> {
    if (this.state === 'OPEN') {
      if (Date.now() - this.lastFailTime > this.timeout) {
        this.state = 'HALF_OPEN'
      } else {
        throw new Error('Circuit breaker is OPEN')
      }
    }
    
    try {
      const result = await operation()
      this.onSuccess()
      return result
    } catch (error) {
      this.onFailure()
      throw error
    }
  }
}
```

## 6. Component Testing Strategy

### 6.1 Unit Testing

```javascript
describe('AuthenticationService', () => {
  let authService: AuthenticationService
  let mockUserRepo: jest.Mocked<IUserRepository>
  let mockTokenService: jest.Mocked<ITokenService>
  
  beforeEach(() => {
    mockUserRepo = createMockUserRepository()
    mockTokenService = createMockTokenService()
    
    authService = new AuthenticationService({
      userRepository: mockUserRepo,
      tokenService: mockTokenService
    })
  })
  
  describe('register', () => {
    it('should create user with hashed password', async () => {
      const userData = {
        email: 'test@example.com',
        password: 'password123',
        username: 'testuser'
      }
      
      mockUserRepo.create.mockResolvedValue(mockUser)
      
      const result = await authService.register(userData)
      
      expect(mockUserRepo.create).toHaveBeenCalledWith(
        expect.objectContaining({
          email: userData.email,
          password: expect.not.stringMatching(userData.password)
        })
      )
      expect(result).toEqual(mockUser)
    })
  })
})
```

### 6.2 Integration Testing

```python
@pytest.mark.integration
class TestGameFlow:
    """Test complete game flow across components"""
    
    async def test_complete_game_session(self, test_client, test_db):
        # Create users
        host = await create_test_user(test_db)
        players = await create_test_players(test_db, count=3)
        
        # Create game
        response = await test_client.post(
            "/api/games/create",
            headers={"Authorization": f"Bearer {host.token}"},
            json={"settings": {"maxPlayers": 4, "rounds": 5}}
        )
        assert response.status_code == 201
        game_data = response.json()
        
        # Players join
        for player in players:
            join_response = await test_client.post(
                "/api/games/join",
                headers={"Authorization": f"Bearer {player.token}"},
                json={"roomCode": game_data["roomCode"]}
            )
            assert join_response.status_code == 200
            
        # Start game
        start_response = await test_client.post(
            f"/api/games/{game_data['id']}/start",
            headers={"Authorization": f"Bearer {host.token}"}
        )
        assert start_response.status_code == 200
        
        # Simulate gameplay
        for round in range(5):
            # Get question
            question = await test_client.get(
                f"/api/games/{game_data['id']}/current-question"
            )
            
            # Submit answers
            for player in players:
                await test_client.post(
                    f"/api/games/{game_data['id']}/answer",
                    headers={"Authorization": f"Bearer {player.token}"},
                    json={"answer": "A", "timeElapsed": 5.2}
                )
                
        # Verify final state
        final_state = await test_client.get(
            f"/api/games/{game_data['id']}/results"
        )
        assert final_state.json()["status"] == "completed"
        assert len(final_state.json()["rankings"]) == 4
```

## 7. Component Deployment

### 7.1 Container Configuration

```dockerfile
# Base image for all services
FROM node:18-alpine AS base
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

# Auth service
FROM base AS auth-service
COPY --from=base /app/node_modules ./node_modules
COPY ./services/auth ./
EXPOSE 8001
CMD ["node", "server.js"]

# Game service
FROM base AS game-service
COPY --from=base /app/node_modules ./node_modules
COPY ./services/game ./
EXPOSE 8002
CMD ["node", "server.js"]
```

### 7.2 Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: auth-service
  labels:
    app: auth-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: auth-service
  template:
    metadata:
      labels:
        app: auth-service
    spec:
      containers:
      - name: auth-service
        image: trivia/auth-service:1.0.0
        ports:
        - containerPort: 8001
        env:
        - name: DB_CONNECTION
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: connection-string
        livenessProbe:
          httpGet:
            path: /health
            port: 8001
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8001
          initialDelaySeconds: 5
          periodSeconds: 5
```

## 8. Component Monitoring

### 8.1 Health Checks

```typescript
interface HealthCheck {
  name: string
  check(): Promise<HealthStatus>
}

class DatabaseHealthCheck implements HealthCheck {
  name = 'database'
  
  async check(): Promise<HealthStatus> {
    try {
      await this.db.query('SELECT 1')
      return { status: 'healthy', details: {} }
    } catch (error) {
      return { 
        status: 'unhealthy', 
        details: { error: error.message }
      }
    }
  }
}

// Aggregate health endpoint
app.get('/health', async (req, res) => {
  const checks = await Promise.all(
    healthChecks.map(async (check) => ({
      [check.name]: await check.check()
    }))
  )
  
  const overall = checks.every(c => 
    Object.values(c)[0].status === 'healthy'
  )
  
  res.status(overall ? 200 : 503).json({
    status: overall ? 'healthy' : 'unhealthy',
    checks: Object.assign({}, ...checks)
  })
})
```

### 8.2 Component Metrics

```python
# Prometheus metrics
from prometheus_client import Counter, Histogram, Gauge

# Request metrics
request_count = Counter(
    'app_requests_total',
    'Total requests',
    ['method', 'endpoint', 'status']
)

request_duration = Histogram(
    'app_request_duration_seconds',
    'Request duration',
    ['method', 'endpoint']
)

# Business metrics
active_games = Gauge(
    'game_sessions_active',
    'Number of active game sessions'
)

players_online = Gauge(
    'players_online_total',
    'Total players currently online'
)

# Custom game metrics
questions_answered = Counter(
    'questions_answered_total',
    'Total questions answered',
    ['category', 'difficulty', 'correct']
)
```

## 9. Component Security

### 9.1 Authentication Middleware

```javascript
const authMiddleware = async (req, res, next) => {
  const token = req.headers.authorization?.split(' ')[1]
  
  if (!token) {
    return res.status(401).json({ error: 'No token provided' })
  }
  
  try {
    const decoded = await tokenService.verify(token)
    req.user = decoded
    next()
  } catch (error) {
    if (error.name === 'TokenExpiredError') {
      return res.status(401).json({ error: 'Token expired' })
    }
    return res.status(403).json({ error: 'Invalid token' })
  }
}
```

### 9.2 Input Validation

```typescript
// Validation schemas
const schemas = {
  createGame: Joi.object({
    settings: Joi.object({
      maxPlayers: Joi.number().min(2).max(20).required(),
      rounds: Joi.number().min(1).max(50).required(),
      timePerQuestion: Joi.number().min(5).max(120).required(),
      category: Joi.string().valid(...VALID_CATEGORIES).required()
    }).required()
  }),
  
  submitAnswer: Joi.object({
    questionId: Joi.string().uuid().required(),
    answer: Joi.string().max(1000).required(),
    timeElapsed: Joi.number().min(0).max(120).required()
  })
}

// Validation middleware
const validate = (schema) => (req, res, next) => {
  const { error, value } = schema.validate(req.body)
  
  if (error) {
    return res.status(400).json({
      error: 'Validation failed',
      details: error.details.map(d => d.message)
    })
  }
  
  req.validatedBody = value
  next()
}
```

## 10. Component Evolution

### 10.1 Versioning Strategy

- **API Versioning**: URL path versioning (/v1/, /v2/)
- **Message Versioning**: Schema evolution with backward compatibility
- **Database Versioning**: Migrations with rollback support

### 10.2 Feature Toggles

```typescript
class FeatureToggle {
  private features: Map<string, FeatureConfig>
  
  isEnabled(feature: string, context?: FeatureContext): boolean {
    const config = this.features.get(feature)
    if (!config) return false
    
    // Check if globally enabled
    if (config.enabled) return true
    
    // Check percentage rollout
    if (config.percentage && context?.userId) {
      const hash = this.hash(feature + context.userId)
      return (hash % 100) < config.percentage
    }
    
    // Check specific user/group enablement
    if (config.enabledFor && context) {
      return config.enabledFor.includes(context.userId) ||
             config.enabledFor.includes(context.groupId)
    }
    
    return false
  }
}
```

This component architecture provides the blueprint for building a modular, scalable, and maintainable system with clear boundaries and well-defined interfaces."""

        # Save the document
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"component_architecture_{timestamp}.md"
        filepath = os.path.join(self.output_dir, "architecture", filename)
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w') as f:
            f.write(component_doc)
            
        return {
            'type': 'Component Architecture',
            'name': filename,
            'path': filepath,
            'preview': component_doc[:500] + '...'
        }
    
    async def _generate_data_architecture(self) -> Dict[str, str]:
        """Generate data architecture document"""
        data_doc = """# Data Architecture Document

## 1. Overview

This document defines the data architecture for the Trivia Game application, including data models, storage strategies, and data flow patterns.

## 2. Data Architecture Principles

- **Data Integrity**: ACID compliance for critical transactions
- **Scalability**: Horizontal partitioning and sharding strategies
- **Performance**: Optimized for read-heavy workloads
- **Flexibility**: Schema evolution without downtime
- **Security**: Encryption at rest and in transit

## 3. Logical Data Model

### 3.1 Entity Relationship Diagram

```mermaid
erDiagram
    User ||--o{ GameSession : creates
    User ||--o{ PlayerStats : has
    User ||--o{ Achievement : earns
    User ||--o{ Friend : has
    
    GameSession ||--|{ GamePlayer : contains
    GameSession ||--o{ GameRound : has
    GameSession }|--|| GameType : uses
    
    GamePlayer }o--|| User : is
    GamePlayer ||--o{ PlayerAnswer : submits
    
    GameRound ||--|{ Question : contains
    GameRound ||--o{ PlayerAnswer : receives
    
    Question }o--|| Category : belongs_to
    Question ||--|{ AnswerOption : has
    
    PlayerAnswer }o--|| AnswerOption : selects
    PlayerAnswer }o--|| GamePlayer : from
```

### 3.2 Core Entities

#### User Entity
```sql
-- Users table with extended profile information
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    
    -- Profile data
    display_name VARCHAR(100),
    avatar_url VARCHAR(500),
    bio TEXT,
    
    -- Account status
    is_active BOOLEAN DEFAULT true,
    email_verified BOOLEAN DEFAULT false,
    account_type VARCHAR(20) DEFAULT 'free', -- free, premium, admin
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login_at TIMESTAMP WITH TIME ZONE,
    
    -- Preferences (JSONB for flexibility)
    preferences JSONB DEFAULT '{
        "notifications": {
            "email": true,
            "push": true,
            "game_invites": true
        },
        "privacy": {
            "profile_visible": true,
            "stats_visible": true
        },
        "gameplay": {
            "sound_enabled": true,
            "animations_enabled": true
        }
    }'::jsonb
);

-- Indexes for performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_created_at ON users(created_at);
CREATE INDEX idx_users_preferences ON users USING gin(preferences);
```

#### Game Session Entity
```sql
-- Game sessions with comprehensive tracking
CREATE TABLE game_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    room_code VARCHAR(10) UNIQUE NOT NULL,
    
    -- Game configuration
    host_id UUID NOT NULL REFERENCES users(id),
    game_type_id INTEGER NOT NULL REFERENCES game_types(id),
    max_players INTEGER NOT NULL DEFAULT 8,
    
    -- Status tracking
    status VARCHAR(20) NOT NULL DEFAULT 'waiting',
    -- waiting, starting, in_progress, paused, completed, abandoned
    
    -- Settings (flexible JSON)
    settings JSONB NOT NULL DEFAULT '{
        "rounds": 10,
        "time_per_question": 20,
        "difficulty": "medium",
        "categories": [],
        "power_ups_enabled": true
    }'::jsonb,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP WITH TIME ZONE,
    ended_at TIMESTAMP WITH TIME ZONE,
    
    -- Metadata
    total_questions INTEGER DEFAULT 0,
    total_duration_seconds INTEGER,
    
    -- Constraints
    CONSTRAINT valid_status CHECK (
        status IN ('waiting', 'starting', 'in_progress', 'paused', 'completed', 'abandoned')
    ),
    CONSTRAINT valid_player_count CHECK (max_players BETWEEN 2 AND 100)
);

-- Partitioning by month for historical data
CREATE TABLE game_sessions_2024_01 PARTITION OF game_sessions
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');
```

#### Question Bank
```sql
-- Questions with versioning and metadata
CREATE TABLE questions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Question content
    question_text TEXT NOT NULL,
    question_type VARCHAR(20) NOT NULL DEFAULT 'multiple_choice',
    -- multiple_choice, true_false, fill_blank, image_based
    
    -- Metadata
    category_id INTEGER NOT NULL REFERENCES categories(id),
    difficulty VARCHAR(20) NOT NULL,
    points INTEGER NOT NULL DEFAULT 100,
    time_limit_seconds INTEGER DEFAULT 20,
    
    -- Media attachments
    image_url VARCHAR(500),
    audio_url VARCHAR(500),
    
    -- Usage tracking
    times_used INTEGER DEFAULT 0,
    times_answered_correctly INTEGER DEFAULT 0,
    average_response_time_seconds DECIMAL(5,2),
    
    -- Quality control
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    reported_count INTEGER DEFAULT 0,
    
    -- Versioning
    version INTEGER NOT NULL DEFAULT 1,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Localization support
    language_code VARCHAR(5) DEFAULT 'en-US',
    translations JSONB DEFAULT '{}'::jsonb
);

-- Answer options for questions
CREATE TABLE answer_options (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    question_id UUID NOT NULL REFERENCES questions(id) ON DELETE CASCADE,
    
    option_text TEXT NOT NULL,
    is_correct BOOLEAN NOT NULL DEFAULT false,
    explanation TEXT,
    
    display_order INTEGER NOT NULL,
    
    UNIQUE(question_id, display_order)
);
```

## 4. Physical Data Model

### 4.1 Storage Architecture

```yaml
storage_layers:
  hot_storage:
    technology: PostgreSQL (Primary)
    data:
      - Active users
      - Current game sessions
      - Recent activities (30 days)
    characteristics:
      - SSD storage
      - High IOPS
      - Synchronous replication
      
  warm_storage:
    technology: PostgreSQL (Read Replicas)
    data:
      - Historical games (30-90 days)
      - User statistics
      - Leaderboards
    characteristics:
      - SSD storage
      - Asynchronous replication
      - Read-only access
      
  cold_storage:
    technology: S3 + Parquet files
    data:
      - Games older than 90 days
      - Archived user data
      - Historical analytics
    characteristics:
      - Object storage
      - Compressed format
      - Batch access only
      
  cache_layer:
    technology: Redis Cluster
    data:
      - Active sessions
      - User profiles
      - Hot questions
      - Real-time scores
    characteristics:
      - In-memory storage
      - Millisecond latency
      - TTL-based expiration
```

### 4.2 Database Sharding Strategy

```sql
-- User sharding by user_id hash
CREATE OR REPLACE FUNCTION get_user_shard(user_id UUID) 
RETURNS INTEGER AS $$
BEGIN
    RETURN abs(hashtext(user_id::text)) % 4; -- 4 shards
END;
$$ LANGUAGE plpgsql;

-- Shard configuration
-- Shard 0: users_shard_0, games_shard_0
-- Shard 1: users_shard_1, games_shard_1
-- Shard 2: users_shard_2, games_shard_2
-- Shard 3: users_shard_3, games_shard_3

-- Route queries to appropriate shard
CREATE OR REPLACE FUNCTION route_to_shard(
    table_name TEXT,
    shard_key UUID
) RETURNS TEXT AS $$
DECLARE
    shard_number INTEGER;
BEGIN
    shard_number := get_user_shard(shard_key);
    RETURN format('%s_shard_%s', table_name, shard_number);
END;
$$ LANGUAGE plpgsql;
```

## 5. Data Flow Architecture

### 5.1 Real-time Data Pipeline

```mermaid
graph LR
    A[Game Events] --> B[Event Stream<br/>Kafka]
    B --> C[Stream Processor<br/>Flink]
    C --> D[Real-time Analytics<br/>Redis]
    C --> E[Data Lake<br/>S3]
    C --> F[Time Series DB<br/>TimescaleDB]
    
    D --> G[Live Dashboard]
    E --> H[Batch Analytics<br/>Spark]
    F --> I[Historical Reports]
```

### 5.2 Event Sourcing Pattern

```python
# Event store schema
class GameEvent:
    event_id: UUID
    session_id: UUID
    player_id: UUID
    event_type: str  # game_started, question_shown, answer_submitted, etc.
    event_data: dict
    timestamp: datetime
    
# Event handlers
event_handlers = {
    'game_started': handle_game_started,
    'player_joined': handle_player_joined,
    'question_shown': handle_question_shown,
    'answer_submitted': handle_answer_submitted,
    'round_completed': handle_round_completed,
    'game_ended': handle_game_ended
}

# Event processing
async def process_event(event: GameEvent):
    # Store event
    await event_store.append(event)
    
    # Update projections
    handler = event_handlers.get(event.event_type)
    if handler:
        await handler(event)
    
    # Publish to subscribers
    await event_bus.publish(event)
```

## 6. Data Access Patterns

### 6.1 Repository Pattern Implementation

```typescript
// Base repository interface
interface IRepository<T> {
  findById(id: string): Promise<T | null>
  findAll(filter?: Partial<T>): Promise<T[]>
  create(entity: Omit<T, 'id'>): Promise<T>
  update(id: string, entity: Partial<T>): Promise<T>
  delete(id: string): Promise<boolean>
}

// User repository with caching
class UserRepository implements IRepository<User> {
  constructor(
    private db: Database,
    private cache: RedisClient
  ) {}
  
  async findById(id: string): Promise<User | null> {
    // Check cache first
    const cached = await this.cache.get(`user:${id}`)
    if (cached) {
      return JSON.parse(cached)
    }
    
    // Query database
    const user = await this.db.query(
      'SELECT * FROM users WHERE id = $1',
      [id]
    )
    
    if (user) {
      // Cache for 30 minutes
      await this.cache.setex(
        `user:${id}`,
        1800,
        JSON.stringify(user)
      )
    }
    
    return user
  }
  
  async updateProfile(id: string, profile: UserProfile): Promise<User> {
    const user = await this.db.transaction(async (trx) => {
      // Update user
      const updated = await trx.query(
        `UPDATE users 
         SET display_name = $2, bio = $3, updated_at = NOW()
         WHERE id = $1
         RETURNING *`,
        [id, profile.displayName, profile.bio]
      )
      
      // Log the change
      await trx.query(
        `INSERT INTO user_audit_log (user_id, action, changes)
         VALUES ($1, 'profile_update', $2)`,
        [id, JSON.stringify(profile)]
      )
      
      return updated
    })
    
    // Invalidate cache
    await this.cache.del(`user:${id}`)
    
    return user
  }
}
```

### 6.2 Query Optimization Patterns

```sql
-- Materialized view for leaderboards
CREATE MATERIALIZED VIEW leaderboard_daily AS
SELECT 
    u.id as user_id,
    u.username,
    u.display_name,
    u.avatar_url,
    COUNT(DISTINCT gs.id) as games_played,
    SUM(gp.final_score) as total_score,
    AVG(gp.final_score) as avg_score,
    MAX(gp.final_score) as best_score,
    DATE(gs.ended_at) as game_date
FROM users u
JOIN game_players gp ON u.id = gp.user_id
JOIN game_sessions gs ON gp.session_id = gs.id
WHERE gs.status = 'completed'
    AND gs.ended_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY u.id, DATE(gs.ended_at);

-- Refresh strategy
CREATE OR REPLACE FUNCTION refresh_leaderboard()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY leaderboard_daily;
END;
$$ LANGUAGE plpgsql;

-- Schedule refresh every hour
SELECT cron.schedule(
    'refresh-leaderboard',
    '0 * * * *',
    'SELECT refresh_leaderboard()'
);
```

## 7. Data Security Architecture

### 7.1 Encryption Strategy

```python
# Field-level encryption for sensitive data
class EncryptedField:
    def __init__(self, kms_key_id: str):
        self.kms_key_id = kms_key_id
        self.kms_client = boto3.client('kms')
        
    def encrypt(self, plaintext: str) -> str:
        response = self.kms_client.encrypt(
            KeyId=self.kms_key_id,
            Plaintext=plaintext.encode()
        )
        return base64.b64encode(response['CiphertextBlob']).decode()
        
    def decrypt(self, ciphertext: str) -> str:
        response = self.kms_client.decrypt(
            CiphertextBlob=base64.b64decode(ciphertext)
        )
        return response['Plaintext'].decode()

# Usage in models
class UserModel:
    email = EncryptedField(kms_key_id='user-data-key')
    phone_number = EncryptedField(kms_key_id='user-data-key')
    
    # Regular fields
    username = StringField()
    created_at = DateTimeField()
```

### 7.2 Data Access Control

```sql
-- Row-level security policies
ALTER TABLE game_sessions ENABLE ROW LEVEL SECURITY;

-- Players can only see games they're in
CREATE POLICY game_access_policy ON game_sessions
    FOR SELECT
    USING (
        host_id = current_user_id()
        OR EXISTS (
            SELECT 1 FROM game_players
            WHERE session_id = game_sessions.id
            AND user_id = current_user_id()
        )
    );

-- Users can only update their own profiles
CREATE POLICY user_update_policy ON users
    FOR UPDATE
    USING (id = current_user_id())
    WITH CHECK (id = current_user_id());
```

## 8. Data Migration Strategy

### 8.1 Schema Versioning

```sql
-- Migration tracking table
CREATE TABLE schema_migrations (
    version VARCHAR(20) PRIMARY KEY,
    description TEXT,
    applied_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Example migration
-- V1.2.0__add_user_achievements.sql
BEGIN;

CREATE TABLE achievements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    icon_url VARCHAR(500),
    points INTEGER NOT NULL DEFAULT 10,
    category VARCHAR(50),
    criteria JSONB NOT NULL
);

CREATE TABLE user_achievements (
    user_id UUID REFERENCES users(id),
    achievement_id UUID REFERENCES achievements(id),
    earned_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    progress JSONB DEFAULT '{}'::jsonb,
    PRIMARY KEY (user_id, achievement_id)
);

INSERT INTO schema_migrations (version, description)
VALUES ('V1.2.0', 'Add achievements system');

COMMIT;
```

### 8.2 Zero-Downtime Migration Patterns

```python
# Blue-green migration for critical changes
class BlueGreenMigration:
    def __init__(self, source_db, target_db):
        self.source = source_db
        self.target = target_db
        self.replicator = DataReplicator()
        
    async def execute(self):
        # Phase 1: Setup replication
        await self.replicator.start(self.source, self.target)
        
        # Phase 2: Apply schema changes to target
        await self.apply_schema_changes()
        
        # Phase 3: Sync data
        await self.sync_data()
        
        # Phase 4: Verify data integrity
        if not await self.verify_integrity():
            raise MigrationError("Data integrity check failed")
            
        # Phase 5: Switch traffic
        await self.switch_traffic()
        
        # Phase 6: Cleanup
        await self.cleanup_old_schema()
```

## 9. Data Analytics Architecture

### 9.1 Analytics Data Warehouse

```sql
-- Star schema for analytics
-- Fact table: game_plays
CREATE TABLE fact_game_plays (
    play_id UUID PRIMARY KEY,
    
    -- Dimensions
    user_id UUID NOT NULL,
    session_id UUID NOT NULL,
    date_id INTEGER NOT NULL,
    time_id INTEGER NOT NULL,
    
    -- Metrics
    score INTEGER NOT NULL,
    questions_answered INTEGER NOT NULL,
    correct_answers INTEGER NOT NULL,
    avg_response_time_ms INTEGER,
    power_ups_used INTEGER DEFAULT 0,
    
    -- Foreign keys
    FOREIGN KEY (user_id) REFERENCES dim_users(user_id),
    FOREIGN KEY (session_id) REFERENCES dim_sessions(session_id),
    FOREIGN KEY (date_id) REFERENCES dim_date(date_id),
    FOREIGN KEY (time_id) REFERENCES dim_time(time_id)
);

-- Dimension: users
CREATE TABLE dim_users (
    user_id UUID PRIMARY KEY,
    username VARCHAR(50),
    account_type VARCHAR(20),
    registration_date DATE,
    country VARCHAR(2),
    age_group VARCHAR(20),
    is_active BOOLEAN
);

-- Dimension: date
CREATE TABLE dim_date (
    date_id INTEGER PRIMARY KEY,
    full_date DATE NOT NULL,
    year INTEGER,
    quarter INTEGER,
    month INTEGER,
    week INTEGER,
    day_of_week INTEGER,
    is_weekend BOOLEAN,
    is_holiday BOOLEAN
);
```

### 9.2 Real-time Analytics Pipeline

```python
# Streaming analytics with Apache Flink
class GameAnalyticsJob:
    def __init__(self):
        self.env = StreamExecutionEnvironment.get_execution_environment()
        
    def process_game_events(self):
        # Source: Kafka game events
        game_events = self.env.add_source(
            FlinkKafkaConsumer(
                'game-events',
                JsonDeserializationSchema(),
                kafka_properties
            )
        )
        
        # Calculate real-time metrics
        metrics = game_events \
            .key_by(lambda x: x['session_id']) \
            .window(TumblingEventTimeWindows.of(Time.minutes(5))) \
            .aggregate(
                GameMetricsAggregator(),
                GameMetricsWindowFunction()
            )
        
        # Sink to multiple destinations
        metrics.add_sink(
            ElasticsearchSink(es_config)  # For dashboards
        )
        
        metrics.add_sink(
            JDBCSink(
                "INSERT INTO realtime_metrics VALUES (?, ?, ?, ?)",
                postgres_config  # For persistence
            )
        )
        
        self.env.execute("Game Analytics Pipeline")
```

## 10. Data Governance

### 10.1 Data Retention Policies

```python
# Automated data retention
class DataRetentionManager:
    policies = {
        'game_sessions': {
            'active': timedelta(days=7),
            'archived': timedelta(days=90),
            'deleted': timedelta(days=365)
        },
        'user_activity': {
            'detailed': timedelta(days=30),
            'aggregated': timedelta(days=365),
            'deleted': timedelta(days=730)
        },
        'chat_messages': {
            'active': timedelta(days=30),
            'deleted': timedelta(days=90)
        }
    }
    
    async def apply_retention_policies(self):
        for table, policy in self.policies.items():
            # Move to archive
            if 'archived' in policy:
                await self.archive_old_data(
                    table,
                    policy['active'],
                    policy['archived']
                )
            
            # Delete expired data
            await self.delete_expired_data(
                table,
                policy['deleted']
            )
            
            # Create audit log
            await self.log_retention_action(table)
```

### 10.2 Data Quality Monitoring

```sql
-- Data quality checks
CREATE TABLE data_quality_rules (
    id UUID PRIMARY KEY,
    table_name VARCHAR(100) NOT NULL,
    column_name VARCHAR(100),
    rule_type VARCHAR(50) NOT NULL,
    rule_definition JSONB NOT NULL,
    severity VARCHAR(20) DEFAULT 'warning',
    is_active BOOLEAN DEFAULT true
);

-- Example rules
INSERT INTO data_quality_rules (table_name, column_name, rule_type, rule_definition) VALUES
('users', 'email', 'format', '{"pattern": "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"}'),
('game_sessions', 'started_at', 'consistency', '{"check": "started_at <= ended_at"}'),
('questions', 'difficulty', 'values', '{"allowed": ["easy", "medium", "hard", "expert"]}');

-- Quality check function
CREATE OR REPLACE FUNCTION check_data_quality()
RETURNS TABLE(
    table_name VARCHAR,
    issue_count INTEGER,
    details JSONB
) AS $$
BEGIN
    -- Run all active rules
    RETURN QUERY
    SELECT 
        r.table_name,
        COUNT(*) as issue_count,
        jsonb_agg(
            jsonb_build_object(
                'column', r.column_name,
                'rule', r.rule_type,
                'violations', violations
            )
        ) as details
    FROM data_quality_rules r
    CROSS JOIN LATERAL (
        SELECT COUNT(*) as violations
        FROM execute_quality_check(r)
    ) AS violations
    WHERE r.is_active
    GROUP BY r.table_name;
END;
$$ LANGUAGE plpgsql;
```

This data architecture provides a comprehensive foundation for managing all data aspects of the trivia game application, from storage and processing to security and governance."""

        # Save the document
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"data_architecture_{timestamp}.md"
        filepath = os.path.join(self.output_dir, "architecture", filename)
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w') as f:
            f.write(data_doc)
            
        return {
            'type': 'Data Architecture',
            'name': filename,
            'path': filepath,
            'preview': data_doc[:500] + '...'
        }

    # Continue with other architecture generation methods...
    # _generate_api_architecture, _generate_integration_architecture, etc.
    # Plus the existing security-focused methods

    def _get_next_steps(self, outputs: List[Dict], pr_info: Dict = None) -> List[str]:
        """Generate next steps based on the architecture documents created"""
        next_steps = []
        
        # Add PR-related steps if PR was created
        if pr_info and pr_info.get('status') == 'success':
            next_steps.extend([
                f"📋 Pull Request created: {pr_info.get('pr_url', 'N/A')}",
                f"👥 Reviewers assigned: {', '.join(pr_info.get('reviewers', []))}",
                "⏳ Awaiting architecture review",
                "🔄 Address review feedback when received",
                "✅ Merge after all approvals"
            ])
        
        # Add document-specific next steps
        for output in outputs:
            doc_type = output.get('type', '')
            
            if 'System Architecture' in doc_type:
                next_steps.extend([
                    "🏗️ Review with technical leads for alignment",
                    "📊 Create implementation roadmap",
                    "🎯 Define component boundaries"
                ])
            elif 'Component Architecture' in doc_type:
                next_steps.extend([
                    "🔧 Define detailed interfaces",
                    "📝 Create component implementation tickets",
                    "🧪 Design integration test scenarios"
                ])
            elif 'Data Architecture' in doc_type:
                next_steps.extend([
                    "💾 Review with DBA team",
                    "📊 Plan migration strategies",
                    "🔒 Validate security measures"
                ])
            elif 'Security Architecture' in doc_type:
                next_steps.extend([
                    "🛡️ Security review with InfoSec team",
                    "📋 Create security implementation checklist",
                    "🔍 Plan penetration testing"
                ])
        
        # Add general architectural next steps
        next_steps.extend([
            "📚 Update project documentation",
            "👥 Share with development team",
            "📅 Schedule architecture review meeting",
            "🎯 Create implementation work items"
        ])
        
        return list(dict.fromkeys(next_steps))  # Remove duplicates while preserving order