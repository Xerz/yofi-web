from flask import Flask, render_template, request, redirect, url_for, flash
import os
from yo_ficator import replace_e_with_yo

app = Flask(__name__)
app.secret_key = 'supersecretkey'
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file:
            filename = file.filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            return redirect(url_for('edit_file', filename=filename))
    return render_template('upload.html')


@app.route('/edit/<filename>', methods=['GET', 'POST'])
def edit_file(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    with open(filepath, 'r', encoding='utf-8') as file:
        content = file.read()

    if request.method == 'POST':
        content = request.form['content']
        processed_content = replace_e_with_yo(content)
        with open(filepath, 'w', encoding='utf-8') as file:
            file.write(processed_content)
        flash('File saved successfully!')
        return redirect(url_for('index'))

    processed_content = replace_e_with_yo(content)
    return render_template('edit.html', content=processed_content, filename=filename)


if __name__ == '__main__':
    app.run(debug=True)