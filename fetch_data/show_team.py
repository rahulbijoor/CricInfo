import duckdb

def view_teams():
    conn = duckdb.connect('\simple_regression\CricInfo\cricket_matches.db')
    sample_records = conn.execute(f"SELECT * FROM partnerships WHERE match_id = 101014 and innings_id = 1").fetchall()
    for record in sample_records:
        print(record)
    conn.close()
    
view_teams()