from datetime import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_login import UserMixin

app = Flask(__name__)
app.secret_key = b"secret"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_BINDS'] = {
    'reg': 'sqlite:///reg.db'
  
}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)

migrate = Migrate(app,db)
login_manager = LoginManager(app)
@login_manager.user_loader
def user_loader(user_id):
    return User.query.get(int(user_id))

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    password = db.Column(db.String(20))

class RegUser(db.Model, UserMixin):
    __bind_key__ = 'reg'
    id = db.Column(db.Integer, primary_key=True)
    RegName = db.Column(db.String(20))
    RegPassword = db.Column(db.String(20))  
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    about_me = db.Column(db.String(200))  
    last_seen = db.Column(db.DateTime)  



class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime, default=datetime.utcnow)  # Значення за замовчуванням для created
    title = db.Column(db.String(100))  # Поле для назви посту
    content = db.Column(db.Text)  # Поле для змісту посту
    type = db.Column(db.String(100), default='Type')  # Значення за замовчуванням для type
    enabled = db.Column(db.Boolean, default=True)  # Значення за замовчуванням для enabled

    def __repr__(self):
        return f"Post(id={self.id}, created={self.created}, type={self.type}, enabled={self.enabled})"
    
