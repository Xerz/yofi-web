import codecs
import re
import os

dict_true = {}
dict_if = {}

def resource_path(relative_path):
    return os.path.join(os.path.abspath('.'), relative_path)

def load_dict_from_file(filepath, target_dict):
    with codecs.open(resource_path(filepath), 'r', 'utf-8') as file:
        content = file.read().replace('\r\n', '\n').replace('\r', '\n')
        for line in content.split('\n'):
            if "*" not in line and line.strip():
                cleaned_line = line.lower().strip()
                if "(" in cleaned_line:
                    base_word, variations = cleaned_line.split("(")
                    variations = re.sub(r'\)', '', variations)
                else:
                    base_word = cleaned_line
                    variations = ""
                if "|" in variations:
                    variations_list = variations.split("|")
                    for variation in variations_list:
                        full_word = base_word + variation
                        key = re.sub(r'ё', 'е', full_word)
                        target_dict[key] = full_word
                else:
                    full_word = base_word
                    key = re.sub(r'ё', 'е', full_word)
                    target_dict[key] = full_word

def start_yoficator():
    global dict_true, dict_if
    load_dict_from_file('yo.dat', dict_true)
    load_dict_from_file('yoif.dat', dict_if)

def replace_and_highlight_true_words(content):
    global dict_true
    pattern = re.compile(r'\b\w+\b')
    matches = pattern.finditer(content)
    offset = 0
    replace_count = 0
    for match in matches:
        word = match.group().lower()
        if word in dict_true:
            replacement = dict_true[word]
            highlighted = f'<span class="highlight-green">{replacement}</span>'
            start, end = match.start() + offset, match.end() + offset
            content = content[:start] + highlighted + content[end:]
            offset += len(highlighted) - (end - start)
            replace_count += 1
    return content, replace_count

def find_next_word(content, start_index):
    global dict_true, dict_if
    pattern = re.compile(r'\b\w+\b')
    matches = pattern.finditer(content, start_index)
    for match in matches:
        word = match.group().lower()
        if word in dict_if:
            return match.start(), match.end()
    return len(content), len(content)

def set_yo(content, start, end):
    global dict_if
    word = content[start:end]
    lower_word = word.lower()
    if lower_word in dict_if:
        dict_word = dict_if[lower_word]
        new_word = ''
        for cc, c in zip(word, dict_word):
            if cc.isupper():
                new_word += c.upper()
            else:
                new_word += c
        content = content[:start] + new_word + content[end:]
        return content, start + len(new_word)
    return content, start

def highlight_word(content, start, end):
    word = content[start:end]
    highlighted = f'<span class="highlight">{word}</span>'
    return content[:start] + highlighted + content[end:]
