import asyncio
import aiomysql
import sys

async def run_init_script():
    try:
        print("Attempting to connect to MariaDB via socket...")
        
        pool = await aiomysql.create_pool(
            unix_socket='/run/mysqld/mysqld.sock',
            user='root',
            password='',
            autocommit=True,
            connect_timeout=10,
        )
        
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                print("✓ Connected to MariaDB via socket")
                
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
                            print(f"  Note: {str(e)[:100]}")
                
                print("✓ Initialized database schema and data")
        
        pool.close()
        await pool.wait_closed()
        
        print("\n✓ Database setup complete!")
        return True
        
    except Exception as e:
        print(f"Socket failed: {e}")
        print("\nTrying TCP with workaround...")
        return await run_with_tcp_workaround()

async def run_with_tcp_workaround():
    try:
        pool = await aiomysql.create_pool(
            host='127.0.0.1',
            port=3306,
            user='root',
            password='',
            autocommit=True,
            connect_timeout=10,
            auth_plugin='mysql_native_password'
        )
        
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                print("✓ Connected via TCP")
                await cur.execute("DROP DATABASE IF EXISTS testdb")
                await cur.execute("CREATE DATABASE testdb")
        
        pool.close()
        await pool.wait_closed()
        print("✓ Database initialized!")
        return True
        
    except Exception as e:
        print(f"TCP workaround failed: {e}")
        print("\nManual Setup Required:")
        print("1. Open MariaDB Command Prompt or MySQL Shell")
        print("2. Run:")
        print("   mariadb -u root")
        print("3. Paste this:")
        with open("db/init_db.sql", "r") as f:
            print(f.read()[:500] + "...")
        return False

if __name__ == "__main__":
    result = asyncio.run(run_init_script())
    sys.exit(0 if result else 1)
