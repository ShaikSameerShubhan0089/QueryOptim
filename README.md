# MariaDB Query Optimizer + Claude Agents

Final, ready-to-run project that runs 4 Claude-powered agents (Query Optimizer, Schema Advisor, Cost Advisor, Data Validator)
against a MariaDB database. It exposes a FastAPI `/analyze` endpoint and includes a simple frontend.

## Quick start

1. Copy files into `mariadb-query-optimizer` folder (exact structure).
2. Create virtualenv and activate:
   ```
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   ```
3. Install deps:
   ```
   pip install -r requirements.txt
   ```
4. Set up MariaDB:
   - Install MariaDB locally.
   - Run `mysql -u root -p < db/init_db.sql` to create testdb and sample data.
5. Set environment variables:
   - Copy `.env.example` to `.env`.
   - Set `CLAUDE_API_KEY` to your Anthropic API key.
   - Adjust DB settings if needed (defaults to localhost:3306, user=appuser, pass=app_pass123, db=testdb).
6. Run the server:
   ```
   ./run.sh
   ```
   Or `uvicorn main:app --reload --host 0.0.0.0 --port 8000`
7. Open http://localhost:8000 in browser.
8. Paste a SELECT query (e.g., `SELECT * FROM customers c JOIN sales s ON c.customer_id = s.customer_id WHERE s.sale_amount > 100;`), click Run Analysis.
9. View optimized query, recommendations, warnings, explain plan, sample rows, and AI insights.

## Features

- **Query Optimization**: Rewrites queries for better performance, suggests indexes.
- **Schema Advice**: Recommends indexes, partitioning, column changes.
- **Cost Estimation**: Estimates IO/runtime costs, tips to reduce.
- **Data Validation**: Checks sample rows for quality issues.
- **Safety**: Only allows SELECT/CTE queries; blocks DML/DDL.
- **Frontend**: Simple UI for input/analysis.
- **Async**: Uses aiomysql for non-blocking DB ops.

## Troubleshooting

- **Claude errors**: Ensure CLAUDE_API_KEY is valid and has quota. Use latest model (claude-3-5-sonnet-20241022). If 404, check key validity.
- **DB connection**: Ensure MariaDB is running, credentials correct in .env.
- **JSON parsing**: Claude responses may vary; improved parsing with fallbacks.
- **No sample rows**: Query might be complex; check logs.
- **Import errors**: Ensure all deps installed (`pip install -r requirements.txt`).

## Architecture

- `main.py`: FastAPI app, endpoints, agent orchestration.
- `agents/`: 4 Claude agents with MariaDB-specific prompts.
- `utils/claude_client.py`: Async Claude API calls with retries.
- `db/mariadb_client.py`: Async MariaDB client for EXPLAIN, samples, schema.
- `static/`: Frontend HTML/JS/CSS.
- `db/init_db.sql`: Sample DB setup.
# project-2
# project-2
# project-2
