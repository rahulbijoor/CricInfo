import http.client
import duckdb
import json
import os
import time

def fetch_batsmen_details(match_id):
    """
    Fetch batsmen details for a specific match_id
    
    Args:
        match_id (int): Unique identifier for the match
    
    Returns:
        list: List of batsmen details or None if fetch fails
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
        
        # Prepare batsmen details list
        batsmen_details = []
        
        # Extract batsmen details from each innings
        for scorecard in match_data.get('scoreCard', []):
            innings_id = scorecard.get('inningsId')
            bat_team_details = scorecard.get('batTeamDetails', {})
            
            # Team details
            bat_team_id = bat_team_details.get('batTeamId')
            bat_team_name = bat_team_details.get('batTeamName')
            bat_team_short_name = bat_team_details.get('batTeamShortName')
            
            # Process each batsman
            batsmen_data = bat_team_details.get('batsmenData', {})
            for bat_key, batsman in batsmen_data.items():
                batsmen_details.append({
                    'match_id': match_id,
                    'innings_id': innings_id,
                    'bat_team_id': bat_team_id,
                    'bat_team_name': bat_team_name,
                    'bat_team_short_name': bat_team_short_name,
                    'batsman_id': batsman.get('batId'),
                    'batsman_name': batsman.get('batName'),
                    'is_captain': batsman.get('isCaptain', False),
                    'is_keeper': batsman.get('isKeeper', False),
                    'runs': batsman.get('runs', 0),
                    'balls_faced': batsman.get('balls', 0),
                    'dots': batsman.get('dots', 0),
                    'fours': batsman.get('fours', 0),
                    'sixes': batsman.get('sixes', 0),
                    'minutes': batsman.get('mins', 0),
                    'strike_rate': batsman.get('strikeRate', 0.0),
                    'out_description': batsman.get('outDesc', ''),
                    'bowler_id': batsman.get('bowlerId', 0),
                    'fielder1_id': batsman.get('fielderId1', 0),
                    'fielder2_id': batsman.get('fielderId2', 0),
                    'fielder3_id': batsman.get('fielderId3', 0),
                    'wicket_code': batsman.get('wicketCode', '')
                })
        
        return batsmen_details
    
    except Exception as e:
        print(f"Error fetching batsmen details for match {match_id}: {e}")
        return None

def store_batsmen_details(db_path):
    """
    Fetch and store batsmen details for international matches
    
    Args:
        db_path (str): Path to DuckDB database
    """
    # Connect to DuckDB
    con = duckdb.connect(db_path)
    
    try:
        # Fetch match_ids from international_matches that don't have corresponding batsmen details
        match_ids = con.execute("""
            SELECT DISTINCT im.match_id 
            FROM international_matches im
            
        """).fetchall()
        
        for (match_id,) in match_ids:
            # Fetch batsmen details from API
            batsmen_data = fetch_batsmen_details(match_id)
            
            if not batsmen_data:
                print(f"No batsmen data found for match {match_id}")
                continue
            
            # Prepare batch insert
            insert_batch = []
            for batsman in batsmen_data:
                insert_batch.append((
                    batsman['match_id'],
                    batsman['innings_id'],
                    batsman['bat_team_id'],
                    batsman['bat_team_name'],
                    batsman['bat_team_short_name'],
                    batsman['batsman_id'],
                    batsman['batsman_name'],
                    batsman['is_captain'],
                    batsman['is_keeper'],
                    batsman['runs'],
                    batsman['balls_faced'],
                    batsman['dots'],
                    batsman['fours'],
                    batsman['sixes'],
                    batsman['minutes'],
                    batsman['strike_rate'],
                    batsman['out_description'],
                    batsman['bowler_id'],
                    batsman['fielder1_id'],
                    batsman['fielder2_id'],
                    batsman['fielder3_id'],
                    batsman['wicket_code']
                ))
            
            # Batch insert batsmen details
            con.executemany("""
                INSERT INTO batsmen_details (
                    match_id, 
                    innings_id,
                    bat_team_id, 
                    bat_team_name, 
                    bat_team_short_name, 
                    batsman_id, 
                    batsman_name, 
                    is_captain, 
                    is_keeper, 
                    runs, 
                    balls_faced, 
                    dots, 
                    fours, 
                    sixes, 
                    minutes, 
                    strike_rate, 
                    out_description, 
                    bowler_id, 
                    fielder1_id, 
                    fielder2_id, 
                    fielder3_id, 
                    wicket_code
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, insert_batch)
            
            print(f"Updated batsmen details for match {match_id}")
            
            # Respect API rate limits
            time.sleep(1)
    
    except Exception as e:
        print(f"Error updating batsmen details: {e}")
    
    finally:
        con.close()

def main():
    # Configuration
    DB_PATH = '\simple_regression\CricInfo\cricket_matches.db'
    
    # Run the update
    store_batsmen_details(DB_PATH)

if __name__ == "__main__":
    main()