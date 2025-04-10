from flask import Flask, render_template, request
import fitz  # PyMuPDF
import os

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

@app.route("/", methods=["GET", "POST"])
def index():
    extracted_text = None

    if request.method == "POST":
        pdf_file = request.files["pdf"]
        if pdf_file.filename.endswith(".pdf"):
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], pdf_file.filename)
            pdf_file.save(filepath)

            # Extract text
            doc = fitz.open(filepath)
            extracted_text = "\n\n".join([page.get_text() for page in doc])
            doc.close()

    return render_template("index.html", extracted_text=extracted_text)

if __name__ == "__main__":
    app.run(debug=True)
