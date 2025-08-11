# Trivia Game Full Specification

This specification document provides complete technical details for implementing the Trivia Game application with exact reproduction of functionality, behavior, and user experience. No code is included - only precise specifications.

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Architecture Specification](#2-architecture-specification)
3. [User Interface Specification](#3-user-interface-specification)
4. [Business Logic Specification](#4-business-logic-specification)
5. [Data Model Specification](#5-data-model-specification)
6. [API Integration Specification](#6-api-integration-specification)
7. [Middleware Server Specification](#7-middleware-server-specification)
8. [Question Generation Specification](#8-question-generation-specification)
9. [Verification System Specification](#9-verification-system-specification)
10. [Storage and Persistence Specification](#10-storage-and-persistence-specification)
11. [Error Handling Specification](#11-error-handling-specification)
12. [Performance Specification](#12-performance-specification)
13. [Security Specification](#13-security-specification)
14. [Testing Specification](#14-testing-specification)
15. [Deployment Specification](#15-deployment-specification)
16. [Version Management Specification](#16-version-management-specification)
17. [Website Specification](#17-website-specification)
18. [UI Design Resources Specification](#18-ui-design-resources-specification)

--- 
## 1. System Overview

### 1.1 Application Identity
- **Name**: Trivia By Grok
- **Package Identifier**: org.brumbiesoft.triviabyclaude
- **Current Version**: 3.0.0 (Build 51)
- **Platform Support**: Android (API 29+) and iOS (14.0+)

### 1.2 Core Functionality
The application generates AI-powered trivia quizzes on any user-specified topic using the Grok AI model (grok-3-mini). Questions are generated in batches, optionally verified for accuracy, enhanced with relevant images, and presented in an interactive quiz format.

### 1.3 Key Differentiators
- Single batch question generation (not progressive loading)
- Optional fact verification via web search
- Automatic image integration for visual questions
- Comprehensive feedback system
- Complete offline history viewing
- No user registration required

---

## 2. Architecture Specification

### 2.1 Client Architecture Pattern
**Pattern**: Model-View-ViewModel (MVVM) with Repository Pattern

**Layer Responsibilities**:
- **Presentation Layer**: UI components and ViewModels
- **Domain Layer**: Business logic and use cases
- **Data Layer**: Repositories, network services, and local storage

### 2.2 Component Communication
- ViewModels communicate with UI via observable state
- ViewModels access data through Repository interfaces
- Repositories coordinate between network and storage layers
- All asynchronous operations use platform-specific patterns (Coroutines for Android, Combine/async-await for iOS)

### 2.3 Dependency Flow
- UI depends on ViewModels
- ViewModels depend on Repositories
- Repositories depend on Services and Storage
- No circular dependencies allowed
- Dependency injection preferred for testability

### 2.4 State Management
- Each screen has dedicated ViewModel with observable state
- State updates trigger UI recomposition
- Navigation state managed separately from screen state
- Persistent state stored in platform-specific storage

---

## 3. User Interface Specification

### 3.1 Screen Navigation Flow
1. **Main Setup Screen** → Quiz Generation → **Quiz Screen** → Quiz Complete → **Results Screen**
2. From Results: → **Summary Screen** | **History Screen** | Play Again | Main Setup
3. From Main Setup: → **History Screen** → History Item → **Summary Screen**
4. From Quiz Screen: → **Feedback Dialog** → Submit → Return to Quiz
5. From Main Setup: → **App Info Screen** → **Release Notes Screen**

### 3.2 Main Setup Screen

**Layout Structure**:
- Vertical layout with centered content
- Maximum width: 600dp/points
- Padding: 16dp/points on all sides

**Components** (top to bottom):
1. **App Logo/Title**
   - Text: "Trivia By Grok"
   - Font: System default, bold, 24sp/points
   - Color: Primary theme color
   - Margin bottom: 32dp/points

2. **Topic Input Field**
   - Label: "Enter a topic"
   - Placeholder: "e.g., Ancient History, Space, Movies"
   - Maximum length: 100 characters
   - Border: 1dp/point, rounded corners (8dp/points radius)
   - Height: 56dp/points
   - Clear button when text present

3. **Number of Questions Selector**
   - Label: "Number of questions"
   - Input type: Numeric stepper or dropdown
   - Range: 1-20
   - Default: 10
   - Increment/decrement buttons: 44x44dp/points minimum

4. **Difficulty Selector**
   - Label: "Select difficulty"
   - Type: Segmented control or dropdown
   - Options in order:
     - Novice (Elementary School Level)
     - Apprentice (High School Senior Level)
     - Journeyman (Undergraduate Level)
     - Expert (Post-Graduate Level)
     - Master (Professor Level)
   - Default: Novice
   - Each option: minimum 44dp/points height

5. **Start Quiz Button**
   - Text: "Start Quiz"
   - Style: Primary filled button
   - Width: Full width of content area
   - Height: 56dp/points
   - Disabled state: When topic empty
   - Loading state: Shows spinner and "Generating Questions..."

6. **Bottom Navigation**
   - Quiz History button (left aligned)
   - App Info button (right aligned)
   - Height: 48dp/points
   - Icon size: 24x24dp/points

**Validation Behavior**:
- Topic validation on input: Remove leading/trailing spaces
- Show error below field for invalid input
- Age verification dialog for adult content topics
- Network check before generation starts

### 3.3 Quiz Generation Loading

**During Generation**:
- Overlay prevents interaction
- Centered loading indicator
- Status text updates:
  - "Generating questions..." (0-3 seconds)
  - "Creating quiz on [topic]..." (3-10 seconds)
  - "Almost ready..." (10+ seconds)
- Show elapsed time counter
- Cancel button available after 5 seconds

### 3.4 Quiz Screen

**Layout Structure**:
- Full screen with safe area insets
- Maximum content width: 800dp/points on tablets

**Header Section** (always visible):
- Question counter: "Question X of Y" (left aligned)
- Current score: "Score: X/Y" (right aligned)
- Difficulty indicator below counters
- Progress bar showing completion (4dp/points height)

**Question Display Area**:
- Question text:
  - Font: System default, 18sp/points
  - Line height: 1.5x font size
  - Padding: 16dp/points
  - Maximum 10 lines before scrolling

**Image Display** (for visual questions):
- Aspect ratio: Maintain original up to 16:9
- Maximum height: 40% of screen height
- Loading placeholder with spinner
- Error state: Generic image icon
- Rounded corners: 8dp/points
- Margin: 16dp/points

**Answer Options Area**:
- Four option cards in 2x2 grid on tablets, vertical list on phones
- Each option card:
  - Minimum height: 80dp/points
  - Padding: 16dp/points
  - Border: 2dp/points, rounded 8dp/points
  - Tap target: Entire card
  - Disabled after selection

**Answer States**:
- Unselected: Light background, dark text
- Selected Correct: Green background, white text, checkmark icon
- Selected Wrong: Red background, white text, X icon
- Correct (not selected): Green border, green text

**Post-Answer Display**:
- Explanation box appears below options
- Background: Light accent color
- Padding: 16dp/points
- Icon: Info symbol
- Auto-scroll to show explanation

**Navigation**:
- Next Question button (appears after answer)
- Report Issue button (always visible, bottom right)
- No back navigation during quiz

### 3.5 Results Screen

**Content Layout**:
1. **Result Circle**
   - Size: 200x200dp/points
   - Shows score as "X/Y"
   - Percentage below in smaller text
   - Animated fill based on percentage
   - Colors: Green (>70%), Orange (50-70%), Red (<50%)

2. **Performance Message**
   - Font: Bold, 20sp/points
   - Margin: 24dp/points
   - Text based on percentage:
     - 90-100%: "Excellent!"
     - 80-89%: "Great job!"
     - 70-79%: "Good work!"
     - 60-69%: "Keep trying!"
     - Below 60%: "Practice more!"

3. **Quiz Details**
   - Topic name
   - Difficulty level
   - Time taken (if implemented)
   - Question count

4. **Action Buttons** (vertical stack):
   - "Try Easier Difficulty" (if not Novice)
   - "Retry Same Difficulty"
   - "Try Harder Difficulty" (if not Master)
   - "View Detailed Summary"
   - "Enter Custom Settings"
   - "Quiz History"
   - Each button: full width, 48dp/points height

### 3.6 Summary Screen

**Layout**: Scrollable list of all questions

**Summary Header**:
- Quiz topic and difficulty
- Final score
- Date and time
- Share button (if implemented)

**Each Question Item**:
- Question number and text
- Image thumbnail (if visual question)
- User's answer with icon (✓ or ✗)
- Correct answer (if different)
- Explanation (expandable)
- Visual indicator: Green for correct, red for incorrect

### 3.7 History Screen

**Header Section**:
- Title: "Quiz History"
- Statistics card:
  - Total quizzes completed
  - Average score percentage
  - Favorite topic (most played)
- Clear All button

**History List**:
- Each item shows:
  - Topic name (bold)
  - Score and percentage
  - Difficulty level
  - Date and time
  - Delete swipe action (platform specific)
- Sorted by date descending
- Load more pagination after 50 items

### 3.8 Feedback Dialog

**Modal Layout**:
- Title: "Report an Issue"
- Current question displayed (read-only)
- Issue type selector:
  - Incorrect answer marked as correct
  - Poorly worded question
  - Multiple correct answers
  - Correct answer not in options
  - Image doesn't match question
  - Technical issue
  - Other
- Description field (optional, multiline)
- Cancel and Submit buttons

### 3.9 App Info Screen

**Content Sections**:
1. App icon and name
2. Version: "3.0.0 (Build 51)"
3. Description text
4. Links:
   - Release Notes
   - Privacy Policy (if applicable)
   - Terms of Service (if applicable)
5. Developer info
6. Third-party licenses

### 3.10 Visual Design Specifications

**Color Scheme**:
- Primary: Platform default accent
- Success: Green (#4CAF50 or system green)
- Error: Red (#F44336 or system red)
- Warning: Orange (#FF9800 or system orange)
- Background: System background
- Surface: System surface
- Text: System label colors

**Typography**:
- Use system fonts throughout
- Sizes: 14sp/points (body), 16sp/points (subtitle), 18sp/points (title), 24sp/points (large title)
- Line height: 1.5x for body text
- Letter spacing: Platform defaults

**Animations**:
- Screen transitions: Platform standard (300ms)
- Score circle fill: 1000ms ease-out
- Answer reveal: 200ms fade
- Loading spinner: Continuous rotation
- Card selection: Scale 0.95 on press

**Accessibility**:
- All text contrast ratio ≥ 4.5:1
- Touch targets ≥ 44x44dp/points
- Screen reader labels for all controls
- Focus indicators for keyboard navigation
- Motion reduction support

---

## 4. Business Logic Specification

### 4.1 Topic Validation Logic

**Validation Rules**:
1. Trim whitespace from input
2. Check length: 1-100 characters
3. Check for empty or whitespace-only
4. Check against blocked terms list
5. Check for potential prompt injection patterns
6. Classify as adult content if matches patterns

**Adult Content Detection**:
Trigger age verification for topics containing:
- Explicit content keywords
- Violence-related terms
- Substance-related terms
- Gambling-related terms

**Invalid Topic Handling**:
- Show specific error message
- Suggest alternative phrasing
- Log validation failure reason

### 4.2 Question Generation Logic

**Generation Process**:
1. Calculate total questions needed: requested + 15 buffer
2. Construct AI prompt with topic, difficulty, count
3. Send single request to Grok AI via middleware
4. Parse response into question objects
5. Validate each question structure
6. Filter invalid questions
7. Apply answer validation rules
8. Optionally verify facts
9. Shuffle answer options
10. Take requested number of valid questions
11. Handle insufficient questions

**Question Validation Rules**:
1. Must have all required fields
2. Question text 10-500 characters
3. Exactly 4 answer options
4. Each option 1-200 characters
5. Correct answer must exist in options
6. Explanation 20-1000 characters
7. No duplicate options
8. No obvious patterns (A,B,C,D or 1,2,3,4)

**Answer Validation Logic**:
- Check if question contains quoted text
- If quoted text equals correct answer exactly, reject
- If quoted text is partial or different, accept
- Check for answer keywords in question
- Reject if answer appears verbatim in question

### 4.3 Quiz Flow Logic

**State Management**:
- Track current question index (0-based)
- Track user answers array
- Track score counter
- Track question display state
- Prevent navigation during answer animation

**Answer Selection Logic**:
1. Disable all option buttons
2. Mark selected option
3. Reveal correct answer
4. Update score if correct
5. Show explanation
6. Enable next navigation
7. Log answer for analytics

**Progress Tracking**:
- Update progress bar: (currentIndex + 1) / totalQuestions
- Update question counter display
- Check for quiz completion
- Transition to results when done

### 4.4 Scoring Logic

**Score Calculation**:
- One point per correct answer
- No partial credit
- No time bonus (currently)
- No difficulty multiplier
- Percentage: (correct / total) * 100
- Round percentage to whole number

**Performance Classification**:
- Calculate percentage score
- Map to performance tier
- Select appropriate message
- Determine available next actions
- Store result for history

### 4.5 History Management Logic

**Storage Rules**:
- Generate unique ID per quiz
- Store immediately on completion
- Keep unlimited history (no auto-cleanup)
- Maintain chronological order
- Update statistics on each addition

**Deletion Logic**:
- Single item: Remove from storage, recalculate stats
- Clear all: Confirmation required, reset statistics
- Cascade delete: Remove associated summaries

**Statistics Calculation**:
- Total quizzes: Count of all items
- Average score: Sum of percentages / count
- Update on every change
- Cache for performance

### 4.6 Feedback Processing Logic

**Feedback Creation**:
1. Capture current question data
2. Include user's answer
3. Add issue type and description
4. Collect device metadata
5. Generate timestamp
6. Create unique feedback ID
7. Store locally first
8. Queue for server sync

**Sync Logic**:
- Check network availability
- Batch upload all pending feedback
- On success: Delete local copies
- On failure: Retry with exponential backoff
- Maximum 5 retry attempts
- Persist across app restarts

### 4.7 Image Integration Logic

**Image Decision Logic**:
Add images for questions about:
- Geography and landmarks
- Animals and nature
- Space and celestial objects
- Vehicles and transportation
- Architecture and buildings
- Art and paintings
- Food and cuisine
- Scientific equipment
- Sports and athletes
- Flags and symbols

**Image Search Process**:
1. Extract key terms from question
2. Remove common words
3. Prioritize nouns and proper nouns
4. Construct search query
5. Request via Pexels API
6. Select first medium-quality result
7. Validate image URL
8. Mark question as visual

**Copyright Protection**:
- Never add images for entertainment content
- Skip images for people (unless historical)
- Avoid branded products
- Use generic terms for search

### 4.8 Difficulty Scaling Logic

**Difficulty Characteristics**:

**Novice** (Elementary School Level):
- Basic facts and concepts
- Common knowledge
- Simple vocabulary
- Obvious distractors

**Apprentice** (High School Senior Level):
- Detailed knowledge required
- Some analysis needed
- Academic vocabulary
- Plausible distractors

**Journeyman** (Undergraduate Level):
- Specialized knowledge
- Critical thinking required
- Technical terms
- Subtle differences in options

**Expert** (Post-Graduate Level):
- Deep expertise needed
- Complex relationships
- Professional terminology
- Very similar options

**Master** (Professor Level):
- Cutting-edge knowledge
- Nuanced understanding
- Research-level content
- Expertly crafted distractors

---

## 6. API Integration Specification

### 6.1 Middleware Communication

**Base Configuration**:
- Protocol: HTTPS only
- Base URL: https://triviaapp-api.brumbiesoft.org
- Content-Type: application/json
- Timeout: 450 seconds for generation, 30 seconds for others
- Retry strategy: Exponential backoff with 5 attempts
- Authentication: Bearer token in Authorization header

**Request Headers**:
- Authorization: Bearer [API_SECRET_KEY]
- Content-Type: application/json
- Accept: application/json
- User-Agent: TriviaApp/[version] ([platform]/[os_version])

### 6.2 Question Generation Endpoint

**Endpoint**: POST /api/claude

**Request Structure**:
- topic: String (required)
- count: Integer (required, 1-35)
- difficulty: String (required, exact match to difficulty levels)

**Response Structure**:
Array of:
- question: String
- options: Array of 4 Strings
- correctAnswer: String
- explanation: String
- imageUrl: String or null
- isVisual: Boolean

**Error Responses**:
- 400: Invalid request parameters
- 401: Invalid or missing authentication
- 408: Request timeout
- 429: Rate limit exceeded
- 500: Server error
- 503: Service unavailable

**Parsing Rules**:
- Validate array structure
- Ensure all required fields present
- Handle null/missing imageUrl
- Validate options array length
- Verify correctAnswer exists in options

### 6.3 Image Search Endpoint

**Endpoint**: POST /api/pexels/search

**Request Structure**:
- query: String (required)
- per_page: Integer (optional, default 1)

**Response Structure**:
- photos: Array of photo objects
  - id: Integer
  - src: Object
    - medium: String (URL)

**Image URL Validation**:
- Must be HTTPS
- Must be valid URL format
- Must be accessible (platform allows hotlinking)
- Store URL, not image data

### 6.4 Fact Verification Endpoint

**Endpoint**: POST /api/search/verify

**Request Structure**:
- query: String (constructed from question)
- includeAiOverview: Boolean (false)
- numResults: Integer (3)

**Response Structure**:
- aiOverviewAnswer: String or null
- searchResults: Array of:
  - title: String
  - snippet: String
  - url: String
  - extractedAnswer: String or null
- consensus: Boolean
- consensusAnswer: String or null
- confidence: Float (0-1)

**Verification Logic**:
- Currently disabled by default
- When enabled:
  - Require 2+ sources agreeing
  - Normalize answers for comparison
  - Accept on empty results if configured
  - 500ms delay between verifications

### 6.5 Feedback Endpoints

**Submit Feedback**: POST /api/feedback

**Request Structure**:
- questionData: Question object
- feedbackType: String
- description: String or null
- deviceInfo: DeviceInfo object
- appVersion: String

**Response**: 201 Created with feedback ID

**Fetch Feedback**: GET /api/feedback

**Response**: Array of feedback items with server IDs

**Delete Feedback**: DELETE /api/feedback/:id

**Response**: 204 No Content

**Batch Operations**:
- Upload all pending feedback in single request
- Delete successfully synced items
- Handle partial success

### 6.6 Health Check

**Endpoint**: GET /api/health

**No Authentication Required**

**Response Structure**:
- status: String ("healthy")
- version: String
- timestamp: String
- database: String ("connected" or "disconnected")

**Usage**:
- Check before making requests
- Show server status in UI if down
- Cache result for 60 seconds

### 6.7 Network Error Handling

**Retry Strategy**:
1. Initial delay: 1 second
2. Exponential backoff: 1s, 2s, 4s, 8s, 16s
3. Maximum 5 attempts
4. Only retry on:
   - Network timeouts
   - 503 Service Unavailable
   - 502 Bad Gateway
   - Connection errors

**User Feedback**:
- Show loading indicator immediately
- Update message after 10 seconds
- Show retry option after 30 seconds
- Display specific error messages
- Suggest offline mode for history

---

## 7. Middleware Server Specification

### 7.1 Server Architecture

**Technology Stack**:
- Runtime: Node.js 18+
- Framework: Express.js
- Database: PostgreSQL 13+
- Process Manager: PM2
- Reverse Proxy: Nginx
- SSL: Let's Encrypt certificates

**Environment Configuration**:
- NODE_ENV: production
- PORT: 3000
- API_SECRET_KEY: 64-character hex string
- GROK_API_KEY: xAI API key
- PEXELS_API_KEY: Pexels API key
- DATABASE_URL: PostgreSQL connection string

### 7.2 Request Processing

**Middleware Pipeline**:
1. Request logging
2. CORS handling
3. Body parsing (JSON)
4. Authentication check
5. Rate limiting
6. Route handling
7. Error handling
8. Response logging

**Authentication Logic**:
- Extract Bearer token from Authorization header
- Compare with API_SECRET_KEY
- Return 401 if missing or invalid
- Skip for health endpoint

**Rate Limiting**:
- 100 requests per minute per IP
- 429 response when exceeded
- Reset counter every minute
- Exempt health check endpoint

### 7.3 External Service Integration

**Grok AI Integration**:
- Model: grok-3-mini
- Temperature: 0.7
- Max tokens: 4000
- System prompt: Detailed instructions for trivia generation
- Response format: JSON array
- Timeout: 450 seconds
- Parse and validate response

**Pexels Integration**:
- API endpoint: https://api.pexels.com/v1/search
- Authorization header with API key
- Default 1 result per search
- Select medium-sized images
- Cache results for 15 minutes
- Handle rate limits gracefully

**Wikipedia Integration**:
- Use REST API v1
- Search endpoint for summaries
- Extract relevant paragraphs
- Parse for answer verification
- Handle disambiguation pages
- 10-second timeout

### 7.4 Database Schema

**Feedback Table**:
- id: UUID primary key, auto-generated
- question_data: JSONB containing question object
- feedback_type: VARCHAR(50)
- description: TEXT nullable
- device_info: JSONB
- timestamp: TIMESTAMP WITH TIME ZONE
- processed: BOOLEAN default false
- app_version: VARCHAR(20)

**Indexes**:
- timestamp (for sorting)
- feedback_type (for filtering)
- processed (for cleanup)

**Connection Pool**:
- Minimum connections: 2
- Maximum connections: 10
- Connection timeout: 30 seconds
- Idle timeout: 10 minutes
- SSL required for production

### 7.5 Deployment Configuration

**PM2 Configuration**:
- Instances: 2 (cluster mode)
- Auto-restart on failure
- Log rotation daily
- Memory limit: 512MB per instance
- Environment variables from file

**Nginx Configuration**:
- HTTPS redirect from HTTP
- SSL certificate handling
- Proxy to localhost:3000
- WebSocket support
- Request/response timeouts: 600s
- Client max body size: 10MB

**Server Updates**:
- Zero-downtime deployment
- Git pull from repository
- NPM dependency installation
- Database migrations
- PM2 graceful reload
- Health check verification

---

## 8. Question Generation Specification

### 8.1 AI Prompt Construction

**System Prompt Components**:
1. Role definition as trivia expert
2. Output format specification (JSON)
3. Question quality requirements
4. Difficulty level descriptions
5. Visual question guidelines
6. Content safety rules

**User Prompt Template**:
"Generate [count] trivia questions about [topic] at [difficulty] difficulty level."

**Additional Instructions**:
- Ensure factual accuracy
- Avoid ambiguous questions
- Create plausible distractors
- Include detailed explanations
- Suggest visual questions where appropriate
- Vary question types

### 8.2 Question Types

**Supported Types**:
1. **Factual**: Direct knowledge questions
2. **Identification**: "Which of these..." format
3. **True/False** (converted to multiple choice)
4. **Numerical**: Dates, quantities, measurements
5. **Conceptual**: Understanding of ideas
6. **Visual**: Requires image for context

**Type Distribution**:
- Aim for variety within topic constraints
- At least 20% should be visual-friendly
- No more than 30% numerical
- Balance difficulty across types

### 8.3 Answer Generation Rules

**Correct Answer**:
- Must be unambiguously correct
- Appropriate length for option
- No trick wording
- Factually accurate
- Currently accurate (not outdated)

**Distractor Rules**:
- Plausible but clearly wrong
- Similar length to correct answer
- Same category/type as answer
- No joke or obviously wrong options
- Graduated difficulty in distractors

**Option Ordering**:
- Random shuffle after generation
- No patterns (ABCD, 1234)
- Equal distribution of correct positions
- Store original order for debugging

### 8.4 Explanation Requirements

**Content Requirements**:
- Explain why answer is correct
- Address why distractors are wrong
- Add interesting context
- Include relevant dates/numbers
- Cite sources if applicable

**Length Guidelines**:
- Minimum: 20 characters
- Target: 100-200 characters
- Maximum: 1000 characters
- Complete sentences required
- Educational tone

### 8.5 Topic-Specific Rules

**Geography**:
- Include map-based questions
- Current country names
- Verify disputed territories
- Add flag/landmark images

**Science**:
- Use accepted theories
- Include units of measurement
- Avoid cutting-edge research
- Add diagram images where helpful

**History**:
- Verify dates carefully
- Consider cultural perspectives
- Avoid controversial interpretations
- Include historical images

**Entertainment**:
- No copyrighted images
- Focus on facts, not opinions
- Verify release dates
- Avoid spoilers

**Sports**:
- Current team names
- Verify statistics
- Include action images
- Consider international sports

### 8.6 Difficulty Calibration

**Novice Calibration**:
- Common knowledge facts
- Simple vocabulary
- Recent or famous subjects
- Clear distinctions between options
- Shorter questions

**Master Calibration**:
- Specialized knowledge
- Technical terminology
- Subtle distinctions
- Historical depth
- Complex relationships

**Progressive Difficulty**:
- Each level approximately 20% harder
- Consistent within a quiz
- Appropriate to topic depth
- Consider user feedback

---

## 9. Verification System Specification

### 9.1 Verification Configuration

**System Settings**:
- verificationEnabled: Boolean (currently false)
- acceptOnEmptyResults: Boolean (true)
- requireConsensusCount: Integer (2)
- verificationTimeout: Integer (30 seconds)
- delayBetweenVerifications: Integer (500ms)

**When to Skip Verification**:
- System disabled
- Network unavailable
- Previous timeouts
- Rate limit reached
- Topic marked as unverifiable

### 9.2 Search Query Construction

**Query Building Rules**:
1. Remove question marks
2. Extract key nouns
3. Add current year for time-sensitive
4. Append "facts" keyword
5. Limit to 10 words
6. Remove filler words

**Query Optimization**:
- Prefer specific terms
- Include proper nouns
- Add context words
- Avoid pronouns
- Use question stem

### 9.3 Answer Extraction

**Extraction Process**:
1. Search web for query
2. Extract text from top 3 results
3. Find answer patterns
4. Normalize extracted text
5. Compare with options
6. Calculate confidence

**Normalization Rules**:
- Convert to lowercase
- Remove punctuation
- Trim whitespace
- Remove articles (a, an, the)
- Handle number formats
- Standardize units

### 9.4 Consensus Algorithm

**Consensus Calculation**:
1. Collect all extracted answers
2. Group by normalized form
3. Count occurrences
4. Find most common
5. Check against threshold
6. Verify matches expected

**Acceptance Criteria**:
- At least 2 sources agree
- OR majority if 3+ sources
- AND matches our answer
- OR marked as disputed
- Handle empty results

### 9.5 Confidence Scoring

**Confidence Factors**:
- Number of agreeing sources (40%)
- Source reliability (30%)
- Answer clarity (20%)
- Recent publication (10%)

**Score Thresholds**:
- High (>0.8): Strong consensus
- Medium (0.5-0.8): Likely correct
- Low (<0.5): Uncertain
- Zero: No verification possible

---

## 10. Storage and Persistence Specification

### 10.1 Local Storage Strategy

**Platform Storage Mechanisms**:
- Android: SharedPreferences with MODE_PRIVATE
- iOS: UserDefaults with standard suite
- Both: JSON serialization for complex objects
- Both: Synchronous writes for critical data

**Storage Keys and Limits**:
- Maximum 10MB total storage
- Individual key limit: 1MB
- Chunking for large data
- Compression for summaries
- Cleanup old data at 8MB

### 10.2 Data Serialization

**JSON Encoding Rules**:
- UTF-8 encoding
- Escape special characters
- Null handling: omit or empty string
- Date format: ISO 8601
- Float precision: 2 decimal places
- Pretty printing disabled

**Object Serialization**:
- All objects have toJSON method
- Consistent property ordering
- Enum values as strings
- Arrays preserve order
- Maps as objects

### 10.3 Data Migration

**Version Detection**:
- Store schema version
- Check on app launch
- Run migrations sequentially
- Backup before migration
- Rollback on failure

**Migration Strategies**:
- Add fields with defaults
- Transform data structures
- Merge duplicate entries
- Clean corrupted data
- Update statistics

### 10.4 Caching Strategy

**Cache Layers**:
1. Memory cache for active quiz
2. Disk cache for summaries
3. Network cache for images
4. API response cache

**Cache Invalidation**:
- Quiz completion clears active
- Summary cache: 7 days
- Image cache: 30 days
- API cache: 15 minutes
- Manual clear option

### 10.5 Backup and Recovery

**Automatic Backup**:
- Before major operations
- On app background
- Before clearing data
- Maximum 3 backups
- Rotate oldest

**Recovery Process**:
1. Detect corrupted data
2. Attempt repair
3. Offer restore option
4. Load from backup
5. Merge with current
6. Validate result

---

## 11. Error Handling Specification

### 11.1 Error Categories

**Network Errors**:
- No internet connection
- Timeout exceeded
- Server unreachable
- Invalid response
- Rate limit exceeded

**Validation Errors**:
- Invalid topic
- Invalid parameters
- Insufficient questions
- Corrupted data
- Schema mismatch

**System Errors**:
- Storage full
- Memory pressure
- Permission denied
- App killed
- Dependency failure

### 11.2 Error Recovery

**Automatic Recovery**:
- Network: Retry with backoff
- Storage: Clear cache
- Memory: Release resources
- Data: Load from backup
- State: Restore from saved

**User-Initiated Recovery**:
- Retry button
- Skip question
- Clear cache
- Reset app
- Contact support

### 11.3 Error Messaging

**Message Components**:
1. What went wrong
2. Why it happened
3. What to do next
4. Retry option
5. Alternative action

**Message Examples**:
- "Unable to generate questions. Check your internet connection and try again."
- "This topic couldn't be verified. Try a different topic or disable verification."
- "Storage full. Clear some quiz history to continue."

### 11.4 Error Logging

**Log Levels**:
- DEBUG: Detailed flow
- INFO: Normal operations
- WARN: Recoverable issues
- ERROR: Failures
- FATAL: Crashes

**Log Content**:
- Timestamp
- Error category
- Stack trace
- User action
- App state
- Device info

### 11.5 Graceful Degradation

**Offline Functionality**:
- View history
- View summaries
- Delete local data
- Access settings
- Show cached content

**Partial Functionality**:
- Generate without images
- Skip verification
- Reduce question count
- Use cached topics
- Simplify animations

---

## 12. Performance Specification

### 12.1 Performance Targets

**Response Times**:
- App launch: <3 seconds
- Screen transition: <300ms
- Button response: <100ms
- Question generation: <60 seconds
- Image loading: <2 seconds
- History loading: <500ms

**Resource Usage**:
- Memory: <200MB active
- Storage: <50MB app
- Network: <1MB per quiz
- Battery: <5% per hour
- CPU: <50% sustained

### 12.2 Optimization Strategies

**Memory Optimization**:
- Release unused screens
- Compress images
- Limit cache size
- Lazy load content
- Recycle views

**Network Optimization**:
- Batch requests
- Compress payloads
- Cache responses
- Preload images
- Cancel unused

**UI Optimization**:
- Minimize redraws
- Optimize layouts
- Async operations
- Hardware acceleration
- Efficient animations

### 12.3 Performance Monitoring

**Metrics to Track**:
- Generation time
- API latency
- Frame rate
- Memory usage
- Crash rate
- ANR/hang rate

**Performance Logging**:
- Sample 10% of users
- Log key operations
- Track percentiles
- Alert on regression
- Weekly reports

### 12.4 Scalability

**Load Handling**:
- Queue long operations
- Throttle requests
- Progressive loading
- Graceful degradation
- Resource pooling

**Growth Planning**:
- Database indexing
- API versioning
- Cache strategy
- CDN for images
- Horizontal scaling

---

## 13. Security Specification

### 13.1 Authentication Security

**API Key Management**:
- Never store in source code
- Use environment variables
- Rotate keys quarterly
- Different keys per environment
- Monitor usage

**Token Handling**:
- HTTPS only
- Bearer token format
- No token in URLs
- Secure storage
- Clear on logout

### 13.2 Data Security

**Sensitive Data**:
- No PII collected
- Anonymous usage
- Local storage only
- No cloud backup
- User control

**Encryption**:
- HTTPS for transit
- Platform encryption at rest
- No custom crypto
- Secure random
- Key management

### 13.3 Input Validation

**Validation Rules**:
- Length limits
- Character whitelist
- SQL injection prevention
- XSS prevention
- Path traversal prevention

**Sanitization**:
- HTML encoding
- URL validation
- File type checking
- Size limits
- Content scanning

### 13.4 Platform Security

**Android Security**:
- ProGuard obfuscation
- Certificate pinning
- Anti-tampering
- Secure storage
- Permission minimal

**iOS Security**:
- App Transport Security
- Keychain usage
- Code signing
- Entitlements
- Privacy manifest

### 13.5 Security Monitoring

**Threat Detection**:
- Unusual patterns
- Rate anomalies
- Failed auth
- Data exfiltration
- Privilege escalation

**Incident Response**:
- Automatic blocking
- Alert generation
- Log collection
- User notification
- Patch deployment

---

## 14. Testing Specification

### 14.1 Test Categories

**Unit Tests**:
- ViewModels: State management, business logic
- Repositories: Data operations
- Services: API communication
- Utilities: Helper functions
- Models: Serialization

**Integration Tests**:
- API integration
- Database operations
- Navigation flow
- State persistence
- Error scenarios

**UI Tests**:
- Complete quiz flow
- History management
- Feedback submission
- Settings changes
- Edge cases

### 14.2 Test Coverage Requirements

**Coverage Targets**:
- Overall: 70% minimum
- ViewModels: 90%
- Business logic: 85%
- UI components: 60%
- Utilities: 95%

**Critical Paths**:
- Question generation: 100%
- Answer validation: 100%
- Score calculation: 100%
- Data persistence: 95%
- Error handling: 90%

### 14.3 Test Data

**Mock Data Sets**:
- Valid questions (50 samples)
- Invalid questions (20 samples)
- Edge cases (30 samples)
- Different topics (10 each)
- All difficulties

**Test Scenarios**:
- Happy path
- Network failures
- Invalid inputs
- Concurrent operations
- State restoration
- Memory pressure

### 14.4 Performance Testing

**Load Tests**:
- 20 questions generation
- 100 history items
- Rapid navigation
- Image loading
- Background/foreground

**Stress Tests**:
- Low memory
- Slow network
- Large responses
- Rapid clicking
- Orientation changes

### 14.5 Test Automation

**CI/CD Pipeline**:
- Pre-commit hooks
- Unit tests on push
- Integration tests on PR
- UI tests on merge
- Performance tests weekly

**Test Reporting**:
- Coverage reports
- Failure analysis
- Performance trends
- Flaky test tracking
- Test duration

---

## 5. Data Model Specification

### 5.1 Core Data Structures

**Question Object**:
- question: String (10-500 characters)
- options: Array of 4 Strings (1-200 characters each)
- correctAnswer: String (must match one option exactly)
- explanation: String (20-1000 characters)
- imageUrl: String (optional, valid URL format)
- isVisual: Boolean (true if imageUrl present)
- questionId: String (optional, for deduplication)

**QuizConfiguration**:
- topic: String (1-100 characters)
- numberOfQuestions: Integer (1-20)
- difficulty: Enum (Novice|Apprentice|Journeyman|Expert|Master)
- timestamp: DateTime

**QuizResult**:
- configuration: QuizConfiguration
- questions: Array of Question
- userAnswers: Array of String
- score: Integer
- percentage: Float
- completedAt: DateTime
- quizId: String (UUID)

**QuizHistoryItem**:
- quizId: String (UUID)
- topic: String
- difficulty: String
- score: Integer
- totalQuestions: Integer
- percentage: Float
- completedAt: DateTime

**QuizSummary**:
- quizId: String (references QuizHistoryItem)
- questions: Array of Question
- userAnswers: Array of String
- configuration: QuizConfiguration

**FeedbackItem**:
- feedbackId: String (UUID)
- questionData: Question
- userAnswer: String
- feedbackType: Enum (INCORRECT_ANSWER|POORLY_WORDED|MULTIPLE_CORRECT|ANSWER_NOT_IN_OPTIONS|IMAGE_MISMATCH|TECHNICAL_ISSUE|OTHER)
- description: String (optional, 0-500 characters)
- deviceInfo: DeviceInfo
- appVersion: String
- timestamp: DateTime
- syncStatus: Enum (PENDING|SYNCED|FAILED)

**DeviceInfo**:
- platform: String (Android|iOS)
- osVersion: String
- deviceModel: String
- screenSize: String
- locale: String

**AppStatistics**:
- totalQuizzes: Integer
- averageScore: Float
- lastUpdated: DateTime
- topicFrequency: Map<String, Integer>

### 5.2 Storage Schemas

**SharedPreferences/UserDefaults Keys**:
- quiz_history: JSON array of QuizHistoryItem
- quiz_summaries: JSON map of quizId to QuizSummary
- feedback_queue: JSON array of FeedbackItem
- app_statistics: JSON of AppStatistics
- question_usage_history: JSON map of topic to Set<questionId>
- user_preferences: JSON of preferences
- last_sync_attempt: DateTime
- api_config: JSON of configuration

**Data Persistence Rules**:
- All data stored as JSON strings
- Use platform-specific secure storage where available
- Implement migration for schema changes
- Validate data on read
- Handle corrupt data gracefully

---

## 15. Deployment Specification

### 15.1 Build Configuration

**Android Build Settings**:
- Minimum SDK: 29 (Android 10)
- Target SDK: 35
- Compile SDK: 35
- Build Tools: 35.0.0
- Gradle: 8.5
- Kotlin: 1.9.24
- ProGuard rules for release
- Signing configuration

**iOS Build Settings**:
- Minimum iOS: 14.0
- Swift Version: 5.0
- Xcode: 15.0+
- Bitcode: Disabled
- Architecture: arm64
- Code signing required

**Version Management**:
- Version name: MAJOR.MINOR.PATCH
- Version code: Sequential integer
- Build number: Auto-increment
- Git tag on release

### 15.2 Release Process

**Pre-Release Checklist**:
1. Run all tests
2. Update version numbers
3. Update release notes
4. Test on physical devices
5. Check crash reports
6. Verify API compatibility

**Build Steps**:
1. Clean build directory
2. Generate release build
3. Run ProGuard/R8
4. Sign with release key
5. Generate AAB/IPA
6. Verify package

**Distribution**:
- Android: Google Play Console
- iOS: App Store Connect
- Beta: Internal testing track
- Production: Phased rollout
- Monitor crash reports

### 15.3 Environment Configuration

**Development Environment**:
- API URL: https://triviaapp-api.brumbiesoft.org
- Debug logging enabled
- Strict mode enabled
- Mock data available
- Fast timeouts

**Production Environment**:
- API URL: https://triviaapp-api.brumbiesoft.org
- Debug logging disabled
- Crash reporting enabled
- Real data only
- Standard timeouts

**Configuration Management**:
- BuildConfig for Android
- Info.plist for iOS
- Environment variables
- Feature flags
- Remote config

### 15.4 Monitoring and Analytics

**Crash Reporting**:
- Automatic crash collection
- Stack trace symbolication
- User metrics
- Device information
- Custom logs

**Performance Monitoring**:
- App launch time
- Screen load time
- API response time
- Memory usage
- Battery impact

**Usage Analytics**:
- Quiz completions
- Topic popularity
- Difficulty distribution
- Error rates
- Feature usage

**Privacy Compliance**:
- No PII collection
- Anonymous identifiers
- Opt-out available
- Data retention policy
- GDPR compliance

### 15.5 Update Strategy

**Update Mechanisms**:
- Automatic updates (default)
- In-app update prompts
- Force update for critical
- Staged rollouts
- A/B testing support

**Backward Compatibility**:
- API version checking
- Data migration support
- Feature degradation
- Error messaging
- Rollback capability

---

## 16. Version Management Specification

### 16.1 Version History

**Current Version**: 3.0.0 (Build 51)
- Major change: Grok AI integration
- Single batch generation
- Performance improvements
- Bug fixes

**Version Numbering**:
- MAJOR: Breaking changes
- MINOR: New features
- PATCH: Bug fixes
- BUILD: Auto-increment

### 16.2 Release Notes Format

**Required Sections**:
1. What's New
2. Improvements
3. Bug Fixes
4. Known Issues

**Content Guidelines**:
- User-focused language
- Specific features
- No technical jargon
- Highlight benefits
- Thank users

### 16.3 Git Workflow

**Branch Strategy**:
- main: Production ready
- develop: Integration
- feature/*: New features
- bugfix/*: Bug fixes
- release/*: Release prep

**Commit Guidelines**:
- Descriptive messages
- Reference issues
- Atomic commits
- No code in messages
- Sign commits

**Release Tags**:
- Format: v3.0.0
- Annotated tags
- Release notes in tag
- GPG signed
- Automated builds

### 16.4 Dependency Management

**Update Strategy**:
- Monthly security updates
- Quarterly feature updates
- Test before updating
- Document changes
- Rollback plan

**Version Pinning**:
- Exact versions in production
- Range versions in development
- Lock files committed
- Automated checks
- Security scanning

### 16.5 Documentation Updates

**Documentation Types**:
- User documentation
- API documentation
- Developer guides
- Release notes
- Change logs

**Update Process**:
1. Update with code changes
2. Review for accuracy
3. Version documentation
4. Publish updates
5. Archive old versions

---

## 17. Website Specification

### 17.1 Website Overview

**Purpose**: Marketing and information site for BrumbieSoft and TriviaApp

**Domain**: brumbiesoft.org

**Hosting**: Static HTML files, can be hosted on any web server

**Pages**:
1. Index/Homepage (index.html)
2. Privacy Policy (privacy-policy.html)

### 17.2 Homepage Specification

**URL**: https://brumbiesoft.org/

**Page Structure**:

**Header Section**:
- Title: "BrumbieSoft - Mobile App Development"
- Viewport: Responsive, width=device-width, initial-scale=1.0
- Character encoding: UTF-8

**Content Layout**:
1. **Company Branding**
   - Heading: "🧠 BrumbieSoft" (h1, centered)
   - Subheading: "Mobile App Development" (h2)

2. **App Section**
   - Title: "TriviaApp - AI-Powered Quiz Game"
   - Description: Brief overview of app capabilities
   - Features list with emoji indicators:
     - 🤖 AI-generated questions on any topic
     - 🎯 Multiple difficulty levels
     - 📊 Quiz history and progress tracking
     - 🔒 Age-appropriate content filtering
     - 🖼️ Visual questions with dynamic images
   - Download button: "Download from Google Play Store (Coming Soon)"

3. **API Services Section**
   - Title: "API Services"
   - Description: Brief overview of middleware capabilities
   - API endpoint display with link to health check

4. **Footer**
   - Navigation links: Privacy Policy | Contact
   - Copyright notice: "© 2025 BrumbieSoft. All rights reserved."

**Visual Design**:
- Container: Maximum width 800px, centered
- Background: Light gray (#f4f4f4)
- Content box: White background, 30px padding, 10px border radius
- Primary color: Green (#4CAF50)
- Font: Arial, sans-serif
- Line height: 1.6
- Box shadow: Subtle (0 0 10px rgba(0,0,0,0.1))

**Interactive Elements**:
- Download button: Green background, white text, hover effect
- Links: Green color, no underline
- Email link: mailto:brumbie@brumbiesoft.org

### 17.3 Privacy Policy Specification

**URL**: https://brumbiesoft.org/privacy-policy.html

**Page Structure**:

**Header Section**:
- Title: "Privacy Policy - TriviaByClaude | BrumbieSoft"
- Back navigation link to homepage

**Content Sections** (in order):

1. **Title and Metadata**
   - Page title: "Privacy Policy for TriviaByClaude"
   - Effective date: July 15, 2025
   - Developer: BrumbieSoft
   - Contact: brumbie@brumbiesoft.org

2. **Overview**
   - Brief description of app purpose
   - Introduction to privacy practices

3. **Information We Collect**
   - Information You Provide:
     - Quiz preferences
     - Feedback submissions
     - Age verification
   - Automatically Collected:
     - App usage data
     - Device information
     - Network status

4. **How We Use Your Information**
   - Question generation
   - Fact-checking
   - Image enhancement
   - App improvement
   - Support services

5. **Data Sharing and Third Parties**
   - AI Services:
     - Claude AI (Anthropic)
     - Perplexity AI
   - Supporting Services:
     - Pexels
     - Email services
   - No sale of data statement

6. **Data Storage and Security**
   - Local storage practices
   - Encryption (HTTPS)
   - Data retention
   - No user accounts

7. **Children's Privacy**
   - Age restriction (13+)
   - No collection from children
   - Contact for concerns

8. **Your Rights**
   - Access to local data
   - Deletion via uninstall
   - Opt-out options

9. **Changes to Policy**
   - Update procedures
   - Notification methods

10. **Contact Information**
    - Email address
    - Website URL
    - Developer name

**Visual Design**:
- Consistent with homepage styling
- Green accent color for headings
- Contact info in highlighted box
- Professional, readable layout

### 17.4 Technical Requirements

**HTML Standards**:
- DOCTYPE: HTML5
- Language: en
- Valid semantic HTML
- No external dependencies

**CSS Requirements**:
- Inline styles (no external CSS files)
- Mobile-responsive design
- Print-friendly layout
- Cross-browser compatible

**Performance**:
- Page size: <50KB per page
- No JavaScript required
- Fast loading times
- SEO-friendly structure

**Accessibility**:
- Proper heading hierarchy
- Sufficient color contrast
- Readable font sizes
- Keyboard navigation support

### 17.5 Maintenance Requirements

**Update Frequency**:
- Privacy policy: As needed for compliance
- Homepage: When app features change
- Contact info: Verify quarterly

**Version Control**:
- Track changes in git
- Document update reasons
- Maintain update history

**Deployment**:
- Can be hosted anywhere
- No server-side processing
- Static file serving only
- HTTPS required

**Monitoring**:
- Check for broken links
- Verify email addresses
- Test on multiple devices
- Analytics optional

---

## 18. UI Design Resources Specification

### 18.1 Design Resources Overview

**Resource Directory**: `/design-resources/`

**Purpose**: Centralized location for all UI design assets, specifications, and templates

**Organization**:
```
design-resources/
├── app-icons/
├── ui-icons/
├── logos/
├── backgrounds/
├── mockups/
├── color-palettes/
└── specifications/
```

### 18.2 App Icon Specifications

**Primary App Icon**:
- **Name**: ic_launcher
- **Current Design**: Abstract geometric design with gradient
- **Background Color**: #484A63 (dark purple-grey)
- **Foreground Elements**: 
  - Cyan accent (#00DDDD)
  - Blue accent (#0088FF)
  - Green accent (#0b98e0)
- **Style**: Modern geometric with angular elements
- **Format**: Adaptive icon (separate foreground and background layers)

**EXISTING ICON ASSETS**:

**Android Icons (WebP format)**:
- **mipmap-mdpi**: ic_launcher.webp, ic_launcher_round.webp, ic_launcher_foreground.webp
- **mipmap-hdpi**: ic_launcher.webp, ic_launcher_round.webp, ic_launcher_foreground.webp
- **mipmap-xhdpi**: ic_launcher.webp, ic_launcher_round.webp, ic_launcher_foreground.webp
- **mipmap-xxhdpi**: ic_launcher.webp, ic_launcher_round.webp, ic_launcher_foreground.webp
- **mipmap-xxxhdpi**: ic_launcher.webp, ic_launcher_round.webp, ic_launcher_foreground.webp
- **mipmap-anydpi-v26**: ic_launcher.xml (adaptive), ic_launcher_round.xml (adaptive)

**Adaptive Icon Configuration**:
- Background: Solid color (#484A63)
- Foreground: Vector drawable with geometric design
- Safe zone: 66dp of 108dp total
- Masks: Circle and rounded square supported

**Required Additional Sizes**:
- Google Play Store: 512x512px PNG
- Feature Graphic: 1024x500px

**iOS Icons** (to be created):
- Must match Android design language
- Use same color scheme
- Square format (no transparency)
- All sizes listed in previous specification

### 18.3 UI Icons Specifications

**Navigation Icons** (24x24dp base size):

1. **History Icon**
   - Style: Outlined clock or list
   - Weight: 2dp stroke
   - Color: Inherit from theme

2. **Info Icon**
   - Style: Circled "i"
   - Weight: 2dp stroke
   - Color: Inherit from theme

3. **Feedback Icon**
   - Style: Flag or exclamation in triangle
   - Weight: 2dp stroke
   - Color: Inherit from theme

4. **Settings Icon**
   - Style: Gear
   - Weight: 2dp stroke
   - Color: Inherit from theme

5. **Share Icon**
   - Style: Connected dots or arrow
   - Weight: 2dp stroke
   - Color: Inherit from theme

**Answer State Icons** (36x36dp):

1. **Correct Answer**
   - Style: Checkmark in circle
   - Color: White on green background
   - Weight: 3dp stroke

2. **Wrong Answer**
   - Style: X in circle
   - Color: White on red background
   - Weight: 3dp stroke

3. **Selected State**
   - Style: Radio button filled
   - Color: Primary color
   - Weight: 2dp stroke

### 18.4 Logo Specifications

**App Logo/Title**:
- **Current Asset**: title_image.png
- **Text**: "Trivia By Grok" (to be updated from "Trivia By Claude")
- **Current Design**: Text-based title image
- **Background**: Transparent or dark theme compatible
- **Colors**: Uses app theme colors (cyan/blue accents)
- **Usage**: Main setup screen header

**App Icon Logo**:
- **Design**: Abstract geometric shape
- **Colors**: 
  - Background: #484A63
  - Accents: #00DDDD, #0088FF, #0b98e0
- **Style**: Modern, angular design
- **No text in icon**: Following platform guidelines

**Company Logo**:
- **Text**: "BrumbieSoft"
- **Currently**: Text only, no graphic mark
- **Font**: System default
- **Color**: Inherits from theme

### 18.5 Background Assets

**EXISTING BACKGROUND ASSETS**:

**1. Main Background**:
- **File**: trivia_by_claude_background.jpg
- **Size**: 33,792 bytes
- **Description**: Dark themed background image
- **Usage**: App splash/loading screens

**2. Title Image**:
- **File**: title_image.png
- **Size**: 595,773 bytes
- **Description**: Main branding image with app title
- **Usage**: Main setup screen header

**3. Gradient Spacer**:
- **File**: gradient_spacer.png
- **Size**: 67,666 bytes
- **Description**: Gradient element for visual separation
- **Usage**: UI element separator

**XML Drawable Resources**:

**4. Launcher Background**:
- **File**: ic_launcher_background.xml
- **Type**: Color resource
- **Value**: #484A63
- **Usage**: Adaptive icon background layer

**5. Launcher Foreground**:
- **File**: ic_launcher_foreground.xml
- **Type**: Vector drawable
- **Description**: Geometric foreground design
- **Usage**: Adaptive icon foreground layer

### 18.6 Color Palette Specification

**EXACT COLOR VALUES FROM APP**:

**Icon/Brand Colors**:
- **Icon Background**: #484A63 (dark purple-grey)
- **Icon Green**: #0b98e0 (actually cyan-blue)
- **Icon Cyan**: #00DDDD
- **Icon Blue**: #0088FF

**Primary Theme Colors**:
- **Purple 200**: #BB86FC
- **Purple 500**: #6200EE (colorPrimary)
- **Purple 700**: #3700B3 (colorPrimaryDark)

**Secondary Colors**:
- **Teal 200**: #00DDDD (colorAccent)
- **Teal 700**: #0088FF

**Background Colors**:
- **Window Background**: #484A63 (grey_900)
- **Grey 800**: #525468
- **Grey 700**: #5C5E6D

**Status Colors**:
- **Error Red**: #E53E3E (red_600)
- **Success Green**: #0b98e0 (green_500)
- **Info Blue**: #0088FF (blue_500)
- **Warning Orange**: #DD6B20 (orange_500)

**Base Colors**:
- **Black**: #000000
- **White**: #FFFFFF

### 18.7 Typography Resources

**CURRENT APP TYPOGRAPHY**:

**System Fonts**:
- **Android**: Roboto (system default)
- **iOS**: SF Pro (system default)

**Text Colors**:
- **Primary Text**: #FFFFFF (on dark backgrounds)
- **Secondary Text**: #FFFFFF (on dark backgrounds)
- **Accent Text**: #00DDDD (teal_200)

**Font Hierarchy** (as implemented):
- **Large Title**: 32sp, bold (quiz topic display)
- **Title**: 24sp, bold (screen headers)
- **Subtitle**: 20sp, medium (section headers)
- **Body**: 16sp, regular (question text)
- **Button**: 16sp, medium (action buttons)
- **Caption**: 14sp, regular (helper text)
- **Score Display**: 48sp, bold (results screen)

**Text Styling**:
- Line height: 1.5x font size
- Letter spacing: Platform default
- All caps: Avoided except for buttons

### 18.8 Component Visual Specifications

**Buttons**:
- **Primary Button**:
  - Height: 56dp
  - Corner radius: 28dp (pill shape)
  - Background: Primary color
  - Text: White, 16sp, medium
  - Shadow: 4dp elevation
  - Pressed state: 90% opacity

- **Secondary Button**:
  - Height: 48dp
  - Corner radius: 8dp
  - Background: Transparent
  - Border: 2dp, primary color
  - Text: Primary color, 16sp, medium

**Cards**:
- Background: White
- Corner radius: 8dp
- Shadow: 2dp elevation
- Padding: 16dp
- Margin: 8dp

**Input Fields**:
- Height: 56dp
- Corner radius: 8dp
- Border: 1dp, light gray
- Focus border: 2dp, primary color
- Padding: 16dp horizontal
- Label: 12sp, above field

### 18.9 Animation Resources

**Loading Animation**:
- **Style**: Rotating brain or question marks
- **Duration**: 1.5s per rotation
- **Easing**: Ease-in-out
- **Colors**: Primary color fade

**Success Animation**:
- **Style**: Checkmark draw-in
- **Duration**: 0.5s
- **Easing**: Spring effect
- **Color**: Success green

**Error Animation**:
- **Style**: Shake effect
- **Duration**: 0.3s
- **Amplitude**: 10dp
- **Color**: Error red flash

### 18.10 Image Templates

**Question Image Frame**:
- **Aspect Ratio**: 16:9
- **Corner Radius**: 8dp
- **Loading State**: Gray placeholder with spinner
- **Error State**: Gray with image icon
- **Maximum Height**: 240dp

**Thumbnail Template**:
- **Size**: 80x80dp
- **Corner Radius**: 4dp
- **Loading State**: Gray shimmer

### 18.11 Export Guidelines

**File Formats**:
- **Vector Icons**: SVG primary, PNG fallback
- **Raster Images**: PNG with transparency
- **App Icons**: Platform-specific (WebP for Android, PNG for iOS)
- **Backgrounds**: JPEG for photos, PNG for patterns

**Naming Convention**:
- Lowercase with underscores
- Prefixes: ic_ (icons), bg_ (backgrounds), img_ (images)
- Suffixes: Size identifiers (_24dp, _48dp)
- Platform identifiers (_android, _ios)

**Optimization**:
- Vector when possible
- Compress PNGs (TinyPNG or similar)
- Multiple resolutions for raster
- Maximum 100KB per asset

### 18.12 Mockup Requirements

**Screen Mockups**:
- All major screens at phone size (360x640dp)
- Key screens at tablet size (768x1024dp)
- Light and dark theme versions
- Error and empty states

**Marketing Materials**:
- App store screenshots (platform-specific sizes)
- Feature graphics
- Promotional banners
- Social media templates

### 18.13 Accessibility Considerations

**Icon Requirements**:
- Minimum 44x44dp touch targets
- High contrast versions
- Clear metaphors
- Consistent style

**Color Requirements**:
- WCAG AA compliance (4.5:1 contrast)
- Color-blind friendly palettes
- Don't rely on color alone
- Test with grayscale

### 18.14 Platform-Specific Adaptations

**Android Material Design**:
- Material Design 3 components
- Dynamic color support
- Ripple effects
- Elevation shadows

**iOS Human Interface**:
- SF Symbols integration
- Blur effects
- Haptic feedback triggers
- Dynamic type support

### 18.15 Asset Delivery

**ACTUAL FOLDER STRUCTURE WITH RESOURCES**:
```
design-resources/
├── README.md (asset guidelines)
├── app-icons/
│   ├── android/
│   │   ├── adaptive-icon/
│   │   │   ├── ic_launcher_background.xml
│   │   │   └── ic_launcher_foreground.xml
│   │   ├── mipmap-mdpi/
│   │   │   ├── ic_launcher.webp
│   │   │   ├── ic_launcher_foreground.webp
│   │   │   └── ic_launcher_round.webp
│   │   ├── mipmap-hdpi/
│   │   │   ├── ic_launcher.webp
│   │   │   ├── ic_launcher_foreground.webp
│   │   │   └── ic_launcher_round.webp
│   │   ├── mipmap-xhdpi/
│   │   │   ├── ic_launcher.webp
│   │   │   ├── ic_launcher_foreground.webp
│   │   │   └── ic_launcher_round.webp
│   │   ├── mipmap-xxhdpi/
│   │   │   ├── ic_launcher.webp
│   │   │   ├── ic_launcher_foreground.webp
│   │   │   └── ic_launcher_round.webp
│   │   ├── mipmap-xxxhdpi/
│   │   │   ├── ic_launcher.webp
│   │   │   ├── ic_launcher_foreground.webp
│   │   │   └── ic_launcher_round.webp
│   │   └── mipmap-anydpi-v26/
│   │       ├── ic_launcher.xml
│   │       └── ic_launcher_round.xml
│   └── ios/
│       └── AppIcon.appiconset/ (to be created)
├── ui-icons/
│   ├── navigation/ (currently using system icons)
│   ├── status/ (checkmark/X created programmatically)
│   └── actions/ (using Material icons)
├── logos/
│   ├── app-logo/ (uses title_image.png)
│   └── company-logo/ (text only currently)
├── backgrounds/
│   ├── main/
│   │   ├── trivia_by_claude_background.jpg (33KB)
│   │   ├── title_image.png (596KB)
│   │   └── gradient_spacer.png (68KB)
│   └── categories/ (not implemented)
├── mockups/
│   ├── phone/ (to be created)
│   └── tablet/ (to be created)
├── color-palettes/
│   └── colors.json (actual app colors)
└── specifications/
    ├── dimensions.json
    └── typography.json
```

**Version Control**:
- Track all assets in git
- Use Git LFS for large files
- Tag releases with asset versions
- Document changes in README

### 18.16 Critical Visual Implementation Notes

**EXACT REPRODUCTION REQUIREMENTS**:

**1. Dark Theme Only**:
- App uses dark theme exclusively
- Window background: #484A63
- All text: White (#FFFFFF)
- No light theme variant implemented

**2. Icon Design Language**:
- Geometric, angular design
- Not a brain icon as might be expected
- Uses cyan/blue gradient accents
- WebP format for all density buckets

**3. Color Naming Mismatch**:
- "green_500" is actually cyan (#0b98e0)
- "purple" theme but grey/blue appearance
- Accent colors are cyan/blue, not green

**4. Current UI Icons**:
- App uses system/Material icons
- No custom navigation icons
- Status indicators drawn programmatically
- Checkmark: White circle with check
- X mark: White circle with X

**5. Visual Hierarchy**:
- Dark background (#484A63) throughout
- Cyan accent (#00DDDD) for interactive elements
- Blue (#0088FF) for secondary actions
- White text on all screens

**6. Missing Assets to Create**:
- iOS icon set (matching Android design)
- Play Store listing graphics
- Custom navigation icons (optional)
- Category-specific backgrounds (optional)
- Marketing screenshots

**7. Text Rendering**:
- All text pure white on dark
- No text shadows or effects
- System fonts only
- High contrast design

**8. Component Styling**:
- Flat design (no gradients in UI)
- Minimal shadows/elevation
- Rounded corners on cards/buttons
- Cyan/blue color for emphasis

**9. Image Handling**:
- Question images: 16:9 aspect ratio
- Rounded corners (8dp)
- Gray placeholder during load
- No image borders

**10. Animation Style**:
- Subtle, quick transitions
- No elaborate animations
- Focus on functionality
- Platform-standard timing

---

## Appendices

### Appendix A: Glossary

**Technical Terms**:
- **AI Model**: Artificial intelligence system for generating content
- **API**: Application Programming Interface for service communication
- **Bearer Token**: Authentication method using token in header
- **Distractor**: Incorrect answer option in multiple choice question
- **Middleware**: Server layer between app and external services
- **ProGuard**: Android code obfuscation tool
- **SharedPreferences**: Android local storage mechanism
- **UserDefaults**: iOS local storage mechanism
- **UUID**: Universally Unique Identifier
- **ViewModel**: Component managing UI-related data

**Business Terms**:
- **Difficulty Level**: Question complexity rating from Novice to Master
- **Fact Checking**: Verification of answer accuracy
- **Quiz Summary**: Detailed review of completed quiz
- **Topic**: Subject area for quiz questions
- **Visual Question**: Question requiring image for context

### Appendix B: Platform Differences

**UI Differences**:
- Navigation: Back button (Android) vs gesture (iOS)
- Dialogs: Material (Android) vs UIKit (iOS)
- Typography: Roboto (Android) vs SF Pro (iOS)
- Icons: Material Icons vs SF Symbols
- Animations: Platform-specific timing

**Technical Differences**:
- Storage: SharedPreferences vs UserDefaults
- Networking: OkHttp vs URLSession
- Async: Coroutines vs Combine
- DI: Hilt vs manual
- Testing: JUnit vs XCTest

### Appendix C: Error Codes

**Client Error Codes**:
- E001: Network connection failed
- E002: Invalid topic entered
- E003: Question generation failed
- E004: Storage full
- E005: Data corruption detected

**Server Error Codes**:
- S001: Authentication failed
- S002: Rate limit exceeded
- S003: External service error
- S004: Database error
- S005: Invalid request format

### Appendix D: Configuration Values

**Timeouts**:
- Network connect: 30 seconds
- Network read: 30 seconds
- Question generation: 450 seconds
- Image loading: 10 seconds
- Verification: 30 seconds

**Limits**:
- Topic length: 100 characters
- Question count: 1-20
- History items: Unlimited
- Feedback length: 500 characters
- Retry attempts: 5

**Defaults**:
- Question count: 10
- Difficulty: Novice
- Verification: Disabled
- Auto-update: Enabled
- Animations: Enabled

### Appendix E: Third-Party Services

**Grok AI (xAI)**:
- Purpose: Question generation
- Model: grok-3-mini
- Cost: $0.000043 per question
- Rate limit: Varies
- Documentation: xAI developer portal

**Pexels**:
- Purpose: Image search
- Plan: Free tier
- Rate limit: 200 per hour
- Attribution: Not required
- Documentation: pexels.com/api

**Wikipedia**:
- Purpose: Fact verification
- API: REST v1
- Rate limit: Reasonable use
- License: CC BY-SA
- Documentation: wikipedia.org/api

---

## Document Information

**Version**: 1.0
**Date**: July 28, 2025
**Purpose**: Complete specification for exact reproduction of Trivia Game application
**Audience**: Developers, AI assistants, technical implementers
**Maintenance**: Update with each major version release

**Important Notes**:
1. This document contains NO code - only specifications
2. All measurements and values are exact requirements
3. Platform-specific details are clearly marked
4. Implementation must match these specifications exactly
5. Any deviations require documentation and approval

---