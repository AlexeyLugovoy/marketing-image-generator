import PIL
from PIL import Image 
import numpy as np
import matplotlib.pyplot as plt


def display_images(images: dict | list, show_axes: bool = True, grid: tuple = (1, None), figsize: tuple = (15, 5), tight_layout: bool = True):
    if isinstance(images, list):
        titles = []
        for i, img in enumerate(images):
            if isinstance(img, np.ndarray):
                if len(img.shape) == 2:
                    mode = "L"
                if img.shape[2] == 3:
                    mode = 'RGB'
                if img.shape[2] == 4:
                    mode = 'RGBA'
                else:
                    mode = 'N/A'
                title = f"img{i}, {img.shape}, {mode}, N/A"
            else:
                title = f"img{i}, {img.size}, {img.mode}, {img.format}"
            titles.append(title)

        images_with_titles = dict(zip(titles, images))
    else:
        images_with_titles = images

    num_images = len(images_with_titles)
    rows, cols = grid if grid[1] is not None else (grid[0], max(1, num_images // grid[0]))
    fig, axes = plt.subplots(rows, cols, figsize=figsize)
    axes = axes.flatten() if num_images > 1 else [axes]

    for ax, (title, image) in zip(axes, images_with_titles.items()):
        ax.imshow(image if isinstance(image, np.ndarray) else np.array(image))
        ax.set_title(title)
        if not show_axes:
            ax.axis('off')
    
    if tight_layout:
        plt.tight_layout()
    plt.show()
    



