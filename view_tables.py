import duckdb

# Connect to the database
conn = duckdb.connect('my_local_database.duckdb')

# List all tables in the database
print("Tables in the database:")
tables = conn.execute("SHOW TABLES").fetchall()
table_names = [table[0] for table in tables]

print("\nRecord Counts:")
for table_name in table_names:
    # Count total records in each table
    row_count = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
    print(f"{table_name}: {row_count} records")

# Optionally, you can print more details
print("\nTable Details:")
for table_name in table_names:
    print(f"\nTable: {table_name}")
    
    # Get table structure
    columns = conn.execute(f"PRAGMA table_info({table_name})").fetchall()
    print("Columns:")
    for column in columns:
        print(f"  - {column[1]} ({column[2]})")

# Close the connection
conn.close()