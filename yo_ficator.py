import codecs
import re
import os

dict_true = {}
dict_if = {}

def resource_path(relative_path):
    return os.path.join(os.path.abspath('.'), relative_path)

def start_yoficator():
    global dict_true, dict_if
    with codecs.open(resource_path('yo.dat'), 'r', 'utf-8') as file:
        for line in file:
            if "*" not in line:
                cleaned_line = line.rstrip('\n')
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
                        dict_true[key] = full_word
                else:
                    full_word = base_word
                    key = re.sub(r'ё', 'е', full_word)
                    dict_true[key] = full_word

    with codecs.open(resource_path('yoif.dat'), "r", "utf-8") as file:
        for line in file:
            if "*" not in line:
                cleaned_line = line.rstrip('\n')
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
                        dict_if[key] = full_word
                else:
                    full_word = base_word
                    key = re.sub(r'ё', 'е', full_word)
                    dict_if[key] = full_word

def replace_and_highlight_true_words(content):
    global dict_true
    pattern = re.compile(r'\b\w+\b')
    matches = pattern.finditer(content)
    offset = 0
    for match in matches:
        word = match.group().lower()
        if word in dict_true:
            replacement = dict_true[word]
            highlighted = f'<span class="highlight-green">{replacement}</span>'
            start, end = match.start() + offset, match.end() + offset
            content = content[:start] + highlighted + content[end:]
            offset += len(highlighted) - (end - start)
    return content

def find_next_word(content, start_index):
    global dict_true, dict_if
    pattern = re.compile(r'\b\w+\b')
    matches = pattern.finditer(content, start_index)
    for match in matches:
        word = match.group().lower()
        if word in dict_if:
            return match.start(), match.end()
    print('No more words found')
    return len(content), len(content)

def set_yo(content, start, end):
    global dict_if
    word = content[start:end].lower()
    if word in dict_if:
        replacement = dict_if[word]
        content = content[:start] + replacement + content[end:]
        return content, start + len(replacement)
    return content, start

def highlight_word(content, start, end):
    word = content[start:end]
    highlighted = f'<span class="highlight">{word}</span>'
    return content[:start] + highlighted + content[end:]
