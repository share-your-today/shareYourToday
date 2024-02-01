from flask_wtf import FlaskForm
from models import Member
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, EqualTo

class RegisterForm(FlaskForm):
    user_id = StringField('user_id', validators=[DataRequired()])
    name = StringField('name', validators=[DataRequired()])
    pwd = PasswordField('pwd', validators=[DataRequired(), EqualTo('re_pwd')]) #equalTo("필드네임")
    re_pwd = PasswordField('re_pwd', validators=[DataRequired()])


class LoginForm(FlaskForm):
    class UserPassword(object):
        def __init__(self, message=None):
            self.message = message
        def __call__(self,form,field):
            user_id = form['user_id'].data
            pwd = field.data
            member = Member.query.filter_by(user_id=user_id).first()
            if member.pwd != pwd:
                # raise ValidationError(message % d)
                raise ValueError('Wrong password')
    user_id = StringField('user_id', validators=[DataRequired()])
    pwd = PasswordField('pwd', validators=[DataRequired(), UserPassword()]) 
   