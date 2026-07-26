"""Chat API routes — streaming SSE endpoint for AI chat."""

import uuid

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sse_starlette.sse import EventSourceResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.api.deps import get_database_session, get_authenticated_user
from app.schemas.chat import ChatRequest, ChatResponse
from app.pipeline.langchain_pipeline import pipeline
from app.models.chat_history import ChatHistory

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: AsyncSession = Depends(get_database_session),
    current_user: dict = Depends(get_authenticated_user),
):
    """Process a chat message and return a complete response."""
    # Get conversation context
    conversation_history = ""
    if request.conversation_id:
        conversation_history = await _get_conversation_context(
            db, request.conversation_id
        )

    # Process through pipeline
    response = await pipeline.process_question(
        request=request,
        db=db,
        conversation_history=conversation_history,
    )

    # Save to chat history
    await _save_chat_messages(db, current_user, request, response)

    return response


@router.post("/stream")
async def chat_stream(
    request: ChatRequest,
    db: AsyncSession = Depends(get_database_session),
    current_user: dict = Depends(get_authenticated_user),
):
    """Stream chat response via Server-Sent Events."""
    conversation_history = ""
    if request.conversation_id:
        conversation_history = await _get_conversation_context(
            db, request.conversation_id
        )

    async def event_generator():
        async for event in pipeline.process_question_stream(
            request=request,
            db=db,
            conversation_history=conversation_history,
        ):
            yield event

    return EventSourceResponse(event_generator(), media_type="text/event-stream")


async def _get_conversation_context(
    db: AsyncSession, conversation_id: uuid.UUID, limit: int = 10
) -> str:
    """Retrieve recent messages for context-aware follow-up."""
    result = await db.execute(
        select(ChatHistory)
        .where(ChatHistory.conversation_id == conversation_id)
        .order_by(desc(ChatHistory.created_at))
        .limit(limit)
    )
    messages = result.scalars().all()
    messages.reverse()

    context_parts = []
    for msg in messages:
        context_parts.append(f"{msg.role}: {msg.content}")
        if msg.sql_query:
            context_parts.append(f"SQL: {msg.sql_query}")

    return "\n".join(context_parts)


async def _save_chat_messages(
    db: AsyncSession,
    current_user: dict,
    request: ChatRequest,
    response: ChatResponse,
):
    """Persist user message and AI response to chat_history."""
    user_id = current_user.get("sub")

    # Save user message
    user_msg = ChatHistory(
        conversation_id=response.conversation_id,
        user_id=user_id,
        role="user",
        content=request.question,
        language=request.language,
    )
    db.add(user_msg)

    # Save AI response
    ai_msg = ChatHistory(
        conversation_id=response.conversation_id,
        user_id=user_id,
        role="assistant",
        content=response.answer,
        sql_query=response.sql.query if response.sql else None,
        sql_result=(
            {"columns": response.sql.columns, "row_count": response.sql.row_count}
            if response.sql else None
        ),
        chart_data=response.chart.model_dump() if response.chart else None,
        graph_data=response.graph.model_dump() if response.graph else None,
        confidence=response.confidence,
        language=response.language,
        metadata_json={
            "evidence_refs": response.evidence_refs,
            "suggested_questions": response.suggested_questions,
        },
    )
    db.add(ai_msg)
    await db.flush()
