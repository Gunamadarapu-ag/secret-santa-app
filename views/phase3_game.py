import streamlit as st
import time
from datetime import datetime, timezone
from modules.db_service import get_santa_clues, get_all_employee_names, update_game_status, start_game_timer

def calculate_time_left(start_time_str):
    """Calculates minutes left out of 30 minutes"""
    if not start_time_str:
        return 30 # Full time if not started
    
    # Parse DB timestamp (ISO format)
    try:
        start_dt = datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))
    except:
        # Fallback if format is weird
        return 30
        
    now_dt = datetime.now(timezone.utc)
    
    elapsed_seconds = (now_dt - start_dt).total_seconds()
    minutes_left = 30 - (elapsed_seconds / 60)
    
    return max(0, int(minutes_left))

def show_upload_ui(token, status, task_desc):
    """Helper to show G-Form Button and Confirm Checkbox"""
    with st.container(border=True):
        st.info("Don't worry, only the Admin can see this until the Reveal Party!")
        
        # --- REPLACE THIS LINK ---
        google_form_link = "https://forms.gle/KoCUrg5TWikWqbGH6" 
        # -------------------------
        
        st.markdown(
            f"""
            <a href="{google_form_link}" target="_blank" style="text-decoration: none;">
                <button style="background-color: #FF4B4B; color: white; border: none; border-radius: 5px; padding: 10px 20px; font-weight: bold; cursor: pointer; width: 100%;">
                    📤 Click Here to Upload Proof
                </button>
            </a>
            """, 
            unsafe_allow_html=True
        )

        st.markdown("---")
        st.write("Once uploaded, confirm below:")

        with st.form(f"confirm_{status}_form"):
            confirm = st.checkbox(f"I confirm I have done the task: '{task_desc}'")
            submit_btn = st.form_submit_button("Submit & Finish Game")
            
            if submit_btn:
                if not confirm:
                    st.error("Please tick the checkbox!")
                else:
                    update_game_status(token, status, proof_url="Uploaded via Google Form")
                    st.balloons()
                    time.sleep(2)
                    st.rerun()

def show_game_page(user):
    
    # --- 1. START TIMER ON FIRST LOAD ---
    # Only if Santa has submitted clues AND timer hasn't started yet
    santa_row = get_santa_clues(user['email'])
    
    if santa_row and santa_row['clues_submitted'] and not user['game_start_time']:
        start_game_timer(user['secret_token'])
        st.rerun() # Refresh to get the timestamp
    
    # --- 2. CALCULATE TIME ---
    minutes_left = 30
    if user.get('game_start_time'):
        minutes_left = calculate_time_left(user['game_start_time'])
    
    is_time_up = minutes_left <= 0

    # --- 3. HEADER WITH TIMER ---
    col_head, col_timer = st.columns([3, 1])
    with col_head:
        st.header("🕵️ My Mystery")
    with col_timer:
        if not user['game_completed'] and santa_row and santa_row['clues_submitted']:
            if is_time_up:
                st.metric("Time Left", "0 min", delta="-30m", delta_color="inverse")
            else:
                st.metric("Time Left", f"{minutes_left} min", delta_color="normal")

    # --- 4. CHECK COMPLETION ---
    if user['game_completed']:
        status = user.get('guess_status')
        st.info("✅ You have completed the game!")
        
        if status == 'correct':
            st.balloons()
            st.success("🎉 You Guessed CORRECTLY!")
            st.markdown(f"**Your Victory Task was:** {user.get('bonus_task')}")
        else:
            st.error("💀 You Failed!")
            st.markdown(f"**Your Penalty Task was:** {user.get('dare_task')}")
            
        st.write("Your proof has been recorded.")
        return

    # --- 5. WAIT FOR SANTA ---
    if not santa_row or not santa_row['clues_submitted']:
        st.info("⏳ Your Santa hasn't created your game yet. Come back later!")
        return

    # --- 6. DISPLAY CLUES ---
    st.markdown("### 🧩 Who is your Santa?")
    with st.container(border=True):
        st.markdown(f"**Clue 1:** {santa_row['clue_1']}")
        st.markdown(f"**Clue 2:** {santa_row['clue_2']}")
        st.markdown(f"**Clue 3:** {santa_row['clue_3']}")
    
    # --- 7. GUESSING FORM ---
    all_employees = get_all_employee_names()
    
    # If time is up, force fail state
    if is_time_up and not st.session_state.get('wrong_guess') and not st.session_state.get('correct_guess'):
        st.error("⏰ TIME IS UP! You failed to guess in time.")
        st.session_state['wrong_guess'] = True 

    if not st.session_state.get('wrong_guess') and not st.session_state.get('correct_guess'):
        with st.form("guessing_form"):
            guess = st.selectbox("I think my Santa is...", ["Select Name"] + all_employees, disabled=is_time_up)
            btn = st.form_submit_button("🎲 Submit Guess", disabled=is_time_up)
            
            if btn:
                if guess == "Select Name":
                    st.warning("Pick a name!")
                elif guess == santa_row['name']:
                    st.session_state['correct_guess'] = True
                    st.rerun()
                else:
                    st.session_state['wrong_guess'] = True
                    st.rerun()

    # --- 8. UPLOAD UI ---
    
    # CASE A: WIN (Bonus Task)
    if st.session_state.get('correct_guess'):
        st.success("🎉 CORRECT! You found them!")
        st.markdown("---")
        st.header("🌟 VICTORY LAP")
        st.markdown(f"**You unlocked the Bonus Task:** {santa_row['bonus_task']}")
        st.write("Upload a video of your victory to complete the game!")
        
        show_upload_ui(user['secret_token'], 'correct', santa_row['bonus_task'])

    # CASE B: LOSE (Dare Task)
    if st.session_state.get('wrong_guess'):
        if not is_time_up:
            st.error(f"❌ WRONG! It is NOT the right person.")
        st.markdown("---")
        st.header("😈 THE PENALTY")
        st.markdown(f"**You must:** {santa_row['dare_task']}")
        
        show_upload_ui(user['secret_token'], 'failed', santa_row['dare_task'])