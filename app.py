import io
import zipfile
from flask import Flask, request, send_file, render_template_string
from PIL import Image, ImageOps

app = Flask(__name__)

HTML_TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Multi-File Augmentation</title>
    <style>
        body { font-family: sans-serif; padding: 50px; background: #f4f4f4; }
        .container { background: white; padding: 40px; border-radius: 8px; max-width: 600px; margin: 0 auto; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #333; }
        p { color: #666; }
        .btn { background-color: #0078D4; color: white; padding: 12px 24px; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; margin-top: 10px;}
        .btn:hover { background-color: #005a9e; }
        input[type=file] { margin-bottom: 20px; padding: 10px; border: 1px dashed #ccc; width: 90%; }
        .note { font-size: 0.9em; color: #888; margin-top: 20px; border-top: 1px solid #eee; padding-top: 15px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Batch Data Augmentation</h1>
        <p>Select <strong>one or more</strong> photos. For each photo, the tool will generate <strong>12 variations</strong>:</p>
        <ul>
            <li>multiple scales </li>
            <li>multiple rotate per scale...</li>
        </ul>
        
        <form action="/augment" method="post" enctype="multipart/form-data">
            <input type="file" name="files" accept="image/*" multiple required>
            <br>
            <input type="submit" value="Process Batch & Download Zip" class="btn">
        </form>
        <p class="note"><strong>Total variations per uploaded image:</strong> 4 (scales) * 3 (rotations: original, left, right) = 12 images.</p>
    </div>
</body>
</html>
"""

# --- CONFIGURATION ---
ZOOM_SCALES = [0.5, 0.7, 0.9, 1.1] # 0.0 means original.. eg: 0.5 medium, 1.0 far
ROTATION_ANGLES = [0, -5, 5]  # 0 degrees (original), -5 degrees (left), 5 degrees (right)

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/augment', methods=['POST'])
def augment():
    uploaded_files = request.files.getlist('files')
    
    if not uploaded_files or uploaded_files[0].filename == '':
        return "No files selected", 400

    try:
        memory_file = io.BytesIO()
        with zipfile.ZipFile(memory_file, 'w') as zf:
            
            for file in uploaded_files:
                original_img = Image.open(file.stream)
                
                # Fix: Convert to RGB if image is PNG/RGBA to avoid errors saving as JPEG
                if original_img.mode in ('RGBA', 'P'):
                    original_img = original_img.convert('RGB')
                
                clean_name = file.filename.rsplit('.', 1)[0]
                
                # Loop for scaling
                for scale in ZOOM_SCALES:
                    # Apply padding for scaling (0.0 scale means no padding)
                    if scale > 0:
                        border_w = int(original_img.width * scale) // 2
                        border_h = int(original_img.height * scale) // 2
                        scaled_img = ImageOps.expand(original_img, border=(border_w, border_h), fill='black')
                    else:
                        scaled_img = original_img # No padding if scale is 0
                    
                    # Loop for rotation
                    for angle in ROTATION_ANGLES:
                        # Rotate the scaled image. expand=True keeps the whole image visible.
                        rotated_img = scaled_img.rotate(angle, expand=True, fillcolor='black')
                        
                        img_buffer = io.BytesIO()
                        rotated_img.save(img_buffer, format='JPEG', quality=90)
                        
                        # Create a unique filename: e.g., "myphoto_scale_0.5_rot_5.jpg"
                        archive_name = f"{clean_name}_scale_{scale}_rot_{angle}.jpg"
                        
                        zf.writestr(archive_name, img_buffer.getvalue())

        memory_file.seek(0)
        
        return send_file(
            memory_file,
            mimetype='application/zip',
            as_attachment=True,
            download_name='batch_augmentation_results.zip'
        )

    except Exception as e:
        return f"Error processing batch: {str(e)}", 500

if __name__ == '__main__':
    print("Server running at http://localhost:5001")
    app.run(port=5001, debug=True)