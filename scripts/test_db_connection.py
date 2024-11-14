import os
import sys
import pyodbc
from dotenv import load_dotenv

def test_sql_server_connection():
    """Test connection to SQL Server database"""
    load_dotenv()

    # Get connection parameters from environment variables
    params = {
        'driver': os.getenv('DB_DRIVER', 'ODBC Driver 17 for SQL Server'),
        'server': os.getenv('DB_HOST', 'localhost'),
        'database': os.getenv('DB_NAME', 'nemy_pos'),
        'user': os.getenv('DB_USER', 'sa'),
        'password': os.getenv('DB_PASSWORD'),
        'port': os.getenv('DB_PORT', '1433'),
    }

    try:
        # Build connection string
        conn_str = (
            f"DRIVER={{{params['driver']}}};"
            f"SERVER={params['server']},{params['port']};"
            f"DATABASE={params['database']};"
            f"UID={params['user']};"
            f"PWD={params['password']};"
            "Encrypt=yes;TrustServerCertificate=yes;"
        )

        # Try to establish connection
        print("Attempting to connect to SQL Server...")
        conn = pyodbc.connect(conn_str, timeout=30)
        
        # Test the connection
        cursor = conn.cursor()
        cursor.execute("SELECT @@VERSION")
        row = cursor.fetchone()
        
        print("\nConnection successful!")
        print(f"SQL Server version: {row[0]}\n")

        # Test database permissions
        print("Testing database permissions...")
        cursor.execute("SELECT HAS_DBACCESS('nemy_pos')")
        has_access = cursor.fetchone()[0]
        print(f"Database access: {'Granted' if has_access else 'Denied'}\n")

        cursor.close()
        conn.close()
        return True

    except pyodbc.Error as e:
        print(f"\nError connecting to SQL Server: {str(e)}")
        print("\nTroubleshooting steps:")
        print("1. Verify SQL Server is running")
        print("2. Check credentials in .env file")
        print("3. Ensure SQL Server allows remote connections")
        print("4. Verify ODBC Driver is installed")
        print("5. Check firewall settings")
        return False

if __name__ == "__main__":
    success = test_sql_server_connection()
    sys.exit(0 if success else 1) 