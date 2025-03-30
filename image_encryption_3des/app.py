from flask import Flask, render_template, request, send_file, redirect, url_for, flash
import os
from encryption import encrypt_image, decrypt_image, generate_key

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "static/encrypted/"
app.config["DECRYPTED_FOLDER"] = "static/decrypted/"
app.config["SECRET_KEY"] = "supersecretkey"

# Ensure folders exist
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
os.makedirs(app.config["DECRYPTED_FOLDER"], exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")

@app.route("/encrypt", methods=["POST"])
def encrypt():
    if "image" not in request.files:
        flash("No file uploaded", "error")
        return redirect(url_for("index"))

    file = request.files["image"]
    if file.filename == "":
        flash("No selected file", "error")
        return redirect(url_for("index"))

    file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    encrypted_path = os.path.join(app.config["UPLOAD_FOLDER"], "encrypted_" + file.filename)
    
    file.save(file_path)
    
    # Encrypt image
    key, image_size = encrypt_image(file_path, encrypted_path, generate_key())

    # Save key & image size
    key_path = os.path.join(app.config["UPLOAD_FOLDER"], "key.bin")
    with open(key_path, "wb") as key_file:
        key_file.write(key)

    size_path = os.path.join(app.config["UPLOAD_FOLDER"], "size.txt")
    with open(size_path, "w") as size_file:
        size_file.write(f"{image_size[0]},{image_size[1]}")

    flash("Image Encrypted Successfully!", "success")
    return send_file(encrypted_path, as_attachment=True)

@app.route("/decrypt", methods=["POST"])
def decrypt():
    if "file" not in request.files:
        flash("No file uploaded", "error")
        return redirect(url_for("index"))

    file = request.files["file"]
    if file.filename == "":
        flash("No selected file", "error")
        return redirect(url_for("index"))

    encrypted_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    decrypted_path = os.path.join(app.config["DECRYPTED_FOLDER"], "decrypted.jpg")

    file.save(encrypted_path)

    # Load encryption key
    key_path = os.path.join(app.config["UPLOAD_FOLDER"], "key.bin")
    if not os.path.exists(key_path):
        flash("Encryption key not found!", "error")
        return redirect(url_for("index"))

    with open(key_path, "rb") as key_file:
        key = key_file.read()

    # Load image size
    size_path = os.path.join(app.config["UPLOAD_FOLDER"], "size.txt")
    if not os.path.exists(size_path):
        flash("Image size data not found!", "error")
        return redirect(url_for("index"))

    with open(size_path, "r") as size_file:
        width, height = map(int, size_file.read().strip().split(","))

    decrypt_image(encrypted_path, decrypted_path, key, (width, height))

    flash("Image Decrypted Successfully!", "success")
    return send_file(decrypted_path, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
