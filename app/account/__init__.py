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




class RegUser(db.Model, UserMixin):
    __bind_key__ = 'reg'
    id = db.Column(db.Integer, primary_key=True)
    RegName = db.Column(db.String(20))
    RegPassword = db.Column(db.String(20))  
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    about_me = db.Column(db.String(200))  
    last_seen = db.Column(db.DateTime)  


