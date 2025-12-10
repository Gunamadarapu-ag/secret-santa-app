import streamlit as st
from supabase import create_client, Client

# Initialize Connection
def init_supabase():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

# --- ADMIN FUNCTIONS ---
def init_game_db(matches_df):
    """
    Admin: 
    1. Wipes all Chat Messages
    2. Wipes all Participants
    3. Inserts New Pairs
    This ensures a completely fresh start for the new event.
    """
    supabase = init_supabase()
    
    # --- STEP 1: WIPE OLD DATA ---
    # We use .neq("id", "dummy") as a hack to "Delete All Rows" 
    # (since every ID is not equal to a dummy zero UUID)
    dummy_uuid = "00000000-0000-0000-0000-000000000000"
    
    try:
        # A. Clear Messages first (Child table)
        supabase.table('messages').delete().neq("id", dummy_uuid).execute()
        
        # B. Clear Participants (Parent table)
        supabase.table('participants').delete().neq("id", dummy_uuid).execute()
        
    except Exception as e:
        st.error(f"⚠️ Error wiping old data: {str(e)}")
        # We continue anyway, just in case the table was already empty
def add_more_participants(matches_df):
    """
    Safely adds NEW participants (e.g., Chennai) to the existing game
    WITHOUT deleting the old ones (Bangalore).
    """
    supabase = init_supabase()
    rows = matches_df.to_dict('records')
    try:
        # Just Insert, Do NOT Delete
        data, count = supabase.table('participants').insert(rows).execute()
        return data.data if hasattr(data, 'data') else data[1]
    except Exception as e:
        st.error(f"DB Error: {e}")
        return None
        
    # --- STEP 2: INSERT NEW DATA ---
    rows = matches_df.to_dict('records')
    try:
        data, count = supabase.table('participants').insert(rows).execute()
        return data.data if hasattr(data, 'data') else data[1]
    except Exception as e:
        st.error(f"❌ DB Insert Error: {e}")
        return None
def get_participant_count():
    """Returns the total number of players in the game"""
    supabase = init_supabase()
    # Select count of rows. We fetch 'head' to get count without data
    resp = supabase.table('participants').select("*", count='exact').execute()
    return resp.count if resp.count is not None else 0

def get_pending_santas():
    """Fetches list of users who have NOT submitted clues yet (The missing function!)"""
    supabase = init_supabase()
    # Check where clues_submitted is FALSE
    resp = supabase.table('participants').select("*").eq('clues_submitted', False).execute()
    return resp.data if resp.data else []

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
def submit_clues_and_dare(token, c1, c2, c3, dare, bonus):
    """Updates clues, dare, AND bonus"""
    supabase = init_supabase()
    supabase.table('participants').update({
        'clue_1': c1,
        'clue_2': c2,
        'clue_3': c3,
        'dare_task': dare,
        'bonus_task': bonus,
        'clues_submitted': True
    }).eq('secret_token', token).execute()

def start_game_timer(token):
    """Sets the start time if it hasn't been set yet"""
    supabase = init_supabase()
    # Fetch current user to check if time is already set to avoid resetting it
    # But since we call this only when needed, we can do a safe update
    # Note: We rely on the frontend to check if it's None before calling this, 
    # but we can double check here or just update if null.
    
    # We will use a condition: only update if game_start_time is null
    # Supabase filter: .is_("game_start_time", "null")
    supabase.table('participants').update({
        'game_start_time': 'now()'
    }).eq('secret_token', token).is_("game_start_time", "null").execute()

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

# --- CHAT FUNCTIONS ---

def get_token_by_email(email):
    """Helper to find the token of the person we want to chat with"""
    supabase = init_supabase()
    resp = supabase.table('participants').select("secret_token").eq('email', email).execute()
    if resp.data: return resp.data[0]['secret_token']
    return None

def get_santa_token(my_email):
    """Helper to find the token of the person who is MY Santa"""
    supabase = init_supabase()
    resp = supabase.table('participants').select("secret_token").eq('match_email', my_email).execute()
    if resp.data: return resp.data[0]['secret_token']
    return None

def send_message(sender_token, receiver_token, text, role):
    """
    Role must be 'santa' (if I am sending to my child) 
    or 'child' (if I am sending to my Santa)
    """
    supabase = init_supabase()
    supabase.table('messages').insert({
        'sender_token': sender_token,
        'receiver_token': receiver_token,
        'message_text': text,
        'sender_role': role
    }).execute()

def get_messages(user_token, other_token):
    """
    Fetch conversation between two specific tokens.
    We fetch all messages involving the User, then filter strictly for the Other person.
    """
    supabase = init_supabase()
    
    # 1. Fetch ALL messages where I am the Sender OR I am the Receiver
    # This ensures we get every message I've ever touched
    response = supabase.table('messages').select("*").or_(
        f"sender_token.eq.{user_token},receiver_token.eq.{user_token}"
    ).order('created_at').execute()
    
    all_msgs = response.data if response.data else []
    
    # 2. Filter in Python (Strict Pairing)
    # Only keep messages where the 'other' person is the specific 'other_token' we asked for
    filtered = []
    for msg in all_msgs:
        if (msg['sender_token'] == user_token and msg['receiver_token'] == other_token) or \
           (msg['sender_token'] == other_token and msg['receiver_token'] == user_token):
            filtered.append(msg)
    return filtered