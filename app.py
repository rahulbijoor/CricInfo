import dash
import dash_bootstrap_components as dbc
import pandas as pd

from data_loader import connect_database, load_data, merge_match_data
from layouts import create_dashboard_layout
from callbacks import register_callbacks

# Initialize the Flask-Dash application
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Main application setup
def setup_dashboard():
    # Connect to database
    conn = connect_database()
    
    # Load data
    international_matches = load_data(conn, 'international_matches')
    match_details = load_data(conn, 'match_details')
    
    # Merge dataframes
    merged_df = merge_match_data(international_matches, match_details)
    
    # Extensive debugging for series dropdown
    print("Merged DataFrame Shape:", merged_df.shape)
    print("Merged DataFrame Columns:", merged_df.columns.tolist())
    
    # Check series column
    if 'series_name' in merged_df.columns:
        print("Series Name Unique Values:")
        print(merged_df['series_name'].unique())
        print("Series Name Value Counts:")
        print(merged_df['series_name'].value_counts())
    
    # Prepare series dropdown with more robust handling
    try:
        # Remove NaN values and strip whitespace
        unique_series = merged_df['series_name'].dropna().str.strip().unique()
        
        # Create options, ensuring non-empty series names
        series_options = [
            {'label': series, 'value': series} 
            for series in unique_series 
            if series and series.strip()
        ]
        
        # Always add 'All Series' option
        series_options.insert(0, {'label': 'All Series', 'value': 'All Series'})
        
        print("Generated Series Options:")
        for option in series_options:
            print(option)
    except Exception as e:
        print(f"Error creating series options: {e}")
        series_options = [{'label': 'All Series', 'value': 'All Series'}]
    
    # Create layout
    app.layout = create_dashboard_layout(series_options)
    
    # Register callbacks
    register_callbacks(app, merged_df)

# Setup the dashboard
setup_dashboard()

# Main entry point
if __name__ == '__main__':
    app.run_server(debug=True)