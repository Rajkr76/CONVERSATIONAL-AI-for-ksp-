"""Answer generation service using Llama 3.1 for natural language summaries."""

import json
from decimal import Decimal
from typing import AsyncGenerator

from app.services.llm_service import llm_service
from app.schemas.chat import SQLResult


ANSWER_SYSTEM_PROMPT = """You are a senior crime intelligence analyst for Karnataka State Police (KSP).
Your role is to analyze SQL query results from the KSP crime database and provide clear,
professional, evidence-backed answers.

Rules:
- Be concise and professional
- Reference specific data from the results
- Highlight key findings and patterns
- If the data is numerical, mention exact numbers
- If asked about trends, identify patterns
- Always cite evidence from the query results
- If results are empty, say so clearly
- Format numbers with Indian number system (lakhs, crores)
- Use markdown formatting for readability
"""

ANSWER_PROMPT_TEMPLATE = """### User Question
{question}

### SQL Query Used
```sql
{sql_query}
```

### Query Results ({row_count} rows)
{results_preview}

### Task
Based on the above query results, provide a clear, professional analysis answering the user's question.
Include specific numbers and evidence references. Format your response with markdown."""


CONFIDENCE_PROMPT = """Rate your confidence in this answer from 0.0 to 1.0 based on:
- Data completeness: Were enough rows returned?
- Query accuracy: Does the SQL correctly address the question?
- Result clarity: Are the results unambiguous?

Question: {question}
SQL: {sql_query}
Row count: {row_count}

Reply with ONLY a number between 0.0 and 1.0."""


SUGGESTIONS_PROMPT = """Given this conversation about crime data analysis:

Question: {question}
Answer summary: {answer_summary}

Generate exactly 3 follow-up questions that a police officer or analyst might ask next.
Format: Return ONLY a JSON array of 3 strings, no other text.
Example: ["Question 1?", "Question 2?", "Question 3?"]"""


class AnswerService:
    """Generates natural language answers from SQL results using Llama 3.1."""

    def _format_results_preview(self, result: SQLResult, max_rows: int = 20) -> str:
        """Format SQL results as a readable table for the LLM."""
        if not result.rows:
            return "No results returned."

        preview_rows = result.rows[:max_rows]

        # Build markdown table
        if not result.columns:
            return json.dumps(preview_rows, indent=2, default=str)

        header = "| " + " | ".join(result.columns) + " |"
        separator = "| " + " | ".join(["---"] * len(result.columns)) + " |"
        rows_str = []
        for row in preview_rows:
            cells = [str(row.get(col, ""))[:50] for col in result.columns]
            rows_str.append("| " + " | ".join(cells) + " |")

        table = "\n".join([header, separator] + rows_str)

        if result.row_count > max_rows:
            table += f"\n\n... and {result.row_count - max_rows} more rows"

        return table

    async def generate_answer(
        self, question: str, sql_query: str, result: SQLResult
    ) -> str:
        """Generate a complete answer from SQL results."""
        results_preview = self._format_results_preview(result)

        prompt = ANSWER_PROMPT_TEMPLATE.format(
            question=question,
            sql_query=sql_query,
            row_count=result.row_count,
            results_preview=results_preview,
        )

        return await llm_service.generate_answer(
            prompt=prompt,
            system=ANSWER_SYSTEM_PROMPT,
        )

    async def stream_answer(
        self, question: str, sql_query: str, result: SQLResult
    ) -> AsyncGenerator[str, None]:
        """Stream answer tokens for SSE."""
        results_preview = self._format_results_preview(result)

        prompt = ANSWER_PROMPT_TEMPLATE.format(
            question=question,
            sql_query=sql_query,
            row_count=result.row_count,
            results_preview=results_preview,
        )

        async for token in llm_service.stream_answer(
            prompt=prompt,
            system=ANSWER_SYSTEM_PROMPT,
        ):
            yield token

    async def estimate_confidence(
        self, question: str, sql_query: str, row_count: int
    ) -> Decimal:
        """Estimate confidence score for the answer."""
        try:
            prompt = CONFIDENCE_PROMPT.format(
                question=question,
                sql_query=sql_query,
                row_count=row_count,
            )
            response = await llm_service.generate_answer(prompt)

            # Extract number from response
            import re
            numbers = re.findall(r"0\.\d+|1\.0|0|1", response.strip())
            if numbers:
                confidence = float(numbers[0])
                return Decimal(str(min(max(confidence, 0.0), 1.0)))
        except Exception:
            pass

        # Heuristic fallback
        if row_count == 0:
            return Decimal("0.3")
        elif row_count > 100:
            return Decimal("0.85")
        elif row_count > 10:
            return Decimal("0.75")
        else:
            return Decimal("0.65")

    async def generate_suggestions(
        self, question: str, answer_summary: str
    ) -> list[str]:
        """Generate follow-up question suggestions."""
        try:
            prompt = SUGGESTIONS_PROMPT.format(
                question=question,
                answer_summary=answer_summary[:200],
            )
            response = await llm_service.generate_answer(prompt)

            # Try to parse JSON array
            import re
            json_match = re.search(r"\[.*\]", response, re.DOTALL)
            if json_match:
                suggestions = json.loads(json_match.group())
                if isinstance(suggestions, list):
                    return [str(s) for s in suggestions[:3]]
        except Exception:
            pass

        # Fallback suggestions
        return [
            "Show me the trend over time",
            "Break this down by district",
            "Which officers are involved?",
        ]


# Singleton
answer_service = AnswerService()
