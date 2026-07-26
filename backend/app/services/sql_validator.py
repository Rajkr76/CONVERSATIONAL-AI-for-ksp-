"""SQL safety validator — whitelist SELECT, block destructive operations."""

import re
import sqlparse


class SQLValidationError(Exception):
    """Raised when SQL fails validation."""
    pass


# ─── Blocked patterns ───────────────────────────────────────────
BLOCKED_KEYWORDS = [
    r"\bUPDATE\b", r"\bDELETE\b", r"\bDROP\b", r"\bALTER\b",
    r"\bINSERT\b", r"\bTRUNCATE\b", r"\bCREATE\b", r"\bGRANT\b",
    r"\bREVOKE\b", r"\bEXEC\b", r"\bEXECUTE\b", r"\bMERGE\b",
    r"\bCALL\b", r"\bCOPY\b", r"\bLOAD\b",
]

BLOCKED_PATTERN = re.compile(
    "|".join(BLOCKED_KEYWORDS), re.IGNORECASE
)

# Block comment-based injection
COMMENT_PATTERN = re.compile(r"(--|/\*|\*/|;.*--)")

# Max query length
MAX_QUERY_LENGTH = 5000


def validate_sql(sql: str) -> str:
    """
    Validate and sanitize a SQL query.

    Rules:
    - Must be a SELECT statement only
    - No UPDATE, DELETE, DROP, ALTER, INSERT, TRUNCATE
    - No SQL injection patterns (comments, semicolons followed by statements)
    - Max length enforcement
    - Returns cleaned SQL
    """
    if not sql or not sql.strip():
        raise SQLValidationError("Empty SQL query")

    # Remove leading/trailing whitespace
    cleaned = sql.strip()

    # Remove trailing semicolons
    cleaned = cleaned.rstrip(";").strip()

    # Length check
    if len(cleaned) > MAX_QUERY_LENGTH:
        raise SQLValidationError(
            f"Query exceeds maximum length of {MAX_QUERY_LENGTH} characters"
        )

    # Parse SQL to check statement type
    parsed = sqlparse.parse(cleaned)
    if not parsed:
        raise SQLValidationError("Unable to parse SQL query")

    statement = parsed[0]
    stmt_type = statement.get_type()

    # Only allow SELECT (and WITH for CTEs)
    if stmt_type and stmt_type.upper() not in ("SELECT", "UNKNOWN"):
        raise SQLValidationError(
            f"Only SELECT statements are allowed. Got: {stmt_type}"
        )

    # Check first keyword
    first_token = None
    for token in statement.tokens:
        if not token.is_whitespace:
            first_token = str(token).upper().strip()
            break

    if first_token and first_token not in ("SELECT", "WITH", "("):
        raise SQLValidationError(
            f"Query must start with SELECT or WITH. Got: {first_token}"
        )

    # Check for blocked keywords
    match = BLOCKED_PATTERN.search(cleaned)
    if match:
        raise SQLValidationError(
            f"Blocked keyword detected: {match.group()}"
        )

    # Check for multiple statements (injection attempts)
    statements = [s for s in sqlparse.split(cleaned) if s.strip()]
    if len(statements) > 1:
        raise SQLValidationError(
            "Multiple SQL statements are not allowed"
        )

    # Check for dangerous comment patterns
    if COMMENT_PATTERN.search(cleaned):
        # Allow -- only at end of line (common in generated SQL)
        lines = cleaned.split("\n")
        for line in lines:
            line_stripped = line.strip()
            if line_stripped.startswith("--"):
                continue  # Comment-only lines are fine
            if "/*" in line_stripped or "*/" in line_stripped:
                raise SQLValidationError(
                    "Block comments are not allowed in queries"
                )

    return cleaned


def extract_sql_from_response(response: str) -> str:
    """Extract SQL from LLM response that may contain markdown or explanation."""
    # Try to find SQL in code blocks
    code_block_pattern = re.compile(
        r"```(?:sql)?\s*\n?(.*?)\n?```", re.DOTALL | re.IGNORECASE
    )
    match = code_block_pattern.search(response)
    if match:
        return match.group(1).strip()

    # Try to find SELECT statement directly
    select_pattern = re.compile(
        r"((?:WITH|SELECT)\s+.+?)(?:\n\n|\Z)", re.DOTALL | re.IGNORECASE
    )
    match = select_pattern.search(response)
    if match:
        return match.group(1).strip()

    # Return the raw response as last resort
    return response.strip()
