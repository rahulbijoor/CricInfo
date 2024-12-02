import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import duckdb
import pandas as pd
import os
import http.client
import json

# Initialize the Dash app
app = dash.Dash(__name__)
app.title = "Cricket Analytics Dashboard"

# Setup connection to DuckDB
conn = duckdb.connect(database='my_local_database.duckdb', read_only=False)

# Function to fetch and parse match data from the API
def fetch_match_data():
    conn = http.client.HTTPSConnection("cricbuzz-cricket.p.rapidapi.com")
    
    headers = {
        'x-rapidapi-key': os.getenv("RAPIDAPI_KEY2"),
        'x-rapidapi-host': "cricbuzz-cricket.p.rapidapi.com"
    }

    # Send GET request to fetch data
    conn.request("GET", "/matches/v1/recent", headers=headers)
    res = conn.getresponse()
    data = res.read()

    # Load the JSON response and check for 'typeMatches'
    try:
        data = json.loads(data.decode("utf-8"))
        type_matches = data.get('typeMatches', [])
    except (json.JSONDecodeError, KeyError):
        print("Error: Unable to decode JSON or missing 'typeMatches' key")
        return pd.DataFrame()

    match_data = []
    for match_type in type_matches:
        for series in match_type.get('seriesMatches', []):
            # Navigate into the 'seriesAdWrapper' to access match details
            series_info = series.get('seriesAdWrapper', {})
            for match in series_info.get('matches', []):
                match_info = match.get('matchInfo', {})
                match_score = match.get('matchScore', {})

                # Extract relevant details
                team1 = match_info.get('team1', {})
                team2 = match_info.get('team2', {})
                team1_score = match_score.get('team1Score', {}).get('inngs1', {})
                team2_score = match_score.get('team2Score', {}).get('inngs1', {})

                # Append data
                match_data.append({
                    "match_id": match_info.get('matchId', ''),
                    "series_name": match_info.get('seriesName', 'Unknown Series'),
                    "match_desc": match_info.get('matchDesc', ''),
                    "status": match_info.get('status', ''),
                    "venue": match_info.get('venueInfo', {}).get('ground', 'Unknown Ground'),
                    "team1": team1.get('teamName', ''),
                    "team1_score": team1_score.get('runs', 0),
                    "team1_wickets": team1_score.get('wickets', 0),
                    "team2": team2.get('teamName', ''),
                    "team2_score": team2_score.get('runs', 0),
                    "team2_wickets": team2_score.get('wickets', 0),
                })

    if not match_data:
        print("Error: No match data found in response")
        return pd.DataFrame()

    return pd.DataFrame(match_data)

# Fetch initial data
df_matches = fetch_match_data()
if df_matches.empty:
    print("Error: No data retrieved from the API.")
else:
    print("Data retrieved successfully:")
    print(df_matches.head())

# Create a table in DuckDB to store match data
conn.execute("""
    CREATE TABLE IF NOT EXISTS matches (
        match_id INTEGER,
        series_name STRING,
        match_desc STRING,
        status STRING,
        venue STRING,
        team1 STRING,
        team1_score INTEGER,
        team1_wickets INTEGER,
        team2 STRING,
        team2_score INTEGER,
        team2_wickets INTEGER
    )
""")

# Insert data into DuckDB
for match in df_matches.itertuples(index=False):
    conn.execute("""
        INSERT INTO matches (
            match_id, series_name, match_desc, status, venue, 
            team1, team1_score, team1_wickets, team2, team2_score, team2_wickets
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (match.match_id, match.series_name, match.match_desc, match.status, match.venue,
          match.team1, match.team1_score, match.team1_wickets, match.team2, match.team2_score, match.team2_wickets))

print("Data inserted successfully")

# Define the layout of the Dash app
app.layout = html.Div(children=[
    html.H1("Cricket Analytics Dashboard"),

    # Dropdown to select match
    dcc.Dropdown(
        id='match-dropdown',
        options=[{'label': f"{row['team1']} vs {row['team2']}", 'value': row['match_id']}
                 for _, row in df_matches.iterrows()],
        placeholder="Select a match",
    ),

    # Button to fetch player info
    html.Button("Show Player Info", id="player-info-btn", n_clicks=0),

    # Graph to show data visualization
    dcc.Graph(id="score-graph"),

    # Placeholder for player info
    html.Div(id="player-info")
])

# Callback to update graph based on selected match
@app.callback(
    Output('score-graph', 'figure'),
    Input('match-dropdown', 'value')
)
def update_graph(match_id):
    if match_id:
        # Query DuckDB for the selected match's score data
        query = f"SELECT * FROM matches WHERE match_id = {match_id}"
        match_data = conn.execute(query).fetchdf()
        
        # Extracting team names and scores for visualization
        team1 = match_data.iloc[0]['team1']
        team2 = match_data.iloc[0]['team2']
        team1_score = match_data.iloc[0]['team1_score']
        team2_score = match_data.iloc[0]['team2_score']
        team1_wickets = match_data.iloc[0]['team1_wickets']
        team2_wickets = match_data.iloc[0]['team2_wickets']
        
        # Create a DataFrame for easy plotting
        score_data = pd.DataFrame({
            "Team": [team1, team2],
            "Runs": [team1_score, team2_score],
            "Wickets": [team1_wickets, team2_wickets]
        })

        # Plotting a bar chart to compare runs
        fig = px.bar(
            score_data,
            x="Team",
            y="Runs",
            color="Team",
            text="Wickets",
            title=f"Score Comparison: {team1} vs {team2}",
            labels={"Runs": "Total Runs", "Wickets": "Wickets Lost"}
        )
        fig.update_traces(texttemplate="Wickets: %{text}", textposition="outside")

    else:
        fig = px.bar(title="Select a match to view details")

    return fig

conn.execute("""
    CREATE TABLE IF NOT EXISTS players (
        match_id INTEGER,
        team_id INTEGER,
        player_id INTEGER,
        player_name STRING,
        role STRING,
        batting_style STRING,
        bowling_style STRING,
        substitute BOOLEAN,
        captain BOOLEAN
    )
""")


def fetch_player_data(match_id, team_id):
    http_conn = http.client.HTTPSConnection("cricbuzz-cricket.p.rapidapi.com")  # Renamed to `http_conn`
    headers = {
        'x-rapidapi-key': os.getenv("RAPIDAPI_KEY2"),
        'x-rapidapi-host': "cricbuzz-cricket.p.rapidapi.com"
    }
    endpoint = f"/mcenter/v1/{match_id}/team/{team_id}"
    http_conn.request("GET", endpoint, headers=headers)
    res = http_conn.getresponse()
    data = res.read()

    # Parse the JSON response
    try:
        data = json.loads(data.decode("utf-8"))
        players_data = data.get("players", {})
        playing_xi = players_data.get("playing XI", [])
        bench = players_data.get("bench", [])

        # Combine playing XI and bench data
        all_players = playing_xi + bench

        if not all_players:
            return pd.DataFrame()

        # Convert to DataFrame
        player_data = pd.DataFrame([
            {
                "match_id": match_id,
                "team_id": team_id,
                "player_id": player['id'],
                "player_name": player['fullName'],
                "role": player['role'],
                "batting_style": player.get('battingStyle', ''),
                "bowling_style": player.get('bowlingStyle', ''),
                "substitute": player.get('substitute', False),
                "captain": player.get('captain', False)
            }
            for player in all_players
        ])

        # Insert into DuckDB
        for player in player_data.itertuples(index=False):
            conn.execute("""
                INSERT INTO players (match_id, team_id, player_id, player_name, role, batting_style, bowling_style, substitute, captain)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (player.match_id, player.team_id, player.player_id, player.player_name, player.role, player.batting_style, player.bowling_style, player.substitute, player.captain))
        print(player_data)
        return player_data

    except (json.JSONDecodeError, KeyError) as e:
        print(f"Error fetching player data: {e}")
        return pd.DataFrame()

    
@app.callback(
    Output('player-info', 'children'),
    [Input('player-info-btn', 'n_clicks'),
     Input('match-dropdown', 'value')]
)
def display_player_info(n_clicks, match_id):
    if n_clicks > 0 and match_id:
        try:
            # Query DuckDB for players of both teams
            query = f"SELECT * FROM players WHERE match_id = {match_id}"
            player_data = conn.execute(query).fetchdf()
            query_match = f"SELECT team1, team2 FROM matches WHERE match_id = {match_id}"
            match_data = conn.execute(query_match).fetchdf()
            
            # Query to get team IDs for both teams
            query_team_ids = f"""
            SELECT teamId, teamName 
            FROM teams 
            WHERE teamName IN ('{match_data['team1'][0]}', '{match_data['team2'][0]}')
            """
            team_data = conn.execute(query_team_ids).fetchdf()
            print(team_data)
            # Fetch player data for both teams
            team1_id = team_data[team_data['teamName'] == match_data['team1'][0]]['teamId'].values[0]
            team2_id = team_data[team_data['teamName'] == match_data['team2'][0]]['teamId'].values[0]
            
            if player_data.empty:
                # Fetch from API if not in DuckDB
                fetch_player_data(match_id, team1_id)  # For team 1
                fetch_player_data(match_id, team2_id)  # For team 2
                player_data = conn.execute(query).fetchdf()

            # Generate player info for display
            player_info_divs = []

            for team_id in player_data['team_id'].unique():
                team_players = player_data[player_data['team_id'] == team_id]
                playing_xi = team_players[team_players['substitute'] == False]
                bench = team_players[team_players['substitute'] == True]

                player_info_divs.append(html.H3(f"Team {team_id} - Playing XI"))
                player_info_divs.extend([
                    html.P(
                        f"{row['player_name']} - {row['role']} {'(C)' if row['captain'] else ''} "
                        f"({row['batting_style']} / {row['bowling_style']})"
                    )
                    for _, row in playing_xi.iterrows()
                ])

                player_info_divs.append(html.H3(f"Team {team_id} - Bench"))
                player_info_divs.extend([
                    html.P(f"{row['player_name']} - {row['role']} ({row['batting_style']} / {row['bowling_style']})")
                    for _, row in bench.iterrows()
                ])

            return html.Div(player_info_divs)

        except Exception as e:
            return f"Error retrieving player data: {str(e)}"
    
    elif n_clicks > 0:
        return "Please select a match first."

    return "Player info will appear here after clicking the button."



# Run the app
if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=8050)
