# Image Generator

## Описание
Генерация продающих изображений с веб-интерфейсом

## Основная информация по проекту
### Версии
- ImgGenerator - actual version
- image_generation - old version (will be removed)

### Структура репозитория
- `ImgGenerator/weights`: Директория для скачивания весов моделей. Скачайте веса [здесь](https://disk.yandex.ru/d/dGy3tpUD90ccCg) и разместите их в этой директории.
  - `ImgGenerator/weights/lora`: Веса после дообучения модели
  - `ImgGenerator/weights/models--stabilityai--stable-diffusion-xl-base-1`: Веса оригинальной модели Stable Diffusion XL Base для работы приложения в автономном режиме
- `ImgGenerator/logs`: Директория для хранения всех результатов генерации с дополнительной мета-информацией, включая сгенерированные изображения
- `ImgGenerator/app/services/image_generator.py`: Логика генерации изображений
- `ImgGenerator/app/services/prompts.py`: Промпты для генерации изображений по продукту/клиенту
- `train_scripts`: Скрипты для обучения модели Stable Diffusion от Diffusers
- `DEMO.ipynb`: Ноутбук с демонстрационным запуском генеративной модели (перед запуском скачайте веса и поместите их в нужную директорию)
- `RND.ipynb`: Ноутбук для экспериментов и бенчмарков моделей

### Как запустить проект
Для удобства мы развернули наш проект на внешнем веб-сервисе: [http://77.223.101.161:8502/](http://77.223.101.161:8502/) \
Также прилагаем инструкцию для запуска на локальной машине

1. **Склонировать проект к себе на локальную машину:**
    ```bash
    git clone <URL_проекта>
    ```
2. **Скачать веса из [Yandex Disk](https://disk.yandex.ru/d/dGy3tpUD90ccCg) и распаковать их в директорию `ImgGenerator/weights` (или в image_generation/weights для старой версии).**
3. **Варианты запуска**
    - **В ноутбуке**
        1. Откройте и выполните ноутбук `DEMO.ipynb`

    - **Локальный веб-сервис**
        1. В терминале перейдите в директорию `ImgGenerator/` и запустите сервис django       
            ```bash
            python manage.py runserver 127.0.0.1:8501
            ```
            При необходимости, предварительно настройте ALLOWED_HOSTS, CSRF_TRUSTED_ORIGINS (и пр. urls) в `ImgGenerator/ImgGenerator/settings.py`
            
        2. В отдельном терминале перейдите в директорию `ImgGenerator/app/streamlit_scripts` и запустите сервис streamlit
            ```bash
            streamlit run app.py
            ```
            При необходимости, настройте django_server_url в `ImgGenerator/app/streamlit_scripts/.streamlit/secrets.toml` (должен соответствовать адресу из шага 1) и address, port в `ImgGenerator/app/streamlit_scripts/.streamlit/config.toml`


## Как использовать веб-сервис
1. Перейдите по адресу, где развернут сервис
2. Войдите или зарегистрируйтесь
3. Выберите или введите название продукта в поле `Product Name`, укажите номер `Client ID` и нажмите `Get Prompts`
4. Отредактируйте текстовые описания в полях `Prompt` и `Negative Prompt` по своему усмотрению
5. Настройте дополнительные параметры через кнопку `Params`, если необходимо
6. Нажмите кнопку `Generate` и дождитесь сгенерированного изображения
7. Оцените изображение с помощью кнопки `Like` или `Dislike`
8. При необходимости, можно посмотреть логи предыдущих генераций, кликнув на кнопку `User Logs`

## Дополнительная информация
1. **Предустановленные пользователи:**
    - Суперюзер: `admin`, пароль: `admin` (только для локального использования)
    - Тестовый пользователь: `test1`, пароль: `test1`
3. **Админская панель**
    - Доступна по адресу: `ip_address/admin/` (только для локального использования)
4. **Структура веб-проекта**
    - Проект сохраняет стандартное расположение и наименование исходных файлов, предусмотренных django
5. **Аппартаная настройка**
    - Для аппаратной настройки инференса следует корректировать файл `ImgGenerator/app/streamlit_scripts/app.py` с соотетствующим параметром DEVICE или логику модели в `ImgGenerator/app/services/image_generator.py`

## Ссылки
- [Внешний веб-сервис](http://77.223.101.161:8502/)
- [Веса модели](https://disk.yandex.ru/d/MoS-gfJ4HmnbGQ)
- [Перезентация по проекту](https://disk.yandex.ru/i/PbJZT9FiVNL2mg)
- [Примеры генераций](https://disk.yandex.ru/d/LclIO4S5KGGf5A)

