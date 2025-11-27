import os
import uuid
from flask import Flask, render_template, request, send_from_directory
from werkzeug.utils import secure_filename

from aug import zoom_out_image

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
OUTPUT_FOLDER = os.path.join(BASE_DIR, "outputs")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/augment", methods=["POST"])
def augment():
    try:
        padding_min = float(request.form.get("padding_min", 0.5))
        padding_max = float(request.form.get("padding_max", 1.5))
    except ValueError:
        padding_min, padding_max = 0.5, 1.5

    if padding_min < 0:
        padding_min = 0.0
    if padding_max < padding_min:
        padding_max = padding_min

    if "images" not in request.files:
        return "No files part in request", 400

    files = request.files.getlist("images")
    if not files:
        return "No files uploaded", 400

    session_id = str(uuid.uuid4())
    session_upload_dir = os.path.join(UPLOAD_FOLDER, session_id)
    session_output_dir = os.path.join(OUTPUT_FOLDER, session_id)
    os.makedirs(session_upload_dir, exist_ok=True)
    os.makedirs(session_output_dir, exist_ok=True)

    output_files = []

    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            input_path = os.path.join(session_upload_dir, filename)
            file.save(input_path)

            output_filename = f"far_{filename}"
            output_path = os.path.join(session_output_dir, output_filename)

            zoom_out_image(
                input_path,
                output_path,
                padding_factor_min=padding_min,
                padding_factor_max=padding_max,
            )

            rel_path = f"{session_id}/{output_filename}"
            output_files.append(rel_path)

    return render_template(
        "results.html",
        output_files=output_files,
        padding_min=padding_min,
        padding_max=padding_max,
    )


@app.route("/outputs/<path:filename>")
def outputs_file(filename):
    return send_from_directory(OUTPUT_FOLDER, filename)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
