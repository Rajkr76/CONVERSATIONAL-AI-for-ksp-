"""Text-to-SQL service using schema-aware prompting for SQLCoder."""

import time
from typing import Optional

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.llm_service import llm_service
from app.services.sql_validator import validate_sql, extract_sql_from_response, SQLValidationError
from app.schemas.chat import SQLResult


# ─── Schema DDL for prompt context ──────────────────────────────
SCHEMA_DDL = """
CREATE TABLE officer (
    id UUID PRIMARY KEY,
    name VARCHAR(200),
    badge_number VARCHAR(50) UNIQUE,
    rank VARCHAR(100),
    department VARCHAR(200),
    station VARCHAR(200),
    phone VARCHAR(20),
    email VARCHAR(255),
    date_of_joining DATE,
    is_active BOOLEAN
);

CREATE TABLE fir (
    id UUID PRIMARY KEY,
    fir_number VARCHAR(50) UNIQUE,
    title VARCHAR(500),
    description TEXT,
    fir_date DATE,
    fir_type VARCHAR(100), -- values: theft, robbery, murder, assault, fraud, cybercrime, kidnapping, drug_offense, domestic_violence, missing_person, accident, property_dispute, sexual_offense, other
    status VARCHAR(50), -- values: open, under_investigation, chargesheet_filed, closed, reopened
    severity VARCHAR(20), -- values: low, medium, high, critical
    ipc_sections TEXT[],
    station VARCHAR(200),
    district VARCHAR(200),
    state VARCHAR(100) DEFAULT 'Karnataka',
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    reporting_officer_id UUID REFERENCES officer(id),
    investigating_officer_id UUID REFERENCES officer(id),
    created_at TIMESTAMP WITH TIME ZONE
);

CREATE TABLE accused (
    id UUID PRIMARY KEY,
    fir_id UUID REFERENCES fir(id),
    name VARCHAR(200),
    alias VARCHAR(200),
    age INTEGER,
    gender VARCHAR(20), -- values: male, female, other
    address TEXT,
    phone VARCHAR(20),
    occupation VARCHAR(200),
    is_arrested BOOLEAN,
    arrest_date DATE,
    bail_status VARCHAR(50) -- values: not_applicable, bail_granted, bail_denied, bail_pending
);

CREATE TABLE victim (
    id UUID PRIMARY KEY,
    fir_id UUID REFERENCES fir(id),
    name VARCHAR(200),
    age INTEGER,
    gender VARCHAR(20),
    injury_type VARCHAR(100),
    injury_severity VARCHAR(50), -- values: none, minor, moderate, severe, fatal
    hospital_name VARCHAR(200),
    is_minor BOOLEAN
);

CREATE TABLE investigation (
    id UUID PRIMARY KEY,
    fir_id UUID REFERENCES fir(id),
    officer_id UUID REFERENCES officer(id),
    description TEXT,
    findings TEXT,
    status VARCHAR(50), -- values: in_progress, completed, pending_review, on_hold
    started_at DATE,
    completed_at DATE
);

CREATE TABLE evidence (
    id UUID PRIMARY KEY,
    fir_id UUID REFERENCES fir(id),
    evidence_type VARCHAR(100), -- values: physical, digital, documentary, testimonial, forensic, photographic, video, audio, other
    description TEXT,
    collected_by UUID REFERENCES officer(id),
    collected_at TIMESTAMP WITH TIME ZONE,
    storage_location VARCHAR(200),
    is_verified BOOLEAN
);

CREATE TABLE witness (
    id UUID PRIMARY KEY,
    fir_id UUID REFERENCES fir(id),
    name VARCHAR(200),
    age INTEGER,
    gender VARCHAR(20),
    statement TEXT,
    statement_date DATE,
    is_reliable BOOLEAN,
    protection_needed BOOLEAN
);

CREATE TABLE criminal_history (
    id UUID PRIMARY KEY,
    accused_id UUID REFERENCES accused(id),
    offense_type VARCHAR(100),
    case_number VARCHAR(50),
    court_name VARCHAR(200),
    conviction_date DATE,
    sentence VARCHAR(200),
    status VARCHAR(50) -- values: recorded, convicted, acquitted, pending
);

CREATE TABLE financial_transaction (
    id UUID PRIMARY KEY,
    fir_id UUID REFERENCES fir(id),
    accused_id UUID REFERENCES accused(id),
    transaction_type VARCHAR(50), -- values: credit, debit, transfer, cash_deposit, cash_withdrawal
    amount DECIMAL(15, 2),
    currency VARCHAR(10) DEFAULT 'INR',
    from_account VARCHAR(100),
    to_account VARCHAR(100),
    bank_name VARCHAR(200),
    transaction_date TIMESTAMP WITH TIME ZONE,
    is_suspicious BOOLEAN
);

CREATE TABLE location_history (
    id UUID PRIMARY KEY,
    accused_id UUID REFERENCES accused(id),
    fir_id UUID REFERENCES fir(id),
    location_name VARCHAR(200),
    address TEXT,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    recorded_at TIMESTAMP WITH TIME ZONE,
    source VARCHAR(100) -- values: cell_tower, cctv, gps, witness, manual, other
);
""".strip()


# ─── Prompt template for SQLCoder ────────────────────────────────
SQL_PROMPT_TEMPLATE = """### Task
Generate a SQL query to answer [{question}]

### Database Schema
The query will run on a database with the following schema:
{schema}

### SQL
Given the database schema, here is the SQL query that answers [{question}]:
```sql
"""


class SQLService:
    """Converts natural language questions to SQL and executes them."""

    def __init__(self):
        self.schema_ddl = SCHEMA_DDL

    def build_prompt(
        self, question: str, conversation_context: str = ""
    ) -> str:
        """Build the SQLCoder prompt with schema context."""
        prompt = SQL_PROMPT_TEMPLATE.format(
            question=question,
            schema=self.schema_ddl,
        )
        if conversation_context:
            prompt = (
                f"### Previous Context\n{conversation_context}\n\n{prompt}"
            )
        return prompt

    async def generate_sql(
        self, question: str, conversation_context: str = ""
    ) -> str:
        """Generate SQL from natural language using SQLCoder."""
        prompt = self.build_prompt(question, conversation_context)
        raw_response = await llm_service.generate_sql(prompt)

        # Extract SQL from response
        sql = extract_sql_from_response(raw_response)

        # Validate safety
        validated_sql = validate_sql(sql)
        return validated_sql

    async def execute_sql(
        self, db: AsyncSession, sql: str
    ) -> SQLResult:
        """Execute a validated SQL query and return results."""
        start_time = time.time()

        try:
            result = await db.execute(text(sql))
            columns = list(result.keys()) if result.returns_rows else []
            rows_raw = result.fetchall() if result.returns_rows else []

            rows = [dict(zip(columns, row)) for row in rows_raw]

            execution_time = (time.time() - start_time) * 1000

            return SQLResult(
                query=sql,
                columns=columns,
                rows=rows[:500],  # Limit to 500 rows
                row_count=len(rows_raw),
                execution_time_ms=round(execution_time, 2),
            )
        except Exception as e:
            raise SQLValidationError(f"SQL execution error: {str(e)}")

    async def question_to_result(
        self,
        db: AsyncSession,
        question: str,
        conversation_context: str = "",
    ) -> tuple[str, SQLResult]:
        """Full pipeline: question → SQL → execute → result."""
        sql = await self.generate_sql(question, conversation_context)
        result = await self.execute_sql(db, sql)
        return sql, result


# Singleton
sql_service = SQLService()
