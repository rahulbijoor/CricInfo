import dash
from dash import dcc, html, Input, Output, dash_table
import plotly.graph_objects as go
import duckdb
import plotly.express as px  # Required for consistent colors

# Initialize Dash app
app = dash.Dash(__name__)
app.title = "Cricket Dashboard"

# Load data from DuckDB
def load_data(query):
    con = duckdb.connect('cricket_matches.db', read_only=True)
    return con.execute(query).df()

# Queries for data
def get_international_matches():
    return load_data("SELECT * FROM international_matches")

def get_team_wins():
    return load_data("""
        SELECT winning_team_name, COUNT(*) as wins
        FROM match_details
        WHERE is_complete = TRUE
        GROUP BY winning_team_name
        ORDER BY wins DESC
    """)

def get_match_formats():
    return load_data("""
        SELECT match_format, COUNT(*) as count
        FROM international_matches
        GROUP BY match_format
    """)

# Load static data
data_international_matches = get_international_matches()
data_team_wins = get_team_wins()
data_match_formats = get_match_formats()

# Layout
app.layout = html.Div([
    dcc.Tabs([
        dcc.Tab(label="Overview", children=[
            html.H2("International Matches Overview"),
            dash_table.DataTable(
                id="international-matches-table",
                columns=[{"name": col, "id": col} for col in data_international_matches.columns],
                data=data_international_matches.to_dict("records"),
                style_table={'overflowX': 'auto'},
                page_size=10,
                row_selectable="single"
            ),
            html.Div([
                dcc.Graph(
                    id="team-wins-bar",
                    figure=px.bar(data_team_wins, x="winning_team_name", y="wins", title="Teams by Number of Wins")
                )
            ]),
            html.Div([
                dcc.Graph(
                    id="match-format-pie",
                    figure=px.pie(data_match_formats, names="match_format", values="count", title="Match Formats")
                )
            ])
        ]),
        dcc.Tab(label="Match Details", children=[
            html.H2("Match Scorecard and Partnerships"),
            html.Div([
                html.Label("Select a Match:"),
                dcc.Dropdown(
                    id="match-dropdown",
                    options=[
                        {"label": f"{row['team1_name']} vs {row['team2_name']} ({row['match_desc']})", "value": row["match_id"]}
                        for _, row in data_international_matches.iterrows()
                    ],
                )
            ]),
            html.Div(id="scorecard-output"),
            html.Div(id="partnership-output")
        ]),
        dcc.Tab(label="Match Summary", children=[
            html.H2("Match Scorecard and Partnerships"),
            html.Div([
                html.Label("Select a Match:"),
                dcc.Dropdown(
                    id="match-dropdown",
                    options=[
                        {"label": f"{row['team1_name']} vs {row['team2_name']} ({row['match_desc']})", "value": row["match_id"]}
                        for _, row in data_international_matches.iterrows()
                    ],
                )
            ]),
            html.Div(id="summary-output")
        ])
        
    ])
])

# Callbacks
@app.callback(
    [Output("scorecard-output", "children"), Output("partnership-output", "children")],
    [Input("match-dropdown", "value")]
)
def update_match_details(match_id):
    if not match_id:
        return "", ""

    # Fetch data for the match
    batsmen_data = load_data(f"""
        SELECT innings_id, bat_team_name AS team_name, batsman_name, runs, balls_faced, fours, sixes, strike_rate
        FROM batsmen_details WHERE match_id = {match_id}
    """)
    bowlers_data = load_data(f"""
        SELECT innings_id, bowl_team_name AS team_name, bowler_name, overs, maidens, runs_conceded, wickets, economy
        FROM bowlers_details WHERE match_id = {match_id}
    """)
    partnership_data = load_data(f"""
        SELECT innings_id, bat1_name AS batsman1,bat1_runs, bat2_name AS batsman2,bat2_runs, total_runs AS runs, total_balls AS balls
        FROM partnerships WHERE match_id = {match_id}
    """)

    # Generate a unique color mapping for players
    unique_players = set(partnership_data['batsman1']).union(set(partnership_data['batsman2']))
    color_map = {player: px.colors.qualitative.Safe[i % len(px.colors.qualitative.Safe)] for i, player in enumerate(unique_players)}

    # Prepare batting and bowling scorecards for each innings
    innings_list = batsmen_data['innings_id'].unique()
    scorecard_content = []

    for innings_id in innings_list:
        # Batting scorecard
        batting_data = batsmen_data[batsmen_data['innings_id'] == innings_id]
        batting_team = batting_data['team_name'].iloc[0]
        scorecard_content.append(html.H3(f"{batting_team} Batting"))

        scorecard_content.append(html.Div([
            dash_table.DataTable(
                columns=[
                    {"name": col.replace('_', ' ').capitalize(), "id": col}
                    for col in ['batsman_name', 'runs', 'balls_faced', 'fours', 'sixes', 'strike_rate']
                ],
                data=batting_data.to_dict("records"),
                style_table={'overflowX': 'auto'},
                page_size=10
            )
        ]))

        # Bowling scorecard
        bowling_data = bowlers_data[bowlers_data['innings_id'] == innings_id]
        bowling_team = bowling_data['team_name'].iloc[0]
        scorecard_content.append(html.H3(f"{bowling_team} Bowling"))

        scorecard_content.append(html.Div([
            dash_table.DataTable(
                columns=[
                    {"name": col.replace('_', ' ').capitalize(), "id": col}
                    for col in ['bowler_name', 'overs', 'maidens', 'runs_conceded', 'wickets', 'economy']
                ],
                data=bowling_data.to_dict("records"),
                style_table={'overflowX': 'auto'},
                page_size=10
            )
        ]))

    # Partnerships - Generate chart for each innings
    partnership_charts = []
    for innings_id in partnership_data['innings_id'].unique():
        innings_partnerships = partnership_data[partnership_data['innings_id'] == innings_id]
        fig = go.Figure()

        for i, row in innings_partnerships.iterrows():
            # Contribution for Batsman 1
            fig.add_trace(go.Bar(
                x=[row["bat1_runs"]],
                y=[f"{row['batsman1']} & {row['batsman2']}"],
                orientation="h",
                name=row["batsman1"],
                marker=dict(color=color_map[row["batsman1"]]),
                text=f"{row['batsman1']} ({row['bat1_runs']} runs)",
                textposition="auto",
                hovertemplate=(
                    f"<b>Batsman:</b> {row['batsman1']}<br>"
                    f"<b>Runs:</b> {row['bat1_runs']}<br>"
                )
            ))

            # Contribution for Batsman 2
            fig.add_trace(go.Bar(
                x=[row["bat2_runs"]],
                y=[f"{row['batsman1']} & {row['batsman2']}"],
                orientation="h",
                name=row["batsman2"],
                marker=dict(color=color_map[row["batsman2"]]),
                text=f"{row['batsman2']} ({row['bat2_runs']} runs)",
                textposition="auto",
                hovertemplate=(
                    f"<b>Batsman:</b> {row['batsman2']}<br>"
                    f"<b>Runs:</b> {row['bat2_runs']}<br>"
                   
                )
            ))

        fig.update_layout(
            title=f"Innings {innings_id} Partnerships",
            xaxis=dict(title="Runs Scored", tickmode="linear",dtick =50),
            yaxis=dict(title="Batsmen Pairs", automargin=True),
            barmode="stack",  # Ensures contributions stack horizontally
            showlegend=True,  # Adds a legend for batsman differentiation
            height=600,  # Adjust chart height for readability
        )

        partnership_charts.append(html.Div([
            html.H3(f"Innings {innings_id} : {batting_team}  Partnership Contributions"),
            dcc.Graph(figure=fig)
        ]))

    return scorecard_content, partnership_charts
@app.callback(
    [Output("summary-output", "children")],
    [Input("match-dropdown", "value")]
)
def update_match_summary(match_id):
    if not match_id:
        return ["Please select a match"]

    # Fetch match details by joining international_matches and match_details
    match_details = load_data(f"""
        SELECT 
            im.team1_name, 
            im.team2_name, 
            im.match_desc, 
            md.winning_team_name as winner_team, 
            md.match_status as match_result, 
            im.venue_ground || ', ' || im.venue_city as venue
        FROM international_matches im
        JOIN match_details md ON im.match_id = md.match_id
        WHERE im.match_id = {match_id}
    """)

    # Fetch batsmen data
    batsmen_data = load_data(f"""
        SELECT 
            innings_id, 
            bat_team_name AS team_name, 
            batsman_name, 
            runs, 
            balls_faced, 
            strike_rate,
            ROW_NUMBER() OVER (PARTITION BY innings_id ORDER BY runs DESC) as rank
        FROM batsmen_details 
        WHERE match_id = {match_id}
    """)

    # Fetch bowlers data
    bowlers_data = load_data(f"""
        SELECT 
            innings_id, 
            bowl_team_name AS team_name, 
            bowler_name, 
            wickets, 
            runs_conceded, 
            economy,
            overs,
            ROW_NUMBER() OVER (PARTITION BY innings_id ORDER BY wickets DESC, economy ASC) as rank
        FROM bowlers_details 
        WHERE match_id = {match_id}
    """)

    # Prepare summary content
    summary_content = []

    # Match Overview
    if not match_details.empty:
        match_info = match_details.iloc[0]
        summary_content.extend([
            html.H3("Match Overview"),
            html.Div([
                html.P(f"Match: {match_info['team1_name']} vs {match_info['team2_name']}"),
                html.P(f"Match Type: {match_info['match_desc']}"),
                html.P(f"Winner: {match_info['winner_team']}"),
                html.P(f"Result: {match_info['match_result']}"),
                html.P(f"Venue: {match_info['venue']}"),
            ])
        ])

    # Top Performers for each innings
    innings_list = batsmen_data['innings_id'].unique()
    for innings_id in innings_list:
        # Top 5 Batsmen
        top_batsmen = batsmen_data[batsmen_data['innings_id'] == innings_id][batsmen_data['rank'] <= 5]
        team_name = top_batsmen['team_name'].iloc[0] if not top_batsmen.empty else "Unknown Team"
        
        summary_content.append(html.H3(f"Innings {innings_id} Top Batsmen - {team_name}"))
        summary_content.append(
            dash_table.DataTable(
                columns=[
                    {"name": col.replace('_', ' ').capitalize(), "id": col}
                    for col in ['batsman_name', 'runs', 'balls_faced', 'strike_rate']
                ],
                data=top_batsmen[['batsman_name', 'runs', 'balls_faced', 'strike_rate']].to_dict("records"),
                style_table={'overflowX': 'auto'},
            )
        )

        # Top 5 Bowlers
        top_bowlers = bowlers_data[bowlers_data['innings_id'] == innings_id][bowlers_data['rank'] <= 5]
        bowling_team_name = top_bowlers['team_name'].iloc[0] if not top_bowlers.empty else "Unknown Team"
        
        summary_content.append(html.H3(f"Innings {innings_id} Top Bowlers - {bowling_team_name}"))
        summary_content.append(
            dash_table.DataTable(
                columns=[
                    {"name": col.replace('_', ' ').capitalize(), "id": col}
                    for col in ['bowler_name', 'wickets', 'runs_conceded', 'economy', 'overs']
                ],
                data=top_bowlers[['bowler_name', 'wickets', 'runs_conceded', 'economy', 'overs']].to_dict("records"),
                style_table={'overflowX': 'auto'},
            )
        )

    return [html.Div(summary_content)]

# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)
