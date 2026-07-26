"""LangChain pipeline orchestrating the full question → answer flow."""

import json
import uuid
from typing import AsyncGenerator
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.sql_service import sql_service
from app.services.sql_validator import SQLValidationError
from app.services.answer_service import answer_service
from app.services.chart_service import chart_service
from app.services.graph_service import graph_service
from app.schemas.chat import (
    ChatRequest, ChatResponse, SQLResult, StreamChunk,
)


class LangChainPipeline:
    """
    Orchestrates the full conversational AI pipeline:
    Question → SQL Generation → SQL Validation → Execution →
    Answer Generation → Chart Detection → Graph Extraction
    """

    async def process_question(
        self,
        request: ChatRequest,
        db: AsyncSession,
        conversation_history: str = "",
    ) -> ChatResponse:
        """Process a question through the complete pipeline (non-streaming)."""
        conversation_id = request.conversation_id or uuid.uuid4()

        try:
            # Step 1: Generate and execute SQL
            sql_query, sql_result = await sql_service.question_to_result(
                db=db,
                question=request.question,
                conversation_context=conversation_history,
            )

            # Step 2: Generate natural language answer
            answer_text = await answer_service.generate_answer(
                question=request.question,
                sql_query=sql_query,
                result=sql_result,
            )

            # Step 3: Estimate confidence
            confidence = await answer_service.estimate_confidence(
                question=request.question,
                sql_query=sql_query,
                row_count=sql_result.row_count,
            )

            # Step 4: Auto-detect chart
            chart_data = chart_service.detect_chart_type(sql_result)

            # Step 5: Extract relationship graph
            graph_data = graph_service.extract_graph(sql_result)

            # Step 6: Generate follow-up suggestions
            suggestions = await answer_service.generate_suggestions(
                question=request.question,
                answer_summary=answer_text[:200],
            )

            # Step 7: Extract evidence references
            evidence_refs = self._extract_evidence_refs(sql_result)

            return ChatResponse(
                conversation_id=conversation_id,
                answer=answer_text,
                sql=sql_result,
                chart=chart_data,
                graph=graph_data,
                confidence=confidence,
                evidence_refs=evidence_refs,
                suggested_questions=suggestions,
                language=request.language,
            )

        except SQLValidationError as e:
            return ChatResponse(
                conversation_id=conversation_id,
                answer=f"⚠️ I couldn't generate a valid query for that question. Error: {str(e)}",
                confidence=Decimal("0.1"),
                suggested_questions=[
                    "How many FIRs were filed this year?",
                    "Show me crime statistics by district",
                    "List all active investigations",
                ],
                language=request.language,
            )
        except Exception as e:
            return ChatResponse(
                conversation_id=conversation_id,
                answer=f"❌ An error occurred while processing your question: {str(e)}",
                confidence=Decimal("0.0"),
                suggested_questions=[
                    "How many FIRs were filed this year?",
                    "Show me crime statistics by district",
                    "List all active investigations",
                ],
                language=request.language,
            )

    async def process_question_stream(
        self,
        request: ChatRequest,
        db: AsyncSession,
        conversation_history: str = "",
    ) -> AsyncGenerator[str, None]:
        """
        Process a question with streaming SSE output.
        Yields JSON-encoded StreamChunk objects.
        """
        conversation_id = str(request.conversation_id or uuid.uuid4())

        try:
            # Step 1: Generate SQL
            yield self._sse_event("status", {"message": "Generating SQL query..."})

            sql_query, sql_result = await sql_service.question_to_result(
                db=db,
                question=request.question,
                conversation_context=conversation_history,
            )

            # Emit SQL result
            yield self._sse_event("sql", {
                "query": sql_result.query,
                "columns": sql_result.columns,
                "rows": sql_result.rows[:20],
                "row_count": sql_result.row_count,
                "execution_time_ms": sql_result.execution_time_ms,
            })

            # Step 2: Stream answer tokens
            yield self._sse_event("status", {"message": "Analyzing results..."})

            full_answer = ""
            async for token in answer_service.stream_answer(
                question=request.question,
                sql_query=sql_query,
                result=sql_result,
            ):
                full_answer += token
                yield self._sse_event("token", {"content": token})

            # Step 3: Chart data
            chart_data = chart_service.detect_chart_type(sql_result)
            if chart_data:
                yield self._sse_event("chart", chart_data.model_dump())

            # Step 4: Graph data
            graph_data = graph_service.extract_graph(sql_result)
            if graph_data:
                yield self._sse_event("graph", graph_data.model_dump())

            # Step 5: Metadata (confidence, suggestions, evidence)
            confidence = await answer_service.estimate_confidence(
                question=request.question,
                sql_query=sql_query,
                row_count=sql_result.row_count,
            )

            suggestions = await answer_service.generate_suggestions(
                question=request.question,
                answer_summary=full_answer[:200],
            )

            evidence_refs = self._extract_evidence_refs(sql_result)

            yield self._sse_event("meta", {
                "conversation_id": conversation_id,
                "confidence": float(confidence),
                "evidence_refs": evidence_refs,
                "suggested_questions": suggestions,
                "language": request.language,
            })

            # Done
            yield self._sse_event("done", {"conversation_id": conversation_id})

        except SQLValidationError as e:
            yield self._sse_event("error", {
                "message": f"SQL validation error: {str(e)}",
                "conversation_id": conversation_id,
            })
        except Exception as e:
            yield self._sse_event("error", {
                "message": f"Processing error: {str(e)}",
                "conversation_id": conversation_id,
            })

    def _sse_event(self, event_type: str, data: dict) -> dict:
        """Format as SSE event dict for EventSourceResponse."""
        chunk = StreamChunk(type=event_type, data=data)
        return {"data": chunk.model_dump_json()}

    def _extract_evidence_refs(self, result: SQLResult, max_refs: int = 5) -> list[str]:
        """Extract evidence references from result rows."""
        refs = []
        for row in result.rows[:max_refs]:
            parts = []
            if "fir_number" in row:
                parts.append(f"FIR: {row['fir_number']}")
            if "name" in row:
                parts.append(f"Name: {row['name']}")
            if "station" in row:
                parts.append(f"Station: {row['station']}")
            if "district" in row:
                parts.append(f"District: {row['district']}")
            if parts:
                refs.append(" | ".join(parts))
        return refs


# Singleton
pipeline = LangChainPipeline()
