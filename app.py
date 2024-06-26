from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file
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

def save_content_to_temp_file(content, temp_id):
    temp_filepath = os.path.join(app.config['TEMP_FOLDER'], temp_id)
    with open(temp_filepath, 'w', encoding='utf-8') as temp_file:
        temp_file.write(content)
    return temp_filepath

def load_content_from_temp_file(temp_id):
    temp_filepath = os.path.join(app.config['TEMP_FOLDER'], temp_id)
    with open(temp_filepath, 'r', encoding='utf-8') as temp_file:
        return temp_file.read()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('Файл не выбран')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('Файл не выбран')
            return redirect(request.url)
        if file:
            filename = file.filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            temp_id = str(uuid.uuid4())
            content = open(filepath, 'r', encoding='utf-8').read()
            start_yoficator()
            content, replace_count = replace_and_highlight_true_words(content)
            temp_filepath = save_content_to_temp_file(content, temp_id)
            session['temp_id'] = temp_id
            session['filename'] = filename
            session['replace_count'] = replace_count
            session['index'] = 0
            session['end_index'] = 0
            session['first'] = True
            session['no_more_words'] = False
            return redirect(url_for('edit_file', temp_id=temp_id))
    return render_template('upload.html')

@app.route('/edit/<temp_id>', methods=['GET', 'POST'])
def edit_file(temp_id):
    content = load_content_from_temp_file(temp_id)
    highlighted_content = highlight_word(content, session['index'], session['end_index'])
    message = ""

    if request.method == 'POST':
        action = request.form['action']
        if action == 'save':
            content = request.form['content']
            content = re.sub(r'<span class="highlight">(.*?)</span>', r'\1', content)
            content = re.sub(r'<span class="highlight-green">(.*?)</span>', r'\1', content)
            with open(os.path.join(app.config['UPLOAD_FOLDER'], session['filename']), 'w', encoding='utf-8') as file:
                file.write(content)
            flash('Файл успешно сохранен!')
            return redirect(url_for('edit_file', temp_id=temp_id))
        elif action == 'next_word':
            if session.get('no_more_words', False):
                session['index'] = 0
                session['end_index'] = 0
                session['no_more_words'] = False
                message = "Начинаем с начала."
            start, end = find_next_word(content, session['end_index'])
            if start == len(content) and end == len(content):
                message = "Больше сомнительных слов нет. Нажмите ещё раз, чтобы начать поиск сначала."
                session['no_more_words'] = True
            else:
                session['index'] = start
                session['end_index'] = end
                session['no_more_words'] = False
            highlighted_content = highlight_word(content, session['index'], session['end_index'])
            save_content_to_temp_file(content, temp_id)
        elif action == 'set_yo':
            content, new_end_index = set_yo(content, session['index'], session['end_index'])
            session['end_index'] = new_end_index
            highlighted_content = highlight_word(content, session['index'], new_end_index)
            save_content_to_temp_file(content, temp_id)
        else:
            highlighted_content = highlight_word(content, session['index'], session['end_index'])

    return render_template('edit.html', content=content, highlighted_content=highlighted_content, filename=session['filename'], index=session['index'], message=message, replace_count=session.get('replace_count', 0))

@app.route('/download/<filename>')
def download_file(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    return send_file(filepath, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, port=8080)
