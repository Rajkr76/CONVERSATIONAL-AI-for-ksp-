# Cursor AI Agent Master Prompt

## KSP Crime Intelligence Platform

> Based on the attached KSP Crime Intelligence Platform Blueprint. This
> prompt intentionally focuses on building the MVP: an AI conversational
> chatbot backed by a mock PostgreSQL database using a local Text-to-SQL
> LLM. The architecture follows the blueprint's on-premise, local-LLM
> approach.

------------------------------------------------------------------------

# Role

You are Cursor AI Agent acting as:

-   Senior Software Architect
-   Senior AI Engineer
-   Senior Full Stack Engineer
-   Senior Database Architect
-   Senior UI/UX Engineer

Your objective is to build a production-quality hackathon MVP.

## Scope

Build ONLY:

-   Conversational AI chatbot
-   Natural Language → SQL
-   PostgreSQL mock database
-   SQL execution
-   AI answer generation
-   Charts
-   Relationship graph
-   Conversation history
-   PDF export
-   Voice input
-   English + Kannada

Do **not** attempt to build every analytics module from the blueprint.

------------------------------------------------------------------------

# Technology Stack

Frontend

-   Next.js
-   React
-   TypeScript
-   TailwindCSS
-   shadcn/ui
-   Framer Motion
-   React Query
-   Zustand

Backend

-   FastAPI
-   SQLAlchemy
-   LangChain
-   JWT
-   Pydantic

AI

-   Ollama
-   SQLCoder 7B (Text-to-SQL)
-   Llama 3.1 8B (Answer generation)

Database

-   PostgreSQL
-   PostGIS
-   Faker generated synthetic data

------------------------------------------------------------------------

# skills.md

``` md
Always use Framer Motion.

Animations:
- Chat messages
- Cards
- Sidebar
- Dialogs
- Statistics
- Loading skeletons
- Page transitions

Rules:
- duration 0.25–0.45 s
- spring animations
- AnimatePresence
- layout animations
- stagger children
- respect prefers-reduced-motion
- enterprise feel
- never over animate
```

------------------------------------------------------------------------

# Architecture

User → Chat UI → SQLCoder → SQL Validation → PostgreSQL → Result Set →
Llama 3.1 → Natural Language Summary → Charts → Relationship Graph

------------------------------------------------------------------------

# Database

Create normalized PostgreSQL schema with foreign keys, indexes and
constraints.

Tables:

-   fir
-   accused
-   victim
-   officer
-   investigation
-   evidence
-   witness
-   criminal_history
-   financial_transaction
-   location_history
-   chat_history

Generate at least 5,000 synthetic rows using Faker.

------------------------------------------------------------------------

# Chat Requirements

-   Streaming responses
-   Context-aware follow-up questions
-   Markdown rendering
-   SQL shown in expandable section
-   Confidence score
-   Evidence references
-   Suggested follow-up questions
-   PDF export
-   Voice input
-   English + Kannada

------------------------------------------------------------------------

# Charts

Automatically render:

-   Bar Chart
-   Line Chart
-   Pie Chart
-   Area Chart

based on SQL result.

------------------------------------------------------------------------

# Relationship Graph

Render React Flow graph when entities are connected.

Nodes:

-   FIR
-   Accused
-   Victim
-   Officer
-   Location
-   Financial Account

------------------------------------------------------------------------

# Security

-   Read-only SQL
-   Prepared statements
-   No UPDATE
-   No DELETE
-   No DROP
-   SQL validation
-   JWT authentication
-   RBAC

------------------------------------------------------------------------

# Coding Standards

-   TypeScript
-   ESLint
-   Prettier
-   Reusable components
-   Maximum \~250 lines/file
-   Clean Architecture
-   Feature-based folders
-   No duplicated code

------------------------------------------------------------------------

# Deliverables

1.  Complete frontend
2.  Complete backend
3.  PostgreSQL schema
4.  Faker seed script
5.  Ollama integration
6.  LangChain pipeline
7.  README
8.  Docker support
9.  Environment templates
10. Demo-ready UI

The resulting application should behave like an AI investigation
assistant that converts natural language into SQL, queries a mock crime
database, generates evidence-backed answers, visualizes results with
charts and relationship graphs, preserves conversation context, and
exports conversations as PDF.
