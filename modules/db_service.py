import streamlit as st
from supabase import create_client, Client

# Initialize Connection
def init_supabase():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

# --- ADMIN FUNCTIONS ---
def init_game_db(matches_df):
    """Admin: Wipes old data and inserts new pairs"""
    supabase = init_supabase()
    rows = matches_df.to_dict('records')
    try:
        data, count = supabase.table('participants').insert(rows).execute()
        return data.data if hasattr(data, 'data') else data[1]
    except Exception as e:
        st.error(f"DB Error: {e}")
        return None

# --- USER FETCHING ---
def get_user_by_token(token):
    supabase = init_supabase()
    try:
        resp = supabase.table('participants').select("*").eq('secret_token', token).execute()
        if resp.data: return resp.data[0]
        return None
    except: return None

def get_target_info(match_email):
    """Get the wishlist of the person I am gifting to"""
    supabase = init_supabase()
    resp = supabase.table('participants').select("wishlist").eq('email', match_email).execute()
    if resp.data: return resp.data[0]
    return None

def get_santa_clues(user_email):
    """Find the clues MY Santa left for ME"""
    supabase = init_supabase()
    # We need to find the row where match_email == my email
    resp = supabase.table('participants').select("*").eq('match_email', user_email).execute()
    if resp.data: return resp.data[0]
    return None

def get_all_employee_names():
    """For the dropdown list when guessing"""
    supabase = init_supabase()
    resp = supabase.table('participants').select("name").execute()
    if resp.data:
        return [row['name'] for row in resp.data]
    return []

# --- PHASE 1: WISHLIST ---
def submit_wishlist(token, wishlist_text):
    supabase = init_supabase()
    supabase.table('participants').update({
        'wishlist': wishlist_text
    }).eq('secret_token', token).execute()

# --- PHASE 2: SUBMIT CLUES ---
def submit_clues_and_dare(token, c1, c2, c3, dare):
    supabase = init_supabase()
    supabase.table('participants').update({
        'clue_1': c1,
        'clue_2': c2,
        'clue_3': c3,
        'dare_task': dare,
        'clues_submitted': True
    }).eq('secret_token', token).execute()

# --- PHASE 3: GAME LOGIC ---
def update_game_status(token, status, proof_url=None):
    """Updates status to 'correct' or 'failed', saves proof string"""
    supabase = init_supabase()
    update_data = {
        'guess_status': status,
        'game_completed': True
    }
    if proof_url:
        update_data['dare_proof_url'] = proof_url
        
    supabase.table('participants').update(update_data).eq('secret_token', token).execute()