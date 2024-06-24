# app.py
import os
import sys
import requests
import streamlit as st
from login import login
from register import register
from main_page import main_page
from logs import display_logs


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.image_generator import ImageGenerator

@st.cache_resource
def initialize_image_generator():
    DEVICE = 'cuda:0'
    weights_path = '../../weights/models--stabilityai--stable-diffusion-xl-base-1'
    lora_weights_path = '../../weights/lora/pytorch_lora_weights.safetensors'
    img_generator = ImageGenerator(device=DEVICE)
    img_generator.initialize_pipeline(weights_path)
    img_generator.load_lora_weights(lora_weights_path)
    return img_generator

img_generator = initialize_image_generator()

# Переменная для хранения состояния аутентификации
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# Создаем вкладки для логина и регистрации
tab_login, tab_register = st.sidebar.tabs(["Login", "Register"])

# Вкладка для логина
with tab_login:
    login()

# Вкладка для регистрации
with tab_register:
    register()

# Основной контент, доступный только после авторизации
if st.session_state.authenticated:
    user_name = st.session_state.username  # формируется в login()
    st.sidebar.success(f"Welcome, {user_name}!")
    main_page(img_generator)
    display_logs()
else:
    st.write("Please log in to view the content.")
