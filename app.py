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

# Setup connection to DuckDB (optional, not used here)
conn = duckdb.connect(database=':memory:', read_only=False)

# Function to fetch match data
def fetch_match_data():
    conn = http.client.HTTPSConnection("cricbuzz-cricket.p.rapidapi.com")
    headers = {
        'x-rapidapi-key': os.getenv("RAPIDAPI_KEY"),
        'x-rapidapi-host': "cricbuzz-cricket.p.rapidapi.com"
    }
    conn.request("GET", "/matches/v1/recent", headers=headers)
    res = conn.getresponse()
    data = res.read()

    try:
        data = json.loads(data.decode("utf-8"))
        type_matches = data.get('typeMatches', [])
    except (json.JSONDecodeError, KeyError):
        print("Error: Unable to decode JSON or missing 'typeMatches' key")
        return pd.DataFrame()

    match_data = []
    for match_type in type_matches:
        for series in match_type.get('seriesMatches', []):
            series_info = series.get('seriesAdWrapper', {})
            for match in series_info.get('matches', []):
                match_info = match.get('matchInfo', {})
                match_score = match.get('matchScore', {})

                team1 = match_info.get('team1', {})
                team2 = match_info.get('team2', {})
                match_data.append({
                    "match_id": match_info.get('matchId', ''),
                    "series_name": match_info.get('seriesName', 'Unknown Series'),
                    "match_desc": match_info.get('matchDesc', ''),
                    "status": match_info.get('status', ''),
                    "venue": match_info.get('venueInfo', {}).get('ground', 'Unknown Ground'),
                    "team1": team1.get('teamName', ''),
                    "team1_id": team1.get('teamId', ''),
                    "team2": team2.get('teamName', ''),
                    "team2_id": team2.get('teamId', ''),
                })

    return pd.DataFrame(match_data)

# Function to fetch player data
def fetch_player_data(match_id, team_id):
    conn = http.client.HTTPSConnection("cricbuzz-cricket.p.rapidapi.com")
    headers = {
        'x-rapidapi-key': os.getenv("RAPIDAPI_KEY"),
        'x-rapidapi-host': "cricbuzz-cricket.p.rapidapi.com"
    }
    endpoint = f"/mcenter/v1/{match_id}/team/{team_id}"
    conn.request("GET", endpoint, headers=headers)
    res = conn.getresponse()
    data = res.read()

    try:
        data = json.loads(data.decode("utf-8"))
        players = data.get('players', {}).get('playing XI', []) + data.get('players', {}).get('bench', [])
        return pd.DataFrame(players)
    except (json.JSONDecodeError, KeyError):
        print("Error: Unable to fetch or decode player data")
        return pd.DataFrame()

# Fetch initial data
df = fetch_match_data()

# Define the layout
app.layout = html.Div(children=[
    html.H1("Cricket Analytics Dashboard"),
    dcc.Dropdown(
        id='match-dropdown',
        options=[{'label': f"{row['team1']} vs {row['team2']}", 'value': row['match_id']}
                 for _, row in df.iterrows()],
        placeholder="Select a match",
    ),
    dcc.Graph(id="score-graph"),
    html.Div(id="player-info"),
])

# Callback to update graph and players info
@app.callback(
    [Output('score-graph', 'figure'),
     Output('player-info', 'children')],
    Input('match-dropdown', 'value')
)
def update_dashboard(match_id):
    if not match_id:
        return px.bar(title="Select a match to view details"), "No players to display."

    match_data = df[df['match_id'] == match_id].iloc[0]
    team1_players = fetch_player_data(match_id, match_data['team1_id'])
    team2_players = fetch_player_data(match_id, match_data['team2_id'])

    # Create player tables
    team1_table = html.Div([
        html.H3(f"{match_data['team1']} Players"),
        html.Table([
            html.Tr([html.Th(col) for col in team1_players.columns]),
            *[html.Tr([html.Td(team1_players.iloc[i][col]) for col in team1_players.columns])
              for i in range(len(team1_players))]
        ])
    ])
    team2_table = html.Div([
        html.H3(f"{match_data['team2']} Players"),
        html.Table([
            html.Tr([html.Th(col) for col in team2_players.columns]),
            *[html.Tr([html.Td(team2_players.iloc[i][col]) for col in team2_players.columns])
              for i in range(len(team2_players))]
        ])
    ])

    # Create the score graph
    fig = px.bar(
        x=[match_data['team1'], match_data['team2']],
        y=[0, 0],  # Replace with actual scores if available
        title=f"Score Comparison: {match_data['team1']} vs {match_data['team2']}",
    )

    return fig, html.Div([team1_table, team2_table])

# Run the app
if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=8050)