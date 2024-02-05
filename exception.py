from functools import wraps

from sqlalchemy.exc import SQLAlchemyError
from flask import flash

from models import db

class DBException(Exception):
    def __init__(self, message, *args) -> None:
        super().__init__(*args)
        self.message = message


def db_commit_error_handler(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
            
        except SQLAlchemyError as e:
            db.session.rollback()
            flash("데이터베이스 저장 중 오류가 발생했습니다.")
            raise DBException("데이터베이스 저장 중 오류가 발생했습니다.", e.args) from e

    return wrapper
