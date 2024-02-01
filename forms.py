from flask_wtf import FlaskForm
from models import Member
from wtforms import StringField, PasswordField
from wtforms.validators import ValidationError, DataRequired, EqualTo

class RegisterForm(FlaskForm):
    # 회원가입 폼을 정의합니다.
    user_id = StringField('user_id', validators=[DataRequired()])
    # 사용자 ID 필드, 데이터가 필요합니다.
    name = StringField('name', validators=[DataRequired()])
    # 사용자 이름 필드, 데이터가 필요합니다.
    pwd = PasswordField(
        'pwd',
        validators=[
            DataRequired(),
            EqualTo('re_pwd', message='비밀번호가 일치하지 않습니다.')  # 비밀번호 일치 여부 검증
        ]
    )
    # 비밀번호 필드, 데이터가 필요하며 재입력된 비밀번호와 일치해야 합니다.
    re_pwd = PasswordField('re_pwd', validators=[DataRequired()])
    # 비밀번호 재입력 필드, 데이터가 필요합니다.

class LoginForm(FlaskForm):
    # 로그인 폼을 정의합니다.
    class UserPassword(object):
        # 사용자 비밀번호 검증을 위한 커스텀 검증 클래스
        def __init__(self, message=None, user_not_found_message=None):
            # 초기화 메서드
            if message is None:
                message = '잘못된 비밀번호'
            self.message = message
            # 비밀번호 오류 메시지 설정
            if user_not_found_message is None:
                user_not_found_message = '존재하지 않는 ID'
            self.user_not_found_message = user_not_found_message
            # 사용자 ID 오류 메시지 설정

        def __call__(self, form, field):
            # 검증 메서드
            user_id = form.user_id.data
            pwd = field.data
            member = Member.query.filter_by(user_id=user_id).first()
            # 사용자 ID에 따른 멤버 조회
            if member is None:
                # 멤버가 존재하지 않을 경우
                raise ValidationError(self.user_not_found_message)
            if member.pwd != pwd:
                # 비밀번호가 일치하지 않을 경우
                raise ValidationError(self.message)

    user_id = StringField('user_id', validators=[DataRequired()])
    # 사용자 ID 필드, 데이터가 필요합니다.
    pwd = PasswordField('pwd', validators=[DataRequired(), UserPassword()])
    # 비밀번호 필드, 데이터가 필요하며 커스텀 검증 클래스를 사용합니다.
