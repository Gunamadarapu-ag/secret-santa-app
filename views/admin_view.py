import streamlit as st
import pandas as pd
from modules.pairing_logic import generate_matches
from modules.db_service import init_game_db, get_participant_count,add_more_participants
from modules.email_service import send_game_links

def show_admin_page():
    st.title("🎅 Secret Santa Admin (Game Mode)")
    try:
        count = get_participant_count()
        st.metric(label="Total Participants Joined", value=count)
    except:
        st.metric(label="Total Participants Joined", value=0)
    st.divider()
    # 2. PASSWORD PROTECTION
    password = st.sidebar.text_input("🔐 Admin Password", type="password")
    
    if password != st.secrets["ADMIN_PASSWORD"]:
        st.warning("⚠️ Enter the Admin Password in the sidebar to access controls.")
        return
    st.success("✅ Admin Access Granted")
    # Check Secrets
    if "GMAIL_USER" not in st.secrets:
        st.error("Secrets missing!")
        return

    # App URL Input
    default_url = "http://localhost:8501" # CHANGE THIS WHEN DEPLOYING
    app_url = st.sidebar.text_input("App URL", value=default_url)

    # 1. Upload
    uploaded_file = st.file_uploader("Upload Employee CSV", type=['csv'])
    
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        
        # 2. Generate Pairs
        if st.button("1. Generate Pairs 🎲"):
            matches_df, errors = generate_matches(df)
            if errors:
                for e in errors: st.error(e)
            else:
                st.success(f"Generated {len(matches_df)} pairs.")
                st.session_state['matches_df'] = matches_df
                st.dataframe(matches_df)

        # 3. Save to DB (Reset Game)
        if 'matches_df' in st.session_state:
            st.divider()
            col1, col2 = st.columns(2)
            
            # OPTION A: NUCLEAR WIPE (For starting fresh next year)
            with col1:
                if st.button("⚠️ Initialize NEW Event (Wipes DB)", type="primary"):
                    st.warning("This deletes ALL existing Bangalore data! Are you sure?")
                    if st.checkbox("Yes, delete everything and start over"):
                        with st.spinner("Wiping and saving..."):
                            data = init_game_db(st.session_state['matches_df'])
                            if data:
                                st.session_state['saved_data'] = data
                                st.success("Database Reset & New Data Added!")

            # OPTION B: APPEND (For adding Chennai now)
            with col2:
                if st.button("➕ Add to Existing Event (Safe)"):
                    with st.spinner("Adding new people..."):
                        # CALL THE NEW FUNCTION
                        data = add_more_participants(st.session_state['matches_df'])
                        if data:
                            st.session_state['saved_data'] = data
                            st.success(f"✅ Added {len(data)} new people! Bangalore data is safe.")
            # 4. SEND EMAILS
            st.divider()
            if 'saved_data' in st.session_state:
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