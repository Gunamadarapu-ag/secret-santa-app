import streamlit as st
import time
from modules.db_service import submit_wishlist

def show_wishlist_page(user):
    """
    Phase 1: The User must submit their wishlist.
    This acts as a 'Gatekeeper'. They cannot proceed until this is done.
    """
    st.title(f"Welcome, {user['name']}! 🎄")
    st.markdown("### Step 1: Help your Secret Santa")
    
    st.info("Before the game begins, you must tell your Santa what you like. They can't read your mind!")
    
    with st.container(border=True):
        st.markdown("**📝 Your Wishlist**")
        st.caption("Be specific! e.g., 'I love dark chocolate,' 'I need a new mousepad,' 'Sci-Fi books'.")
        
        # Form to submit wishlist
        with st.form("wishlist_form"):
            wishlist_text = st.text_area("Dear Santa, I would like...", height=150)
            
            submitted = st.form_submit_button("💾 Save & Enter Game", type="primary", use_container_width=True)
            
            if submitted:
                if not wishlist_text.strip():
                    st.error("Please write something! Don't make your Santa guess.")
                else:
                    with st.spinner("Saving your preferences..."):
                        # Call the DB function
                        submit_wishlist(user['secret_token'], wishlist_text)
                        
                        st.success("Saved! Redirecting...")
                        time.sleep(1)
                        st.rerun() # Reloads the app to move to the next phase