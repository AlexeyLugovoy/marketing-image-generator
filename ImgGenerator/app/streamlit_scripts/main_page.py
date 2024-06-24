# main_page.py
import streamlit as st
import yaml
import time
import os
from PIL import Image
import numpy as np
from googletrans import Translator
import hashlib
import requests
from datetime import datetime
import json


def hash_image(image):
    """Возвращает хэш изображения."""
    return hashlib.md5(image.tobytes()).hexdigest()

def generate_image(img_generator, prompt, negative_prompt, num_inference_steps, height, width, seed):
    start_time = time.time()
    generated_image = img_generator.generate_images(
        prompt=prompt, 
        negative_prompt=negative_prompt,
        num_inference_steps=num_inference_steps,
        guidance_scale=12,
        height=height,
        width=width,
        eta=0.0,
        num_images_per_prompt=1,
        seed=seed
    )[0]
    generation_time_taken = time.time() - start_time
    return generated_image, generation_time_taken

def save_logs_and_image(logs, image, image_file_name):
    log_dir = f"../../logs/{st.session_state.username}"
    image_dir = os.path.join(log_dir, "images")
    os.makedirs(image_dir, exist_ok=True)
    
    image_file_path = os.path.join(image_dir, image_file_name)
    image.save(image_file_path)
    
    # Сохранение логов
    log_file_path = os.path.join(log_dir, "logs.json")
    if os.path.exists(log_file_path) and os.path.getsize(log_file_path) > 0:
        with open(log_file_path, "r") as log_file:
            try:
                existing_logs = json.load(log_file)
            except json.JSONDecodeError:
                existing_logs = []
    else:
        existing_logs = []
    
    if not isinstance(existing_logs, list):
        existing_logs = []

    existing_logs.append(logs)
    
    with open(log_file_path, "w") as log_file:
        json.dump(existing_logs, log_file, ensure_ascii=False, indent=4)


def log_user_action(action, product_name, client_id, generation_time_taken, width, height, seed, num_inference_steps, prompt, negative_prompt, image_file_name):
    logs = {
        "user_name": st.session_state.username,
        "product_name": product_name,
        "client_id": client_id,
        "width": width,
        "height": height,
        "seed": seed,
        "num_inference_steps": num_inference_steps,
        "prompt": prompt,
        "negative_prompt": negative_prompt,
        "generation_time": st.session_state.generation_time.isoformat(),
        "generation_time_taken": generation_time_taken,
        "action": action,
        "file_name": image_file_name
    }
    save_logs_and_image(logs, st.session_state.generated_image, image_file_name)
    st.session_state.last_logged_image_hash = hash_image(st.session_state.generated_image)

def load_prompt_config():
    with open("../services/prompts.yml", "r", encoding="utf-8") as file:
        prompt_config = yaml.safe_load(file)
    return prompt_config

def get_prompts(product_name, client_id, prompt_config):
    client_id = (client_id % 10) // 4 + 1 # чтобы было всегда [0, 3]
    if product_name not in prompt_config['PRODUCT']:
        try:
            translator = Translator()
            translated = translator.translate(product_name, src='ru', dest='en')
            product_describe = translated.text
        except:
            # если нет подключения к интернету
            product_describe = ' '
    else:
        product_describe = prompt_config['PRODUCT'][product_name][client_id]

    prompt = f"{prompt_config['STYLE']['start']} of {product_describe} {prompt_config['STYLE']['end']}, {prompt_config['QUALITY']['prompt']}"
    negative_prompt = f"{prompt_config['QUALITY']['negative_prompt']}"
    return prompt, negative_prompt

def main_page(img_generator):
    st.title("Image Generator")
    
    prompt_config = load_prompt_config()
    
    if 'product_name' not in st.session_state:
        st.session_state.product_name = list(prompt_config['PRODUCT'].keys())[0]
    if 'client_id' not in st.session_state:
        st.session_state.client_id = 1

    col1, col2 = st.columns([1, 1])
    with col1:
        possible_values = list(prompt_config['PRODUCT'].keys())
        st.session_state.product_name = st.selectbox("Product Name", possible_values, index=0)
    with col2:
        st.session_state.client_id = st.number_input("Client ID", value=st.session_state.client_id, step=1)
    
    if st.button("Get Prompts", key="get_prompts"):
        prompt, negative_prompt = get_prompts(st.session_state.product_name, st.session_state.client_id, prompt_config)
        st.session_state.prompt = prompt
        st.session_state.negative_prompt = negative_prompt
    
    if 'prompt' not in st.session_state:
        st.session_state.prompt = " "
    if 'negative_prompt' not in st.session_state:
        st.session_state.negative_prompt = " "
    
    st.session_state.prompt = st.text_area("Prompt", value=st.session_state.prompt, height=100, key="prompt_text_area")
    st.session_state.negative_prompt = st.text_area("Negative Prompt", value=st.session_state.negative_prompt, height=100, key="negative_prompt_text_area")
    
    # Initialize parameters in session state
    if 'height' not in st.session_state:
        st.session_state.height = 512
    if 'width' not in st.session_state:
        st.session_state.width = 512
    if 'seed' not in st.session_state:
        st.session_state.seed = 5
    if 'num_inference_steps' not in st.session_state:
        st.session_state.num_inference_steps = 50

    if 'show_params' not in st.session_state:
        st.session_state.show_params = False

    if st.button("Params", key="show_params_button"):
        st.session_state.show_params = not st.session_state.show_params

    if st.session_state.show_params:
        st.markdown("**Additional Parameters**")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.session_state.height = st.number_input("Height", value=st.session_state.height, key="height_input")
        
        with col2:
            st.session_state.width = st.number_input("Width", value=st.session_state.width, key="width_input")
        
        with col3:
            st.session_state.seed = st.number_input("Seed", value=st.session_state.seed, key="seed_input")
        
        with col4:
            st.session_state.num_inference_steps = st.number_input("Num Inference Steps", value=st.session_state.num_inference_steps, key="num_inference_steps_input")
    
    if st.button("Generate"):
        with st.spinner("Generating image..."):
            generated_image, generation_time_taken = generate_image(
                img_generator=img_generator,
                prompt=st.session_state.prompt, 
                negative_prompt=st.session_state.negative_prompt,
                num_inference_steps=st.session_state.num_inference_steps,
                height=st.session_state.height,
                width=st.session_state.width,
                seed=st.session_state.seed
            )
            st.session_state.generated_image = generated_image
            st.session_state.generation_time = datetime.now()
            st.session_state.generation_time_taken = generation_time_taken

    if 'generated_image' in st.session_state:
        image_file_name = f"{st.session_state.generation_time.strftime('%Y%m%d%H%M%S')}.png"
        st.image(st.session_state.generated_image, caption="Generated Image", width=512)

        like, dislike = st.columns([1, 1])
        with like:
            if st.button("👍 Like", key="like_button"):
                current_image_hash = hash_image(st.session_state.generated_image)
                if 'last_logged_image_hash' in st.session_state and st.session_state.last_logged_image_hash == current_image_hash:
                    st.warning("You already rated this image.")
                else:
                    log_user_action("like", st.session_state.product_name, st.session_state.client_id, st.session_state.generation_time_taken, st.session_state.width, st.session_state.height, st.session_state.seed, st.session_state.num_inference_steps, st.session_state.prompt, st.session_state.negative_prompt, image_file_name)
                    st.success("You liked the image!")
        with dislike:
            if st.button("👎 Dislike", key="dislike_button"):
                current_image_hash = hash_image(st.session_state.generated_image)
                if 'last_logged_image_hash' in st.session_state and st.session_state.last_logged_image_hash == current_image_hash:
                    st.warning("You already rated this image.")
                else:
                    log_user_action("dislike", st.session_state.product_name, st.session_state.client_id, st.session_state.generation_time_taken, st.session_state.width, st.session_state.height, st.session_state.seed, st.session_state.num_inference_steps, st.session_state.prompt, st.session_state.negative_prompt, image_file_name)
                    st.error("You disliked the image.")

        
# Сохранение состояния и запуска функции основного контента
if __name__ == "__main__":
    main_page()




