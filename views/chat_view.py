import streamlit as st
import time
from modules.db_service import get_token_by_email, get_santa_token, get_messages, send_message

def show_chat_tab(user):
    st.header("💬 Secret Communications")
    st.caption("Talk to your Santa or tease your Child here!")

    # Split into two sub-tabs
    tab_child, tab_santa = st.tabs([
        f"🎅 Chat with  My Child", 
        "🕵️ Chat with Secret Santa"
    ])

    # =================================================
    # SECTION 1: CHAT WITH MY CHILD (I am Santa)
    # =================================================
    with tab_child:
        st.info("You are chatting with your **Secret Child**. Keep your identity secret!")
        
        # 1. Find Child's Token
        child_token = get_token_by_email(user['match_email'])
        
        if not child_token:
            st.error("Error: Could not find your child in the database.")
        else:
            # 2. Display Chat History
            messages = get_messages(user['secret_token'], child_token)
            
            # Container for messages
            chat_container = st.container(height=300)
            with chat_container:
                if not messages:
                    st.write("No messages yet. Start the conversation!")
                
                for msg in messages:
                    # If I sent it (as Santa)
                    if msg['sender_token'] == user['secret_token']:
                        with st.chat_message("user", avatar="🎅"):
                            st.write(msg['message_text'])
                    else:
                        # If Child sent it
                        with st.chat_message("assistant", avatar="👶"):
                            st.write(msg['message_text'])

            # 3. Input Input
            with st.form("chat_child_form", clear_on_submit=True):
                text = st.text_input("Message as Santa...")
                sent = st.form_submit_button("Send 🚀")
                if sent and text:
                    send_message(user['secret_token'], child_token, text, 'santa')
                    st.rerun()
            
            if st.button("🔄 Refresh Chat", key="refresh_child"):
                st.rerun()


    # =================================================
    # SECTION 2: CHAT WITH MY SANTA (I am Child)
    # =================================================
    with tab_santa:
        st.info("You are chatting with your **Secret Santa**. You don't know who they are!")
        
        # 1. Find Santa's Token
        santa_token = get_santa_token(user['email'])
        
        if not santa_token:
            st.warning("Your Santa hasn't been assigned correctly yet.")
        else:
            # 2. Display Chat History
            messages = get_messages(user['secret_token'], santa_token)
            
            chat_container_2 = st.container(height=300)
            with chat_container_2:
                if not messages:
                    st.write("It's quiet here... maybe ask for a hint?")
                
                for msg in messages:
                    # If I sent it (as Child)
                    if msg['sender_token'] == user['secret_token']:
                        with st.chat_message("user", avatar="👶"):
                            st.write(msg['message_text'])
                    else:
                        # If Santa sent it
                        with st.chat_message("assistant", avatar="🎅"):
                            st.write(msg['message_text'])

            # 3. Input
            with st.form("chat_santa_form", clear_on_submit=True):
                text = st.text_input("Message your Secret Santa...")
                sent = st.form_submit_button("Send 🚀")
                if sent and text:
                    send_message(user['secret_token'], santa_token, text, 'child')
                    st.rerun()
            
            if st.button("🔄 Refresh Chat", key="refresh_santa"):
                st.rerun()