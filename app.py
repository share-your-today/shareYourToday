from flask import (
    Flask,
    request,
    redirect,
    url_for,
    session,
    flash,
    jsonify,
)
import os
from models import db
from functools import wraps
from endpoint import users, board, chat

from exception import DBException


app = Flask(__name__)
app.register_blueprint(users.bp)
app.register_blueprint(board.bp)
app.register_blueprint(chat.bp)



# 세션 로그린 여부 확인
basedir = os.path.abspath(os.path.dirname(__file__))  # 현재 파일의 절대 경로
dbfile = os.path.join(basedir, "db.sqlite")  # 데이터베이스 파일 경로 설정

# 애플리케이션 설정
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + dbfile
app.config["SQLALCHEMY_COMMIT_ON_TEARDOWN"] = True  # 요청 종료 시 자동 커밋
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False  # 수정사항 추적 비활성화
app.config["SECRET_KEY"] = "wcsfeufhwiquehfdx"  # CSRF 및 세션을 위한 비밀 키
app.config["SESSION_PERMANENT"] = False


db.init_app(app)
with app.app_context():
    db.create_all()  # DB 초기화


@app.before_request
def check_logged_in():
    # 로그인이 필요하지 않은 경로 리스트
    allowed_routes = ["users.login" ,"login", "static", "home", "register", "find_pw"]

    if "user_id" not in session and request.endpoint not in allowed_routes:
        return redirect(url_for("users.login"))
    

@app.route("/")
def home():
    # 세연에서 사용자 이름을 가져옴, 없으면 None
    name = session.get("name", None)
    user_id = session.get("user_id", None)
    if name is None:
        return redirect("/login")  # 로그인하지 않은 사용자는 로그인 페이지로 리디렉션
    return redirect("/board")

if __name__ == "__main__":
    app.run(debug=True, port=8001)  # 디버그 모드로 서버 실행, 포트 8001
