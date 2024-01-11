#importing req class from flask
from datetime import datetime
from flask import Flask, flash, redirect, render_template, url_for
from flask_sqlalchemy import SQLAlchemy
from forms import LoginForm, RegistrationForm

app = Flask(__name__)

app.config['SECRET_KEY'] = '34ixntdgxafiuh45fri7' #for security attacks
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

db = SQLAlchemy(app)

# each class represents each table in the database called as models
class User(db.Model): 
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(20), unique=True, nullable=False)
  email = db.Column(db.String(120), unique=True, nullable=False)
  image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
  password = db.Column(db.String(60), nullable=False)
  posts = db.relationship('Post', backref='author', lazy=True) #one to many relationship

  def __repr__(self):
    return f"User('{self.username}', '{self.email}', '{self.image_file}')"

class Post(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  title = db.Column(db.String(100), nullable=False)
  date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
  content = db.Column(db.Text, nullable=False)
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

  def __repr__(self):
    return f"Post('{self.title}', '{self.date_posted}')"
  

posts = [
    {
        'author': 'Corey Schafer',
        'title': 'Blog Post 1',
        'content': 'First post content',
        'date_posted': 'April 20, 2018'
    },
    {
        'author': 'Corey Schafer',
        'title': 'Blog Post 2',
        'content': 'Second post content',
        'date_posted': 'April 21, 2018'
    }
  ]

@app.route('/')
@app.route('/home')
def home_page():
  return render_template('home.html', posts = posts)

@app.route('/about')
def about_page():
  return render_template('about.html', title = 'About')

@app.route('/register', methods = ['GET', 'POST'])
def register_page():
  form = RegistrationForm()
  if form.validate_on_submit(): 
    flash(f'Account created for {form.username.data}!', 'success')
    return redirect(url_for('home_page'))
  return render_template('register.html', title = 'Register', form = form)

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    form = LoginForm()

    if form.validate_on_submit():
        if form.email.data == 'admin@gmail.com' and form.password.data == 'password':
          flash('Logged in successfully', 'success')
          return redirect(url_for('home_page'))
        else:
          flash('Login unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

if __name__ == '__main__':
  app.run(host = '0.0.0.0', debug = True)