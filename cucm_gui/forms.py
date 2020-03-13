from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, BooleanField, SelectMultipleField
from wtforms.validators import DataRequired, IPAddress, InputRequired


class LoginForm(FlaskForm):
    cucm_ip = StringField('CUCM IP Address', default="10.50.4.20", validators=[DataRequired(), IPAddress()])
    cucm_username = StringField('CUCM Username', default="admin", validators=[DataRequired()])
    cucm_password = PasswordField('CUCM Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')


class Users(FlaskForm):
    user = SelectField('Select a User', validators=[InputRequired()])
    submit = SubmitField('Select User')


class User(FlaskForm):
    firstName = StringField('First Name')
    lastName = StringField('Last Name')
    displayName = StringField('Display Name')
    userGroup = SelectMultipleField('Select the groups the user should belong to')
    submit = SubmitField('Update User')


class UpdateUser(FlaskForm):
    submit = SubmitField('Change User')


class IncludeLDAPUsers(FlaskForm):
    include_ldap = BooleanField('Include LDAP', default=False)
