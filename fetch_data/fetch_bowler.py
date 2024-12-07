import http.client
import duckdb
import json
import os
import time

def fetch_bowlers_details(match_id):
    """
    Fetch bowlers details for a specific match_id
    
    Args:
        match_id (int): Unique identifier for the match
    
    Returns:
        list: List of bowlers details or None if fetch fails
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
        
        # Prepare bowlers details list
        bowlers_details = []
        
        # Extract bowlers details from each innings
        for scorecard in match_data.get('scoreCard', []):
            innings_id = scorecard.get('inningsId')
            bowl_team_details = scorecard.get('bowlTeamDetails', {})
            
            # Team details
            bowl_team_id = bowl_team_details.get('bowlTeamId')
            bowl_team_name = bowl_team_details.get('bowlTeamName')
            bowl_team_short_name = bowl_team_details.get('bowlTeamShortName', '')
            
            # Process each bowler
            bowlers_data = bowl_team_details.get('bowlersData', {})
            for bowl_key, bowler in bowlers_data.items():
                bowlers_details.append({
                    'match_id': match_id,
                    'innings_id': innings_id,
                    'bowl_team_id': bowl_team_id,
                    'bowl_team_name': bowl_team_name,
                    'bowl_team_short_name': bowl_team_short_name,
                    'bowler_id': bowler.get('bowlerId'),
                    'bowler_name': bowler.get('bowlName'),
                    'is_captain': bowler.get('isCaptain', False),
                    'is_keeper': bowler.get('isKeeper', False),
                    'overs': bowler.get('overs', 0.0),
                    'maidens': bowler.get('maidens', 0),
                    'runs_conceded': bowler.get('runs', 0),
                    'wickets': bowler.get('wickets', 0),
                    'economy': bowler.get('economy', 0.0),
                    'no_balls': bowler.get('no_balls', 0),
                    'wides': bowler.get('wides', 0),
                    'dot_balls': bowler.get('dots', 0)
                })
        
        return bowlers_details
    
    except Exception as e:
        print(f"Error fetching bowlers details for match {match_id}: {e}")
        return None

def store_bowlers_details(db_path):
    """
    Fetch and store bowlers details for international matches
    
    Args:
        db_path (str): Path to DuckDB database
    """
    # Connect to DuckDB
    con = duckdb.connect(db_path)
    
    try:
        # Fetch match_ids from international_matches that don't have corresponding bowlers details
        match_ids = con.execute("""
            SELECT DISTINCT im.match_id 
            FROM international_matches im
            LEFT JOIN bowlers_details bd ON im.match_id = bd.match_id
            WHERE bd.match_id IS NULL
        """).fetchall()
        
        for (match_id,) in match_ids:
            # Fetch bowlers details from API
            bowlers_data = fetch_bowlers_details(match_id)
            
            if not bowlers_data:
                print(f"No bowlers data found for match {match_id}")
                continue
            
            # Prepare batch insert
            insert_batch = []
            for bowler in bowlers_data:
                insert_batch.append((
                    bowler['match_id'],
                    bowler['innings_id'],
                    bowler['bowl_team_id'],
                    bowler['bowl_team_name'],
                    bowler['bowl_team_short_name'],
                    bowler['bowler_id'],
                    bowler['bowler_name'],
                    bowler['is_captain'],
                    bowler['is_keeper'],
                    bowler['overs'],
                    bowler['maidens'],
                    bowler['runs_conceded'],
                    bowler['wickets'],
                    bowler['economy'],
                    bowler['no_balls'],
                    bowler['wides'],
                    bowler['dot_balls']
                ))
            
            # Batch insert bowlers details
            con.executemany("""
                INSERT INTO bowlers_details (
                    match_id, 
                    innings_id,
                    bowl_team_id,
                    bowl_team_name,
                    bowl_team_short_name,
                    bowler_id, 
                    bowler_name, 
                    is_captain,
                    is_keeper,
                    overs,
                    maidens,
                    runs_conceded,
                    wickets,
                    economy,
                    no_balls,
                    wides,
                    dot_balls
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, insert_batch)
            
            print(f"Updated bowlers details for match {match_id}")
            
            # Respect API rate limits
            time.sleep(1)
    
    except Exception as e:
        print(f"Error updating bowlers details: {e}")
    
    finally:
        con.close()

def main():
    # Configuration
    DB_PATH = '\simple_regression\CricInfo\cricket_matches.db'
    
    # Run the update
    store_bowlers_details(DB_PATH)

if __name__ == "__main__":
    main()