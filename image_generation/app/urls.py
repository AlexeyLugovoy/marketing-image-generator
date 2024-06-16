from django.urls import path
from django.contrib.auth.views import LogoutView
from .views import (
    CustomLoginView, 
    register,
    generator,
    get_product,
    get_prompts,
    generate_image,
    update_image_feedback
)



urlpatterns = [
    path('', CustomLoginView.as_view(), name='login'),
    path('register/', register, name='register'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('generator/', generator, name='generator'),
    path('get_product/', get_product, name='get_product'),
    path('get_prompts/', get_prompts, name='get_prompts'),
    path('generate_image/', generate_image, name='generate_image'),
    path('update_image_feedback/', update_image_feedback, name='update_image_feedback'),
]
