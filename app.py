from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import Unauthorized

from models import connect_db, db, User, Feedback
from forms import UserForm, LoginForm, DeleteForm, FeedbackForm

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///feedback_app"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "abc123"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False


toolbar = DebugToolbarExtension(app)

connect_db(app)


@app.route('/')
def home_page():
    """Redirect to register page"""
    return redirect('/register')

@app.route('/register', methods = ['GET', 'POST'])
def register_user():
    """Showing a form that when submitted will 
    register/create a user. Processing the registration form by 
    adding a new user."""

    form = UserForm()
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        password = form.password.data

        user = User.register(username,password,email,first_name,last_name)
        db.session.add(user)
        try:
            db.session.commit()
            session['username'] = user.username
            flash('Welcome! Successfully Created Your Account!', 'success')
            return redirect(f"/users/{user.username}")

        except IntegrityError:
            form.username.errors.append('Username taken. Please pick another one')
            form.email.errors.append('This email is being used by someone else. Please pick another one')
            return render_template('register.html', form=form)

    return render_template('register.html', form=form)

@app.route('/login', methods = ['GET','POST'])
def login():
    """Show a login form, log the user in after submitting the form."""

    if 'username' in session:
        return redirect (f"/users/{session['username']}")

    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password) #<User> or False
        if user:
            session['username'] = user.username
            return redirect(f"/users/ {user.username}")
        else:
            form.username.errors = ['Invalid username/password!']
            return render_template('users/login.html', form=form)

    return render_template('users/login.html', form=form)


@app.route('/logout')
def logout():
    """Clear any information from the session and redirect to /
    """

    session.pop('username')
    return redirect('/login')



@app.route('/users/<username>')
def show_user(username):
    """Example page for logged-in-users"""

    if 'username' not in session or username != session['username']:
        raise Unauthorized()

    user = User.query.get(username)
    form = DeleteForm()

    return render_template('users/show.html', user=user, form=form)


@app.route('/users/<username>/delete', methods = ['POST'])
def remove_user(username):
    """Remove user and redirect to login"""

    if 'username' not in session or username != session['username']:
        raise Unauthorized()

    user = User.query.get(username)
    db.session.delete(user)
    db.session.commit()
    session.pop('username')

    return redirect('/login')


@app.route('/users/<username>/feedback/new', methods = ['GET', 'POST'])
def new_feedback(username):
    """Show add-feedback form and prosses it"""

    if 'username' not in session or username != session['username']:
        raise Unauthorized()

    form = FeedbackForm()

    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data

        feedback = Feedback(
            title=title,
            content = content,
            username = username
        )

        db.session.add(feedback)
        db.session.commit()

        return redirect(f'/users/{feedback.username}')

    else:
        return render_template('feedback/new.html', form=form)



@app.route('/feedback/<int:feedback_id>/update', methods = ['GET', 'POST'])
def update_feedback(feedback_id):
    """Show update-feedback form and prosses it"""
    
    feedback = Feedback.query.get(feedback_id)
    
    if "username" not in session or feedback.username != session['username']:
        raise Unauthorized()

    form = FeedbackForm(obj=feedback)

    if form.validate_on_submit():
        feedback.title = form.title.data
        feedback.content = form.content.data

        db.session.commit()

        return redirect(f'/users/{feedback.username}')

    return render_template('/feedback/edit.html', form=form, feedback = feedback)


@app.route("/feedback/<int:feedback_id>/delete", methods=["POST"])
def delete_feedback(feedback_id):
    """Delete feedback."""

    feedback = Feedback.query.get(feedback_id)
    if "username" not in session or feedback.username != session['username']:
        raise Unauthorized()

    form = DeleteForm()

    if form.validate_on_submit():
        db.session.delete(feedback)
        db.session.commit()

    return redirect(f"/users/{feedback.username}")