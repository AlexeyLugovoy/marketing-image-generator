import streamlit as st
from PIL import Image
import json
from datetime import datetime
import os

def load_logs(user_name):
    log_file_path = os.path.join("../../logs", user_name, "logs.json")
    if os.path.getsize(log_file_path) == 0:
        return []  # Возвращаем пустой список, если файл пуст
    with open(log_file_path, "r") as f:
        logs = json.load(f)
    return logs

def load_image(file_name, user_name):
    image_path = os.path.join("../../logs", user_name, "images", file_name)
    return Image.open(image_path)

def display_logs():
    user_name = st.session_state.username  # Получаем имя пользователя из session_state

    if 'logs' not in st.session_state:
        st.session_state.logs = load_logs(user_name)
    if 'log_index' not in st.session_state:
        st.session_state.log_index = 0
    if 'filter_date' not in st.session_state:
        st.session_state.filter_date = ""
    if 'filter_product' not in st.session_state:
        st.session_state.filter_product = ""
    if 'filtered_logs' not in st.session_state:
        st.session_state.filtered_logs = st.session_state.logs

    if st.sidebar.button("User Logs"):
        st.session_state.show_logs = not st.session_state.get('show_logs', False)

    if st.session_state.get('show_logs', False):
        st.sidebar.title("Logs")
        
        st.sidebar.markdown("**Filter Logs**")
        filter_date = st.sidebar.text_input("Date (YYYY-MM-DD)", value=st.session_state.filter_date)
        filter_product = st.sidebar.text_input("Product Name", value=st.session_state.filter_product)
        
        if st.sidebar.button("Apply Filter"):
            st.session_state.filter_date = filter_date
            st.session_state.filter_product = filter_product

            filtered_logs = st.session_state.logs
            if filter_date:
                filtered_logs = [log for log in filtered_logs if log['generation_time'].startswith(filter_date)]
            if filter_product:
                filtered_logs = [log for log in filtered_logs if filter_product.lower() in log['product_name'].lower()]
            
            st.session_state.filtered_logs = filtered_logs
            st.session_state.log_index = 0  # Сброс индекса для отображения

        logs_to_display = st.session_state.filtered_logs[st.session_state.log_index:st.session_state.log_index + 5]

        for i, log in enumerate(logs_to_display):
            st.sidebar.markdown("---")
            if st.sidebar.button("View Full Image", key=f"view_{st.session_state.log_index + i}"):
                image = load_image(log['file_name'], user_name)
                st.image(image, caption=f"Prompt: {log['prompt']}, Negative Prompt: {log['negative_prompt']}, Seed: {log['seed']}, Num Inference Steps: {log['num_inference_steps']}", use_column_width=True)
            else:
                image = load_image(log['file_name'], user_name)
                st.sidebar.image(image, width=100)
                st.sidebar.markdown(f"**User Name:** {log['user_name']}")
                st.sidebar.markdown(f"**Product Name:** {log['product_name']}")
                st.sidebar.markdown(f"**Client ID:** {log['client_id']}")
                st.sidebar.markdown(f"**Prompt:** {log['prompt']}")
                st.sidebar.markdown(f"**Negative Prompt:** {log['negative_prompt']}")
                st.sidebar.markdown(f"**Height:** {log['height']}")
                st.sidebar.markdown(f"**Width:** {log['width']}")
                st.sidebar.markdown(f"**Seed:** {log['seed']}")
                st.sidebar.markdown(f"**Num Inference Steps:** {log['num_inference_steps']}")
                st.sidebar.markdown(f"**Generation Time:** {log['generation_time']}")
                st.sidebar.markdown(f"**Generation Time Taken:** {log['generation_time_taken']}")
                st.sidebar.markdown(f"**Action:** {log['action']}")
                st.sidebar.markdown(f"**File Name:** {log['file_name']}")

        if st.sidebar.button("Load more logs"):
            st.session_state.log_index += 5

# Сохранение состояния и запуска функции основного контента
if __name__ == "__main__":
    display_logs()


