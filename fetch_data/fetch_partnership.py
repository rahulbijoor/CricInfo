import http.client
import duckdb
import json
import os
import time

def fetch_partnerships_details(match_id):
    """
    Fetch partnership details for a specific match_id
    
    Args:
        match_id (int): Unique identifier for the match
    
    Returns:
        list: List of partnership details or None if fetch fails
    """
    try:
        conn = http.client.HTTPSConnection("cricbuzz-cricket.p.rapidapi.com")
        headers = {
            'x-rapidapi-key': os.getenv("RAPIDAPI_KEY2"),
            'x-rapidapi-host': "cricbuzz-cricket.p.rapidapi.com"
        }
        
        # Fetch scorecard data for the specific match
        conn.request("GET", f"/mcenter/v1/{match_id}/scard", headers=headers)
        res = conn.getresponse()
        data = res.read().decode("utf-8")
        
        # Parse the JSON data
        match_data = json.loads(data)
        
        # Prepare partnerships details list
        partnerships_details = []
        
        # Extract partnerships from each innings
        for scorecard in match_data.get('scoreCard', []):
            match_id = scorecard.get('matchId')
            innings_id = scorecard.get('inningsId')
            
            # Get partnerships data
            partnerships_data = scorecard.get('partnershipsData', {})
            
            # Process each partnership
            for partnership_key, partnership in partnerships_data.items():
                # Extract partnership ID from the key (e.g., 'pat_1' -> 1)
                try:
                    partnership_id = int(partnership_key.split('_')[1])
                except (IndexError, ValueError):
                    partnership_id = 0
                
                partnerships_details.append({
                    'match_id': match_id,
                    'innings_id': innings_id,
                    'partnership_id': partnership_id,
                    'bat1_id': partnership.get('bat1Id', 0),
                    'bat1_name': partnership.get('bat1Name', ''),
                    'bat1_runs': partnership.get('bat1Runs', 0),
                    'bat1_fours': partnership.get('bat1fours', 0),
                    'bat1_sixes': partnership.get('bat1sixes', 0),
                    'bat2_id': partnership.get('bat2Id', 0),
                    'bat2_name': partnership.get('bat2Name', ''),
                    'bat2_runs': partnership.get('bat2Runs', 0),
                    'bat2_fours': partnership.get('bat2fours', 0),
                    'bat2_sixes': partnership.get('bat2sixes', 0),
                    'total_runs': partnership.get('totalRuns', 0),
                    'total_balls': partnership.get('totalBalls', 0)
                })
        
        return partnerships_details
    
    except Exception as e:
        print(f"Error fetching partnerships details for match {match_id}: {e}")
        return None

def store_partnerships_details(db_path):
    """
    Fetch and store partnerships details for international matches
    
    Args:
        db_path (str): Path to DuckDB database
    """
    # Connect to DuckDB
    con = duckdb.connect(db_path)
    
    try:
        # Fetch match_ids from international_matches that don't have corresponding partnerships details
        match_ids = con.execute("""
            SELECT DISTINCT im.match_id 
            FROM international_matches im
        """).fetchall()
        
        for (match_id,) in match_ids:
            # Fetch partnerships details from API
            partnerships_data = fetch_partnerships_details(match_id)
            
            if not partnerships_data:
                print(f"No partnerships data found for match {match_id}")
                continue
            
            # Prepare batch insert
            insert_batch = []
            for partnership in partnerships_data:
                insert_batch.append((
                    partnership['match_id'],
                    partnership['innings_id'],
                    partnership['partnership_id'],
                    partnership['bat1_id'],
                    partnership['bat1_name'],
                    partnership['bat1_runs'],
                    partnership['bat1_fours'],
                    partnership['bat1_sixes'],
                    partnership['bat2_id'],
                    partnership['bat2_name'],
                    partnership['bat2_runs'],
                    partnership['bat2_fours'],
                    partnership['bat2_sixes'],
                    partnership['total_runs'],
                    partnership['total_balls']
                ))
            
            # Batch insert partnerships details
            con.executemany("""
                INSERT INTO partnerships (
                    match_id, 
                    innings_id, 
                    partnership_id,
                    bat1_id, 
                    bat1_name, 
                    bat1_runs, 
                    bat1_fours, 
                    bat1_sixes,
                    bat2_id, 
                    bat2_name, 
                    bat2_runs, 
                    bat2_fours, 
                    bat2_sixes,
                    total_runs,
                    total_balls
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, insert_batch)
            
            print(f"Updated partnerships details for match {match_id}")
            
            # Respect API rate limits
            time.sleep(1)
    
    except Exception as e:
        print(f"Error updating partnerships details: {e}")
    
    finally:
        con.close()

def main():
    # Configuration
    DB_PATH = '\simple_regression\CricInfo\cricket_matches.db'
    
    # Run the update
    store_partnerships_details(DB_PATH)

if __name__ == "__main__":
    main()