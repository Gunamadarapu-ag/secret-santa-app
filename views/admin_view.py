import streamlit as st
import pandas as pd

# Import ALL necessary modules
from modules.pairing_logic import generate_matches
from modules.db_service import (
    init_game_db, 
    get_participant_count, 
    add_more_participants, 
    get_pending_santas 
)
from modules.email_service import send_game_links, send_clue_reminders

def show_admin_page():
    st.title("🎅 Secret Santa Admin")
    
    # --- 1. LIVE DASHBOARD METRICS (Auto-Loaded) ---
    try:
        total_count = get_participant_count()
        
        # Fetch pending list immediately to show status
        pending_list = get_pending_santas()
        pending_count = len(pending_list)
        completed_count = total_count - pending_count
        
        # Display Columns
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Elves", total_count)
        col2.metric("Clues Submitted", completed_count)
        col3.metric("Pending", pending_count, delta=f"-{pending_count}", delta_color="inverse")
        
        # Progress Bar
        if total_count > 0:
            progress = completed_count / total_count
            st.progress(progress, text=f"Game Setup Progress: {int(progress*100)}%")
            
    except Exception as e:
        st.error("Could not load metrics. Check Database connection.")
    
    st.divider()

    # --- 2. PASSWORD PROTECTION ---
    password = st.sidebar.text_input("🔐 Admin Password", type="password")
    
    if password != st.secrets["ADMIN_PASSWORD"]:
        st.warning("⚠️ Enter the Admin Password in the sidebar to access controls.")
        return 

    st.success("✅ Admin Access Granted")

    # --- 3. CONFIGURATION ---
    default_url = "http://localhost:8501/" 
    app_url = st.sidebar.text_input("App URL", value=default_url)

    # --- 4. UPLOAD & GENERATE ---
    uploaded_file = st.file_uploader("Upload CSV (For New Location/Batch)", type=['csv'])
    
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        
        if st.button("1. Generate Pairs 🎲"):
            matches_df, errors = generate_matches(df)
            if errors:
                for e in errors: st.error(e)
            else:
                st.success(f"Generated {len(matches_df)} pairs.")
                st.session_state['matches_df'] = matches_df
                st.dataframe(matches_df)

        # --- 5. SAVE TO DATABASE ---
        if 'matches_df' in st.session_state:
            st.divider()
            st.write("### 💾 Saving Options")
            
            col1, col2 = st.columns(2)
            
            # OPTION A: NUCLEAR WIPE
            with col1:
                if st.button("⚠️ Initialize NEW Event (Wipes DB)", type="primary"):
                    st.warning("This deletes ALL existing data! Are you sure?")
                    if st.checkbox("Yes, delete everything"):
                        with st.spinner("Wiping and saving..."):
                            data = init_game_db(st.session_state['matches_df'])
                            if data:
                                st.session_state['saved_data'] = data
                                st.success("Database Reset & New Data Added!")

            # OPTION B: SAFE ADD
            with col2:
                if st.button("➕ Add to Existing Event (Safe)"):
                    with st.spinner("Adding new people..."):
                        data = add_more_participants(st.session_state['matches_df'])
                        if data:
                            st.session_state['saved_data'] = data
                            st.success(f"✅ Added {len(data)} new people! Existing data is safe.")

            # --- 6. SEND WELCOME EMAILS ---
            st.divider()
            if 'saved_data' in st.session_state:
                st.info(f"Ready to email {len(st.session_state['saved_data'])} users.")
                if st.button("3. Send Game Links 📧"):
                    with st.spinner("Sending emails..."):
                        s, f, l = send_game_links(
                            st.session_state['saved_data'], 
                            st.secrets["GMAIL_USER"], 
                            st.secrets["GMAIL_PASS"], 
                            app_url
                        )
                    st.success(f"Sent: {s}, Failed: {f}")
                    if l: st.write(l)

    # --- 7. NUDGE LAZY SANTAS (UPDATED) ---
    st.divider()
    st.header("📢 Nudge Lazy Santas")
    
    # We already fetched 'pending_list' at the top, so we use it here directly.
    if pending_count == 0:
        st.success("🎉 Everyone has submitted their clues! The game is fully active.")
    else:
        st.warning(f"⚠️ {pending_count} people have NOT submitted clues yet.")
        
        with st.expander(f"View Pending List ({pending_count})"):
            pending_names = [u['name'] for u in pending_list]
            st.write(pending_names)
        
        st.write("Send them a warning email?")
        
        # THE THREAT BUTTON
        if st.button("📨 Send 'Default Clue' Warning"):
            with st.spinner("Sending threats..."):
                s, f, l = send_clue_reminders(
                    pending_list,
                    st.secrets["GMAIL_USER"], 
                    st.secrets["GMAIL_PASS"], 
                    app_url
                )
            st.success(f"Sent {s} reminders!")
            if f > 0: st.error(f"Failed: {f}")
    
    # # --- 8. GRAND REVEAL MODE ---
    # st.sidebar.divider()
    # if st.sidebar.button("🎬 Launch Grand Reveal Mode"):
    #     st.session_state['reveal_mode'] = True
    #     st.rerun()