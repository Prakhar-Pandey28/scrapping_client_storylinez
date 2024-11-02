# utils.py

def clean_text(text):
    """Cleans and standardizes text data."""
    return text.strip().replace('\n', ' ') if text else ""
