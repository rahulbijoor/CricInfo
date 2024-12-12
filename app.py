import dash
from dash import dcc, html, Input, Output, dash_table
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import duckdb
import pandas as pd
import plotly.express as px  

app = dash.Dash(__name__)
app.title = "Cricket Dashboard"


def load_data(query):
    con = duckdb.connect('cricket_matches.db', read_only=True)
    return con.execute(query).df()

# Queries for data
def get_international_matches():
    return load_data("SELECT * FROM international_matches m JOIN match_details md ON m.match_id = md.match_id")

def get_team_wins(data_international_matches):
    return data_international_matches.groupby('winning_team_name').size().reset_index(name='wins').sort_values('wins', ascending=False)

def get_match_formats(data_international_matches):
    return data_international_matches['match_format'].value_counts().reset_index(name='count')

data_international_matches = get_international_matches()
data_team_wins = get_team_wins(data_international_matches)
data_match_formats = get_match_formats(data_international_matches)

try:
    series_options = [{'label': series, 'value': series} 
                      for series in data_international_matches['series_name'].unique() 
                      if pd.notna(series)]
    series_options.insert(0, {'label': 'All Series', 'value': 'All Series'})
except Exception as e:
    print(f"Error creating series options: {e}")
    series_options = [{'label': 'All Series', 'value': 'All Series'}]

# Layout
app.layout = html.Div([ html.H1("StumpStats"),
    dcc.Tabs([ 
        dcc.Tab(label="Series Overview", children=[
            html.H2("Series Overview"),
            dbc.Row([
                dbc.Col([
                    html.H4("Select Series"),
                    dcc.Dropdown(
                        id='series-dropdown',
                        options=series_options,
                        value='All Series',
                        clearable=False
                    )
                ], width=6)
            ], className="mb-4"),
            dbc.Row([
                dbc.Col([
                    html.H4("Match Details"),
                    dash_table.DataTable(
                        id='match-table',
                        columns=[
                            {"name": "Match ID", "id": "match_id"},
                            {"name": "Series", "id": "series_name"},
                            {"name": "Match Description", "id": "match_desc"},
                            {"name": "Team 1", "id": "team1_name"},
                            {"name": "Team 2", "id": "team2_name"},
                            {"name": "Status", "id": "status"}
                        ],
                        style_table={'overflowX': 'auto'},
                        style_cell={'textAlign': 'left'},
                        page_size=11
                    )
                ], width=12)
                ]),

            dbc.Row([
                dbc.Col([
                    html.H4("Teams by Number of Matches"),
                    dcc.Graph(id='wins-bar-chart')
                ], width=6),
        
                dbc.Col([
                    html.H4("Match Formats Distribution"),
                    dcc.Graph(id='format-pie-chart')
                ], width=6)
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
            html.H2("Match Summary"),
            html.Div([
                html.Label("Select a Match:"),
                dcc.Dropdown(
                    id="match2-dropdown",
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

# Callback to update match table
@app.callback(
    Output('match-table', 'data'),
    Input('series-dropdown', 'value')
)
def update_match_table(selected_series):
    try:
        if selected_series == 'All Series':
            df_filtered = data_international_matches
        else:
            df_filtered = data_international_matches[data_international_matches['series_name'] == selected_series]
        
        # Select and rename columns for display
        table_data = df_filtered[['match_id', 'series_name', 'match_desc', 'team1_name', 'team2_name', 'status']].to_dict('records')
        return table_data
    except Exception as e:
        print(f"Error in update_match_table: {e}")
        return []

# Callback to update wins bar chart
@app.callback(
    Output('wins-bar-chart', 'figure'),
    Input('series-dropdown', 'value')
)
def update_wins_chart(selected_series):
    try:
        if selected_series == 'All Series':
            df_filtered = data_international_matches
        else:
            df_filtered = data_international_matches[data_international_matches['series_name'] == selected_series]
        
        # Count wins by team
        wins_df = get_team_wins(df_filtered)
        
        fig = px.bar(
            wins_df, 
            x='winning_team_name', 
            y='wins', 
            title='Team Matches',
            labels={'winning_team_name': 'Team', 'wins': 'Number of Wins'}
        )
        fig.update_yaxes(
            tickmode='linear',  # Set tick mode to linear
            tick0=0,            # Start ticks at 0
            dtick=1             # Increment ticks by 1
        )
        return fig
    except Exception as e:
        print(f"Error in update_wins_chart: {e}")
        return go.Figure()

# Callback to update match formats pie chart
@app.callback(
    Output('format-pie-chart', 'figure'),
    Input('series-dropdown', 'value')
)
def update_format_chart(selected_series):
    try:
        if selected_series == 'All Series':
            df_filtered = data_international_matches
        else:
            df_filtered = data_international_matches[data_international_matches['series_name'] == selected_series]
        
        # Count match formats
        format_df = get_match_formats(df_filtered)
        
        fig = px.pie(
            format_df, 
            values='count', 
            names='match_format', 
            title='Match Formats Distribution'
        )
        return fig
    except Exception as e:
        print(f"Error in update_format_chart: {e}")
        return go.Figure()

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
    [Input("match2-dropdown", "value")]
)
def update_match_summary(match_id):
    if not match_id:
        return [' ']

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
            dbc.Container([
                create_match_overview(match_info)
            ])
        ])

    # Top Performers for each innings
    innings_list = sorted(batsmen_data['innings_id'].unique())
    if innings_list is None:
        summary_content.append(html.P("No innings data found."))
        return [html.Div(summary_content)]
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

def create_match_overview(match_info):
    """
    Create a visually appealing match overview card using Dash and Bootstrap Components
    
    :param match_info: Dictionary containing match information
    :return: Dash HTML component with styled match overview
    """
    return dbc.Card(
        [
            dbc.CardHeader(
                html.H4(
                    "Match Overview", 
                    className="text-center text-white mb-0 font-weight-bold",
                    style={
                        'font-family': "'Roboto', sans-serif",
                        'letter-spacing': '1px',
                        'text-transform': 'uppercase'
                    }
                ),
                className="bg-gradient-primary py-3 shadow-sm"
            ),
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        html.H5(
                            "Match Details", 
                            className="text-primary mb-3",
                            style={
                                'font-weight': '600',
                                'border-bottom': '2px solid #007bff',
                                'padding-bottom': '10px'
                            }
                        ),
                        dbc.ListGroup([
                            dbc.ListGroupItem([
                                html.Strong(
                                    "Teams: ", 
                                    className="me-2 text-muted",
                                    style={'font-size': '0.9rem'}
                                ),
                                html.Span(
                                    f"{match_info['team1_name']} vs {match_info['team2_name']}", 
                                    style={
                                        'font-weight': '500',
                                        'color': '#333'
                                    }
                                )
                            ], className="d-flex justify-content-between align-items-center py-2"),
                            dbc.ListGroupItem([
                                html.Strong(
                                    "Match Type: ", 
                                    className="me-2 text-muted",
                                    style={'font-size': '0.9rem'}
                                ),
                                html.Span(
                                    match_info['match_desc'],
                                    style={
                                        'font-weight': '500',
                                        'color': '#333'
                                    }
                                )
                            ], className="d-flex justify-content-between align-items-center py-2"),
                        ], flush=True)
                    ], md=6),
                    dbc.Col([
                        html.H5(
                            "Result", 
                            className="text-success mb-3",
                            style={
                                'font-weight': '600',
                                'border-bottom': '2px solid #28a745',
                                'padding-bottom': '10px'
                            }
                        ),
                        dbc.ListGroup([
                            dbc.ListGroupItem([
                                html.Strong(
                                    "Winner: ", 
                                    className="me-2 text-muted",
                                    style={'font-size': '0.9rem'}
                                ),
                                html.Span(
                                    match_info['winner_team'],
                                    style={
                                        'font-weight': '500',
                                        'color': '#333'
                                    }
                                )
                            ], className="d-flex justify-content-between align-items-center py-2"),
                            dbc.ListGroupItem([
                                html.Strong(
                                    "Venue: ", 
                                    className="me-2 text-muted",
                                    style={'font-size': '0.9rem'}
                                ),
                                html.Span(
                                    match_info['venue'],
                                    style={
                                        'font-weight': '500',
                                        'color': '#333'
                                    }
                                )
                            ], className="d-flex justify-content-between align-items-center py-2"),
                        ], flush=True)
                    ], md=6),
                ], className="g-3"),
                html.Hr(className="my-4", style={'border-top': '2px solid #e9ecef'}),
                dbc.Alert(
                    match_info['match_result'],
                    color="info",
                    className="text-center font-weight-bold",
                    style={
                        'font-family': "'Times New Roman', sans-serif",
                        'font-size': '2.5rem',
                        'border-radius': '5px',
                        'padding': '1rem'
                    }
                )
            ], className="p-4")
        ],
        className="shadow-lg rounded-lg border-0 mb-4",
        style={
            'font-family': "'Roboto', sans-serif",
            'max-width': '800px',
            'margin': '0 auto'
        }
    )

# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)
