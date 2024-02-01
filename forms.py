from flask_wtf import FlaskForm
from models import Member
from wtforms import StringField, PasswordField
from wtforms.validators import ValidationError,DataRequired, EqualTo

class RegisterForm(FlaskForm):
    user_id = StringField('user_id', validators=[DataRequired()])
    name = StringField('name', validators=[DataRequired()])
    pwd = PasswordField(
        'pwd',
        validators=[
            DataRequired(),
            EqualTo('re_pwd', message='비밀번호가 일치하지 않습니다.')  # 메시지 추가
        ]
    )
    re_pwd = PasswordField('re_pwd', validators=[DataRequired()])

class LoginForm(FlaskForm):
    class UserPassword(object):
        def __init__(self, message=None, user_not_found_message=None):
            if message is None:
                message = '잘못된 비밀번호'
            self.message = message
            if user_not_found_message is None:
                user_not_found_message = '존재하지 않는 ID'
            self.user_not_found_message = user_not_found_message

        def __call__(self, form, field):
            user_id = form.user_id.data
            pwd = field.data
            member = Member.query.filter_by(user_id=user_id).first()
            if member is None:
                raise ValidationError(self.user_not_found_message)
            if member.pwd != pwd:
                raise ValidationError(self.message)

    user_id = StringField('user_id', validators=[DataRequired()])
    pwd = PasswordField('pwd', validators=[DataRequired(), UserPassword()])

