import streamlit as st
from supabase import create_client, Client

# Initialize connection
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# Insert a fake row
data, count = supabase.table('participants').insert({
    "name": "Test User", 
    "email": "test@test.com"
}).execute()

print("Inserted Data:", data)