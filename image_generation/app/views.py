import os
import io
import json
import yaml
import time
import base64
from PIL import Image
from pathlib import Path
from datetime import datetime
from googletrans import Translator
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.generic import View
from django.utils.decorators import method_decorator

from .services.image_generator import ImageGenerator
from .forms import RegisterForm, LoginForm


# Путь к корневой директории проекта
BASE_DIR = Path(__file__).resolve().parent.parent

file_path = Path(__file__).parent / 'services' / 'prompts.yml'
with open(file_path, 'r', encoding='utf-8') as file:
    CONFIG = yaml.safe_load(file)

WEIGHTS_PATH = BASE_DIR / 'weights' / 'models--stabilityai--stable-diffusion-xl-base-1'
LORA_WEIGHTS_PATH = BASE_DIR / 'weights' / 'lora' / 'pytorch_lora_weights.safetensors'
DEVICE = 'cuda:0'
IMG_GENERATOR = ImageGenerator(device=DEVICE)
IMG_GENERATOR.initialize_pipeline(WEIGHTS_PATH)
IMG_GENERATOR.load_lora_weights(LORA_WEIGHTS_PATH)


class CustomLoginView(LoginView):
    template_name = 'login.html'
    authentication_form = LoginForm

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('generator')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})

@login_required
def generator(request):
    print("User:", request.user)
    return render(request, 'tilda_wrapper.html', {'username': request.user.username})




def get_product(request):    
    return JsonResponse({'products': list(CONFIG['PRODUCT'].keys())})


@csrf_exempt
def get_prompts(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        product_name = data.get('input_text')

        if product_name not in CONFIG['PRODUCT']:
            translator = Translator()
            translated = translator.translate(product_name, src='ru', dest='en')
            product_describe = translated.text
        else:
            product_describe = CONFIG['PRODUCT'][product_name]

        prompt = f"{CONFIG['STYLE']['start']} of {product_describe} {CONFIG['STYLE']['end']}, {CONFIG['QUALITY']['prompt']}"
        negative_prompt = f"{CONFIG['QUALITY']['negative_prompt']}"
        return JsonResponse({'prompt': prompt, 'negative_prompt': negative_prompt})
    return JsonResponse({'error': 'Invalid request'}, status=400)

# @csrf_exempt
# def generate_image(request):
#     if request.method == 'POST':
#         prompts = request.POST.get('prompts', '')
#         negative_prompts = request.POST.get('negative_prompts', '')
#         height = int(request.POST.get('height', 512))
#         width = int(request.POST.get('width', 512))
#         seed = request.POST.get('seed', 5)

#         print(height, width, seed)
        
#         # Генерация черного квадрата 512x512
#         img = Image.new('RGB', (height, width), color = (0, 0, 0))
#         buffered = io.BytesIO()
#         img.save(buffered, format="PNG")
#         img_str = base64.b64encode(buffered.getvalue()).decode()

#         return JsonResponse({'image': img_str, 'width': width, 'height': height})
#     return JsonResponse({'error': 'Invalid request'}, status=400)


@csrf_exempt
def generate_image(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request'}, status=400)
    else:
        user_id = request.user.username
        prompt = request.POST.get('prompt', '')
        negative_prompt = request.POST.get('negative_prompt', '')

        try:
            height = int(request.POST.get('height', 512))
            width = int(request.POST.get('width', 512))
            seed = int(request.POST.get('seed', 1))
        except ValueError:
            return JsonResponse({'error': 'Invalid value: expected integers for height, width, and seed.'}, status=400)

        print(user_id, type(user_id))
        print(prompt)
        print(negative_prompt)
        
        start_time = time.time()
        generated_image = IMG_GENERATOR.generate_images(
            prompt=prompt, 
            negative_prompt=negative_prompt,
            num_inference_steps=50,
            guidance_scale=12,
            height=height,
            width=width,
            eta=0.0,
            num_images_per_prompt=1,
            seed=seed
        )[0]
        generation_time = time.time() - start_time
        
        buffered = io.BytesIO()
        generated_image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()

        
        image_name = None
        if user_id != 'anonymous':
            # Создание директории пользователя, если она не существует
            user_dir = BASE_DIR / 'logs' / user_id
            if not user_dir.exists():
                user_dir.mkdir(parents=True)

            # Создание директории для изображений, если она не существует
            images_dir = user_dir / 'generated_images'
            if not images_dir.exists():
                images_dir.mkdir()

            # Сохранение изображения в файл
            image_name = f"{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
            image_path = images_dir / image_name
            with open(image_path, 'wb') as f:
                f.write(buffered.getvalue())

            # Путь к лог-файлу
            log_file = user_dir / 'log.json'

            # Загрузка существующего лог-файла или создание нового
            if log_file.exists():
                with open(log_file, 'r') as f:
                    logs = json.load(f)
            else:
                logs = []

            # Добавление новой записи в логи
            timestamp = datetime.now().isoformat()
            log_entry = {
                # "product_name": prompts,  # todo
                "prompt": prompt,
                "negative_prompt": negative_prompt,
                "height": height,
                "width": width,
                "seed": seed,
                "timestamp": timestamp,
                "generation_time": generation_time,
                "image_path": str(image_path),
                "like": None
            }
            logs.append(log_entry)

            # Сохранение обновленного лог-файла
            with open(log_file, 'w') as f:
                json.dump(logs, f, indent=4)

        return JsonResponse({'image': img_str, 'width': width, 'height': height, 'image_name': image_name, 'user_id': user_id, 'timestamp': timestamp})

        
@csrf_exempt
def update_image_feedback(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_id = data.get('user_id')
            timestamp = data.get('timestamp')
            like = data.get('like')

            if not all([user_id, timestamp, like is not None]):
                return JsonResponse({'success': False, 'error': 'Missing data'})

            # Путь к лог файлу
            log_file_path = BASE_DIR / 'logs' / user_id / 'log.json'

            if not os.path.exists(log_file_path):
                return JsonResponse({'success': False, 'error': 'Log file not found'})

            # Читаем содержимое лог файла
            with open(log_file_path, 'r') as log_file:
                logs = json.load(log_file)

            # Находим запись с соответствующим timestamp и обновляем like
            updated = False
            for entry in logs:
                if entry['timestamp'] == timestamp:
                    entry['like'] = like
                    updated = True
                    break

            if not updated:
                return JsonResponse({'success': False, 'error': 'Timestamp not found in log'})

            # Записываем обновленные логи обратно в файл
            with open(log_file_path, 'w') as log_file:
                json.dump(logs, log_file, indent=4)

            return JsonResponse({'success': True})
        
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})


