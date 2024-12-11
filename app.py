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

# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)
