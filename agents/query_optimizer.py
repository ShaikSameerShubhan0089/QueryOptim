# agents/query_optimizer.py
import json
import logging
from typing import Dict, Any
from utils.claude_client import call_claude_json

logger = logging.getLogger(__name__)

async def optimize_query(sql: str,
                   schema: Dict[str, Any],
                   explain: Dict[str, Any],
                   sample_rows: Dict[str, Any],
                   target_engine: str = "mariadb") -> Dict[str, Any]:
    """
    Groq-powered Query Optimizer (MariaDB-focused)
    - Calls Groq with schema + EXPLAIN + SQL
    - Expects structured JSON with optimized query, recommendations, warnings, impact, etc.
    """

    schema_str = json.dumps(schema, indent=2, default=str) if schema and not isinstance(schema, dict) or (isinstance(schema, dict) and schema.get("error") is None) else "Schema unavailable"
    explain_str = json.dumps(explain, indent=2, default=str) if explain and isinstance(explain, list) else "Explain plan unavailable"
    sample_rows_str = json.dumps(sample_rows, indent=2, default=str) if sample_rows and isinstance(sample_rows, dict) else "Sample rows unavailable"

    prompt = f"""You are a world-class SQL performance tuning agent specialized in MariaDB/MySQL.

Your ONLY task: optimize SQL queries for performance.

ORIGINAL QUERY:
{sql}

SCHEMA CONTEXT:
{schema_str}

EXPLAIN PLAN:
{explain_str}

SAMPLE ROWS:
{sample_rows_str}

OPTIMIZATION RULES - ALWAYS FIND IMPROVEMENTS:
1. ALWAYS rewrite query with at least ONE concrete improvement (even 0.1% counts)
2. Replace SELECT * with explicit columns (reduces data transfer)
3. Add indexes on JOIN, WHERE, ORDER BY, GROUP BY columns
4. Create composite indexes for multi-column filtering
5. Reorder WHERE conditions for earliest/most restrictive filtering first
6. Add LIMIT clauses to restrict result sets
7. Use covering indexes to avoid table lookups
8. Detect: full table scans (type=ALL), filesort, temp tables, cross joins
9. Never return original query unchanged - improve it

RESPONSE FORMAT - RETURN VALID JSON ONLY:
{{
  "optimized_query": "SELECT ...",
  "why_faster": "explanation",
  "recommendations": ["tip1", "tip2", "tip3"],
  "warnings": ["warning1"],
  "estimated_impact": "low|medium|high",
  "engine_advice": ["MariaDB specific advice"],
  "materialization_advice": ["advice"]
}}

CRITICAL RULES:
- optimized_query MUST be different from original query (show concrete improvements)
- Recommendations MUST be 3+ specific actionable items
- Even if query seems optimal, suggest indexes, explicit columns, or covering indexes
- Estimate impact realistically based on EXPLAIN rows and scan types
- If SELECT *, ALWAYS rewrite with explicit columns
- If type=ALL in EXPLAIN, MUST suggest indexes"""

    try:
        logger.debug(f"Calling Groq API for query optimization")
        resp = await call_claude_json(prompt, max_tokens=2000, temperature=0.3)
        
        if "error" in resp:
            logger.warning(f"Query optimizer error: {resp.get('error')}")
            return {
                "status": "error",
                "details": {
                    "error": resp.get("error"),
                    "optimized_query": sql,
                    "recommendations": [],
                    "warnings": ["Unable to optimize query"],
                    "estimated_impact": "unknown"
                }
            }
        
        required_fields = ["optimized_query", "why_faster", "recommendations", "warnings", "estimated_impact"]
        missing_fields = [f for f in required_fields if f not in resp]
        
        if missing_fields:
            logger.warning(f"Query optimizer missing fields: {missing_fields}")
        
        resp.setdefault("optimized_query", sql)
        resp.setdefault("why_faster", "Performance optimization analysis complete")
        resp.setdefault("recommendations", ["Add indexes on JOIN and WHERE columns", "Consider using explicit columns instead of SELECT *", "Implement covering indexes for better query efficiency"])
        resp.setdefault("warnings", [])
        resp.setdefault("estimated_impact", "medium")
        resp.setdefault("engine_advice", ["Use InnoDB for better concurrent access"])
        resp.setdefault("materialization_advice", [])
        
        return {"status": "success", "details": resp}
    except Exception as e:
        logger.exception(f"Query optimization exception: {e}")
        return {
            "status": "error",
            "details": {
                "error": str(e),
                "optimized_query": sql,
                "recommendations": [],
                "warnings": [f"Query optimization failed: {str(e)}"],
                "estimated_impact": "unknown"
            }
        }
