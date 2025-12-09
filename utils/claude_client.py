import json
import re
import logging
import asyncio
import httpx
from utils.config import Config

GROQ_API_KEY = Config.GROQ_API_KEY

logger = logging.getLogger(__name__)

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

def _extract_json_from_text(text: str):
    """Extract JSON from Groq's text response."""
    if not text:
        raise ValueError("Empty text")

    text = re.sub(r'```json\s*|\s*```', '', text).strip()

    json_match = re.search(r'\{.*\}', text, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(0))
        except json.JSONDecodeError:
            pass

    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Could not parse JSON from text: {e}")

async def call_claude_raw(prompt: str, model: str = "llama-3.3-70b-versatile", max_tokens: int = 800, temperature: float = 0.7):
    """Call Groq API and return raw response with retry logic."""
    if not GROQ_API_KEY:
        logger.error("GROQ_API_KEY not configured")
        return {"error": "GROQ_API_KEY not set in environment."}
    
    payload = {
        "model": model,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "messages": [{"role": "user", "content": prompt}],
    }
    
    logger.debug(f"Groq API Request - Model: {model}, Max Tokens: {max_tokens}")
    logger.debug(f"Payload keys: {list(payload.keys())}")

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    max_retries = 2
    last_error = None
    
    for attempt in range(max_retries):
        try:
            async with httpx.AsyncClient(timeout=120.0, limits=httpx.Limits(max_connections=5)) as client:
                logger.debug(f"POST {GROQ_URL} (attempt {attempt + 1}/{max_retries})")
                r = await client.post(GROQ_URL, headers=headers, json=payload)
                text = r.text
                
                try:
                    data = r.json()
                except Exception:
                    data = None
                
                logger.debug(f"Response Status: {r.status_code}")
                
                if r.status_code == 400:
                    logger.error(f"400 Bad Request from Groq: {text}")
                    if data:
                        logger.error(f"Error details: {json.dumps(data, indent=2)}")
                    return {"error": "Bad Request", "status": 400, "body": text}
                
                if r.status_code == 401:
                    logger.error(f"401 Unauthorized - Invalid or expired API key")
                    return {"error": "Unauthorized - Check your API key", "status": 401, "body": text}
                
                if r.status_code == 429:
                    logger.warning(f"429 Rate Limited - Free tier quota exceeded")
                    return {"error": "Rate limited - Free tier quota exceeded", "status": 429, "body": text}
                
                if r.status_code < 200 or r.status_code >= 300:
                    logger.error(f"Groq returned {r.status_code}: {text}")
                    last_error = {"error": "Groq request failed", "status": r.status_code, "body": text}
                    if attempt < max_retries - 1:
                        logger.info(f"Retrying... (attempt {attempt + 2}/{max_retries})")
                        await asyncio.sleep(2 ** attempt)
                        continue
                    return last_error
                
                if isinstance(data, dict):
                    choices = data.get("choices", [])
                    if isinstance(choices, list) and len(choices) > 0:
                        message = choices[0].get("message", {})
                        text_out = message.get("content", "")
                        return {"text": text_out, "raw": data}
                
                return {"text": str(data) if data is not None else text, "raw": data}
                
        except (httpx.TimeoutException, httpx.ConnectError, httpx.ReadError) as e:
            last_error = str(e)
            logger.warning(f"Network error on attempt {attempt + 1}/{max_retries}: {type(e).__name__}: {e}")
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                logger.info(f"Waiting {wait_time}s before retry...")
                await asyncio.sleep(wait_time)
                continue
            else:
                logger.error(f"All retries failed. Last error: {last_error}")
                return {"error": "Network timeout - Groq API unavailable", "details": str(last_error)}
        except Exception as e:
            logger.exception(f"Exception calling Groq API: {e}")
            return {"error": "Request failed", "details": str(e)}
    
    return {"error": "Failed after retries", "details": str(last_error)}

async def call_claude_json(prompt: str, model: str = "llama-3.3-70b-versatile", max_tokens: int = 1200, temperature: float = 0.1):
    """Call Groq and parse JSON response."""
    raw_response = await call_claude_raw(prompt, model, max_tokens, temperature)
    
    if "error" in raw_response:
        return {"error": raw_response["error"], "raw": raw_response.get("raw")}
    
    text = raw_response.get("text", "")
    try:
        parsed = _extract_json_from_text(text)
        return parsed
    except Exception as e:
        logger.warning("Failed to parse JSON from Groq output: %s", e)
        return {"error": "Failed to parse JSON response", "raw_text": text}
