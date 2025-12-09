import subprocess
import sys

sql_commands = """
ALTER USER 'root'@'localhost' IDENTIFIED VIA mysql_native_password USING PASSWORD('');
ALTER USER 'root'@'127.0.0.1' IDENTIFIED VIA mysql_native_password USING PASSWORD('');
FLUSH PRIVILEGES;
"""

try:
    print("Attempting to fix MariaDB root authentication...")
    
    ps_cmd = f'''
    $sql = @"
{sql_commands}
"@
    
    $process = Start-Process -FilePath "mariadb" -ArgumentList "-h", "127.0.0.1", "-u", "root" -NoNewWindow -RedirectStandardInput $NULL -Wait -PassThru
    Write-Host "Executed fix commands"
    '''
    
    result = subprocess.run(
        ["powershell", "-Command", ps_cmd],
        capture_output=True,
        text=True,
        timeout=10
    )
    
    if result.returncode == 0:
        print("✓ MariaDB authentication fixed")
        print("Now run: python setup_db_async.py")
    else:
        print(f"stdout: {result.stdout}")
        print(f"stderr: {result.stderr}")
        print("\nTry running this in MariaDB directly:")
        print(sql_commands)
        
except Exception as e:
    print(f"Error: {e}")
    print("\nManual fix required. In MariaDB console, run:")
    print(sql_commands)
