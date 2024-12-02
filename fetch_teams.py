import http.client
import json
import duckdb

# Cricbuzz API Configuration
CRICBUZZ_API_HOST = "cricbuzz-cricket.p.rapidapi.com"
CRICBUZZ_API_KEY = "7326019f34mshbc97d432ec40833p17533djsnea484f172332"
ENDPOINT = "/teams/v1/international"

# DuckDB Database Configuration
DUCKDB_FILE = "my_local_database.duckdb"
TABLE_NAME = "teams"

def fetch_team_data():
    """Fetch team data from the Cricbuzz API."""
    conn = http.client.HTTPSConnection(CRICBUZZ_API_HOST)
    headers = {
        'x-rapidapi-key': CRICBUZZ_API_KEY,
        'x-rapidapi-host': CRICBUZZ_API_HOST
    }
    conn.request("GET", ENDPOINT, headers=headers)
    response = conn.getresponse()
    if response.status != 200:
        raise Exception(f"API request failed with status {response.status}")
    data = response.read()
    return json.loads(data.decode("utf-8"))

def store_data_in_duckdb(data):
    """Store the team data in a DuckDB table."""
    # Extract team details
    teams = []
    for team in data.get("list", []):
        if "teamId" in team and "teamName" in team and "teamSName" in team and "imageId" in team:
            teams.append((team["teamId"], team["teamName"], team["teamSName"], team["imageId"]))

    if not teams:
        print("No team data to insert.")
        return

    # Connect to DuckDB and create table
    conn = duckdb.connect(DUCKDB_FILE)
    conn.execute(f"""
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            teamId INTEGER,
            teamName TEXT,
            teamSName TEXT,
            imageId INTEGER
        )
    """)
    
    # Insert data
    conn.executemany(f"INSERT INTO {TABLE_NAME} VALUES (?, ?, ?, ?)", teams)
    print(f"Inserted {len(teams)} records into {TABLE_NAME} table.")

if __name__ == "__main__":
    try:
        print("Fetching team data...")
        team_data = fetch_team_data()
        print("Storing team data in DuckDB...")
        store_data_in_duckdb(team_data)
        print("Team data successfully stored.")
    except Exception as e:
        print(f"An error occurred: {e}")