import os

from flask import Flask, render_template, request, redirect, url_for, session
import uuid

from data.config import XOR_KEY, UPLOAD_FOLDER
from data.functions import load_data, save_data, initialize_json_files, encrypt_password

app = Flask(__name__)
app.secret_key = str(uuid.uuid4())


@app.route('/')
def index():
    """Главная страница"""
    products = load_data('db/products.json')
    users = load_data('db/users.json')
    return render_template('index.html', products=products, users=users)


@app.route('/add_avatar', methods=['GET', 'POST'])
def add_avatar():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        file = request.files['avatar']
        users = load_data('db/users.json')
        if username in users and encrypt_password(users[username]['password'], XOR_KEY) == password:
            filepath = os.path.join(UPLOAD_FOLDER, f'{username}_avatar.{file.filename.split(".", 1)[1]}')
            avatar = f'users_avatars/{username}_avatar.{file.filename.split(".", 1)[1]}'
            users = load_data('db/users.json')
            users[username]['avatar'] = avatar
            session['user'] = {
                "username": username,
                "phone": users[username]['phone'],
                "role": users[username]['role'],
                "avatar": avatar
            }
            save_data('db/users.json', users)
            file.save(filepath)
            return "Аватар успешно изменен!"

        return "Неверный логин или пароль!"

    return render_template('add_avatar.html')




@app.route('/delete_avatar', methods=['POST'])
def delete_avatar():
    username = request.form['name']
    users = load_data('db/users.json')
    os.remove(f"static/{users[username]['avatar']}")
    users[username]['avatar'] = 'users_avatars/default/default.jpg'
    session['user'] = {
        "username": username,
        "phone": users[username]['phone'],
        "role": users[username]['role'],
        "avatar": users[username]['avatar']
    }
    save_data('db/users.json', users)
    return 'Аватар удален успешно'

@app.route('/create_ad', methods=['GET', 'POST'])
def create_ad():
    """Страница создания объявления"""
    if 'user' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        category = request.form['category']
        name = request.form['name']
        description = request.form['description']

        new_ad = {
            "category": category,
            "name": name,
            "description": description,
            "status": "pending",
            "user": session['user']['username'],
            "phone": session['user']['phone']
        }

        products = load_data('db/products.json')
        products[str(uuid.uuid4())] = new_ad
        save_data('db/products.json', products)

        return redirect(url_for('profile'))

    return render_template('create_ad.html')


@app.route('/admin')
def admin():
    """Админ панель"""
    if 'user' not in session or session['user']['role'] != 'admin':
        return redirect(url_for('login'))

    products = load_data('db/products.json')
    pending_ads = {k: v for k, v in products.items() if v['status'] == 'pending'}
    current_user_name = session['user']['username']
    return render_template('admin.html', ads=pending_ads, current_user_name=current_user_name)


@app.route('/approve_ad/<ad_id>')
def approve_ad(ad_id):
    """Одобрение объявления"""
    if 'user' not in session or session['user']['role'] != 'admin':
        return redirect(url_for('login'))

    products = load_data('db/products.json')
    if ad_id in products:
        products[ad_id]['status'] = 'approved'
        save_data('db/products.json', products)

    return redirect(url_for('admin'))


@app.route('/reject_ad/<ad_id>')
def reject_ad(ad_id):
    """Отклонение объявления"""
    if 'user' not in session or session['user']['role'] != 'admin':
        return redirect(url_for('login'))

    products = load_data('db/products.json')
    if ad_id in products:
        products[ad_id]['status'] = 'rejected'
        save_data('db/products.json', products)

    return redirect(url_for('admin'))


@app.route('/profile')
def profile():
    """Страница профиля"""
    if 'user' not in session:
        return redirect(url_for('login'))

    products = load_data('db/products.json')
    current_user_role = session['user']['role']
    current_user_name = session['user']['username']
    current_user_avatar = session['user']['avatar']
    user_ads = {k: v for k, v in products.items() if v['user'] == session['user']['username']}
    return render_template('profile.html', ads=user_ads, current_user_role=current_user_role,
                           current_user_name=current_user_name, current_user_avatar=current_user_avatar)


@app.route('/delete_ad/<ad_id>')
def delete_ad(ad_id):
    """Удалить объявление"""
    if 'user' not in session:
        return redirect(url_for('login'))

    products = load_data('db/products.json')
    if ad_id in products and products[ad_id]['user'] == session['user']['username']:
        del products[ad_id]
        save_data('db/products.json', products)

    return redirect(url_for('profile'))


@app.route('/change_ad/<ad_id>')
def change_ad(ad_id):
    """Изменение объявления"""
    if 'user' not in session:
        return redirect(url_for('login'))

    products = load_data('db/products.json')
    if ad_id in products and products[ad_id]['user'] == session['user']['username']:
        del products[ad_id]
        save_data('db/products.json', products)

    return redirect(url_for('profile'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Страница регистрации"""
    if request.method == 'POST':
        username = request.form['username']
        password = encrypt_password(request.form['password'], XOR_KEY)
        phone = request.form['phone']
        file = request.files['avatar']
        if file.filename != '':
            filepath = os.path.join(UPLOAD_FOLDER, f'{username}_avatar.{file.filename.split(".", 1)[1]}')
            avatar = f'users_avatars/{username}_avatar.{file.filename.split(".", 1)[1]}'
            file.save(filepath)
        else:
            avatar = 'users_avatars/default/default.jpg'
        users = load_data('db/users.json')
        if username in users:
            return "Пользователь уже существует!"

        users[username] = {
            "password": password,
            "phone": phone,
            "role": "user",
            "avatar": avatar
        }
        save_data('db/users.json', users)

        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Страница входа"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        users = load_data('db/users.json')
        if username in users and encrypt_password(users[username]['password'], XOR_KEY) == password:
            session['user'] = {
                "username": username,
                "phone": users[username]['phone'],
                "role": users[username]['role'],
                "avatar": users[username]['avatar']
            }
            return redirect(url_for('profile'))

        return "Неверный логин или пароль!"

    return render_template('login.html')


@app.route('/logout')
def logout():
    """Выйти из профиля"""
    session.pop('user', None)
    return redirect(url_for('index'))


if __name__ == '__main__':
    initialize_json_files()
    app.run(debug=True, port=8080)
