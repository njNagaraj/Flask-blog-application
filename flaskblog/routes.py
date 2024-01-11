from flask import flash, redirect, render_template, url_for
from flaskblog import app
from flaskblog.forms import RegistrationForm, LoginForm
from flaskblog.models import User, Post

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