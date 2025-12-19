import streamlit as st
import time
import requests
from streamlit_lottie import st_lottie

# --- IMPORTING YOUR MODULES ---
from views.admin_view import show_admin_page
from views.phase1_wishlist import show_wishlist_page
from views.phase2_santa import show_santa_dashboard
from views.phase3_game import show_game_page
from views.chat_view import show_chat_tab
from views.reveal_view import show_grand_reveal

from modules.db_service import get_user_by_token

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Secret Santa 2025", 
    page_icon="🎅", 
    layout="centered",
    initial_sidebar_state="expanded"
)

# --- ASSETS & ANIMATIONS ---
def load_lottieurl(url):
    try:
        r = requests.get(url)
        return r.json() if r.status_code == 200 else None
    except: return None

# Animation: Santa flying in sleigh
LOTTIE_SANTA = "https://lottie.host/801a2f64-1629-4d93-9428-1422792e3423/8XfD7Xk39m.json" 

# --- MAIN APP LOGIC ---

# 1. GET TOKEN FROM URL
query_params = st.query_params
token = query_params.get("token", None)

# ---------------------------------------------------------
# SCENARIO A: NO TOKEN -> ADMIN AREA
# ---------------------------------------------------------
if not token:
    # Check if Admin triggered the Grand Reveal Mode
    if st.session_state.get('reveal_mode'):
        show_grand_reveal()
        st.sidebar.divider()
        if st.sidebar.button("🔙 Exit Reveal Mode"):
             st.session_state['reveal_mode'] = False
             st.rerun()
    else:
        show_admin_page()

# ---------------------------------------------------------
# SCENARIO B: TOKEN EXISTS -> USER AREA
# ---------------------------------------------------------
else:
    user = get_user_by_token(token)
    
    if not user:
        st.error("❌ Invalid or Expired Link. Please contact the Admin.")
    else:
        # --- 1. SIDEBAR INFO ---
        st.sidebar.markdown(f"### 👤 {user['name']}")
        st.sidebar.caption(f"Location: {user['location']}")
        st.sidebar.divider()
        
        # --- 2. GAME RULES ---
        with st.sidebar.expander("📜 Game Rules", expanded=False):
            st.markdown("""
            **📅 Important Dates:**
            *   **Game Starts:** Today!
            *   **Reveal Date:** Dec 19th
            
            **🎁 Gift Guidelines:**
            *   **Max Value:** 1000 INR.
            *   **Delivery:** Online or In-Person.
            
            **🎭 The Game:**
            *   Santa must be guessed within 3 clues.
            *   **Wrong Guess Penalty:** You must perform the specific **Dare Task** assigned by your Santa! 😈
            """)

        # --- 3. PHASE MANAGEMENT ---
        
        # CHECK PHASE 1: Has the user submitted a wishlist?
        if not user.get('wishlist'):
            # Only snow on first load
            if 'intro_snow' not in st.session_state:
                st.snow()
                st.session_state['intro_snow'] = True
                
            lottie_santa = load_lottieurl(LOTTIE_SANTA)
            if lottie_santa: st_lottie(lottie_santa, height=200)
            
            show_wishlist_page(user)
            
        else:
            # PHASE 2 & 3: MAIN DASHBOARD
            st.title("🎄 Secret Santa Dashboard")
            
            # --- NAVIGATION BAR (Replaces Tabs for Snow Effect) ---
            # We use st.radio to behave like tabs, but it allows us to trigger events on change
            selected_tab = st.radio(
                "Navigate:", 
                ["🎅 My Mission", "🕵️ My Mystery", "💬 Secret Chat"], 
                horizontal=True,
                label_visibility="collapsed" # Hides the label text
            )
            
            # --- SNOW LOGIC ---
            # Detect if the tab changed from the last run
            if 'current_tab' not in st.session_state:
                st.session_state.current_tab = selected_tab
            
            # If the user clicked a different tab, trigger snow and update state
            if st.session_state.current_tab != selected_tab:
                st.snow() 
                st.session_state.current_tab = selected_tab

            st.divider()

            # --- RENDER SELECTED VIEW ---
            
            if selected_tab == "🎅 My Mission":
                show_santa_dashboard(user)

            elif selected_tab == "🕵️ My Mystery":
                # 🔒 LOCK LOGIC
                if False: # Set to True to Lock, False to Unlock
                    st.info("🔒 This section is locked!")
                    st.write("### 📅 The Guessing Game begins in 2 Days!")
                    st.write("Use this time to chat with your Santa and Child in the Chat tab.")
                    
                    # --- NEW CINEMATIC VIEW (Full Width) ---
                    st.markdown(
                        """
                        <style>
                            /* Container to center and stretch */
                            .cinematic-container {
                                width: 100%;
                                display: block;
                                margin: 0 auto;
                                overflow: hidden; /* Hides spillover */
                                border-radius: 12px;
                                box-shadow: 0 4px 12px rgba(0,0,0,0.5);
                            }
                            
                            /* The Video/GIF itself */
                            .cinematic-video {
                                width: 100% !important;  /* Force full width */
                                height: auto;            /* Maintain aspect ratio */
                                display: block;
                                object-fit: cover;       /* Ensure it covers the space */
                            }
                        </style>

                        <div class="cinematic-container">
                            <!-- High Quality Widescreen Santa GIF -->
                            <img src="https://i.gifer.com/Ft6C.gif" class="cinematic-video">
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    # ---------------------------
                    
                else:
                    # Unlocked Game View
                    show_game_page(user)

            elif selected_tab == "💬 Secret Chat":
                show_chat_tab(user)