import dash_bootstrap_components as dbc
from dash import html, dcc, dash_table

def create_series_dropdown(series_options):
    """
    Create series dropdown component.
    
    Args:
        series_options (list): List of series dropdown options
    
    Returns:
        dbc.Col: Dropdown column
    """
    return dbc.Col([
        html.H4("Select Series"),
        dcc.Dropdown(
            id='series-dropdown',
            options=series_options,
            value='All Series',
            clearable=False
        )
    ], width=6)

def create_match_details_table():
    """
    Create match details table component.
    
    Returns:
        dbc.Col: Match details table column
    """
    return dbc.Col([
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
            page_size=10
        )
    ], width=12)

def create_charts():
    """
    Create charts row with team matches and match formats.
    
    Returns:
        dbc.Row: Charts row
    """
    return dbc.Row([
        dbc.Col([
            html.H4("Teams by Number of Matches"),
            dcc.Graph(id='wins-bar-chart')
        ], width=6),
        
        dbc.Col([
            html.H4("Match Formats Distribution"),
            dcc.Graph(id='format-pie-chart')
        ], width=6)
    ])

def create_dashboard_layout(series_options):
    """
    Create full dashboard layout.
    
    Args:
        series_options (list): List of series dropdown options
    
    Returns:
        dbc.Container: Full dashboard layout
    """
    return dbc.Container([
        html.H1("Cricket Match Analysis Dashboard", className="text-center my-4"),
        
        dbc.Row([create_series_dropdown(series_options)], className="mb-4"),
        
        dbc.Row([create_match_details_table()], className="mb-4"),
        
        create_charts()
    ], fluid=True)