from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from flask import Flask, abort, render_template, redirect, url_for, flash, request, session
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor, CKEditorField
# Using markdown to correct the issue with CKEditorField
import markdown
# from flask_gravatar import Gravatar
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user, login_required
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text, Boolean, event, DateTime, func
from sqlalchemy.engine import Engine
import sqlite3
from flask_migrate import Migrate
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
# Import your forms from the forms.py
from forms import *
import os
from flask_session import Session
from cs50 import SQL
from flask_mail import Mail, Message
# Load python-dotenv
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


year = date.today().year
DateTime(timezone=True)
# Set datetime to DT in UTC
DT = datetime.now(timezone.utc)


app = Flask(__name__)

# to unify all conifg
class BaseConfig:
    SECRET_KEY = os.getenv("FLASK_KEY")
    SQLALCHEMY_DATABASE_URI = os.getenv("DB_URI", "sqlite:///posts.db")

    # CKEditor
    CKEDITOR_PKG_TYPE = "standard"

    # Sessions
    SESSION_PERMANENT = False
    SESSION_TYPE = "filesystem"
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)

    # Mail
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = "sotcode2025@gmail.com"
    MAIL_PASSWORD = os.getenv("GMAIL_APP_PW")
    MAIL_DEFAULT_SENDER = "sotcode2025@gmail.com"

class DevConfig(BaseConfig):
    DEBUG = True
    
class ProdConfig(BaseConfig):
    DEBUG = False
    
app.config.from_object(DevConfig)
if not app.config["SECRET_KEY"]:
    raise ValueError("FLASK_KEY is missing. Set it in .env or environment variables.")
if not app.config["SQLALCHEMY_DATABASE_URI"]:
    raise ValueError("DB_URI is missing. Set it in .env or environment variables.")

# Configure CKEditor
# app.config['CKEDITOR_PKG_TYPE'] = 'standard'
ckeditor = CKEditor(app)
# Configure CSRF
csrf = CSRFProtect()
csrf.init_app(app)

Bootstrap5(app)
# Configure Flask_Session to use filesystem (instead of signed cookies)
# app.config["SESSION_PERMANENT"] = False
# app.config["SESSION_TYPE"] = "filesystem"
# app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=30)
Session(app)

# configure flask_mail
# app.config.update(
#     MAIL_SERVER="smtp.gmail.com",
#     MAIL_PORT=587,
#     MAIL_USE_TLS=True,
#     MAIL_USERNAME="sotcode2025@gmail.com",
#     MAIL_PASSWORD= os.environ.get('GMAIL_APP_PW'),
#     MAIL_DEFAULT_SENDER="sotcode2025@gmail.com"
# )
mail = Mail(app)

# TODO: Configure Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)

# # Configure Gravatar for adding profile avatar
# gravatar = Gravatar(
#     app,
#     size=100,
#     rating="g",
#     default="retro",
#     force_default=False,
#     force_lower=False,
#     use_ssl=True,
#     base_url=None,
# )
# # gravatar = Gravatar()
# # gravatar.init_app(app)

#  To replace flask_gravatar with custom gravatar function


import hashlib

def gravatar_url(email, size=100):
    email = email.strip().lower().encode("utf-8")
    hash = hashlib.md5(email).hexdigest()
    return f"https://www.gravatar.com/avatar/{hash}?s={size}&d=retro"

# make gravatar available
app.jinja_env.globals["gravatar_url"] = gravatar_url


# Create a user_loader callback
@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)


# CREATE DATABASE
class Base(DeclarativeBase):
    pass
# app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DB_URI", "sqlite:///posts.db")
db = SQLAlchemy(model_class=Base)
db.init_app(app)

# # Configure CS50 Library to use SQLite database
# db = SQL("sqlite:///posts.db")

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# check_inactivty() function
@app.before_request
def check_inactivity():
    if current_user.is_authenticated:
        now = DT
        last_activity = session.get("last_activity")

        if last_activity:
            last_activity = datetime.fromisoformat(last_activity)

            if now - last_activity > timedelta(minutes=30):
                logout_user()
                session.clear()
                flash("Your session expired due to inactivity. Please log in again.", "warning")
                return redirect(url_for("login"))

        session["last_activity"] = now.isoformat()


# TODO: Create a User table for all your registered users.
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250))
    email: Mapped[str] = mapped_column(String(250), unique=True)
    password_hash: Mapped[str] = mapped_column(String(250))
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


    # This will act like the list of BlogPost objects attached to each User.
    # The "author" refers to the author property in the BlogPost class.
    posts = relationship("BlogPost", back_populates="author", cascade="all, delete-orphan",
        passive_deletes=True)

    # The "comment_author" refers to the author property in the BlogPost class.
    comments = relationship("Comment", back_populates="comment_author", cascade="all, delete-orphan",
        passive_deletes=True)

    # contact_messages: relationship of one sender -> to many contact messages
    contact_messages = relationship("Contact", back_populates="sender", cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)



# CONFIGURE TABLES
class BlogPost(db.Model):
    __tablename__ = "blog_posts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # Create Foreign Key, "users.id" the users refers to the tablename of User.
    author_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Create reference to the User object. The "posts" refers to the posts property in the User class
    author = relationship("User", back_populates="posts")

    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    subtitle: Mapped[str] = mapped_column(String(250), nullable=True)
    date: Mapped[str] = mapped_column(String(250), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    img_url: Mapped[str] = mapped_column(String(500), nullable=True)

    # Add Parent relationship
    comments = relationship("Comment", back_populates="parent_post", cascade="all, delete-orphan",
        passive_deletes=True)

    # Implement soft delete for blog_posts as well so we can save them in db table for future use
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

# Create a Deleted Posts table for blog posts
class DeletedPosts(db.Model):
    __tablename__ = "deleted_posts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    delete_post_id: Mapped[int] = mapped_column(Integer)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    subtitle: Mapped[str] = mapped_column(String(250), nullable=True)
    date: Mapped[str] = mapped_column(String(250), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    img_url: Mapped[str] = mapped_column(String(500), nullable=True)

    deleted_at: Mapped[str] = mapped_column(DateTime, default=lambda: DT,
    nullable=False)


# Create a Comment table for users to leave
class Comment(db.Model):
    __tablename__ = "comments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # Add Child relationship
    # users.id refers to the tablename of the User class
    # comments refer to the comments property in the User class
    author_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    comment_author = relationship("User", back_populates="comments")

    # Add Child relationship
    post_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("blog_posts.id", ondelete="CASCADE"), nullable=False)
    parent_post = relationship("BlogPost", back_populates="comments")

    text: Mapped[str] = mapped_column(Text, nullable=False)
    date: Mapped[str] = mapped_column(DateTime, default=lambda: DT, nullable=False)

# Create a Contact table for users to send message
class Contact(db.Model):
    __tablename__ = "contact_msgs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    sender_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    # Add Child relationship back to User
    sender = relationship("User", back_populates="contact_messages")

    name: Mapped[str] = mapped_column(String(250), nullable=False)
    email: Mapped[str] = mapped_column(String(250), nullable=False)
    phone: Mapped[str] = mapped_column(String(20), nullable=True)
    message: Mapped[str] = mapped_column(Text, nullable=False)

    # # Added later
    # ALTER TABLE contact_msgs
    # ADD COLUMN sent_at DATETIME DEFAULT CURRENT_TIMESTAMP
    sent_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.current_timestamp())


# Implement delete deleted_posts after 30 days with the aid of ChatGPT Atlas
def purge_old_deleted_posts():
    cutoff = DT - timedelta(days=30)

    deleted_posts = DeletedPosts.query.filter(
        DeletedPosts.deleted_at < cutoff
    ).all()

    for post in deleted_posts:
        deleted = BlogPost.query.get(post.delete_post_id)
        if deleted:
            db.session.delete(deleted)

        db.session.delete(post)

    db.session.commit()

# This is my App startup
with app.app_context():
    db.create_all()
    # TODO: Set exactly one admin #ChatGPT Atlas

    # Remove is_admin from everyone by setting them to False
    User.query.update({User.is_admin: False})

    # Set admin user (use if (or try...except) in case admin isn't found)
    admin = User.query.filter_by(id=1).first()
    if not admin:
        admin = User(
            name="Admin",
            email="admin@example.com",
            is_admin=True
        )
        admin.set_password(os.environ.get("ADMIN_PW"))
        db.session.add(admin)
    else:
        admin.is_admin = True

    # Purge old_deleted_posts
    purge_old_deleted_posts()

    db.session.commit()

@event.listens_for(User, "before_insert")
@event.listens_for(User, "before_update")
def enforce_single_admin(mapper, connection, target):
    if target.is_admin:
        connection.execute(
            User.__table__.update()
            .where(User.id != target.id)
            .values(is_admin=False)
        )

# Enable foreign keys when app starts (SQLite only)
@event.listens_for(Engine, "connect")
def enable_sqlite_fk(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

# Create admin-only decorator
def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # If current_user is_admin=False
        if not current_user.is_admin:
            flash("Admin authorization only")
            abort(403)
        # Otherwise continue with the route function
        return f(*args, **kwargs)
    return decorated_function


# Create commenter-only decorator
def commenter_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = db.session.execute(db.select(Comment).where(Comment.author_id == current_user.id)).scalar()
        if not current_user.is_authenticated or current_user.id != user.author_id:
            # return abort(403)
            flash("Log in required")
            return redirect("/login")
        # Otherwise continue with the route function
        return f(*args, **kwargs)
    return decorated_function

# Set to user timezone
def convert_to_local(utc_dt):
    user_tz = session.get("timezone", "UTC")
    return utc_dt.astimezone(ZoneInfo(user_tz))

# TODO: Use Werkzeug to hash the user's password when creating a new user.
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        pw = form.password.data
        confirmation_pw = form.confirmation_pw.data
        result = db.session.execute(db.select(User).where(User.email == email))
        user = result.scalar()
        if user:
            # User already exists
            flash('Email already registered, Please log in!')
            return redirect(url_for('login'))
        if not name or not email or not pw or not confirmation_pw:
            flash("Missing field(s)")
        if pw != confirmation_pw:
            flash("Password mismatch")
        new_user = User(
            name = name,
            email = email,
        )
        # Set password using the method set_password in the User db
        new_user.set_password(pw)

        db.session.add(new_user)
        db.session.commit()
        flash("Account created successfully", "success")

        # Log in and authenticate user after added details to database
        login_user(new_user)
        session.permanent = True
        session["last_activity"] = DT.isoformat()
        return redirect(url_for('get_all_posts'))

    return render_template("register.html", form=form, year=year, current_user=current_user)


# TODO: Retrieve a user from the database based on their email.
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        # Find user by email
        result = db.session.execute(db.select(User).where(User.email == email))
        user = result.scalar()

        if user and user.check_password(password):
            login_user(user)
            session.permanent = True
            session["last_activity"] = DT.isoformat()
            return redirect(url_for('get_all_posts'))
        elif not user:
            flash('Login unsuccessful. Check email', 'error')
            return redirect(url_for('login'))
        else:
            flash('Login unsuccessful. Check password', 'error')
            return redirect(url_for('login'))

    return render_template("login.html", form=form, year=year, current_user=current_user)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('get_all_posts'))


@app.route('/')
def get_all_posts():
    result = db.session.execute(db.select(BlogPost).where(BlogPost.is_deleted == False))
    posts = result.scalars().all()
    delete_post_form = DeletePostForm()
    return render_template("index.html", all_posts=posts, delete_post_form=delete_post_form, year=year, current_user=current_user)


# TODO: Allow logged-in users to comment on posts
@app.route("/post/<int:post_id>", methods=["GET", "POST"])
def show_post(post_id):
    requested_post = db.get_or_404(BlogPost, post_id)
    # print(requested_post.body)
    # Using markdown to correct the issue with CKEditorField
    html_body = markdown.markdown(requested_post.body, extensions=["extra", "nl2br", "sane_lists", "codehilite"])
    # print(html_body)
    # Add the CommentForm to the route

    comment_form = CommentForm()
    delete_comment_form = DeleteCommentForm()
    # Only allow logged-in users to comment on posts
    if comment_form.validate_on_submit():
        if not current_user.is_authenticated:
            flash('Login required. Login or Register to comment', 'error')
            return redirect(url_for('login'))
        new_comment = Comment(
            text=markdown.markdown(comment_form.text.data),
            comment_author=current_user,
            parent_post=requested_post,
            date= DT
        )

        db.session.add(new_comment)
        db.session.commit()

        return redirect(url_for('show_post', post_id=post_id))

    return render_template("post.html", post=requested_post,
                            html_body=html_body,
                              form=comment_form,
                                delete_comment_form=delete_comment_form,
                                  year=year,
                                    current_user=current_user)

@app.route("/delete/comment/<int:comment_id>/<int:post_id>", methods=["GET", "POST"])
@login_required
@commenter_only
def delete_comment(comment_id, post_id):
    requested_comment = db.get_or_404(Comment, comment_id)
    form = DeleteCommentForm()

    db.session.delete(requested_comment)
    db.session.commit()
    return redirect(url_for('show_post', post_id=post_id, form=form))


# TODO: Use a decorator so only an admin user can create a new post
@app.route("/new-post", methods=["GET", "POST"])
@admin_only
def add_new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
            author=current_user,
            date=date.today().strftime("%B %d, %Y")
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html", form=form, year=year, current_user=current_user)


# TODO: Use a decorator so only an admin user can edit a post
@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
@admin_only
def edit_post(post_id):
    post = db.get_or_404(BlogPost, post_id)
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        author=post.author,
        body=post.body
    )
    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.img_url.data
        post.author = current_user
        post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("show_post", post_id=post.id))
    return render_template("make-post.html", form=edit_form, is_edit=True, year=year, current_user=current_user)


# TODO: Use a decorator so only an admin user can delete a post
def soft_delete_post(post):
    # post_to_delete = db.get_or_404(BlogPost, post_id)
    # Make is_deleted True so we can add it to deleted_posts table
    deleted_post = DeletedPosts(
        delete_post_id=post.id,
        title=post.title,
        subtitle=post.subtitle,
        body=post.body,
        img_url=post.img_url,
        date=post.date,
        deleted_at=DT
    )
    # db.session.delete(post_to_delete)
    db.session.add(deleted_post)
    post.is_deleted = True
    db.session.commit()

@app.route("/delete/<int:post_id>", methods=["GET", "POST"])
@admin_only
def delete_post(post_id):
    post_to_delete = db.get_or_404(BlogPost, post_id)
    # post = BlogPost.query.get_or_404(id)
    delete_post_form = DeletePostForm()

    if delete_post_form.validate_on_submit():

        soft_delete_post(post_to_delete)

        flash("Post was moved to trash", "success")
    return redirect(url_for('get_all_posts', post_id=post_to_delete.id, delete_post_form=delete_post_form))

@app.route("/admin/deleted-posts")
@admin_only
def deleted_posts_dashboard():
    posts = DeletedPosts.query.order_by(
        DeletedPosts.deleted_at.desc()
    ).all()
    form = DeletePostForm() # create instance to be used in force_delete
    restore_post_form = RestorePostForm()

    return render_template("admin_deleted_posts.html", posts=posts, form=form, restore_post_form=restore_post_form)

@app.route("/admin/restore-post/<int:id>", methods=["GET", "POST"])
@admin_only
def restore_post_route(id):
    deleted_post = DeletedPosts.query.get_or_404(id)
    form = RestorePostForm()

    if form.validate_on_submit():
        original_post = BlogPost.query.get(deleted_post.delete_post_id)

        if original_post:
            original_post.is_deleted = False
            db.session.delete(deleted_post)
            db.session.commit()

    return redirect(url_for("deleted_posts_dashboard", form=form))

@app.route("/admin/force-delete-post/<int:id>", methods=["GET", "POST"])
@admin_only
def force_delete_post(id):
    deleted_post = DeletedPosts.query.get_or_404(id)

    original_post = BlogPost.query.get(deleted_post.delete_post_id)

    if original_post:
        db.session.delete(original_post)

    db.session.delete(deleted_post)
    db.session.commit()

    flash("Post permanently deleted", "success")

    return redirect(url_for("deleted_posts_dashboard"))


@app.route("/about")
def about():
    return render_template("about.html", year=year, current_user=current_user)

# function for sending the user's contact email
def send_contact_email(contact):
    msg = Message(
        subject="New Contact Message",
        recipients=["admin@example.com", "sotcode2025@gmail.com"],
        body=f"""
            Name: {contact.name}
            Email: {contact.email}
            Phone: {contact.phone}
            Message:
            {contact.message}
            """
                )
    mail.send(msg)

@app.route("/contact", methods=["GET", "POST"])
def contact():
    # Implement the contact form to be sent to sotcode2025@gmail.com
    form = ContactForm()
    name = form.name.data
    email = form.email.data
    phone = form.phone.data
    message = form.message.data

    if form.validate_on_submit():
        if not name or not email or not message:
            flash("Missing Field")

        contact = Contact(
            sender=current_user if current_user.is_authenticated else None,
            name=name,
            email=email,
            phone=phone,
            message=message
        )

        db.session.add(contact)
        db.session.commit()

        send_contact_email(contact)

        flash("Your message has been sent successfully!", "success")
        return redirect(url_for("contact"))

    return render_template("contact.html", form=form, year=year, current_user=current_user)


# Create a route for Admin to see contact messages
@app.route("/admin/messages")
@login_required
@admin_only
def admin_msgs():
    messages = Contact.query.order_by(Contact.sent_at.desc()).all()
    return render_template("admin_messages.html", messages=messages, year=year, current_user=current_user)


# Implement change_password
@app.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    """Allow users to change their passwords."""
    # rename password column to password_hash
    # ALTER TABLE users RENAME COLUMN password TO password_hash;
    form = ChangePasswordForm()
    new_pw = form.new_pw.data
    confirmation_pw = form.confirmation_pw.data

    if form.validate_on_submit():
        if not new_pw or not confirmation_pw:
            flash("Missing fields")

        if new_pw != confirmation_pw:
            flash("Password mismatch")

        # # If using SQL from cs50 with db
        # db.execute("UPDATE users SET password = ? WHERE id = ?", new_password, session[id])

        # with SQLAlchemy
        # TODO: Check for how to update db form on SQLAlchemy
        # Update password in db
        current_user.set_password(new_pw)
        db.session.commit()

        flash("Password updated successfully", "success")

        return redirect("/")
    return render_template("change_password.html", form=form, year=year, current_user=current_user)


if __name__ == "__main__":
    app.run(debug=False, port=5000)

