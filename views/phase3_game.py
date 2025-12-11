import streamlit as st
import time
from modules.db_service import get_santa_clues, get_all_employee_names, update_game_status



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
    
    # --- 1. HEADER ---
    st.header("🕵️ My Mystery")
    st.caption("Read the clues and guess who your Santa is!")

    # --- 2. CHECK COMPLETION ---
    if user['game_completed']:
        status = user.get('guess_status')
        st.info("✅ You have completed the game!")
        
        if status == 'correct':
            st.balloons()
            st.success("🎉 You Guessed CORRECTLY!")
            st.markdown(f"**Your Victory Task was:** {user.get('bonus_task')}")
        else:
            st.error(" You Failed!")
            st.markdown(f"**Your Penalty Task was:** {user.get('dare_task')}")
            
        st.write("Your proof has been recorded. See you at the Reveal!")
        return

    # --- 3. WAIT FOR SANTA ---
    santa_row = get_santa_clues(user['email'])
    
    if not santa_row or not santa_row['clues_submitted']:
        st.warning("⏳ Your Santa hasn't created your clues yet. Check back later!")
        st.image("https://i.gifer.com/Ft6C.gif")
        return

    # --- 4. DISPLAY CLUES ---
    st.markdown("### 🧩 The Clues")
    with st.container(border=True):
        st.write(f"**1. (Hard):** {santa_row['clue_1']}")
        st.write(f"**2. (Medium):** {santa_row['clue_2']}")
        st.write(f"**3. (Easy):** {santa_row['clue_3']}")
    
    # --- 5. GUESSING FORM ---
    all_employees = get_all_employee_names()
    
    if not st.session_state.get('wrong_guess') and not st.session_state.get('correct_guess'):
        with st.form("guessing_form"):
            guess = st.selectbox("I think my Santa is...", ["Select Name"] + all_employees)
            btn = st.form_submit_button("🎲 Submit Guess")
            
            if btn:
                if guess == "Select Name":
                    st.warning("Pick a name!")
                elif guess == santa_row['name']:
                    st.session_state['correct_guess'] = True
                    st.rerun()
                else:
                    st.session_state['wrong_guess'] = True
                    st.rerun()

    # --- 6. UPLOAD UI ---
    
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
        st.error(f"❌ WRONG! It is NOT the right person.")
        st.markdown("---")
        st.header("😈 THE PENALTY")
        st.markdown(f"**You must:** {santa_row['dare_task']}")
        
        show_upload_ui(user['secret_token'], 'failed', santa_row['dare_task'])