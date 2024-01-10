#importing req class from flask
from flask import Flask, render_template, url_for, flash, redirect
from forms import RegistrationForm, LoginForm
app = Flask(__name__)

app.config['SECRET_KEY'] = '34ixntdgxafiuh45fri7' #for security attacks

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

@app.route('/login', methods = ['GET', 'POST'])
def login_page():
  form = LoginForm()
  if form.validate_on_submit(): 
    flash(f'Welcom {form.username.data}!', 'success')
    return redirect(url_for('home_page'))
  render_template('login.html', title = 'Login', form = form)

if __name__ == '__main__':
  app.run(host = '0.0.0.0', debug = True)