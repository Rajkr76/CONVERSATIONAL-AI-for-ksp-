"""Conversation history API routes."""

from uuid import UUID
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func, delete

from app.api.deps import get_database_session, get_authenticated_user
from app.models.chat_history import ChatHistory
from pydantic import BaseModel

router = APIRouter(prefix="/history", tags=["History"])


class ConversationSummary(BaseModel):
    """Summary of a conversation for the sidebar."""
    conversation_id: UUID
    title: str
    message_count: int
    last_message_at: str
    language: str


class ConversationMessage(BaseModel):
    """A single message in a conversation."""
    id: UUID
    role: str
    content: str
    sql_query: Optional[str] = None
    sql_result: Optional[dict] = None
    chart_data: Optional[dict] = None
    graph_data: Optional[dict] = None
    confidence: Optional[float] = None
    language: str
    metadata: Optional[dict] = None
    created_at: str


@router.get("/", response_model=list[ConversationSummary])
async def list_conversations(
    limit: int = Query(default=50, le=200),
    db: AsyncSession = Depends(get_database_session),
    current_user: dict = Depends(get_authenticated_user),
):
    """List all conversations for the current user."""
    user_id = current_user.get("sub")

    result = await db.execute(
        select(
            ChatHistory.conversation_id,
            func.min(ChatHistory.content).label("first_message"),
            func.count(ChatHistory.id).label("message_count"),
            func.max(ChatHistory.created_at).label("last_message_at"),
            func.min(ChatHistory.language).label("language"),
        )
        .where(ChatHistory.user_id == user_id)
        .group_by(ChatHistory.conversation_id)
        .order_by(desc(func.max(ChatHistory.created_at)))
        .limit(limit)
    )
    conversations = result.all()

    return [
        ConversationSummary(
            conversation_id=conv.conversation_id,
            title=conv.first_message[:80] + "..." if len(conv.first_message) > 80 else conv.first_message,
            message_count=conv.message_count,
            last_message_at=str(conv.last_message_at),
            language=conv.language or "en",
        )
        for conv in conversations
    ]


@router.get("/{conversation_id}", response_model=list[ConversationMessage])
async def get_conversation(
    conversation_id: UUID,
    db: AsyncSession = Depends(get_database_session),
    current_user: dict = Depends(get_authenticated_user),
):
    """Get all messages in a conversation."""
    user_id = current_user.get("sub")

    result = await db.execute(
        select(ChatHistory)
        .where(
            ChatHistory.conversation_id == conversation_id,
            ChatHistory.user_id == user_id,
        )
        .order_by(ChatHistory.created_at)
    )
    messages = result.scalars().all()

    if not messages:
        raise HTTPException(status_code=404, detail="Conversation not found")

    return [
        ConversationMessage(
            id=msg.id,
            role=msg.role,
            content=msg.content,
            sql_query=msg.sql_query,
            sql_result=msg.sql_result,
            chart_data=msg.chart_data,
            graph_data=msg.graph_data,
            confidence=float(msg.confidence) if msg.confidence else None,
            language=msg.language,
            metadata=msg.metadata_json,
            created_at=str(msg.created_at),
        )
        for msg in messages
    ]


@router.delete("/{conversation_id}")
async def delete_conversation(
    conversation_id: UUID,
    db: AsyncSession = Depends(get_database_session),
    current_user: dict = Depends(get_authenticated_user),
):
    """Delete a conversation and all its messages."""
    user_id = current_user.get("sub")

    await db.execute(
        delete(ChatHistory).where(
            ChatHistory.conversation_id == conversation_id,
            ChatHistory.user_id == user_id,
        )
    )

    return {"status": "deleted", "conversation_id": str(conversation_id)}
