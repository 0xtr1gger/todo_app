import xmlrpc.client

import wtforms.validators
from flask_wtf import FlaskForm
from wtforms.fields import StringField, PasswordField, DateField
from wtforms.validators import InputRequired, EqualTo, Email, ValidationError, Optional

import re

def password_validate(form, field, min=8, max=200):
    if len(field.data) < min:
        raise ValidationError('The password is too short. It must be at least 8 characters.')
    if len(field.data) > max:
        raise ValidationError('Whow, slow down. The password is absurdly long.')

    special_characters = '~`!@#$%^&*()_-+=\{\}[]|\\/<>,.:;"\''

    if not any(char in special_characters for char in field.data):
        raise ValidationError('The password must contains at least one special character.')
    if not any(char.isdigit() for char in field.data):
        raise ValidationError('The password must contain at least one digit.')
    if not any(char.isalpha() for char in field.data):
        raise ValidationError('The password must contain at least one letter.')


def email_validate(form, field, min=12, max=13):
    email_regex = r'^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$'
    pattern = re.compile(email_regex)
    if not pattern.match(field.data):
        raise ValidationError('Invalid email address format.')

# custom length validator
class Length(object):
    def __init__(self, min=3, max=100, min_message=None, max_message=None, field='field'):
        self.min = min
        self.max = max

        if not min_message:
            min_message = f'The field must be at least {min} characters long.'
        self.min_message = min_message

        if not max_message:
            max_message = f'The field must not be more than {max} characters long.'
        self.max_message = max_message

    def __call__(self, form, field):
        length = len(field.data)
        if length < self.min:
            raise ValidationError(self.min_message)
        if length > self.max:
            raise ValidationError(self.max_message)


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[
        InputRequired(message='Username is required.'),
        Length(min=2, max=100, min_message=f'Username must be at least 2 characters long.', max_message=f'Username must not exceed 100 characters long.')

    ])
    email = StringField('Email address', validators=[
        InputRequired(message='Email address is required.'),
        Email('Invalid email address format.')
    ])

    password = PasswordField('Password', validators=[
        InputRequired(message='Password field is required.'),
        # password_validate,
        EqualTo('repeat_password', message='Passwords must match.')
    ])

    repeat_password = PasswordField('Repeat password', validators=[
        InputRequired(message='Repeat password.')
    ])


class LoginForm(FlaskForm):
    email = StringField('Email address', validators=[
        InputRequired('Email address is required'),
        Email('Invalid email address format.')
    ])
    password = StringField('Password', validators=[InputRequired()])

class TaskForm(FlaskForm):
    title = StringField('Title', validators=[
        InputRequired('Please, specify the task title')
    ])
    description = StringField('Description')
    deadline = DateField('Deadline', format='%Y-%m-%d', validators=[Optional()])
