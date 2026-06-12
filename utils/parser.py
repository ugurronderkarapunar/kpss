import re

def parse_question_text(full_text):
    """
    OCR metninden soru kökü ve seçenekleri ayırır.
    Seçenekler A) ... B) ... şeklinde olmalı.
    Döndürülen: {'question': str, 'A': str, 'B': str, 'C': str, 'D': str, 'E': str}
    """
    full_text = full_text.strip()
    option_pattern = r'([A-E])\)\s*(.*?)(?=\n[A-E]\)|\Z)'
    matches = re.findall(option_pattern, full_text, re.DOTALL)
    options = {}
    for letter, text in matches:
        options[letter] = text.strip()

    # Soru kökü: ilk seçenekten önceki kısım
    first_option_pos = len(full_text)
    for letter in ['A','B','C','D','E']:
        pos = full_text.find(f"{letter})")
        if pos != -1 and pos < first_option_pos:
            first_option_pos = pos
    question = full_text[:first_option_pos].strip()

    # Eksik seçenekleri boş string ile doldur
    for letter in ['A','B','C','D','E']:
        if letter not in options:
            options[letter] = ""

    return {"question": question, **options}
