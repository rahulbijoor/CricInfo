import duckdb
import pandas as pd

def connect_database(db_path='cricket_matches.db'):
    """
    Establish a connection to the DuckDB database.
    
    Args:
        db_path (str): Path to the database file
    
    Returns:
        duckdb.DuckDBPyConnection: Database connection
    """
    try:
        conn = duckdb.connect(db_path, read_only=True)
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

def load_data(conn, table_name):
    """
    Load data from a specific table in the database.
    
    Args:
        conn (duckdb.DuckDBPyConnection): Database connection
        table_name (str): Name of the table to load
    
    Returns:
        pd.DataFrame: Loaded dataframe
    """
    try:
        df = pd.read_sql(f'SELECT * FROM {table_name}', conn)
        print(f"Loaded {table_name} successfully.")
        print(f"Columns in {table_name}: {df.columns.tolist()}")
        print(f"Shape of {table_name}: {df.shape}")
        print(f"First few rows of {table_name}:")
        print(df.head())
        return df
    except Exception as e:
        print(f"Error loading {table_name}: {e}")
        return pd.DataFrame()

def merge_match_data(international_matches, match_details):
    """
    Merge international matches and match details dataframes.
    
    Args:
        international_matches (pd.DataFrame): International matches dataframe
        match_details (pd.DataFrame): Match details dataframe
    
    Returns:
        pd.DataFrame: Merged dataframe
    """
    if not international_matches.empty and not match_details.empty:
        try:
            # Print merge information
            print("International Matches Shape:", international_matches.shape)
            print("Match Details Shape:", match_details.shape)
            
            # Attempt merge with different strategies
            merged_df = pd.merge(international_matches, match_details, on='match_id', how='left')
            
            # Ensure series information
            if 'series_name' not in merged_df.columns:
                if 'series_name_x' in merged_df.columns:
                    merged_df['series_name'] = merged_df['series_name_x']
                elif 'series_name_y' in merged_df.columns:
                    merged_df['series_name'] = merged_df['series_name_y']
            
            # Logging merged dataframe information
            print("Merged DataFrame Shape:", merged_df.shape)
            print("Merged DataFrame Columns:", merged_df.columns.tolist())
            
            return merged_df
        except Exception as e:
            print(f"Merge error: {e}")
            return international_matches
    return pd.DataFrame()