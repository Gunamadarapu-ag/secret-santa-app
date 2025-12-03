import streamlit as st
import time
from modules.db_service import get_santa_clues, get_all_employee_names, update_game_status

def show_game_page(user):
    st.header("🕵️ My Mystery (Player Mode)")
    
    # 1. CHECK IF GAME IS COMPLETED
    if user['game_completed']:
        status = user.get('guess_status')
        if status == 'correct':
            st.balloons()
            st.success("🎉 YOU WON! You guessed your Santa correctly!")
        else:
            st.error("💀 You Failed the Guess!")
            st.info("But you submitted your dare proof, so you are safe... for now.")
            st.markdown(f"[View Your Proof]({user.get('dare_proof_url')})")
        return

    # 2. GET SANTA'S DATA (The row where match_name == ME)
    santa_row = get_santa_clues(user['email'])
    
    if not santa_row or not santa_row['clues_submitted']:
        st.info("⏳ Your Santa hasn't created your game yet. Come back later!")
        return

    # 3. THE GAME UI
    st.markdown("### 🧩 Who is your Santa?")
    st.write("Read the clues and make your guess.")
    
    with st.container(border=True):
        st.markdown(f"**Clue 1:** {santa_row['clue_1']}")
        st.markdown(f"**Clue 2:** {santa_row['clue_2']}")
        st.markdown(f"**Clue 3:** {santa_row['clue_3']}")
    
    # 4. GUESSING FORM
    all_employees = get_all_employee_names()
    
    with st.form("guessing_form"):
        guess = st.selectbox("I think my Santa is...", ["Select Name"] + all_employees)
        
        # Logic: If they already failed locally but haven't uploaded proof, we show Dare UI
        # But to keep it simple, we do it in one flow.
        
        btn = st.form_submit_button("🎲 Submit Guess")
        
        if btn:
            if guess == "Select Name":
                st.warning("Pick a name!")
            elif guess == santa_row['name']:
                # CORRECT GUESS
                update_game_status(user['secret_token'], 'correct')
                st.balloons()
                st.success("CORRECT! 🎉")
                time.sleep(1)
                st.rerun()
            else:
                # WRONG GUESS -> TRIGGER DARE
                st.session_state['wrong_guess'] = True

    # 5. DARE UI (Only shows if they guessed wrong)
    if st.session_state.get('wrong_guess'):
        st.error(f"❌ WRONG! It is NOT {guess}.")
        st.markdown("---")
        st.header("😈 THE PENALTY")
        st.markdown(f"**You must:** {santa_row['dare_task']}")
        
        with st.container(border=True):
            st.markdown("### 📸 Step 1: Upload Proof")
            st.write("Since you missed the guess, you must upload a video/photo of you doing the dare.")
            st.info("Don't worry, only the Admin can see this until the Reveal Party!")

            # LINK TO YOUR GOOGLE FORM
            # REPLACE 'YOUR_GOOGLE_FORM_LINK_HERE' with the actual link you copied!
            google_form_link = "YOUR_GOOGLE_FORM_LINK_HERE" 
            
            st.markdown(
                f"""
                <a href="{google_form_link}" target="_blank" style="text-decoration: none;">
                    <button style="
                        background-color: #FF4B4B;
                        color: white;
                        border: none;
                        border-radius: 5px;
                        padding: 10px 20px;
                        font-weight: bold;
                        cursor: pointer;
                        width: 100%;
                        font-size: 16px;
                        margin-bottom: 15px;">
                        📤 Click Here to Upload Proof
                    </button>
                </a>
                """, 
                unsafe_allow_html=True
            )

            st.markdown("---")
            st.markdown("### ✅ Step 2: Confirm Submission")
            st.write("Once you have uploaded the file in the Google Form, come back here and confirm.")

            with st.form("confirm_proof_form"):
                # We use a checkbox to make them physically acknowledge it
                confirm = st.checkbox("I swear on my Secret Santa honor that I uploaded the proof.")
                
                submit_btn = st.form_submit_button("Submit & Finish Game")
                
                if submit_btn:
                    if not confirm:
                        st.error("Please tick the checkbox to confirm!")
                    else:
                        # We send a placeholder string for the URL since the file is in your Form now
                        update_game_status(user['secret_token'], 'failed', proof_url="Uploaded via Google Form")
                        
                        st.balloons()
                        st.success("Proof confirmed! You are safe... for now. See you at the party! 🎄")
                        time.sleep(2)
                        st.rerun()
        st.error(f"❌ WRONG! It is NOT {guess}.")
        st.markdown("---")
        st.header("😈 THE PENALTY")
        st.markdown(f"**You must:** {santa_row['dare_task']}")
        
        with st.form("dare_proof_form"):
            st.write("Upload your proof (Preferably a **Video** 🎥) to Google Drive and paste the link here:")
            
            # --- NEW ADDITION: Link to open Google Drive ---
            st.markdown(
                """
                <a href="https://drive.google.com/drive/my-drive" target="_blank" style="text-decoration: none;">
                    <button style="
                        background-color: #ffffff;
                        border: 1px solid #d2d2d2;
                        border-radius: 5px;
                        padding: 5px 10px;
                        cursor: pointer;
                        color: #31333F;
                        font-size: 14px;
                        display: flex;
                        align-items: center;
                        gap: 5px;
                        margin-bottom: 10px;">
                        📂 Open Google Drive to Upload
                    </button>
                </a>
                """, 
                unsafe_allow_html=True
            )
            # -----------------------------------------------

            proof_link = st.text_input("Paste your Link here (Make sure access is 'Anyone with link')")
            
            submit_proof = st.form_submit_button("✅ Submit Proof")
            
            if submit_proof:
                if not proof_link:
                    st.error("We need proof! Don't be shy.")
                else:
                    update_game_status(user['secret_token'], 'failed', proof_link)
                    st.success("Proof recorded. See you at the reveal party!")
                    time.sleep(1)
                    st.rerun()