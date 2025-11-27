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
    </style>
</head>
<body>
    <div class="container">
        <h1>Batch Data Augmentation</h1>
        <p>Select <strong>one or more</strong> photos. The tool will generate 3 variations (Medium, Far, Very Far) for <em>every</em> photo you upload.</p>
        
        <form action="/augment" method="post" enctype="multipart/form-data">
            <input type="file" name="files" accept="image/*" multiple required>
            <br>
            <input type="submit" value="Process Batch & Download Zip" class="btn">
        </form>
    </div>
</body>
</html>
"""

ZOOM_SCALES = [0.3, 0.5, 0.7, 0.9]

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/augment', methods=['POST'])
def augment():
    # fetch  list of all uploaded files
    uploaded_files = request.files.getlist('files')
    
    if not uploaded_files or uploaded_files[0].filename == '':
        return "No files selected", 400

    try:
        # create an in-memory ZIP file
        memory_file = io.BytesIO()
        with zipfile.ZipFile(memory_file, 'w') as zf:
            
            # Outer Loop: go thru every uploaded photo
            for file in uploaded_files:
                original_img = Image.open(file.stream)
                
                # fix: Convert to RGB if image is PNG/RGBA to avoid errors saving as JPEG
                if original_img.mode in ('RGBA', 'P'):
                    original_img = original_img.convert('RGB')
                
                # Inner Lop - create multiple scale for each photo
                for scale in ZOOM_SCALES:
                    border_w = int(original_img.width * scale) // 2
                    border_h = int(original_img.height * scale) // 2
                    
                    aug_img = ImageOps.expand(original_img, border=(border_w, border_h), fill='black')
                    
                    img_buffer = io.BytesIO()
                    # We save everything as JPEG to keep it simple/compatible
                    aug_img.save(img_buffer, format='JPEG', quality=90)
                    
                    # Create a unique filename: "originalName_scale_0.5.jpg"
                    clean_name = file.filename.rsplit('.', 1)[0]
                    archive_name = f"{clean_name}_scale_{scale}.jpg"
                    
                    zf.writestr(archive_name, img_buffer.getvalue())

        # Prepare Zip for download
        memory_file.seek(0)
        
        return send_file(
            memory_file,
            mimetype='application/zip',
            as_attachment=True,
            download_name='batch_augmentation_results.zip'
        )

    except Exception as e:
        return f"Error processing batch: {str(e)}", 500

if __name__ == '__main