import streamlit as st
import pandas as pd
from modules.pairing_logic import generate_matches
from modules.db_service import init_game_db
from modules.email_service import send_game_links

def show_admin_page():
    st.title("🎅 Secret Santa Admin (Game Mode)")
    
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
            
            with col1:
                if st.button("2. Initialize Game DB 💾"):
                    with st.spinner("Wiping old data & saving new..."):
                        data = init_game_db(st.session_state['matches_df'])
                        if data:
                            st.session_state['saved_data'] = data
                            st.success("✅ Database Initialized!")

            # 4. Send Emails
            with col2:
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