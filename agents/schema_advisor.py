# agents/schema_advisor.py
import json
import logging
import re
from utils.claude_client import call_claude_json

logger = logging.getLogger(__name__)
FORBIDDEN = ["insert", "update", "delete", "drop", "truncate", "alter", "create", "replace"]

def _is_safe(sql: str):
    q = sql.lower()
    return not any(re.search(rf"\b{kw}\b", q) for kw in FORBIDDEN)

async def advise_schema(sql: str, schema: dict):
    base = {"agent": "schema_advisor", "status": None, "query": sql, "safe_query": None, "details": {}}
    
    if not _is_safe(sql):
        prompt = f"""Query is unsafe (contains DDL/DML): {sql}

Return JSON with safe SELECT equivalent:
{{ "safe_preview": "SELECT ...", "explanation": "Why it's unsafe" }}"""
        
        try:
            resp = await call_claude_json(prompt, max_tokens=400)
            if "error" in resp:
                return {**base, "status": "error", "details": {"error": resp.get("error")}}
            return {**base, "status": "unsafe", "safe_query": resp.get("safe_preview", ""), "details": {"reasoning": resp.get("explanation", "Query contains unsafe operations")}}
        except Exception as e:
            logger.exception(f"Schema advisor unsafe check failed: {e}")
            return {**base, "status": "unsafe", "safe_query": "", "details": {"reasoning": "Query contains unsafe operations"}}

    schema_str = json.dumps(schema, indent=2, default=str) if schema and isinstance(schema, dict) else "Schema unavailable"
    
    prompt = f"""You are a Schema Advisor for MariaDB/MySQL. Suggest schema improvements for query performance.

SQL:
{sql}

SCHEMA:
{schema_str}

TASK: Suggest indexes, partitioning, column type optimizations for faster queries.
Focus on: BTREE indexes for InnoDB, partitioning for large tables, VARCHAR vs TEXT, DECIMAL precision.
Consider denormalization for costly joins or normalization for redundancy.

RESPONSE FORMAT - RETURN VALID JSON ONLY:
{{
  "recommended_indexes": ["CREATE INDEX idx_name ON table(col1, col2)"],
  "schema_changes": ["ALTER TABLE... ADD..."],
  "warnings": ["potential issue"]
}}

If no changes needed, return valid JSON with empty arrays."""
    
    try:
        logger.debug("Calling Groq API for schema analysis")
        resp = await call_claude_json(prompt, max_tokens=1000, temperature=0.3)
        
        if "error" in resp:
            logger.warning(f"Schema advisor error: {resp.get('error')}")
            return {**base, "status": "error", "details": {"error": resp.get("error")}}
        
        details = {
            "recommended_indexes": resp.get("recommended_indexes", []),
            "schema_changes": resp.get("schema_changes", []),
            "warnings": resp.get("warnings", [])
        }
        return {**base, "status": "success", "details": details}
    except Exception as e:
        logger.exception(f"Schema advisor exception: {e}")
        return {**base, "status": "error", "details": {"error": str(e)}}
