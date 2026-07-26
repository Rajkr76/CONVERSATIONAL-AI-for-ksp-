# KSP Crime Intelligence Platform — AI Conversational Chatbot (MVP)

> **Karnataka State Police (KSP) Hackathon MVP**: An AI-powered crime investigation assistant that converts natural language questions into safe PostgreSQL queries using a local Text-to-SQL LLM (SQLCoder), executes queries against a synthetic crime database, generates evidence-backed natural language answers with Llama 3.1, visualizes results with dynamic charts and relationship graphs, and exports full conversation reports as PDFs.

---

## 🏛️ System Architecture

```text
User Question → Chat UI (Next.js) → FastAPI Backend → Ollama (SQLCoder 7B)
                                                             │
                                                     SQL Generation
                                                             ▼
                                                    SQL Safety Validator
                                                  (Read-Only Whitelist)
                                                             │
                                                             ▼
                                                    PostgreSQL Database
                                                             │
                                                    Result Set Execution
                                                             ▼
                                                    Ollama (Llama 3.1 8B)
                                                             │
                                                  Natural Language Answer
                                                  + Confidence Scoring
                                                             │
                                          ┌──────────────────┴──────────────────┐
                                          ▼                                     ▼
                                Chart Auto-Detector                   Relationship Graph
                             (Bar, Line, Pie, Area)                      (React Flow)
```

---

## 🚀 Key Features

- **Natural Language → SQL**: Converts English and Kannada queries into optimized SQL.
- **SQL Safety Validator**: Strict whitelist restricting queries to `SELECT` statements; blocks `UPDATE`, `DELETE`, `DROP`, `ALTER`, `INSERT`.
- **Mock PostgreSQL Database**: 11 normalized tables with foreign keys, PostGIS coordinates, and 5,000+ realistic synthetic Karnataka crime records generated via Faker.
- **Dynamic Charts**: Automatically detects column types to render Recharts Bar, Line, Pie, or Area charts.
- **Entity Relationship Graph**: Interactive React Flow graph visualizing connections between FIRs, accused persons, victims, officers, locations, and financial transactions.
- **PDF Report Export**: Exports complete investigation conversations into styled PDF reports.
- **Voice Input**: Web Speech API integration supporting English (`en-US`) and Kannada (`kn-IN`).
- **Context-Aware History**: Preserves conversation state and provides suggested follow-up questions.
- **JWT & RBAC Security**: Built-in authentication with demo accounts (Admin, Officer, Analyst).

---

## 📁 Repository Structure

```text
DATATHON/
├── docker-compose.yml           # PostgreSQL + Ollama + Backend + Frontend
├── .env.example                 # Global environment configuration
├── prompt.md                    # Agent Blueprint & Prompt specification
├── README.md                    # Project Documentation
│
├── database/
│   └── schema.sql               # PostgreSQL DDL for 11 normalized tables
│
├── backend/                     # FastAPI Backend (Python)
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── app/
│   │   ├── main.py              # FastAPI app & CORS middleware
│   │   ├── core/                # Config, Database Engine, JWT Security
│   │   ├── models/              # SQLAlchemy ORM models (FIR, Accused, Victim, etc.)
│   │   ├── schemas/             # Pydantic schemas (Chat, Auth, SQLResult)
│   │   ├── services/            # Text-to-SQL, LLM Client, Validator, Charts, Graph
│   │   ├── pipeline/            # LangChain streaming orchestration
│   │   └── api/routes/          # Chat, Auth, History, Export API endpoints
│   └── scripts/
│       └── seed_data.py         # Faker seed script generating 5,000+ rows
│
└── frontend/                    # Next.js 14 App Router (TypeScript & Tailwind)
    ├── Dockerfile
    ├── package.json
    ├── src/
    │   ├── app/                 # Next.js App Router (Layouts, Login, Dashboard)
    │   ├── components/
    │   │   ├── chat/            # ChatInput, MessageBubble, SQLAccordion, ConfidenceBadge
    │   │   ├── charts/          # ChartRenderer (Recharts)
    │   │   ├── graph/           # RelationshipGraph (React Flow)
    │   │   ├── layout/          # Sidebar, Topbar
    │   │   └── shared/          # VoiceInput, PDFExportButton
    │   ├── store/               # Zustand state management (chatStore, authStore)
    │   ├── lib/                 # API client, SSE stream reader, Auth storage
    │   └── types/               # TypeScript interfaces
```

---

## 🛠️ Local Development Setup

### 1. Prerequisites
- **PostgreSQL**: Install [PostgreSQL](https://www.postgresql.org/download/). Create a database named `ksp_crime_db` with user `ksp_admin` and password `ksp_secure_2024` (or update `.env` to match your local setup).
- **Ollama**: Install [Ollama](https://ollama.com/) locally and pull the required models:
  ```bash
  ollama pull sqlcoder
  ollama pull llama3.1:8b
  ```
- **Node.js**: Install [Node.js (v18+)](https://nodejs.org/) for the frontend.
- **Python**: Install [Python (3.11+)](https://www.python.org/) for the backend.

### 2. Environment Configuration
Copy the environment template and ensure it matches your local PostgreSQL credentials:
```bash
cp .env.example .env
```
Key variables required in `.env`:
- `DATABASE_URL` / `DATABASE_URL_SYNC`: Connection strings for PostgreSQL.
- `OLLAMA_BASE_URL`: Local Ollama instance (default `http://localhost:11434`).

### 3. Backend Setup (FastAPI)
```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
# source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run seed script to create tables and populate PostgreSQL (5,000+ rows)
python scripts/seed_data.py

# Start FastAPI server
uvicorn app.main:app --reload --port 8000
```
FastAPI Swagger docs will be available at: `http://localhost:8000/docs`

### 4. Frontend Setup (Next.js)
Open a new terminal window:
```bash
cd frontend

# Install dependencies
npm install --legacy-peer-deps

# Start Next.js development server
npm run dev
```
Access the frontend at: `http://localhost:3000`

---

## 🔑 Demo Accounts

| Role | Username | Password |
|---|---|---|
| Admin | `admin` | `admin123` |
| Investigating Officer | `officer1` | `officer123` |
| Analyst | `analyst` | `analyst123` |

---

## 📡 API Endpoints Summary

- `POST /api/auth/login` — Authenticate and receive JWT access token.
- `POST /api/chat/stream` — SSE endpoint for real-time token streaming, SQL generation, chart & graph emission.
- `GET /api/history/` — List conversation history for sidebar.
- `GET /api/history/{id}` — Fetch messages for a specific conversation.
- `GET /api/export/pdf/{id}` — Generate & download a PDF investigation report.
- `GET /api/health` — System health status & Ollama connection check.
