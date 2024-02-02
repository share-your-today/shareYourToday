from typing import Any
from flask_wtf import FlaskForm
from models import Member
from wtforms.validators import ValidationError, DataRequired, EqualTo
from wtforms import StringField, PasswordField


class RegisterForm(FlaskForm):
    # 회원가입 폼을 정의합니다.
    user_id = StringField("user_id", validators=[DataRequired()])
    # 사용자 ID 필드, 데이터가 필요합니다.
    name = StringField("name", validators=[DataRequired()])
    # 사용자 이름 필드, 데이터가 필요합니다.
    pwd = PasswordField(
        "pwd",
        validators=[
            DataRequired(),
            EqualTo("re_pwd", message="비밀번호가 일치하지 않습니다."),  # 비밀번호 일치 여부 검증
        ],
    )
    # 비밀번호 필드, 데이터가 필요하며 재입력된 비밀번호와 일치해야 합니다.
    re_pwd = PasswordField("re_pwd", validators=[DataRequired()])
    # 비밀번호 재입력 필드, 데이터가 필요합니다.


class LoginForm(FlaskForm):
    # 로그인 폼을 정의합니다.
    class UserPassword(object):
        # 사용자 비밀번호 검증을 위한 커스텀 검증 클래스
        def __init__(self, message=None, user_not_found_message=None, account_locked_message=None):
            # 초기화 메서드
            if message is None:
                message = "잘못된 비밀번호"
            self.message = message
            # 비밀번호 오류 메시지 설정
            if user_not_found_message is None:
                user_not_found_message = "존재하지 않는 ID"
            self.user_not_found_message = user_not_found_message
            # 사용자 ID 오류 메시지 설정
            if account_locked_message is None:
                account_locked_message = '계정이 잠겼습니다. 비밀번호를 찾으세요'           
            self.account_locked_message = account_locked_message
            # 계정 잠김 메시지 설정

        def __call__(self, form, field):
            print(f"User ID: {form.user_id.data}")
            print(f"Password: {form.pwd.data}")
            # 검증 메서드
            user_id = form.user_id.data
            pwd = field.data
            member = Member.query.filter_by(user_id=user_id).first()
            # 사용자 ID에 따른 멤버 조회
            if member is None:
                # 멤버가 존재하지 않을 경우
                raise ValidationError(self.user_not_found_message)
            if member.fail_count >= 5:
                # 로그인 실패 횟수가 5 이상일 경우
                raise ValidationError(self.account_locked_message)
            if member.pwd != pwd:
                # 비밀번호가 일치하지 않을 경우
                raise ValidationError(self.message)

    user_id = StringField("user_id", validators=[DataRequired()])
    # 사용자 ID 필드, 데이터가 필요합니다.
    pwd = PasswordField("pwd", validators=[DataRequired(), UserPassword()])
    # 비밀번호 필드, 데이터가 필요하며 커스텀 검증 클래스를 사용합니다.


class BoardForm(FlaskForm):
    title = StringField("제목", validators=[DataRequired()])
    content = StringField("일기 내용", validators=[DataRequired()])
    image_url = StringField("사진 주소")

    def validate_title(self, field):
        if len(field.data) > (300//4):
            raise ValidationError("제목은 75자 이하여야 합니다.")
        
    def validate_image_url(self, field):
        if len(field.data) > (300):
            raise ValidationError("사진 주소는 300자 이하여야 합니다.")
