# Architecture Documentation

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND LAYER                            │
│                                                                  │
│  ┌──────────────────────────┐  ┌────────────────────────────┐  │
│  │   Next.js Application    │  │   React Components         │  │
│  ├──────────────────────────┤  ├────────────────────────────┤  │
│  │ • Map View (4 divisions) │  │ • MapView.tsx              │  │
│  │ • Chat Interface         │  │ • ChatInterface.tsx        │  │
│  │ • Property Results       │  │ • Card, Button components  │  │
│  │ • Responsive Design      │  │                            │  │
│  └──────────────────────────┘  └────────────────────────────┘  │
│           ▲                              ▲                      │
│           │ (HTTP/WebSocket)            │ (Component Props)    │
│           └──────────────────┬───────────┘                      │
│                              ▼                                  │
│                      Axios HTTP Client                          │
└─────────────────────────────────┬────────────────────────────────┘
                                  │
                    ┌─────────────┴────────────┐
                    │ (HTTP/REST/WebSocket)    │
                    ▼                          ▼
┌──────────────────────────────────────────────────────────────────┐
│                  FASTAPI BACKEND LAYER                            │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │              API Routes (app/routes/chat.py)               │ │
│  ├────────────────────────────────────────────────────────────┤ │
│  │  POST /api/chat - Chat endpoint                            │ │
│  │  WS /api/ws/chat - WebSocket endpoint                      │ │
│  │  GET /api/locations - Get divisions                        │ │
│  │  POST /api/search-by-location - Map search                │ │
│  └────────────────────────────────────────────────────────────┘ │
│                           ▼                                      │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │       Agent Orchestrator (agents/orchestrator.py)          │ │
│  ├────────────────────────────────────────────────────────────┤ │
│  │  Workflow Coordinator & State Management                   │ │
│  │  • Initialize SearchContext                               │ │
│  │  • Route through agents                                    │ │
│  │  • Save results to DB                                      │ │
│  │  • Format response                                         │ │
│  └────────────────────────────────────────────────────────────┘ │
│           ▼           ▼          ▼         ▼        ▼        ▼  │
│  ┌──────────────────────────────────────────────────────────────┐│
│  │          SPECIALIZED AGENT SYSTEM                           ││
│  ├──────────────────────────────────────────────────────────────┤│
│  │                                                              ││
│  │  1. Parser Agent              2. Scraper Agent             ││
│  │  └─ NLP parsing               └─ Data collection           ││
│  │  └─ Extract criteria           └─ Planning authority APIs  ││
│  │  └─ Location mapping           └─ Mock data generator       ││
│  │                                                              ││
│  │  3. Filter Agent              4. Developer Intel Agent     ││
│  │  └─ Filter by area            └─ Brochure extraction      ││
│  │  └─ Sort by date              └─ Pricing info             ││
│  │  └─ Apply constraints          └─ RERA verification        ││
│  │                                                              ││
│  │  5. Comparison Agent          6. Recommendation Agent      ││
│  │  └─ Multi-factor scoring      └─ AI reasoning             ││
│  │  └─ Rank properties           └─ Summary generation        ││
│  │  └─ Identify best matches     └─ LLM-powered insights     ││
│  │                                                              ││
│  └──────────────────────────────────────────────────────────────┘│
│  ▲                                                            ▲  │
│  │            SearchContext (Shared State)                   │  │
│  │  ┌─ original_query                                        │  │
│  │  ┌─ location, division, size, price                       │  │
│  │  ┌─ layout_approvals (scraped)                            │  │
│  │  ┌─ filtered_approvals (filtered)                         │  │
│  │  ┌─ developer_brochures (gathered)                        │  │
│  │  ┌─ properties (with pricing)                             │  │
│  │  ┌─ recommendations (ranked)                              │  │
│  │  ┌─ workflow_steps (tracking)                             │  │
│  │  └─ errors (error tracking)                               │  │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
└─────────────────────────┬──────────────────────────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        ▼                 ▼                 ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  PostgreSQL  │  │    Redis     │  │ External APIs│
│  Database    │  │    Cache     │  │              │
├──────────────┤  ├──────────────┤  ├──────────────┤
│• Properties  │  │• Sessions    │  │• Planning    │
│• Developers  │  │• Query cache │  │  Authority  │
│• Layouts     │  │• Brochures   │  │• Developers │
│• Searches    │  │              │  │• RERA       │
│• Interactions│  │              │  │              │
└──────────────┘  └──────────────┘  └──────────────┘
```

## Deployment Architecture

```
┌────────────────────────────────────────────────────────────┐
│                    Docker Environment                      │
├────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐           │
│  │  Frontend  │  │  Backend   │  │ PostgreSQL │  ┌──────┐ │
│  │ Container  │  │ Container  │  │ Container  │  │Redis │ │
│  │            │  │            │  │            │  │      │ │
│  │ Next.js:   │  │ FastAPI:   │  │ Port:5432  │  │Port: │ │
│  │ Port 3000  │  │ Port 8000  │  │            │  │6379  │ │
│  │            │  │            │  │            │  │      │ │
│  └────────────┘  └────────────┘  └────────────┘  └──────┘ │
│        ▲               ▲                ▲            ▲     │
│        └────────────┬──┴────────────────┴────────────┘     │
│                 (Internal Network)                          │
│                                                             │
└────────────────────────────────────────────────────────────┘
         ▲              ▲               ▲
         │              │               │
    ┌────┴──────────────┴───────────────┴────────────┐
    │        Port Mapping (Host)                      │
    │  http://localhost:3000 → Frontend               │
    │  http://localhost:8000 → Backend                │
    │  localhost:5432 → PostgreSQL                    │
    │  localhost:6379 → Redis                         │
    └────────────────────────────────────────────────┘
```

## Data Flow Diagram

```
┌──────────────────┐
│   User Input     │
│  (Chat Message)  │
└────────┬─────────┘
         │
         ▼
    ┌─────────────────────┐
    │  Parser Agent       │  "I want a 30x40 plot..."
    ├─────────────────────┤
    │ NLP Parsing + LLM   │
    │ Extract Criteria    │
    └────────┬────────────┘
             │
             ▼ (Structured Criteria)
    ┌─────────────────────────┐
    │  Scraper Agent          │
    ├─────────────────────────┤
    │ Fetch Planning Layouts  │
    │ From Authority Websites │
    └────────┬────────────────┘
             │
             ▼ (Layout Approvals)
    ┌─────────────────────────┐
    │  Filter Agent           │
    ├─────────────────────────┤
    │ Filter: Area > 5 acres  │
    │ Sort: By Date (DESC)    │
    └────────┬────────────────┘
             │
             ▼ (Filtered Projects)
    ┌─────────────────────────┐
    │  Developer Intel Agent  │
    ├─────────────────────────┤
    │ Get Developer Info      │
    │ Extract Pricing         │
    │ Gather Amenities        │
    └────────┬────────────────┘
             │
             ▼ (Properties + Pricing)
    ┌─────────────────────────┐
    │  Comparison Agent       │
    ├─────────────────────────┤
    │ Score Factors:          │
    │  • Price (30 pts)       │
    │  • Area (25 pts)        │
    │  • RERA (20 pts)        │
    │  • Amenities (15 pts)   │
    │  • Developer (10 pts)   │
    └────────┬────────────────┘
             │
             ▼ (Scored Properties)
    ┌─────────────────────────┐
    │ Recommendation Agent    │
    ├─────────────────────────┤
    │ Generate AI Reasoning   │
    │ Create Summary          │
    │ LLM-based Insights      │
    └────────┬────────────────┘
             │
             ▼
    ┌────────────────────────────┐
    │     JSON Response          │
    ├────────────────────────────┤
    │ • Response Text            │
    │ • Search Criteria          │
    │ • Properties List (top 5)  │
    │ • AI Reasoning             │
    │ • Workflow Trace           │
    └────────┬───────────────────┘
             │
             ▼
    ┌────────────────────────────┐
    │   Frontend Display         │
    ├────────────────────────────┤
    │ • Chat Message             │
    │ • Property Cards           │
    │ • Recommendation Summary   │
    └────────────────────────────┘
             │
             ▼
    ┌────────────────────────────┐
    │  Database Save             │
    ├────────────────────────────┤
    │ • SearchHistory Record     │
    │ • AgentInteraction Logs    │
    │ • Property Records         │
    └────────────────────────────┘
```

## Agent Communication Pattern

```
    ┌─────────────────────────────┐
    │   API Request Handler       │
    │  /api/chat endpoint         │
    └────────────┬────────────────┘
                 │
                 ▼
    ┌─────────────────────────────┐
    │  AgentOrchestrator.         │
    │  process_query()            │
    ├─────────────────────────────┤
    │ 1. Create SearchContext     │
    │ 2. For each agent:          │
    │    - Call agent method      │
    │    - Update context         │
    │    - Log step               │
    │ 3. Save to database         │
    │ 4. Format response          │
    └────────────┬────────────────┘
                 │
        ┌────────┴──────────┐
        │                   │
        ▼                   ▼
    Agent 1 ──────────► Agent 2
        ▲                   │
        │                   ▼
        │               Agent 3
        │                   │
        └───────────────────┘
        
    Shared Context:
    ┌─────────────────────────────┐
    │  SearchContext Object       │
    ├─────────────────────────────┤
    │  read by: All agents        │
    │  written by: Each agent     │
    │  state: Accumulating        │
    └─────────────────────────────┘
```

## Database Schema Relationships

```
SearchHistory (1) ──────────────────(N) AgentInteraction
    │
    │
    └────(N) Property (through search results)


Developer (1) ───────────────────────(N) Property
    │
    │
    └────(N) LayoutApproval (properties associated with developer)


LayoutApproval (1) ──────────────────(N) Property
    │
    └── Approved layouts with project details
    

Property
    ├─ FK: developer_id
    ├─ FK: layout_approval_id
    └─ Pricing, location, amenities
```

## Technology Stack Summary

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | Next.js | React framework for UI |
| | React | Component-based UI |
| | TypeScript | Type-safe JavaScript |
| | Tailwind CSS | Utility-first styling |
| | Axios | HTTP client |
| **Backend** | FastAPI | Web framework |
| | Python | Programming language |
| | SQLAlchemy | ORM for database |
| | Pydantic | Data validation |
| | LangChain | LLM integration |
| | OpenAI | LLM provider |
| **Database** | PostgreSQL | Primary database |
| | Redis | Caching layer |
| **Infrastructure** | Docker | Containerization |
| | Docker Compose | Service orchestration |

## Deployment Options

### Development
- Local Docker Compose (all services)
- Individual services on localhost

### Production
- **Cloud**: AWS, Azure, GCP
- **Compute**: ECS Fargate, Container Apps, GKE
- **Database**: RDS, Azure Database, Cloud SQL
- **Cache**: ElastiCache, Azure Cache, Memorystore
- **CDN**: CloudFront, Azure CDN, Cloud CDN
- **Monitoring**: CloudWatch, Monitor, Cloud Logging

---

**Last Updated**: January 3, 2026
**Version**: 0.1.0
