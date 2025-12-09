# agents/data_validator.py
import json
import logging
from utils.claude_client import call_claude_json

logger = logging.getLogger(__name__)

async def validate_query(sql: str, sample_rows: dict):
    base = {"agent": "data_validator", "status": None, "query": sql, "details": {}}
    
    sample_rows_str = json.dumps(sample_rows, indent=2, default=str) if sample_rows and isinstance(sample_rows, dict) else "No sample data"
    
    prompt = f"""You are a Data Quality Validator for MariaDB. Inspect results for anomalies.

SQL:
{sql}

SAMPLE DATA:
{sample_rows_str}

TASK: Check for data quality issues: missing values, wrong types, suspicious outliers, invalid constraints.
Focus on: DECIMAL precision, DATE formats, ENUM values, foreign key hints, negative/future dates, NULL violations.

RESPONSE FORMAT - RETURN VALID JSON ONLY:
{{
  "issues": ["issue1", "issue2"],
  "confidence": "high|medium|low",
  "reasoning": "analysis summary"
}}

If no issues, return valid JSON with empty issues array and high confidence."""
    
    try:
        logger.debug("Calling Groq API for data validation")
        resp = await call_claude_json(prompt, max_tokens=600, temperature=0.3)
        
        if "error" in resp:
            logger.warning(f"Data validator error: {resp.get('error')}")
            return {**base, "status": "error", "details": {"error": resp.get("error")}}
        
        details = {
            "issues": resp.get("issues", []),
            "confidence": resp.get("confidence", "low"),
            "reasoning": resp.get("reasoning", "Validation complete")
        }
        return {**base, "status": "success", "details": details}
    except Exception as e:
        logger.exception(f"Data validator exception: {e}")
        return {**base, "status": "error", "details": {"error": str(e)}}
