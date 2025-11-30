import streamlit as st
import pandas as pd
import time
import requests
from streamlit_lottie import st_lottie

# Import Modules
from modules.pairing_logic import generate_matches
from modules.db_service import (
    save_matches_to_db, 
    get_user_by_token, 
    mark_as_revealed, 
    submit_survey, 
    get_target_preferences
)
from modules.email_service import send_magic_link_emails, send_confirmation_email

# Page Config
st.set_page_config(page_title="Secret Santa", page_icon="🎅", layout="centered")

# --- ASSETS & HELPERS ---
def load_lottieurl(url):
    try:
        r = requests.get(url)
        if r.status_code != 200: return None
        return r.json()
    except: return None

LOTTIE_GIFT_BOX = "https://assets6.lottiefiles.com/packages/lf20_j1adxgsv.json"
LOTTIE_CONFETTI = "https://assets9.lottiefiles.com/packages/lf20_u4yrau.json"

# --- MAIN LOGIC ---

# 1. CHECK FOR TOKEN (Participant Mode)
query_params = st.query_params
user_token = query_params.get("token", None)

if user_token:
    # ====================================================
    # 🎅 PARTICIPANT VIEW
    # ====================================================
    user = get_user_by_token(user_token)
    
    if not user:
        st.error("❌ Invalid or Expired Link. Please contact the Admin.")
    else:
        st.title(f"Hello, {user['name']}! 🎄")
        st.markdown(f"**Group:** {user['location']}")

        # STEP 1: THE WITTY SURVEY (Gatekeeper)
        if not user.get('survey_completed', False):
            st.markdown("## 🕵️ First, a quick interrogation...")
            st.info("The elves need some intel before giving you your mission.")
            
            with st.container(border=True):
                with st.form("witty_survey"):
                    # Question 1 (Private)
                    st.markdown("### 1. The Betting Pool 🎲")
                    st.write("Be honest... who are you secretly hoping picked your name?")
                    st.caption("*(We won't tell them. This is just for our secret stats!)*")
                    expected_santa = st.text_input("I hope my Santa is...", placeholder="e.g. The Boss, My Bestie")
                    
                    st.divider()
                    
                    # Question 2 (Public to Santa)
                    st.markdown("### 2. Drop a Hint 🎁")
                    st.write("Help your Santa out! What kind of vibe are you feeling this year?")
                    st.caption("*(Your Santa will see this!)*")
                    gift_pref = st.text_area("Dear Santa, I like...", placeholder="e.g. Coffee beans, Sci-Fi books, or 'Surprise me!'")
                    
                    st.divider()
                    
                    # Submit Button
                    submitted = st.form_submit_button("💾 Save Answers & Unlock Mission", type="primary", use_container_width=True)
                    
                if submitted:
                    with st.spinner("Processing your intel..."):
                        submit_survey(user_token, gift_pref, expected_santa)
                        time.sleep(1)
                        st.rerun()

        # STEP 2: THE REVEAL (Unlocked)
        else:
            if user['is_revealed']:
                # --- VIEW AFTER REVEALING ---
                st.success("✅ Mission Active")
                
                # Show Match
                st.markdown("### You are the Secret Santa for:")
                st.header(f"✨ {user['match_name']} ✨")
                st.caption(f"Email: {user['match_email']}")
                
                # Show Match's Wishlist
                target_wishlist = get_target_preferences(user['match_email'])
                with st.expander(f"🎁 See what {user['match_name']} wants!", expanded=True):
                    if target_wishlist and target_wishlist != "No preference listed yet.":
                        st.info(f"📝 **Their Wishlist:** {target_wishlist}")
                    else:
                        st.warning("They hasn't filled out their wishlist yet.")
                
                # st_lottie(load_lottieurl(LOTTIE_CONFETTI), height=200)
                confetti_anim = load_lottieurl(LOTTIE_CONFETTI)
                if confetti_anim:
                    st_lottie(confetti_anim, height=200)
                else:
                    st.markdown("# 🎉")
                    st.balloons()

            else:
                # --- VIEW BEFORE REVEALING ---
                st.markdown("### Your mission is ready to unlock...")
                gift_anim = load_lottieurl(LOTTIE_GIFT_BOX)
                if gift_anim:
                    st_lottie(gift_anim, height=200)
                else:
                    # Fallback: If animation fails, show a standard Gift Emoji/Image so app doesn't crash
                    st.markdown("# 🎁")

                
                
                if st.button("🎁 CLICK TO REVEAL 🎁", type="primary", use_container_width=True):
                    st.balloons()
                    
                    # 1. Update DB
                    mark_as_revealed(user_token)
                    
                    # 2. Get Wishlist for Email
                    target_wishlist = get_target_preferences(user['match_email'])
                    
                    # 3. Send Confirmation Email
                    if "GMAIL_USER" in st.secrets:
                        send_confirmation_email(
                            user['email'], 
                            user['name'], 
                            user['match_name'], 
                            target_wishlist,
                            st.secrets["GMAIL_USER"],
                            st.secrets["GMAIL_PASS"]
                        )
                    
                    st.rerun()

else:
    # ====================================================
    # 🛠️ ADMIN VIEW
    # ====================================================
    st.title("🎅 Secret Santa Admin")
    
    # Credentials Check
    if "GMAIL_USER" not in st.secrets or "SUPABASE_URL" not in st.secrets:
        st.error("❌ Secrets missing! Check .streamlit/secrets.toml")
        st.stop()
    
    sender_email = st.secrets["GMAIL_USER"]
    sender_password = st.secrets["GMAIL_PASS"]

    # App URL Input
    default_url = "http://localhost:8501"
    app_url = st.sidebar.text_input("App URL (for Emails)", value=default_url)
    
    # 1. Upload
    uploaded_file = st.file_uploader("Upload CSV", type=['csv'])
    
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        
        # 2. Generate
        if st.button("1. Generate Pairs 🎲"):
            matches_df, errors = generate_matches(df)
            if errors:
                for e in errors: st.error(e)
            else:
                st.success(f"Generated {len(matches_df)} matches!")
                st.session_state['matches_df'] = matches_df
                st.dataframe(matches_df)

        # 3. Save & Send
        if 'matches_df' in st.session_state:
            st.divider()
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("2. Save to DB 💾"):
                    with st.spinner("Saving..."):
                        data = save_matches_to_db(st.session_state['matches_df'])
                        st.session_state['saved_data'] = data
                    st.success("Saved!")
            
            with col2:
                if 'saved_data' in st.session_state:
                    if st.button("3. Send Magic Links 📧"):
                        with st.spinner("Sending emails..."):
                            sent, failed, logs = send_magic_link_emails(
                                st.session_state['saved_data'], 
                                sender_email, 
                                sender_password, 
                                app_url
                            )
                        if sent > 0: st.success(f"✅ Sent {sent} emails!")
                        if failed > 0: st.error(f"❌ Failed: {failed}")
                        if logs: st.write(logs)