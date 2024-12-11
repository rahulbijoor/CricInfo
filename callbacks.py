import plotly.express as px
import plotly.graph_objs as go
from dash.dependencies import Input, Output

def register_callbacks(app, merged_df):
    """
    Register all dashboard callbacks.
    
    Args:
        app (dash.Dash): Dash application instance
        merged_df (pd.DataFrame): Merged match data
    """
    @app.callback(
        Output('match-table', 'data'),
        Input('series-dropdown', 'value')
    )
    def update_match_table(selected_series):
        try:
            if selected_series == 'All Series':
                df_filtered = merged_df
            else:
                df_filtered = merged_df[merged_df['series_name'] == selected_series]
            
            # Select and rename columns for display
            table_data = df_filtered[['match_id', 'series_name', 'match_desc', 'team1_name', 'team2_name','winning_team_name', 'status']].to_dict('records')
            return table_data
        except Exception as e:
            print(f"Error in update_match_table: {e}")
            return []

    @app.callback(
        Output('wins-bar-chart', 'figure'),
        Input('series-dropdown', 'value')
    )
    def update_wins_chart(selected_series):
        try:
            if selected_series == 'All Series':
                df_filtered = merged_df
            else:
                df_filtered = merged_df[merged_df['series_name'] == selected_series]
            
            # Count wins by team
            wins_df = df_filtered.groupby('winning_team_name').size().reset_index(name='wins')
            wins_df = wins_df.sort_values('wins', ascending=False)
            
            fig = px.bar(
                wins_df, 
                x='winning_team_name', 
                y='wins', 
                title='Team Matches',
                labels={'team1_name': 'Team', 'wins': 'Number of Matches'}
            )
            return fig
        except Exception as e:
            print(f"Error in update_wins_chart: {e}")
            return go.Figure()

    @app.callback(
        Output('format-pie-chart', 'figure'),
        Input('series-dropdown', 'value')
    )
    def update_format_chart(selected_series):
        try:
            if selected_series == 'All Series':
                df_filtered = merged_df
            else:
                df_filtered = merged_df[merged_df['series_name'] == selected_series]
            
            # Count match formats
            format_counts = df_filtered['match_format'].value_counts()
            
            fig = px.pie(
                values=format_counts.values, 
                names=format_counts.index, 
                title='Match Formats Distribution'
            )
            return fig
        except Exception as e:
            print(f"Error in update_format_chart: {e}")
            return go.Figure()