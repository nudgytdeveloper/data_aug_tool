import os
import random
from PIL import Image, ImageOps


def zoom_out_image(
    input_path,
    output_path,
    padding_factor_min: float = 0.5,
    padding_factor_max: float = 1.5,
):
    """Apply a 'zoom-out' effect by padding the image with a border."""
    img = Image.open(input_path)

    factor = random.uniform(padding_factor_min, padding_factor_max)

    border_w = int(img.width * factor) // 2
    border_h = int(img.height * factor) // 2

    img_with_border = ImageOps.expand(
        img,
        border=(border_w, border_h),
        fill="black",
    )

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img_with_border.save(output_path)

    return output_path
