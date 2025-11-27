import streamlit as st
import pandas as pd
from modules.pairing_logic import generate_matches
from modules.email_service import send_secret_santa_emails

# Page Config
st.set_page_config(page_title="Secret Santa Manager", page_icon="🎅")

st.title("🎅 Secret Santa Manager")
st.markdown("Upload your employee CSV to generate pairs and send emails.")

# Sidebar: Credentials
st.sidebar.header("📧 Email Configuration")

# Check if secrets exist in the cloud environment
if "GMAIL_USER" in st.secrets and "GMAIL_PASS" in st.secrets:
    st.sidebar.success("✅ Credentials loaded securely from Secrets.")
    sender_email = st.secrets["GMAIL_USER"]
    sender_password = st.secrets["GMAIL_PASS"]
else:
    # Fallback for local testing (if you haven't set up local secrets)
    st.sidebar.warning("⚠️ Running locally? Enter credentials manually.")
    sender_email = st.sidebar.text_input("Sender Gmail Address")
    sender_password = st.sidebar.text_input("Gmail App Password", type="password")

# 1. File Upload
uploaded_file = st.file_uploader("Upload CSV (Columns: empid, empname, empmail, location)", type=['csv'])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.dataframe(df.head())

    # 2. Generate Pairs
    if st.button("🎲 Generate Pairs"):
        matches_df, errors = generate_matches(df)
        
        if errors:
            st.error("Errors Found:")
            for e in errors:
                st.write(e)
        
        if matches_df is not None and not matches_df.empty:
            st.success(f"Successfully generated {len(matches_df)} pairs!")
            st.dataframe(matches_df)
            
            # Store in session state so we don't lose it
            st.session_state['matches'] = matches_df
        else:
            st.warning("No pairs could be generated.")

# 3. Send Emails Section
if 'matches' in st.session_state and not st.session_state['matches'].empty:
    st.divider()
    st.subheader("🚀 Ready to Notify?")
    st.write(f"This will send {len(st.session_state['matches'])} emails.")
    
    if st.button("Send Emails Now"):
        if not sender_email or not sender_password:
            st.error("Please fill in Email and App Password in the sidebar.")
        else:
            with st.spinner("Sending emails..."):
                sent, failed, logs = send_secret_santa_emails(
                    st.session_state['matches'], 
                    sender_email, 
                    sender_password
                )
            
            if sent > 0:
                st.balloons()
                st.success(f"✅ Sent {sent} emails successfully!")
            
            if failed > 0:
                st.error(f"❌ Failed to send {failed} emails.")
                for log in logs:

                    st.text(log)
