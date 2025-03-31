import json
import os


def load_data(filename):
    if os.path.exists(filename):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    return {}


def save_data(filename, data):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def initialize_json_files():
    if not os.path.exists('db/products.json'):
        with open('data/products.json', 'w', encoding='utf-8') as f:
            json.dump({}, f)

    if not os.path.exists('db/users.json'):
        with open('db/users.json', 'w', encoding='utf-8') as f:
            json.dump({}, f)


def xor_cipher(password, key):
    return ''.join(chr(ord(c) ^ ord(key[i % len(key)])) for i, c in enumerate(password))


def encrypt_password(password, key):
    return xor_cipher(password, key)


def decrypt_password(encrypted_password, key):
    return xor_cipher(encrypted_password, key)
