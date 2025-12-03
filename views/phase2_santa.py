import streamlit as st
import time
from modules.db_service import get_target_info, submit_clues_and_dare

def show_santa_dashboard(user):
    st.header("🎅 My Mission (Santa Mode)")
    st.info(f"You are the Secret Santa for: **{user['match_name']}**")
    
    # 1. SHOW TARGET'S WISHLIST
    target_data = get_target_info(user['match_email'])
    wishlist = target_data.get('wishlist') if target_data else "Not submitted yet."
    
    with st.expander(f"🎁 View {user['match_name']}'s Wishlist", expanded=True):
        if wishlist:
            st.success(f"**They want:** {wishlist}")
        else:
            st.warning("They haven't updated their wishlist yet. Check back later!")

    st.divider()

    # 2. CHECK IF I ALREADY SUBMITTED CLUES
    if user['clues_submitted']:
        st.success("✅ You have submitted your clues! Now wait for them to guess.")
        st.markdown(f"**Your Dare for them:** {user.get('dare_task')}")
    else:
        # 3. FORM TO SUBMIT CLUES
        st.markdown("### 🕵️ Create the Game")
        st.write("You must give 3 clues about YOUR identity so they can guess you.")
        
        with st.form("clues_form"):
            c1 = st.text_input("Clue 1 (Easy)", placeholder="e.g. I sit near the window")
            c2 = st.text_input("Clue 2 (Medium)", placeholder="e.g. I drink black coffee")
            c3 = st.text_input("Clue 3 (Hard)", placeholder="e.g. I have a cat named Luna")
            
            st.markdown("#### 😈 The Penalty")
            st.write("If they guess wrong, what must they do?")
            dare = st.text_input("Dare Task", placeholder="e.g. Record a video singing Jingle Bells")
            
            submit = st.form_submit_button("🚀 Launch Mission", type="primary")
            
            if submit:
                if not c1 or not c2 or not c3 or not dare:
                    st.error("Please fill in all fields!")
                else:
                    with st.spinner("Locking in your clues..."):
                        submit_clues_and_dare(user['secret_token'], c1, c2, c3, dare)
                        st.success("Mission Launched!")
                        time.sleep(1)
                        st.rerun()