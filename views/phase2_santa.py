import streamlit as st
import time
import requests
from streamlit_lottie import st_lottie
from modules.db_service import get_target_info, submit_clues_and_dare

# --- ASSETS ---
def load_lottieurl(url):
    try:
        r = requests.get(url)
        return r.json() if r.status_code == 200 else None
    except: return None

# Fireworks Animation
LOTTIE_FIREWORKS = "https://assets2.lottiefiles.com/packages/lf20_pwohahvd.json"

def show_santa_dashboard(user):
    st.header("🎅 My Mission (Santa Mode)")

    # --- 1. SECRET REVEAL LOGIC ---
    if 'show_target_name' not in st.session_state:
        st.session_state.show_target_name = False

    def toggle_name():
        st.session_state.show_target_name = not st.session_state.show_target_name
        
        # Trigger effects only on reveal
        if st.session_state.show_target_name:
            st.balloons()
            st.toast("🥁 Drumroll please...", icon="🥁")
            time.sleep(0.8) 
            st.toast(f"🎉 It's {user['match_name']}!", icon="🎁")

    # Target Info Container
    with st.container(border=True):
        col_text, col_btn = st.columns([5, 1], gap="small")
        
        with col_text:
            if st.session_state.show_target_name:
                
                # Fireworks
                lottie_fireworks = load_lottieurl(LOTTIE_FIREWORKS)
                if lottie_fireworks:
                    st_lottie(lottie_fireworks, height=150, key="fireworks")
                
                # Glowing Text
                st.markdown(
                    f"""
                    <div style="
                        font-size: 24px; font-weight: bold; color: #ffffff; 
                        background: linear-gradient(45deg, #ff357a, #fff172);
                        padding: 15px; border-radius: 12px; text-align: center;
                        box-shadow: 0 0 20px rgba(255, 53, 122, 0.7);
                        animation: pulse 2s infinite; border: 2px solid white;">
                        🎯 Target: {user['match_name']}
                    </div>
                    <style>
                    @keyframes pulse {{
                        0% {{ transform: scale(1); }} 50% {{ transform: scale(1.02); }} 100% {{ transform: scale(1); }}
                    }}
                    </style>
                    """, 
                    unsafe_allow_html=True
                )
            else:
                st.info("🎯 You are the Secret Santa for: ******************")
        
        with col_btn:
            if st.session_state.show_target_name:
                st.button("🙈 Hide", on_click=toggle_name, use_container_width=True)
            else:
                st.button("👁️ Reveal", on_click=toggle_name, type="primary", use_container_width=True)

    st.divider()

    # --- 2. SIDE-BY-SIDE WISHLISTS ---
    
    target_data = get_target_info(user['match_email'])
    target_wishlist = target_data.get('wishlist') if target_data else "Not submitted yet."
    my_wishlist = user.get('wishlist', "You haven't added one.")

    col_target, col_me = st.columns(2)

    with col_target:
        # Dynamic Name Display
        if st.session_state.show_target_name:
            display_name = user['match_name']
        else:
            display_name = "Your Child"

        st.markdown(f"### 🎁 **{display_name}'s** Wishlist")
        st.caption("(What they want from YOU)")
        
        with st.container(border=True):
            if target_wishlist == "Not submitted yet.":
                st.warning(target_wishlist)
            else:
                st.success(f"📝 {target_wishlist}")

    with col_me:
        st.markdown("### 📝 **Your** Wishlist")
        st.caption("(What you told your Santa)")
        with st.container(border=True):
            st.info(f"{my_wishlist}")

    st.divider()

    # --- 3. CLUES & TASKS FORM ---
    if user['clues_submitted']:
        st.success("✅ You have submitted your clues! Now wait for them to guess.")
        with st.expander("View what you submitted"):
            st.write(f"**Clue 1:** {user.get('clue_1')}")
            st.write(f"**Clue 2:** {user.get('clue_2')}")
            st.write(f"**Clue 3:** {user.get('clue_3')}")
            st.write(f"**Dare:** {user.get('dare_task')}")
            st.write(f"**Bonus:** {user.get('bonus_task')}")
    else:
        st.markdown("### 🕵️ Create the Game")
        st.write("You must give 3 clues about YOUR identity so they can guess you.")
        
        with st.form("clues_form"):
            st.write("### 1. The Clues")
            c1 = st.text_input("Clue 1 (Hard)", placeholder="e.g. I sit near the window")
            c2 = st.text_input("Clue 2 (Medium)", placeholder="e.g. I drink black coffee")
            c3 = st.text_input("Clue 3 (Easy)", placeholder="e.g. I have a cat named Luna")
            
            st.markdown("---")
            st.write("### 2. The Tasks")
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("#### 😈 The Penalty")
                st.caption("If they guess WRONG (Lose)")
                dare = st.text_input("Dare Task", placeholder="e.g. Sing Jingle Bells")
            
            with col2:
                st.markdown("#### 🌟 The Bonus")
                st.caption("If they guess RIGHT (Win)")
                bonus = st.text_input("Victory Task", placeholder="e.g. Do a victory dance")
            
            submit = st.form_submit_button("🚀 Launch Mission", type="primary")
            
            if submit:
                # [Removed Play Jingle Sound Call]
                if not c1 or not c2 or not c3 or not dare or not bonus:
                    st.error("Please fill in ALL fields (Clues, Dare, and Bonus)!")
                else:
                    with st.spinner("Locking in your clues..."):
                        submit_clues_and_dare(user['secret_token'], c1, c2, c3, dare, bonus)
                        st.success("Mission Launched!")
                        time.sleep(1)
                        st.rerun()