from flask import Flask, request, render_template, redirect, url_for, session, flash, make_response, jsonify
import os 
from datetime import datetime
import json
from forms import LoginForm,  UpdateAccountForm
from __init__ import db, RegUser 
from functools import wraps
from werkzeug.utils import secure_filename 

from flask import Blueprint


account_blueprint = Blueprint('account_bp', __name__, template_folder="templates/account")

app = Flask(__name__)
app.config['SECRET_KEY'] = '123456'
user_cookies = {}
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'  
app.config['SQLALCHEMY_BINDS'] = {
    'reg': 'sqlite:///reg.db'
}
UPLOAD_FOLDER = 'app/static/images'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

current_directory = os.path.dirname(__file__)
users_file_path = os.path.join(current_directory, 'users.json')


# Загрузка данных о пользователях из JSON-файла
with open(users_file_path, 'r') as users_file:
    users = json.load(users_file)
app.secret_key = '123456'



@account_blueprint.route('/registered_users')
def registered_users():
    users = RegUser.query.all()  # Отримати всіх зареєстрованих користувачів
    total_users = len(users)  # Загальна кількість зареєстрованих користувачів
    return render_template('registered_users.html', users=users, total_users=total_users)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            flash('Будь ласка, увійдіть для доступу до цієї сторінки', 'error')
            return redirect(url_for('new_login'))
        return f(*args, **kwargs)
    return decorated_function
@account_blueprint.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    username = session.get('username')
    form = UpdateAccountForm()

    if username:
        user = RegUser.query.filter_by(RegName=username).first()

        if user:
            if form.validate_on_submit():
                user.RegName = form.username.data
                user.email = form.email.data
                user.about_me = form.about_me.data  # Оновлення поля About Me
                user.RegPassword = form.password.data  # Оновлення паролю
                db.session.commit()  # Збереження змін у базі даних
                flash('Your account has been updated!', 'success')
                return redirect(url_for('account'))

            form.username.data = user.RegName
            form.email.data = user.email
            form.about_me.data = user.about_me  # Завантаження значення поля About Me у форму
            form.password.data = user.RegPassword  # Завантаження значення паролю у форму

            return render_template('account.html', user=user, form=form)

    flash('Please log in to access this page', 'error')
    return redirect(url_for('new_login'))


@account_blueprint.route('/new_login', methods=['GET', 'POST'])
def new_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = RegUser.query.filter_by(RegName=username).first()

        if user and user.RegPassword == password:
            flash('Успішний вхід', 'success')
            session['username'] = username
            session['email'] = user.email

            
            user.last_seen = datetime.utcnow()
            db.session.commit()

            return redirect(url_for('home'))
        else:
            flash('Невірне ім\'я користувача або пароль', 'error')

    return render_template('NewLogin.html')
@account_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        password = request.form.get('password')
        email = request.form.get('email')
        about_me = request.form.get('about_me')  # Get about_me field from form

        if name and password and email:
            new_reg_user = RegUser(
                RegName=name,
                RegPassword=password,  # Store password as plain text
                email=email,
                about_me=about_me  # Store about_me value
            )
            db.session.add(new_reg_user)
            db.session.commit()
            flash('Користувача успішно зареєстровано.', 'success')
            return redirect(url_for('get_todos'))
        else:
            flash('Ім\'я, пароль або email не можуть бути пустими.', 'error')

    return render_template("reg.html")



@account_blueprint.route('/change_profile_picture', methods=['POST'])
@login_required
def change_profile_picture():
    if 'profile_picture' in request.files:
        file = request.files['profile_picture']
        if file.filename != '':
            # Зміна назви файлу для унікальності та збереження у відповідну теку
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            # Оновлення шляху до фото профілю користувача в базі даних
            username = session.get('username')
            if username:
                user = RegUser.query.filter_by(RegName=username).first()
                if user:
                    user.image_file = filename
                    db.session.commit()
                    flash('Фото профілю змінено успішно.', 'success')
                    return redirect(url_for('account'))

    flash('Помилка при зміні фото профілю.', 'error')
    return redirect(url_for('account'))




@account_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        remember = form.remember.data
        if username in users and users[username] == password:
            flash('Login successful', 'success')
            session['username'] = username

            if not remember:
                return redirect(url_for('home'))
            
            session.permanent = True
            return redirect(url_for('info'))
        else:
            flash('Invalid username or password', 'error')

    return render_template('login.html', form=form)

   

# Создание страницы "info" с информацией для авторизованных пользователей
@account_blueprint.route('/info', methods=['GET', 'POST'])
def info():
    if 'username' in session:
        username = session['username']
        cookies = user_cookies
        message = None

        if request.method == 'POST':
            if 'add_cookie' in request.form:
                cookie_key = request.form['cookie_key']
                cookie_value = request.form['cookie_value']
                cookie_expiry = int(request.form['cookie_expiry'])
                
                user_cookies[cookie_key] = cookie_value

                response = make_response(redirect(url_for('info')))
                response.set_cookie(cookie_key, cookie_value, max_age=cookie_expiry)
                flash(f'Cookie "{cookie_key}" було додано успішно.', 'success')

            if 'delete_cookie' in request.form:
                cookie_key = request.form['cookie_key']
                if cookie_key in user_cookies:
                    response = make_response(redirect(url_for('info')))
                    response.delete_cookie(cookie_key)
                    deleted_value = user_cookies.pop(cookie_key)
                    flash(f'Cookie "{cookie_key}" зі значенням "{deleted_value}" було видалено.', 'success')

            if 'change_password' in request.form:
                new_password = request.form['new_password']
                users[username] = new_password
                with open('app/users.json', 'w') as users_file:
                    json.dump(users, users_file)
                flash('Пароль було змінено успішно.', 'success')

        return render_template('info.html', username=username, cookies=cookies, message=message)
    else:
        flash('Будь ласка, увійдіть для доступу до цієї сторінки', 'error')
        return redirect(url_for('login'))
    
# Додавання ендпоінту для видалення кукі
@account_blueprint.route('/delete_cookie', methods=['POST'])
def delete_cookie():
    cookie_key = request.form['cookie_key']
    if cookie_key in user_cookies:
        deleted_value = user_cookies.pop(cookie_key)  # Видаляємо кукі зі словника
        message = f'Кукі "{cookie_key}" зі значенням "{deleted_value}" було видалено.'
        flash(message, 'success')
    return redirect(url_for('info'))
# Добавьте обработку выхода
@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('Выход выполнен успешно', 'success')
    return redirect(url_for('new_login'))

my_skills = [
    "Навик ходити",
    "Навик їсти",
    "Навик спати",
    "Навик читати",]




@account_blueprint.context_processor
def utility_processor():
    os_info = os.name  
    user_agent = request.headers.get("User-Agent")  
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  

    return dict(os_info=os_info, user_agent=user_agent, current_time=current_time)



