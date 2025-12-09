import os
import glob

common_paths = [
    r"C:\Program Files\MariaDB*\bin",
    r"C:\Program Files (x86)\MariaDB*\bin",
    r"C:\MySQL\bin",
    r"C:\MariaDB\bin",
    r"C:\ProgramData\MariaDB*\bin",
]

for pattern in common_paths:
    results = glob.glob(pattern, recursive=False)
    for path in results:
        mysql_exe = os.path.join(path, "mysql.exe")
        if os.path.exists(mysql_exe):
            print(f"Found: {mysql_exe}")
            print(f"\nRun this in cmd.exe:")
            print(f'  "{mysql_exe}" -h 127.0.0.1 -u root')
            exit(0)

print("mysql.exe not found in common locations")
print("\nSearching C:\ (this may take a while)...")

for root, dirs, files in os.walk("C:\\", topdown=True):
    dirs[:] = [d for d in dirs if d not in ['.git', 'AppData', '$Recycle.bin', 'System Volume Information']]
    if 'mysql.exe' in files:
        mysql_path = os.path.join(root, 'mysql.exe')
        print(f"Found: {mysql_path}")
        print(f"\nRun this in cmd.exe:")
        print(f'  "{mysql_path}" -h 127.0.0.1 -u root')
        exit(0)

print("Still not found")
