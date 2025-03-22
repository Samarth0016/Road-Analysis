from flask import Flask, render_template, request, flash, redirect, url_for, jsonify
import cv2
import os
import subprocess
from werkzeug.utils import secure_filename
import sys


UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

app = Flask(__name__)
app.secret_key = 'the random string'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def processImage(filename, Operation):
    print(f"filename is {filename} and operation is {Operation}")
    image = cv2.imread(f"uploads/{filename}")
    match Operation:
        case "convertgrey":
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            newFilename = f"static/{filename}"
            cv2.imwrite(newFilename, gray)
            return newFilename

        case "convertpng":
            newFilename = f"static/{filename.split('.')[0]}.png"
            cv2.imwrite(newFilename, image)
            return newFilename

        case "convertwebp":
            newFilename = f"static/{filename.split('.')[0]}.webp"
            cv2.imwrite(newFilename, image)
            return newFilename

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/edit", methods=["GET", "POST"])
def edit():
    if request.method == "POST":
        Operation = request.form.get("Operation")

        if 'file' not in request.files:
            return 'No file part'
        file = request.files['file']
        if file.filename == '':
            return 'No selected file'
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            new = processImage(filename, Operation)
            flash(f"Your image has been processed and is available <a href='/{new}' target='_blank'>here</a>")
            return render_template("index.html")
    return render_template("index.html")

# ➡ Added /upload route as requested:
@app.route("/upload", methods=["GET", "POST"])
def upload_image():
    if request.method == "GET":
        return render_template("upload.html")

    if "file" not in request.files:
        flash("No file uploaded.")
        return render_template("upload.html")

    file = request.files["file"]
    if file.filename == "":
        flash("No selected file.")
        return render_template("upload.html")

    if file and allowed_file(file.filename):
        file_path = os.path.join(UPLOAD_FOLDER, secure_filename(file.filename))
        file.save(file_path)
        reference_width = request.form.get("width", "0.955")

        try:
            result = subprocess.run(
                [sys.executable, "object_size.py", "--image", file_path, "--width", reference_width],
                capture_output=True,
                text=True,
                check=True
            )
            output = result.stdout.strip()
            output = "\n".join(line.strip() for line in output.splitlines())
        except subprocess.CalledProcessError as e:
            output = f"Error processing image: {e.stderr}"

        return render_template("upload.html", output=output)

    flash("Invalid file type.")
    return render_template("upload.html")



if __name__ == "__main__":
    app.run(debug=True)
