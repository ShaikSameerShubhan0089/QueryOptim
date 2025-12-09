import subprocess
import sys
import os

def run_init_script():
    try:
        sql_file = os.path.join(os.path.dirname(__file__), "db", "init_db.sql")
        
        commands = [
            "mysql",
            "-h", "127.0.0.1",
            "-u", "root",
            "-e", "DROP DATABASE IF EXISTS testdb; CREATE DATABASE testdb; USE testdb;",
        ]
        
        result = subprocess.run(commands, capture_output=True, text=True, timeout=10)
        
        if result.returncode != 0:
            print(f"✗ Failed to create database: {result.stderr}")
            return False
        
        print("✓ Database created")
        
        commands = [
            "mysql",
            "-h", "127.0.0.1",
            "-u", "root",
            "testdb",
        ]
        
        with open(sql_file, "r") as f:
            script = f.read()
        
        result = subprocess.run(commands, input=script, capture_output=True, text=True, timeout=10)
        
        if result.returncode != 0:
            print(f"✗ Failed to initialize database: {result.stderr}")
            return False
        
        print("✓ Database initialized successfully!")
        return True
        
    except subprocess.TimeoutExpired:
        print("✗ Database initialization timed out")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

if __name__ == "__main__":
    if run_init_script():
        sys.exit(0)
    else:
        sys.exit(1)
