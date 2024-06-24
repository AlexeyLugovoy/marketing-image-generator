import streamlit as st
from auth import check_auth

def login():
    st.title("Login Page")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    django_server_url = st.secrets["django_server_url"]

    if st.button("Login"):
        authenticated, session_id = check_auth(username, password, django_server_url)
        if authenticated:
            st.session_state.authenticated = True
            st.session_state.username = username
            st.session_state.session_id = session_id
            st.success("Login successful!")
        else:
            st.error("Login failed. Please check your username and password or use 'Register' tab")
