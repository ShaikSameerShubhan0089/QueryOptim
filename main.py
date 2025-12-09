from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
import re
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
logging.getLogger("utils.claude_client").setLevel(logging.DEBUG)

from utils.config import Config
from utils.response_formatter import ResponseFormatter
from db.mariadb_client import MariaDBClient
from agents.query_optimizer import optimize_query
from agents.cost_advisor import estimate_cost
from agents.schema_advisor import advise_schema
from agents.data_validator import validate_query

app = FastAPI(title="MariaDB Query Optimizer (AI Agents)")

# CORS (open for dev; tighten for prod)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    sql: str
    run_in_sandbox: bool = True

# DB client (currently single target; you could swap DB based on run_in_sandbox)
db_client = MariaDBClient(
    host=Config.DB_HOST,
    user=Config.DB_USER,
    password=Config.DB_PASSWORD,
    database=Config.DB_NAME,
    port=Config.DB_PORT,
)

@app.on_event("startup")
async def startup_event():
    # Try to connect to MariaDB at startup so we can run EXPLAIN / fetch sample rows
    try:
        await db_client.connect()
    except Exception as e:
        logger.error("DB connect failed at startup: %s", e)

@app.on_event("shutdown")
async def shutdown_event():
    try:
        await db_client.disconnect()
    except Exception as e:
        logger.error("DB disconnect failed during shutdown: %s", e)

# --- Safety: allow only SELECT/CTE queries ---
FORBIDDEN = ["insert", "update", "delete", "drop", "truncate", "alter", "create", "replace"]

def is_select_only(sql: str) -> bool:
    q = sql.strip().lower()
    if any(re.search(rf"\b{kw}\b", q) for kw in FORBIDDEN):
        return False
    return q.startswith("select") or q.startswith("with")

# -------- API endpoint --------
@app.post("/analyze")
async def analyze(request: QueryRequest):
    query = request.sql.strip()
    if not query:
        raise HTTPException(status_code=400, detail="SQL query cannot be empty")

    if not is_select_only(query):
        raise HTTPException(status_code=400, detail="Only SELECT/CTE queries are allowed.")

    if request.run_in_sandbox:
        logger.info("Running query in sandbox mode")

    try:
        logger.info(f"Starting analysis for query: {query[:50]}...")
        
        schema_context = await db_client.get_schema_context(query)
        logger.debug(f"Schema context retrieved: {list(schema_context.keys()) if isinstance(schema_context, dict) else 'error'}")
        
        explain_plan = await db_client.explain(query)
        logger.debug(f"Explain plan retrieved: {type(explain_plan)}")

        try:
            sample_rows = await db_client.fetch_sample_rows(query)
        except Exception as e:
            logger.warning(f"Sample rows fetch failed: {e}")
            sample_rows = {"error": str(e)}

        logger.info("Running Query Optimizer agent...")
        opt = await optimize_query(query, schema_context, explain_plan, sample_rows, target_engine="mariadb")
        logger.debug(f"Query Optimizer result: {opt.get('status')}")
        logger.debug(f"Query Optimizer details: {opt.get('details')}")

        logger.info("Running Cost Advisor agent...")
        cost = await estimate_cost(query, explain_plan)
        logger.debug(f"Cost Advisor result: {cost.get('status')}")
        logger.debug(f"Cost Advisor details: {cost.get('details')}")

        logger.info("Running Schema Advisor agent...")
        schema_adv = await advise_schema(query, schema_context)
        logger.debug(f"Schema Advisor result: {schema_adv.get('status')}")
        logger.debug(f"Schema Advisor details: {schema_adv.get('details')}")

        logger.info("Running Data Validator agent...")
        data_val = await validate_query(query, sample_rows)
        logger.debug(f"Data Validator result: {data_val.get('status')}")
        logger.debug(f"Data Validator details: {data_val.get('details')}")

        logger.info("Formatting response...")
        formatted_response = ResponseFormatter.format_analysis(
            original_query=query,
            schema_context=schema_context,
            explain_plan=explain_plan,
            sample_rows=sample_rows,
            optimizer_output=opt,
            cost_output=cost,
            schema_output=schema_adv,
            data_validator_output=data_val,
            database=Config.DB_NAME
        )
        
        logger.debug(f"Final response database: {formatted_response.get('database')}")
        logger.debug(f"Final response optimization: {formatted_response.get('optimization')}")
        logger.info("Analysis complete, returning formatted response")
        return formatted_response

    except Exception as e:
        logger.exception("Analysis failed")
        raise HTTPException(status_code=500, detail=str(e))

# --- Schema overview endpoint used by frontend button ---
@app.post("/analyze-schema")
async def analyze_schema():
    try:
        full_schema = await db_client.get_full_schema()
        return {"database": Config.DB_NAME, "tables": full_schema}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Serve frontend
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    return FileResponse(os.path.join("static", "index.html"))
