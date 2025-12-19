import streamlit as st
import time
import random
import base64
import os
from modules.db_service import init_supabase

# --- 🎄 YOUR CUSTOM GIF COLLECTION 🎄 ---
CHRISTMAS_GIFS = [
    "https://i.pinimg.com/originals/64/d6/68/64d668edefd478d2e854b8f85860c38d.gif",
    "https://i.pinimg.com/originals/26/4b/fd/264bfdd7c50246d9d073859d0372c4fd.gif",
    "https://media1.tenor.com/m/Ll9uXID1JlUAAAAd/santa-holiday.gif",
    "https://media1.tenor.com/m/GFM8ICHi2YcAAAAC/drunk-santa-christmas.gif",
    "https://media1.tenor.com/m/CGWT7_goYaYAAAAd/santa-christmas.gif",
    "https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExbGR3M3EyNHc0c3Vza3lpbDhhb3dyazRlMTJhcnd2ZWJ6YjJubWwycCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/2LbfRQVHs34V1Ru8Pt/giphy.gif",
    "https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjExZ2gxOWs3aWdocmV3cmllMjYzZzIzZWxnMzl4eGFmMndzdnZtbWFwciZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/dDUC94GA0rtcVQabVi/giphy.gif",
    "https://i.pinimg.com/originals/cd/d0/b8/cdd0b8d91e61c1ac885008bda07c2940.gif",
    "https://media1.giphy.com/media/v1.Y2lkPTZjMDliOTUyaHA2bTMxNzViMnh3cmxxeTVpZHczcWFqYnAzNThtdnpiNGdhdnFmbSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/atYhTwajuBtgpwnnuZ/giphy.gif",
    "https://media1.giphy.com/media/v1.Y2lkPTZjMDliOTUyZ3ZiM29jZWplZ3JmMWhqbXZ4MWFtdjNpeHh5enp1eXV2ZTMyd3ptdiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/adTkWs5OqAZaGW48h0/giphy.gif",
    "https://media4.giphy.com/media/v1.Y2lkPTZjMDliOTUyZHlua3QwOW82ZnN5ajF6eTRzZjVsNDNycGp0cTJxZWVpMGNkNGl5ayZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/10k8HMhtzzk73W/giphy.gif",
    "https://media2.giphy.com/media/v1.Y2lkPTZjMDliOTUyb3dkd3YwN2FwZmg0Ym9scGpvY2x0c3BlNndlcXl5MGlwOXFzODZzeiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/SqFuGemni7Bynbl11F/giphy.gif",
    "https://media4.giphy.com/media/v1.Y2lkPTZjMDliOTUyeDN1YnhvZ2d2ejBxMzNnd3Z0bnFibjBpcTF5ODR2MDBpbnozYTJvYSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/IZek2g6kKZ8AXnAsUJ/giphy.gif"
]

# --- SOUND HELPERS ---
def play_jingle():
    try:
        if os.path.exists("jingle.mp3"):
            with open("jingle.mp3", "rb") as f:
                b64 = base64.b64encode(f.read()).decode()
                st.markdown(f'<audio autoplay style="display:none;"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>', unsafe_allow_html=True)
    except: pass

def play_reveal_sound():
    try:
        if os.path.exists("reveal.mp3"):
            with open("reveal.mp3", "rb") as f:
                b64 = base64.b64encode(f.read()).decode()
                st.markdown(f'<audio autoplay style="display:none;"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>', unsafe_allow_html=True)
    except: pass

def show_grand_reveal():
    st.markdown("<h1 style='text-align: center;'>🎬 The Grand Reveal Event</h1>", unsafe_allow_html=True)

    # ==========================================
    # 🔐 1. SECURITY & LOCATION SELECTION
    # ==========================================
    if 'reveal_authenticated' not in st.session_state:
        st.session_state.reveal_authenticated = False
        st.session_state.reveal_location = None

    if not st.session_state.reveal_authenticated:
        col1, col2 = st.columns(2)
        with col1:
            # RANDOM GIF
            st.image(random.choice(CHRISTMAS_GIFS), use_container_width=True) 
        
        with col2:
            st.info("🔒 Restricted Area: Event Admins Only")
            location = st.selectbox("Select Location", ["Bangalore", "Chennai"])
            password = st.text_input("Event Password", type="password")
            
            if st.button("🔓 Enter Event Mode"):
                play_jingle() 
                try:
                    correct_pass = st.secrets[f"REVEAL_PASS_{location.upper()}"]
                    if password == correct_pass:
                        st.session_state.reveal_authenticated = True
                        st.session_state.reveal_location = location
                        st.success(f"Welcome to {location} Reveal!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("❌ Wrong Password!")
                except:
                    st.error("Secrets not configured.")
        return

    # ==========================================
    # 🎭 2. THE REVEAL DASHBOARD
    # ==========================================
    
    supabase = init_supabase()
    if 'reveal_data' not in st.session_state:
        loc = st.session_state.reveal_location
        resp = supabase.table('participants').select("*").eq('location', loc).execute()
        st.session_state.reveal_data = resp.data
        
    participants = st.session_state.reveal_data
    
    # SIDEBAR
    names_list = [p['name'] for p in participants]
    selected_name = st.sidebar.selectbox("🎯 Pick a Person (The Child)", ["Select"] + names_list)
    
    if st.sidebar.button("🔄 Reset Journey"):
        play_jingle()
        st.session_state.reveal_step = 0
        st.rerun()

    if selected_name == "Select":
        st.info(f"👋 Welcome to the **{st.session_state.reveal_location}** Edition!")
        st.write("Select a person to start.")
        # RANDOM GIF
        st.image(random.choice(CHRISTMAS_GIFS), use_container_width=True)
        return

    person = next(p for p in participants if p['name'] == selected_name)

    if 'reveal_step' not in st.session_state:
        st.session_state.reveal_step = 0

    # --- HEADER ---
    st.markdown(f"<h2 style='text-align: center; color: #FF4B4B;'>Target: {person['name']}</h2>", unsafe_allow_html=True)
    st.progress(st.session_state.reveal_step * 20)

    # --- STEP 0: START ---
    if st.session_state.reveal_step == 0:
        st.write("### 🏁 The Journey Begins")
        st.write(f"Let's see if **{person['name']}** figured it out...")
        
        if st.button("🔍 Start Clue Reveal"):
            play_jingle()
            st.session_state.reveal_step = 1
            st.session_state.clue_count = 1
            st.rerun()

    # --- STEP 1: THE CLUES (ONE BY ONE) ---
    elif st.session_state.reveal_step == 1:
        st.write("### 🧩 The Clues:")
        
        col_clues, col_gif = st.columns([2, 1])
        
        with col_clues:
            with st.container(border=True):
                st.markdown(f"**1. (Hard):** {person['clue_1']}")
                
                if st.session_state.clue_count >= 2:
                    st.divider()
                    st.markdown(f"**2. (Medium):** {person['clue_2']}")
                
                if st.session_state.clue_count >= 3:
                    st.divider()
                    st.markdown(f"**3. (Easy):** {person['clue_3']}")
        
        with col_gif:
            # 🎄 THIS CHANGES EVERY TIME 'RERUN' IS CALLED 🎄
            st.image(random.choice(CHRISTMAS_GIFS), caption="The suspense is building...", use_container_width=True)

        st.markdown("---")
        
        # BUTTON LOGIC
        if st.session_state.clue_count < 3:
            if st.button("➡️ Reveal Next Clue"):
                play_jingle()
                st.session_state.clue_count += 1
                st.rerun() # Rerunning changes the GIF above!
        else:
            st.info("🎤 MC: 'Do you know who it is??'")
            if st.button("🤔 Check Their Guess (Database)"):
                play_jingle()
                st.session_state.reveal_step = 2
                st.rerun()

    # --- STEP 2: THE GUESS STATUS ---
    elif st.session_state.reveal_step == 2:
        st.write("### 🤖 Database Check:")
        status = person['guess_status']
        
        if status == 'correct' or status == 'attempted_correct':
            st.success(f"🎉 YES! {person['name']} guessed CORRECTLY!")
            st.balloons()
            st.markdown(f"**Victory Task:** {person.get('bonus_task')}")
            if st.button("🎭 Go to Reveal"):
                play_jingle()
                st.session_state.reveal_step = 4
                st.rerun()
        else:
            st.error(f"❌ OOPS! They guessed WRONG (or didn't guess).")
            st.markdown(f"**The Penalty was:** {person.get('dare_task')}")
            if st.button("😈 Check for Proof"):
                play_jingle()
                st.session_state.reveal_step = 3
                st.rerun()

    # --- STEP 3: THE PENALTY CHECK ---
    elif st.session_state.reveal_step == 3:
        st.write("### 😈 The Penalty Phase")
        proof_url = person.get('dare_proof_url')
        
        if proof_url and "http" in proof_url:
            st.success("✅ Proof Found!")
            st.markdown(f"[📂 Open Proof Video]({proof_url})")
        else:
            st.warning("⚠️ NO PROOF FOUND!")
            st.markdown("## 🎤 DO IT LIVE! 🎤")
            st.error(f"User must perform: **{person.get('dare_task')}** right now!")
            # Use random gif here too
            st.image(random.choice(CHRISTMAS_GIFS), width=300) 
        
        st.markdown("---")
        if st.button("🎭 Enough Torture... Reveal Santa!"):
            play_jingle()
            st.session_state.reveal_step = 4
            st.rerun()

    # --- STEP 4: THE COUNTDOWN ---
    elif st.session_state.reveal_step == 4:
        placeholder = st.empty()
        for i in range(3, 0, -1):
            placeholder.markdown(f"<h1 style='text-align: center; font-size: 100px;'>{i}</h1>", unsafe_allow_html=True)
            time.sleep(1)
        
        st.session_state.reveal_step = 5
        st.rerun()

    # --- STEP 5: THE BIG REVEAL ---
    elif st.session_state.reveal_step == 5:
        play_reveal_sound() 
        st.balloons()
        
        st.markdown(
            f"""
            <div style="text-align: center;">
                <h2>🎅 The Secret Santa was...</h2>
                <h1 style="font-size: 60px; color: #FF4B4B; text-shadow: 2px 2px #ffeb3b;">
                    ✨ {person['match_name']} ✨
                </h1>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
        st.image(random.choice(CHRISTMAS_GIFS), use_container_width=True) 
        
        st.markdown("---")
        if st.button("🎯 Pick Next Person"):
            play_jingle()
            st.session_state.reveal_step = 0
            st.rerun()