import pandas as pd
import random

def generate_matches(df):
    matches = []
    errors = []
    
    # 1. Clean Data (Strip whitespace from column names and values)
    df.columns = df.columns.str.strip().str.lower()
    # Ensure required columns exist
    required_cols = {'empid', 'empname', 'empmail', 'location'}
    if not required_cols.issubset(df.columns):
        return None, [f"CSV is missing columns. Found: {list(df.columns)}. Required: {required_cols}"]

    # 2. Group and Process
    grouped = df.groupby('location')
    
    for location, group in grouped:
        participants = group.to_dict('records')
        
        # EDGE CASE: Single person
        if len(participants) < 2:
            errors.append(f"❌ Error: Location '{location}' has only 1 employee. Skipped.")
            continue
            
        random.shuffle(participants)
        
        # Circular Chain
        count = len(participants)
        for i in range(count):
            giver = participants[i]
            receiver = participants[(i + 1) % count]
            
            matches.append({
                'Location': location,
                'Giver_Name': giver['empname'],
                'Giver_Email': giver['empmail'],
                'Receiver_Name': receiver['empname'],
                'Receiver_Email': receiver['empmail']
            })
            
    return pd.DataFrame(matches), errors
