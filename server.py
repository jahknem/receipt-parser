from flask import Flask, request, jsonify
from receipt_reader.parser import parse_image
import os
import uuid
from pydantic import ValidationError

app = Flask(__name__)

@app.route("/parse", methods=["POST"])
def parse_receipt_image():
    if "file" not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "No file selected for uploading"}), 400

    if file:
        # Save the file temporarily
        filename = str(uuid.uuid4())
        filepath = os.path.join("/tmp", filename)
        file.save(filepath)

        try:
            # Parse the image
            invoice = parse_image(filepath)
            return jsonify(invoice.dict())
        except (ValidationError, Exception) as e:
            return jsonify({"error": str(e)}), 500
        finally:
            # Clean up the temporary file
            if os.path.exists(filepath):
                os.remove(filepath)

    return jsonify({"error": "An unexpected error occurred"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
