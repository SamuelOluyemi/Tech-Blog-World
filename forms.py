from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, TextAreaField
from wtforms.validators import DataRequired, URL, Length, Regexp, EqualTo, ValidationError, Optional
from flask_ckeditor import CKEditor, CKEditorField


# WTForm for creating a blog post
class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[Optional()])
    img_url = StringField("Blog Image URL", validators=[Optional(), URL()])
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")

# Custom validator for no repeated characters in password; can do for other as well
def no_repeated_characters(form, field):
    pw = field.data or ''
    if len(set(pw)) != len(pw):
        raise ValidationError("Password must not contain repeated characters")

# TODO: Create a RegisterForm to register new users
class RegisterForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=8, message='Password must be at least 8 characters long'),
                                                Regexp(r'.*[a-z].*', message='Must contain a lowercase letter'),
                                                Regexp(r'.*[A-Z].*', message='Must contain an uppercase letter'),
                                                Regexp(r'.*\d.*', message='Must contain a digit'),
                                                Regexp(r'.*[\W_].*', message='Must contain a special character'),
                                                no_repeated_characters
                                                ])
    confirmation_pw = PasswordField("Confirmation", validators=[DataRequired(), EqualTo("password", message="Passwors must match")])
    submit = SubmitField("Sign Me Up!")

# TODO: Create a LoginForm to login existing users
class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Log In")

# TODO: Create a CommentForm so users can leave comments below posts
class CommentForm(FlaskForm):
    text = CKEditorField("Comment", validators=[DataRequired()])
    submit = SubmitField("Submit Comment")


# TODO: Create a ChangePasswordForm so users can change password
class ChangePasswordForm(FlaskForm):
    # current = PasswordField("Password", validators=[DataRequired()])
    new_pw = PasswordField("New", validators=[DataRequired(),
                                                Length(min=8, message='Password must be at least 8 characters long'),
                                                Regexp(r'.*[a-z].*', message='Must contain a lowercase letter'),
                                                Regexp(r'.*[A-Z].*', message='Must contain an uppercase letter'),
                                                Regexp(r'.*\d.*', message='Must contain a digit'),
                                                Regexp(r'.*[\W_].*', message='Must contain a special character'),
                                                no_repeated_characters
                                                ])
    confirmation_pw = PasswordField("Confirmation", validators=[DataRequired(), EqualTo("new_pw", message="Passwors must match")])
    submit = SubmitField("Change Password")

# TODO: Create a ContactForm so anyone or users can contact admin/company
class ContactForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    phone = StringField("Phone", validators=[Optional(), Length(max=20)])
    message = TextAreaField("Message", validators=[DataRequired(), Length(max=2000)])
    submit = SubmitField("Send")

# TODO: Create a DeletePostForm class
class DeletePostForm(FlaskForm):
    submit = SubmitField("Delete")

# TODO: Create a DeleteCommentForm class
class DeleteCommentForm(FlaskForm):
    submit = SubmitField("Delete")

# TODO: Create a RestorePostForm class
class RestorePostForm(FlaskForm):
    submit = SubmitField("Restore")
