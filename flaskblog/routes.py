import re
import secrets
import os
from PIL import Image 
from flask import flash, redirect, render_template, url_for, request, abort
from flaskblog import app, db, bcrypt, mail
from flaskblog.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm, RequestResetForm, ResetPasswordForm
from flaskblog.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required
from flask_login import current_user
from flask_mail import Message
#pillow package for work with images



@app.route('/')
@app.route('/home')
def home_page():
  page = request.args.get('page', 1, type=int)
  posts = Post.query.order_by(Post.date_posted.desc()).paginate(per_page=5, page=page)
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


def save_picture(form_picture): #handling profile pictures extensions and saving user image to our folder
  random_hex = secrets.token_hex(8)
  _, f_ext = os.path.splitext(form_picture.filename)
  picture_fn = random_hex + f_ext
  picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)
  output_size = (120, 120)
  i = Image.open(form_picture)
  i.thumbnail(output_size)
  i.save(picture_path)
  return picture_fn
  
  
@app.route('/account', methods=['GET', 'POST'])
@login_required
def account_page():
    form = UpdateAccountForm()
    if form.validate_on_submit():
      if form.picture.data:
        picture_file = save_picture(form.picture.data)
        current_user.image_file = picture_file
      current_user.username = form.username.data
      current_user.email = form.email.data
      db.session.commit()
      flash('Your account has been updated!', 'success')
      return redirect(url_for('account_page'))
    elif request.method == 'GET':
      form.username.data = current_user.username
      form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account', image_file = image_file, form=form)

@app.route('/post/new', methods=['GET', 'POST'])
@login_required
def new_post():
  form = PostForm()
  if form.validate_on_submit():
    post = Post(title = form.title.data, content = form.content.data, author = current_user)
    db.session.add(post)
    db.session.commit()
    flash('Posted', 'success')
    return redirect(url_for('home_page'))
  return render_template('create_post.html', title='New Post', form=form, legend='New Post')


@app.route('/post/<int:post_id>')
def post(post_id):
  post = Post.query.get_or_404(post_id)
  return render_template('post.html', title=post.title, post=post)


@app.route('/post/<int:post_id>/update', methods=['GET', 'POST'])
@login_required
def update_post(post_id):
  post = Post.query.get_or_404(post_id)
  if post.author != current_user:
    abort(403)
  form = PostForm()
  if form.validate_on_submit():
    post.title = form.title.data
    post.content = form.content.data
    db.session.commit()
    flash('Your post has been updated!', 'success')
    return redirect(url_for('post', post_id=post.id))
  elif request.method == 'GET':
    form.title.data = post.title
    form.content.data = post.content
  return render_template('create_post.html', title='Update Post', form=form, legend='Update Post')

@app.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
  post = Post.query.get_or_404(post_id)
  if post.author != current_user:
    abort(403)
  db.session.delete(post)
  db.session.commit()
  flash('Your post has been deleted!', 'success')
  return redirect(url_for('home_page'))

@app.route( '/user/<string:username>')
def user_posts(username):
  page = request.args.get('page', 1, type=int)
  user = User.query.filter_by(username = username).first_or_404()
  posts = Post.query.filter_by(author=user).order_by(Post.date_posted.desc()).paginate(per_page=5, page=page)
  return render_template('user_posts.html', posts=posts, user=user)

def send_reset_email(user):
  token = user.get_reset_token()
  msg = Message('Password Reset Request', 
                sender='noreply@demo.com', 
                recipients=[user.email])
  msg.body = f'''To reset your password, visit the following link:
{ url_for( 'reset_token', token=token, _external=True) }
  
If you did not make this request then simply ignore this email and no changes will be made.  
'''
  mail.send(msg)
  

@app.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
  if current_user.is_authenticated:
    return redirect(url_for('home_page'))
  form = RequestResetForm()
  if form.validate_on_submit():
    user = User.query.filter_by(email = form.email.data).first()
    send_reset_email(user)
    flash('An email has been sent with instructions to reset your password', 'info')
    return redirect(url_for('login_page'))
  return render_template('reset_request.html', title='Reset Password', form=form)


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
  if current_user.is_authenticated:
    return redirect(url_for('home_page'))
  user = User.verify_reset_token(token)
  if user is None:
    flash('That is an invalid or expired token', 'warning')
    return redirect(url_for('reset_request'))
  form = ResetPasswordForm()
  if form.validate_on_submit(): 
    hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')   # hashing the password for security
    user.password = hashed_password
    db.session.commit()
    flash('Your password has been updated! You are now able to login', 'success')
    return redirect(url_for('login_page'))
  return render_template('reset_token.html', title='Reset Password', form=form)