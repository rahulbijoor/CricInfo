import http.client
import duckdb
import json
import os
import time

def fetch_match_details(match_id):
    """
    Fetch match details from Cricbuzz API for a given match_id
    
    Args:
        match_id (int): Unique identifier for the match
    
    Returns:
        dict: Parsed match details or None if fetch fails
    """
    try:
        conn = http.client.HTTPSConnection("cricbuzz-cricket.p.rapidapi.com")
        headers = {
            'x-rapidapi-key': os.getenv("RAPIDAPI_KEY2"),
            'x-rapidapi-host': "cricbuzz-cricket.p.rapidapi.com"
        }
        
        # Update the URL to use the dynamic match_id
        conn.request("GET", f"/mcenter/v1/{match_id}/scard", headers=headers)
        res = conn.getresponse()
        data = res.read().decode("utf-8")
        
        # Parse the JSON data
        return json.loads(data)
    except Exception as e:
        print(f"Error fetching details for match {match_id}: {e}")
        return None

def update_match_details(db_path):
    """
    Update match_details table with API data for match_ids from matches table
    
    Args:
        db_path (str): Path to DuckDB database
    """
    # Connect to DuckDB
    con = duckdb.connect(db_path)
    
    try:
        # Fetch all match_ids from matches table that are not in match_details
        match_ids = con.execute("""
            SELECT DISTINCT m.match_id 
            FROM international_matches m
           
        """).fetchall()
        
        for (match_id,) in match_ids:
            # Fetch match details from API
            match_data = fetch_match_details(match_id)
            
            if not match_data or 'matchHeader' not in match_data:
                print(f"No details found for match {match_id}")
                continue
            
            # Extract match header details
            header = match_data['matchHeader']
            
            # Insert match details
            con.execute("""
                INSERT INTO match_details (
                    match_id, 
                    match_description, 
                    match_format, 
                    match_type, 
                    is_complete, 
                    is_domestic, 
                    match_start_timestamp, 
                    match_complete_timestamp, 
                    is_day_night, 
                    match_year, 
                    match_state, 
                    match_status, 
                    toss_winner_id, 
                    toss_winner_name, 
                    toss_decision, 
                    winning_team_id, 
                    winning_team_name, 
                    winning_margin, 
                    is_won_by_runs, 
                    is_won_by_innings, 
                    series_id, 
                    series_name
                ) VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 
                    ?, ?
                )
            """, (
                header.get('matchId'),
                header.get('matchDescription'),
                header.get('matchFormat'),
                header.get('matchType'),
                header.get('complete', False),
                header.get('domestic', False),
                header.get('matchStartTimestamp'),
                header.get('matchCompleteTimestamp'),
                header.get('dayNight', False),
                header.get('year'),
                header.get('state'),
                header.get('status'),
                header.get('tossResults', {}).get('tossWinnerId'),
                header.get('tossResults', {}).get('tossWinnerName'),
                header.get('tossResults', {}).get('decision'),
                header.get('result', {}).get('winningteamId'),
                header.get('result', {}).get('winningTeam'),
                header.get('result', {}).get('winningMargin'),
                header.get('result', {}).get('winByRuns', False),
                header.get('result', {}).get('winByInnings', False),
                header.get('seriesId'),
                header.get('seriesName')
            ))
            
            print(f"Updated details for match {match_id}")
            
            # Respect API rate limits
            time.sleep(1)
    
    except Exception as e:
        print(f"Error updating match details: {e}")
    
    finally:
        con.close()

def main():
    # Configuration
    DB_PATH = 'cricket_matches.db'
    
    # Run the update
    update_match_details(DB_PATH)

if __name__ == "__main__":
    main()