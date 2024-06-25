from flask import Flask, render_template, request, redirect, url_for, flash, session
import os
import uuid
import re
from yo_ficator import start_yoficator, find_next_word, set_yo, highlight_word, replace_and_highlight_true_words

app = Flask(__name__)
app.secret_key = 'supersecretkey'
UPLOAD_FOLDER = 'uploads'
TEMP_FOLDER = 'temp'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['TEMP_FOLDER'] = TEMP_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

if not os.path.exists(TEMP_FOLDER):
    os.makedirs(TEMP_FOLDER)

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
            temp_id = str(uuid.uuid4())
            temp_filepath = os.path.join(app.config['TEMP_FOLDER'], temp_id)
            content = open(filepath, 'r', encoding='utf-8').read()
            content = replace_and_highlight_true_words(content)
            with open(temp_filepath, 'w', encoding='utf-8') as temp_file:
                temp_file.write(content)
            start_yoficator()
            session['temp_id'] = temp_id
            session['filename'] = filename
            session['index'] = 0
            session['end_index'] = 0
            session['first'] = True
            return redirect(url_for('edit_file', temp_id=temp_id))
    return render_template('upload.html')

@app.route('/edit/<temp_id>', methods=['GET', 'POST'])
def edit_file(temp_id):
    temp_filepath = os.path.join(app.config['TEMP_FOLDER'], temp_id)
    if not os.path.exists(temp_filepath):
        return redirect(url_for('upload_file'))

    content = open(temp_filepath, 'r', encoding='utf-8').read()
    highlighted_content = highlight_word(content, session['index'], session['end_index'])

    if request.method == 'POST':
        action = request.form['action']
        if action == 'save':
            content = request.form['content']
            content = re.sub(r'<span class="highlight">(.*?)</span>', r'\1', content)
            content = re.sub(r'<span class="highlight-green">(.*?)</span>', r'\1', content)
            with open(os.path.join(app.config['UPLOAD_FOLDER'], session['filename']), 'w', encoding='utf-8') as file:
                file.write(content)
            flash('File saved successfully!')
            return redirect(url_for('index'))
        elif action == 'next_word':
            start, end = find_next_word(content, session['end_index'])
            session['index'] = start
            session['end_index'] = end
            highlighted_content = highlight_word(content, start, end)
            with open(temp_filepath, 'w', encoding='utf-8') as temp_file:
                temp_file.write(content)
        elif action == 'set_yo':
            content, new_end_index = set_yo(content, session['index'], session['end_index'])
            session['end_index'] = new_end_index
            highlighted_content = highlight_word(content, session['index'], new_end_index)
            with open(temp_filepath, 'w', encoding='utf-8') as temp_file:
                temp_file.write(content)
        else:
            highlighted_content = highlight_word(content, session['index'], session['end_index'])

    return render_template('edit.html', content=content, highlighted_content=highlighted_content, filename=session['filename'], index=session['index'])

if __name__ == '__main__':
    app.run(debug=True, port=8080)
