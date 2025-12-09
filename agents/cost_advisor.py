# agents/cost_advisor.py
import json
import logging
from utils.claude_client import call_claude_json

logger = logging.getLogger(__name__)

async def estimate_cost(sql: str, explain):
    base = {"agent": "cost_advisor", "status": None, "query": sql, "details": {}}
    
    explain_str = json.dumps(explain, indent=2, default=str) if explain and isinstance(explain, list) else "No explain data"
    
    prompt = f"""You are a Cost Advisor for MariaDB. Analyze IO cost and runtime.

SQL:
{sql}

EXPLAIN PLAN:
{explain_str}

TASK: Estimate cost/IO/runtime from EXPLAIN and provide concrete cost reduction tips.
Focus on: buffer pool efficiency, query cache hits, index covering, avoiding temp tables/filesort.

RESPONSE FORMAT - RETURN VALID JSON ONLY:
{{
  "estimated_cost": "low|medium|high",
  "cost_saving_tips": ["tip1", "tip2"],
  "warnings": ["warning1"]
}}

If no data available, still return valid JSON with best guess."""
    
    try:
        logger.debug("Calling Groq API for cost analysis")
        resp = await call_claude_json(prompt, max_tokens=800, temperature=0.3)
        
        if "error" in resp:
            logger.warning(f"Cost advisor error: {resp.get('error')}")
            return {**base, "status": "error", "details": {"error": resp.get("error"), "estimated_cost": "unknown"}}
        
        details = {
            "estimated_cost": resp.get("estimated_cost", "medium"),
            "cost_saving_tips": resp.get("cost_saving_tips", []),
            "warnings": resp.get("warnings", [])
        }
        return {**base, "status": "success", "details": details}
    except Exception as e:
        logger.exception(f"Cost advisor exception: {e}")
        return {**base, "status": "error", "details": {"error": str(e), "estimated_cost": "unknown"}}
