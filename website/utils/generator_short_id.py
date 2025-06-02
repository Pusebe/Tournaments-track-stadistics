import string
import random

def generate_short_id(model_class, field_name='short_id', length=4):
    """Genera un ID corto único para cualquier modelo"""
    characters = string.ascii_letters + string.digits
    while True:
        short_id = ''.join(random.choice(characters) for _ in range(length))
        if not model_class.query.filter_by(**{field_name: short_id}).first():
            return short_id