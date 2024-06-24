# если необходимо, в этот же класс пихаем всякие удаление фона и пр
# или добавление фона/текста - крч все, что связано с генерацией картинки

from diffusers import DiffusionPipeline
import torch


class ImageGenerator:
    def __init__(self, device='cpu'):
        self.device = device
        self.pipe = None

    def download_weights(self, dest_folder='./weights'):
        print("download weights to ./weights")
        pass
    
    def initialize_pipeline(
        self,
        pretrained_model_name_or_path='./weights/models--stabilityai--stable-diffusion-xl-base-1', 
        cache_dir='.'):
        
        """ 
        pretrained_model_name_or_path: str, default='./weights/models--stabilityai--stable-diffusion-xl-base-1'
            Could use the standart stabilityai/stable-diffusion-xl-base-1.0 
            from diffusers (but do not forget about cache_dir)
        """
        
        self.pipe = DiffusionPipeline.from_pretrained(
            pretrained_model_name_or_path,
            torch_dtype=torch.float16,
            use_safetensors=True,
            variant="fp16",
            cache_dir=cache_dir
        ).to(self.device)

    
    def load_lora_weights(self, lora_weights_path: str = './weights/lora_weights/pytorch_lora_weights.safetensors'):
        self.pipe.load_lora_weights(lora_weights_path)
        

    def generate_images(
        self, 
        prompt, 
        negative_prompt,
        num_inference_steps=50,
        guidance_scale=12,
        height=512,
        width=512,
        eta=0.0,
        num_images_per_prompt=1,
        seed=1
    ):

        height = self.nearest_multiple_of_8(height)
        width = self.nearest_multiple_of_8(width)
        
        pipe_result = self.pipe(
            prompt=prompt,
            negative_prompt=negative_prompt,
            num_inference_steps=num_inference_steps,
            guidance_scale=guidance_scale,
            height=height,
            width=width,
            eta=eta,
            num_images_per_prompt=num_images_per_prompt,
            generator=torch.Generator(self.device).manual_seed(seed),
        ).images
        
        return pipe_result

    @staticmethod
    def nearest_multiple_of_8(value, greater=True):
        return (value + 7) // 8 * 8 if greater else value // 8 * 8
    