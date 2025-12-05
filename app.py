import streamlit as st
from views.admin_view import show_admin_page
from views.phase1_wishlist import show_wishlist_page
from views.phase2_santa import show_santa_dashboard
from views.phase3_game import show_game_page
from modules.db_service import get_user_by_token
from views.chat_view import show_chat_tab

st.set_page_config(page_title="Secret Santa Game", page_icon="🎄")

# 1. Get Token
query_params = st.query_params
token = query_params.get("token", None)

# 2. ROUTING LOGIC
if not token:
    show_admin_page()
else:
    user = get_user_by_token(token)
    
    if not user:
        st.error("❌ Invalid Link.")
    else:
        # GLOBAL SIDEBAR INFO
        st.sidebar.caption(f"Logged in as: {user['name']}")
        
        # CHECK PHASE 1 (Wishlist)
        if not user.get('wishlist'):
            show_wishlist_page(user)
        else:
            # PHASE 2 & 3 (Main Dashboard)
            st.title("🎄 Secret Santa Dashboard")
        
        # Create 3 Tabs
        tab1, tab2, tab3 = st.tabs([
            "🎅 My Mission (To Do)", 
            "🕵️ My Mystery (To Play)",
            "💬 Messages" 
        ])
        
        with tab1:
            show_santa_dashboard(user)
        
        with tab2:
            show_game_page(user)

        with tab3:
            show_chat_tab(user)