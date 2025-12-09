import asyncio
import aiomysql
import sys

async def run_init_script():
    try:
        print("Attempting to connect to MariaDB...")
        
        pool = await aiomysql.create_pool(
            host='127.0.0.1',
            user='root',
            password='',
            port=3306,
            autocommit=True,
            connect_timeout=10,
        )
        
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                print("✓ Connected to MariaDB")
                
                await cur.execute("DROP DATABASE IF EXISTS testdb")
                print("✓ Dropped old testdb")
                
                await cur.execute("CREATE DATABASE testdb")
                print("✓ Created testdb database")
                
        await asyncio.sleep(0.5)
        
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute("USE testdb")
                
                with open("db/init_db.sql", "r") as f:
                    script = f.read()
                
                for statement in script.split(";"):
                    statement = statement.strip()
                    if statement and "USE testdb" not in statement and "DROP DATABASE" not in statement and "CREATE DATABASE" not in statement:
                        try:
                            await cur.execute(statement)
                        except Exception as e:
                            print(f"  Warning: {e}")
                
                print("✓ Initialized database schema and data")
        
        pool.close()
        await pool.wait_closed()
        
        print("\n✓ Database initialized successfully!")
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(run_init_script())
    sys.exit(0 if result else 1)
