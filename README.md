# Data Augmentation Tool (Web App)

flask web app for data augmentation for machine vision

## Features

- Upload one or more images (PNG/JPG/JPEG).
- Configure padding factor min and max.
- Generates augmented images with random padding (zoom-out effect).
- View and download augmented images from the browser.
- Ready to deploy on Render.com.

## Local Development

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Visit `http://localhost:5000` in your browser.

## Deploying to Render

1. Push this project to your GitHub repo (e.g. `nudgytdeveloper/data_aug_tool`).
2. Go to Render.com → New → Web Service.
3. Connect your GitHub repo.
4. Render will automatically detect `render.yaml` and set up the service:
   - Build command: `pip install -r requirements.txt`
   - Start command: `gunicorn app:app`
5. Deploy and use the generated URL to access your tool.
