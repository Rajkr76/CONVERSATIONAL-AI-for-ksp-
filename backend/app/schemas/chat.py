"""Pydantic schemas for chat endpoints."""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Incoming chat message from the user."""
    question: str = Field(..., min_length=1, max_length=2000)
    conversation_id: Optional[UUID] = None
    language: str = Field(default="en", pattern="^(en|kn)$")


class SQLResult(BaseModel):
    """SQL query and its execution result."""
    query: str
    columns: list[str]
    rows: list[dict]
    row_count: int
    execution_time_ms: float


class ChartData(BaseModel):
    """Auto-detected chart configuration."""
    chart_type: str = Field(..., pattern="^(bar|line|pie|area)$")
    title: str
    labels: list[str]
    datasets: list[dict]


class GraphNode(BaseModel):
    """Node in the relationship graph."""
    id: str
    label: str
    type: str  # fir, accused, victim, officer, location, financial
    data: dict = {}


class GraphEdge(BaseModel):
    """Edge connecting two nodes."""
    id: str
    source: str
    target: str
    label: str


class GraphData(BaseModel):
    """Relationship graph data for React Flow."""
    nodes: list[GraphNode]
    edges: list[GraphEdge]


class ChatResponse(BaseModel):
    """Complete chat response from the AI pipeline."""
    conversation_id: UUID
    answer: str
    sql: Optional[SQLResult] = None
    chart: Optional[ChartData] = None
    graph: Optional[GraphData] = None
    confidence: Decimal = Field(default=Decimal("0.0"), ge=0, le=1)
    evidence_refs: list[str] = []
    suggested_questions: list[str] = []
    language: str = "en"


class StreamChunk(BaseModel):
    """A chunk of streamed response (SSE)."""
    type: str  # "token", "sql", "chart", "graph", "meta", "done", "error"
    data: dict
