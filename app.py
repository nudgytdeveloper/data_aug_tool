import os
from PIL import Image, ImageOps

INPUT_FOLDER = "path/to/your/images"   # for now we only use selected folder by clicking the buton
OUTPUT_FOLDER = "path/to/save/augmented" # output folder dirc

# 0.5 = Adds 50% padding (Medium distance)
# 0.7 = Adds 70% padding (Far distance)
# 0.9 = Adds 100% padding (Very Far)
ZOOM_LEVELS = [0.5, 0.7, 0.9] 

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def create_zoomed_variations(image_path, filename):
    try:
        img = Image.open(image_path)
        
        # Loop through our 3 zoom levels
        for scale in ZOOM_LEVELS:
            
            # Calculate border size based on the specific scale
            border_w = int(img.width * scale) // 2
            border_h = int(img.height * scale) // 2
            
            # Add the border
            img_with_border = ImageOps.expand(img, border=(border_w, border_h), fill='black')
            
            # Save with a unique name for each scale
            # Example: photo_scale_0.5.jpg
            new_filename = f"scale_{scale}_{filename}"
            save_path = os.path.join(OUTPUT_FOLDER, new_filename)
            
            img_with_border.save(save_path)
            print(f"Saved: {new_filename}")
            
    except Exception as e:
        print(f"Error processing {filename}: {e}")

# loop through it
print(f"Starting augmentation... Saving to: {os.path.abspath(OUTPUT_FOLDER)}")
for filename in os.listdir(INPUT_FOLDER):
    if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        create_zoomed_variations(os.path.join(INPUT_FOLDER, filename), filename)