import streamlit as st
import time
from modules.db_service import get_santa_clues, get_all_employee_names, update_game_status, lock_guess_attempt

def show_upload_ui(token, status_for_db, task_desc, header_text, style_type):
    """Helper to show UI for uploading proof after guessing"""
    if style_type == "win":
        st.success("🎉 CORRECT! You found them!")
        st.markdown("---")
        st.header(header_text) # "🌟 VICTORY LAP"
    else:
        st.error("❌ WRONG! It is NOT the right person.")
        st.markdown("---")
        st.header(header_text) # "😈 THE PENALTY"

    st.markdown(f"**Task:** {task_desc}")
    
    with st.container(border=True):
        st.info("Don't worry, only the Admin can see this until the Reveal Party!")
        
        # --- GOOGLE FORM LINK ---
        google_form_link = "YOUR_GOOGLE_FORM_LINK_HERE" 
        
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

        with st.form(f"confirm_form"):
            confirm = st.checkbox(f"I confirm I have uploaded the proof.")
            submit_btn = st.form_submit_button("Submit & Finish Game")
            
            if submit_btn:
                if not confirm:
                    st.error("Please tick the checkbox!")
                else:
                    # Finalize the game (status becomes 'correct' or 'failed')
                    update_game_status(token, status_for_db, proof_url="Uploaded via Google Form")
                    st.balloons()
                    time.sleep(2)
                    st.rerun()

def show_game_page(user):
    st.header("🕵️ My Mystery")
    st.caption("Read the clues and guess who your Santa is!")

    # --- 1. GET CLUES ---
    santa_row = get_santa_clues(user['email'])
    
    if not santa_row or not santa_row['clues_submitted']:
        st.warning("⏳ Your Santa hasn't created your clues yet. Check back later!")
        st.image("https://media.giphy.com/media/l0HlHJGHe3yAMhdQY/giphy.gif")
        return

    # --- 2. CHECK DATABASE STATUS ---
    # This is the critical fix. We check what the DB says, not the browser.
    current_status = user.get('guess_status', 'pending')

    # SCENARIO A: Game Totally Done
    if user['game_completed']:
        st.info("✅ You have completed the game!")
        if 'correct' in current_status:
            st.balloons()
            st.success("🎉 You Guessed CORRECTLY!")
            st.markdown(f"**Your Victory Task was:** {user.get('bonus_task')}")
        else:
            st.error("💀 You Failed!")
            st.markdown(f"**Your Penalty Task was:** {user.get('dare_task')}")
        st.write("Your proof has been recorded.")
        return

    # SCENARIO B: Guessed Right (Locked), Waiting for Upload
    if current_status == 'attempted_correct':
        show_upload_ui(
            user['secret_token'], 'correct', santa_row['bonus_task'], "🌟 VICTORY LAP", "win"
        )
        return

    # SCENARIO C: Guessed Wrong (Locked), Waiting for Upload
    if current_status == 'attempted_wrong':
        show_upload_ui(
            user['secret_token'], 'failed', santa_row['dare_task'], "😈 THE PENALTY", "lose"
        )
        return

    # SCENARIO D: Haven't Guessed Yet (Pending) - SHOW FORM
    # Only show this if status is EXACTLY 'pending'
    if current_status == 'pending':
        st.markdown("### 🧩 The Clues")
        with st.container(border=True):
            st.write(f"**1. (Hard):** {santa_row['clue_1']}")
            st.write(f"**2. (Medium):** {santa_row['clue_2']}")
            st.write(f"**3. (Easy):** {santa_row['clue_3']}")
        
        all_employees = get_all_employee_names()
        
        with st.form("guessing_form"):
            guess = st.selectbox("I think my Santa is...", ["Select Name"] + all_employees)
            btn = st.form_submit_button("🎲 Submit Guess")
            
            if btn:
                if guess == "Select Name":
                    st.warning("Pick a name!")
                else:
                    # 🔴 CRITICAL FIX: Update Database IMMEDIATELY
                    is_correct = (guess == santa_row['name'])
                    
                    with st.spinner("Checking your guess..."):
                        lock_guess_attempt(user['secret_token'], is_correct)
                        time.sleep(1)
                        st.rerun() # Reload page to switch to Scenario B or C