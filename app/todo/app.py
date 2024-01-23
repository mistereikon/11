from flask import Flask, request, render_template, redirect, url_for, session, flash, make_response, jsonify

import os 
from datetime import datetime
import json
from forms import LoginForm,  UpdateAccountForm
from __init__ import db, User, RegUser 
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename 

from flask import Blueprint

todo_blueprint = Blueprint('todo_bp', __name__, template_folder="templates/todo")

app = Flask(__name__)
app.config['SECRET_KEY'] = '123456'
user_cookies = {}
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'  

UPLOAD_FOLDER = 'app/static/images'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

current_directory = os.path.dirname(__file__)
users_file_path = os.path.join(current_directory, 'users.json')

# Загрузка данных о пользователях из JSON-файла
with open(users_file_path, 'r') as users_file:
    users = json.load(users_file)
app.secret_key = '123456'

todos = [
    {"id": 1, "task": "Приклад завдання", "status": "В процесі"},
    {"id": 2, "task": "Інше завдання", "status": "Виконано"}
]



def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            flash('Будь ласка, увійдіть для доступу до цієї сторінки', 'error')
            return redirect(url_for('new_login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/todos/add_user', methods=['POST'])
def add_user():
    name = request.form.get('name')
    password = request.form.get('password')
    
    if name and password:
        
        new_user = User(name=name, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash('Користувача успішно додано до бази даних.', 'success')
    else:
        flash('Ім\'я та пароль не можуть бути пустими.', 'error')

    return redirect(url_for('get_todos'))
@app.route('/todos', methods=['GET'])
@login_required
def get_todos():
    users = User.query.all()  
    return render_template("todos.html", users=users)



@app.route('/todos/delete/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
        flash('Користувача успішно видалено.', 'success')
    else:
        flash('Користувача не знайдено.', 'error')

    return redirect(url_for('get_todos'))
@app.route('/todos/edit_user/<int:user_id>', methods=['POST'])
def edit_user(user_id):
    user = User.query.get(user_id)
    if user:
        new_name = request.form.get('new_name')
        new_password = request.form.get('new_password')
        
        if new_name:
            user.name = new_name
        if new_password:
            user.password = new_password

        db.session.commit()
        flash('Зміни збережено успішно.', 'success')
    else:
        flash('Користувача не знайдено.', 'error')

    return redirect(url_for('get_todos'))


    
# Додавання ендпоінту для видалення кукі
@app.route('/delete_cookie', methods=['POST'])
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

@app.route('/skills')
@app.route('/skills/<int:id>')
@login_required
def display_skills(id=None):
    if id is not None:
        # Якщо передано id, відобразіть навичку зі списку за цим id
        if 0 <= id < len(my_skills):
            skill = my_skills[id]
            return render_template("skills.html", skills=[skill])
        else:
            return "Немає навички з таким id"
    else:
        # Якщо id не передано, відобразіть всі навички і їх загальну кількість
        total_skills = len(my_skills)
        return render_template("skills.html", skills=my_skills, total=total_skills)

@app.route('/tables')
@login_required
def tables():
    return render_template("tables.html")

@app.route("/")
@login_required
def index():
    return render_template("home.html")

@app.route('/home')
@login_required
def home():
    return render_template("home.html")
@app.route('/page1')
def page1():
    return render_template("page1.html")

@app.route('/page2')
def page2():
    return render_template("page2.html")

@app.route('/page3')
def page3():
    return render_template("page3.html")






@app.route('/main')
def main():
    return redirect(url_for("home"))


#http://127.0.0.1:5000/query?name=admin&password=1234 or from form by post
@app.route('/query', methods=["GET", "POST"])
def form():
    if request.method == "POST":
        name = request.form.get("name")
        password = request.form.get("password")
        method = request.method
    else:
        name = request.args.get("name")
        password = request.args.get("password")
        method = request.method
    return render_template("my_form.html", name=name, password=password, method=method)
@app.context_processor
def utility_processor():
    os_info = os.name  
    user_agent = request.headers.get("User-Agent")  
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  

    return dict(os_info=os_info, user_agent=user_agent, current_time=current_time)


