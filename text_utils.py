import re

def remove_tashkeel(text):
    return re.sub(r'[\u0617-\u061A\u064B-\u0652]', '', text)

def normalize_arabic(text):     # TODO: Add more test cases
    text = remove_tashkeel(text)
    text = re.sub("[إأآا]", "ا", text)
    text = re.sub("ى", "ي", text)
    text = re.sub("ؤ", "و", text)
    text = re.sub("ئ", "ي", text)
    text = re.sub("ة", "ه", text)
    return text.strip()