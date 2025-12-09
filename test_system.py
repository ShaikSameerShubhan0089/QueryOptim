#!/usr/bin/env python3

import asyncio
import sys
import json

async def test_system():
    """Test all agent modules for import and basic functionality."""
    
    print("=" * 60)
    print("MariaDB Query Optimizer - System Test")
    print("=" * 60)
    
    try:
        print("\n[1/7] Testing Config module...")
        from utils.config import Config
        print(f"     ✓ Config loaded: DB={Config.DB_NAME}, Host={Config.DB_HOST}")
        
        print("\n[2/7] Testing ResponseFormatter module...")
        from utils.response_formatter import ResponseFormatter
        print("     ✓ ResponseFormatter loaded")
        
        print("\n[3/7] Testing MariaDB client...")
        from db.mariadb_client import MariaDBClient
        db_client = MariaDBClient(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME,
            port=Config.DB_PORT
        )
        print("     ✓ MariaDB client initialized")
        
        print("\n[4/7] Testing Query Optimizer agent...")
        from agents.query_optimizer import optimize_query
        print("     ✓ Query Optimizer imported")
        
        print("\n[5/7] Testing Cost Advisor agent...")
        from agents.cost_advisor import estimate_cost
        print("     ✓ Cost Advisor imported")
        
        print("\n[6/7] Testing Schema Advisor agent...")
        from agents.schema_advisor import advise_schema
        print("     ✓ Schema Advisor imported")
        
        print("\n[7/7] Testing Data Validator agent...")
        from agents.data_validator import validate_query
        print("     ✓ Data Validator imported")
        
        print("\n" + "=" * 60)
        print("✅ All modules loaded successfully!")
        print("=" * 60)
        
        print("\nTesting agent responses (this will call Groq API)...")
        print("-" * 60)
        
        await db_client.connect()
        if db_client.pool:
            print("✓ Database connection successful\n")
            
            test_query = "SELECT customer_id, customer_name, email FROM customers LIMIT 5"
            print(f"Test Query: {test_query}\n")
            
            schema = await db_client.get_schema_context(test_query)
            explain = await db_client.explain(test_query)
            sample_rows = await db_client.fetch_sample_rows(test_query)
            
            print("Running agents...")
            opt = await optimize_query(test_query, schema, explain, sample_rows)
            cost = await estimate_cost(test_query, explain)
            sch_adv = await advise_schema(test_query, schema)
            data_val = await validate_query(test_query, sample_rows)
            
            print(f"\n✓ Query Optimizer: {opt.get('status')}")
            if opt.get('status') == 'success':
                print(f"  - Impact: {opt['details'].get('estimated_impact', 'N/A')}")
            
            print(f"✓ Cost Advisor: {cost.get('status')}")
            if cost.get('status') == 'success':
                print(f"  - Cost: {cost['details'].get('estimated_cost', 'N/A')}")
            
            print(f"✓ Schema Advisor: {sch_adv.get('status')}")
            print(f"✓ Data Validator: {data_val.get('status')}")
            
            print("\n" + "-" * 60)
            print("Testing ResponseFormatter...")
            
            formatted = ResponseFormatter.format_analysis(
                original_query=test_query,
                schema_context=schema,
                explain_plan=explain,
                sample_rows=sample_rows,
                optimizer_output=opt,
                cost_output=cost,
                schema_output=sch_adv,
                data_validator_output=data_val,
                database=Config.DB_NAME
            )
            
            print(f"✓ Response formatted successfully")
            print(f"  Keys: {', '.join(formatted.keys())}")
            
            await db_client.disconnect()
        else:
            print("✗ Database connection failed")
            return False
        
        print("\n" + "=" * 60)
        print("✅ All tests passed!")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(test_system())
    sys.exit(0 if result else 1)
