from flask import Flask, request, render_template, redirect, url_for, session, flash, make_response, jsonify
from data import posts
import os 
from datetime import datetime
import json
from forms import LoginForm,  UpdateAccountForm
from __init__ import db, User, RegUser 
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename 

from flask import Blueprint

home_blueprint = Blueprint('home_bp', __name__, template_folder="templates/home", static_folder="static/home") 

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



 



def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            flash('Будь ласка, увійдіть для доступу до цієї сторінки', 'error')
            return redirect(url_for('new_login'))
        return f(*args, **kwargs)
    return decorated_function






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


@app.route('/skills')

def skills():
    return render_template("skills.html")
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

@app.route('/post/')
@app.route('/post/<int:idx>')
def post(idx=None):
    if idx is not None:
        return render_template("post.html", posts=posts, idx=idx)
    else:
        return render_template("posts.html", posts=posts)


@app.route('/about')
@login_required
def about():
    return render_template("about.html")


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



if __name__ == '__main__':
    db.init_app(app)
    app.run(debug=True, port=8080)