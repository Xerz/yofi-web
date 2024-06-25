import re

def replace_e_with_yo(text):
    # Логика замены 'е' на 'ё'
    text = re.sub(r'\bЕ\b', 'Ё', text)
    text = re.sub(r'\bе\b', 'ё', text)
    return text