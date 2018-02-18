from wtforms import Form, StringField, PasswordField, validators, TextAreaField


class RegisterForm(Form):
    """definations"""
    email = StringField('Email', [validators.Length(min=1, max=50)])
    username = StringField('Username', [validators.Length(min=3, max=20)])
    firstname = StringField('Firstname', [validators.Length(min=1, max=50)])
    lastname = StringField('Lastname', [validators.Length(min=1, max=50)])
    password = PasswordField('password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='not match')
    ])
    confirm = PasswordField('confirm password',)


class AlbumForm(Form):
    """definations"""
    title = StringField('Title', [validators.Length(min=1, max=50)])
    body = TextAreaField('Body', [validators.Length(min=1)])
