from flask import flash, redirect, render_template, url_for, request
from flaskblog import app, db, bcrypt
from flaskblog.forms import RegistrationForm, LoginForm, UpdateAccountForm
from flaskblog.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required
from flask_login import current_user


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
  if current_user.is_authenticated:
    return redirect(url_for('home_page'))
  form = RegistrationForm
  form = RegistrationForm()
  if form.validate_on_submit(): 
    hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')   # hashing the password for security
    user = User(username = form.username.data, email = form.email.data, password = hashed_password)
    db.session.add(user)
    db.session.commit()
    flash(f'Your account has been created! You can now  Login', 'success')
    return redirect(url_for('login_page'))
  return render_template('register.html', title = 'Register', form = form)

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if current_user.is_authenticated:
      return redirect(url_for('home_page'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        password = form.password.data
        if user and bcrypt.check_password_hash(user.password, password):
          login_user(user, remember=form.remember_me.data)
          next_page = request.args.get('next')
          return redirect(next_page) if next_page else redirect(url_for('home_page'))
        else:
         flash('Login unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route('/logout')
def logout_page():
  logout_user()
  return redirect(url_for('home_page'))

@app.route('/account')
@login_required
def account_page():
    form = UpdateAccountForm()
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account', image_file = image_file, form=form)