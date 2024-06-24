import streamlit as st
import requests
import os
import json

def register():
    st.title("Register Page")

    new_username = st.text_input("New Username")
    new_password = st.text_input("New Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")

    django_server_url = st.secrets["django_server_url"]

    if st.button("Register"):
        response = requests.post(f'{django_server_url}/auth/register/', data={
            'username': new_username,
            'password': new_password,
            'confirm_password': confirm_password
        })
        data = response.json()
        if data.get('status') == 'success':
            st.success("Registration successful! You can now log in with your new credentials.")
            create_user_log_directory(new_username)
        else:
            st.error(data.get('message'))

def create_user_log_directory(username):
    base_dir = os.path.join('../../logs', username)
    images_dir = os.path.join(base_dir, 'images')
    
    try:
        os.makedirs(images_dir, exist_ok=True)
        log_file_path = os.path.join(base_dir, 'logs.json')
        
        # Initialize the JSON file with basic structure
        if not os.path.exists(log_file_path):
            with open(log_file_path, 'w') as log_file:
                json.dump([], log_file)
        
        st.info(f"Log directory and files created for user {username}")
    except Exception as e:
        st.error(f"An error occurred while creating log directory: {e}")

# Call the register function to start the Streamlit app
if __name__ == "__main__":
    register()

