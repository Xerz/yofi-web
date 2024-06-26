import codecs
import re
import os

dict_true = {}
dict_if = {}

def resource_path(relative_path):
    return os.path.join(os.path.abspath('.'), relative_path)

def read_and_clean_file(filepath):
    """Reads a file and replaces different line endings with '\n'."""
    with codecs.open(resource_path(filepath), 'r', 'utf-8') as file:
        return file.read().replace('\r\n', '\n').replace('\r', '\n').split('\n')

def load_dict(content, target_dict):
    """Loads words from the content into the target dictionary."""
    for line in content:
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
    yo_content = read_and_clean_file('yo.dat')
    yoif_content = read_and_clean_file('yoif.dat')
    load_dict(yo_content, dict_true)
    load_dict(yoif_content, dict_if)

def replace_with_case(word, replacement):
    """Replaces characters in a word with characters in the replacement, preserving case."""
    new_word = ''
    for cc, c in zip(word, replacement):
        if cc.isupper():
            new_word += c.upper()
        else:
            new_word += c
    return new_word

def replace_and_highlight_true_words(content):
    """Replaces words in the content according to dict_true and highlights them."""
    global dict_true
    pattern = re.compile(r'\b\w+\b')
    matches = pattern.finditer(content)
    offset = 0
    replace_count = 0
    for match in matches:
        word = match.group()
        lower_word = word.lower()
        if lower_word in dict_true:
            replacement = replace_with_case(word, dict_true[lower_word])
            highlighted = f'<span class="highlight-green">{replacement}</span>'
            start, end = match.start() + offset, match.end() + offset
            content = content[:start] + highlighted + content[end:]
            offset += len(highlighted) - (end - start)
            replace_count += 1
    return content, replace_count

def find_next_word(content, start_index):
    """Finds the next word in content that is in dict_if."""
    global dict_true, dict_if
    pattern = re.compile(r'\b\w+\b')
    matches = pattern.finditer(content, start_index)
    for match in matches:
        word = match.group().lower()
        if word in dict_if:
            return match.start(), match.end()
    return len(content), len(content)

def set_yo(content, start, end):
    """Sets the 'ё' character in the word found in content."""
    global dict_if
    word = content[start:end]
    lower_word = word.lower()
    if lower_word in dict_if:
        dict_word = dict_if[lower_word]
        new_word = replace_with_case(word, dict_word)
        content = content[:start] + new_word + content[end:]
        return content, start + len(new_word)
    return content, start

def highlight_word(content, start, end):
    """Highlights a word in the content."""
    word = content[start:end]
    highlighted = f'<span class="highlight">{word}</span>'
    return content[:start] + highlighted + content[end:]
