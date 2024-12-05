import http.client
import duckdb
import json
import os
import time

def fetch_match_innings_details(match_id):
    """
    Fetch innings details for a specific match_id
    
    Args:
        match_id (int): Unique identifier for the match
    
    Returns:
        list: Parsed innings details or None if fetch fails
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
        
        # Return the scoreCard which contains innings details
        return match_data.get('scoreCard', [])
    
    except Exception as e:
        print(f"Error fetching innings details for match {match_id}: {e}")
        return None

def store_innings_details(db_path):
    """
    Fetch and store innings details for international matches
    
    Args:
        db_path (str): Path to DuckDB database
    """
    # Connect to DuckDB
    con = duckdb.connect(db_path)
    
    try:
        # Fetch match_ids from international_matches that don't have corresponding innings details
        match_ids = con.execute("""
            SELECT DISTINCT im.match_id 
            FROM international_matches im
            
        """).fetchall()
        
        for (match_id,) in match_ids:
            # Fetch innings details from API
            innings_details = fetch_match_innings_details(match_id)
            
            if not innings_details:
                print(f"No innings details found for match {match_id}")
                continue
            
            # Prepare to insert innings details
            for innings in innings_details:
                try:
                    # Extract innings details
                    con.execute("""
                        INSERT INTO innings_details (
                            match_id,
                            innings_id,
                            time_score,
                            ball_number,
                            is_declared,
                            is_follow_on,
                            overs,
                            revised_overs,
                            run_rate,
                            total_runs,
                            total_wickets,
                            extras_no_balls,
                            extras_total,
                            extras_byes,
                            extras_penalty,
                            extras_wides,
                            extras_leg_byes
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        match_id,
                        innings.get('inningsId'),
                        innings.get('timeScore'),
                        innings.get('scoreDetails', {}).get('ballNbr'),
                        innings.get('scoreDetails', {}).get('isDeclared', False),
                        innings.get('scoreDetails', {}).get('isFollowOn', False),
                        innings.get('scoreDetails', {}).get('overs'),
                        innings.get('scoreDetails', {}).get('revisedOvers', 0),
                        innings.get('scoreDetails', {}).get('runRate'),
                        innings.get('scoreDetails', {}).get('runs'),
                        innings.get('scoreDetails', {}).get('wickets'),
                        innings.get('extrasData', {}).get('noBalls', 0),
                        innings.get('extrasData', {}).get('total', 0),
                        innings.get('extrasData', {}).get('byes', 0),
                        innings.get('extrasData', {}).get('penalty', 0),
                        innings.get('extrasData', {}).get('wides', 0),
                        innings.get('extrasData', {}).get('legByes', 0)
                    ))
                
                except Exception as e:
                    print(f"Error inserting innings details for match {match_id}: {e}")
            
            print(f"Updated innings details for match {match_id}")
            
            # Respect API rate limits
            time.sleep(1)
    
    except Exception as e:
        print(f"Error updating innings details: {e}")
    
    finally:
        con.close()

def main():
    # Configuration
    DB_PATH = '\simple_regression\CricInfo\cricket_matches.db'
    
    # Run the update
    store_innings_details(DB_PATH)

if __name__ == "__main__":
    main()