import duckdb

def drop_columns_from_match_details(db_path):
    """
    Drop specified columns from match_details table
    
    Args:
        db_path (str): Path to the DuckDB database
    """
    # Connect to the database
    con = duckdb.connect(db_path)
    
    try:
        # List of columns to drop
        columns_to_drop = [
            'match_description',
            'match_format', 
            'match_type', 
            'is_domestic', 
            'match_start_timestamp', 
            'match_complete_timestamp'
        ]
        
        # Drop each column
        for column in columns_to_drop:
            try:
                con.execute(f"ALTER TABLE match_details DROP COLUMN IF EXISTS {column}")
                print(f"Successfully dropped column: {column}")
            except Exception as e:
                print(f"Error dropping column {column}: {e}")
        
        # Verify remaining columns
        print("\nRemaining columns in match_details:")
        result = con.execute("DESCRIBE match_details").fetchall()
        for column in result:
            print(column[0])
    
    except Exception as e:
        print(f"An error occurred: {e}")
    
    finally:
        # Close the database connection
        con.close()

def main():

    DB_PATH = 'cricket_matches.db'
    

    drop_columns_from_match_details(DB_PATH)

if __name__ == "__main__":
    main()