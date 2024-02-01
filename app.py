from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import os
import time
from forms import RegisterForm, LoginForm, BoardForm
from flask_wtf.csrf import CSRFProtect
from flask_sqlalchemy import SQLAlchemy
from models import db, Member, Board, Board_Reply, Message
from datetime import datetime
from functools import wraps

app = Flask(__name__)

messages = []

# 세션 로그린 여부 확인

@app.before_request
def check_logged_in():
    # 로그인이 필요하지 않은 경로 리스트
    allowed_routes = ["login", "static", "home", "register","find_pw"]

    if "user_id" not in session and request.endpoint not in allowed_routes:
        return redirect(url_for("login"))


@app.route("/")
def home():
    # 세연에서 사용자 이름을 가져옴, 없으면 None
    name = session.get("name", None)
    user_id = session.get("user_id", None)
    if name is None:
        return redirect("/login")  # 로그인하지 않은 사용자는 로그인 페이지로 리디렉션
    return redirect('/board')


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    fail_count = 0
    user_id=""
    if form.validate_on_submit():
        user = Member.query.filter_by(user_id=form.user_id.data).first()
        if user:
            # 로그인 성공 처리
            user.fail_count = 0
            db.session.commit()
            session['user_id'] = user.user_id
            session['name'] = user.name
            return redirect('/board')
    else:
        #로그인 실패시 해당 유저가 있는지 확인
        user = Member.query.filter_by(user_id=form.user_id.data).first()
        if user:
            user_id=user.user_id
            user.fail_count += 1
            fail_count=user.fail_count
            db.session.commit()
            if(user.fail_count>=5):
                if form.validate_on_submit():
                    return render_template('login.html', form=form, fail_count=fail_count, user_id=user_id)
    return render_template('login.html', form=form, fail_count=fail_count,user_id=user_id)


@app.route("/logout", methods=["GET"])
def logout():
    session.clear()
    return redirect('/login')

@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if request.method == "POST" and form.validate():
        user_id = form.user_id.data
        name = form.name.data
        pwd = form.pwd.data

        if Member.query.filter_by(user_id=user_id).first() is not None:
            flash("이미 존재하는 사용자 아이디입니다.")
            return redirect(url_for("register"))
            flash('이미 존재하는 사용자 아이디입니다.')
            return redirect(url_for('register'))

        try:
            member = Member(user_id=user_id, name=name, pwd=pwd)
            db.session.add(member)
            db.session.commit()
            flash("회원가입이 성공했습니다! ")

            # 자동 로그인을 위한 세션 설정
            session['user_id'] = user_id
            session['name'] = name

            return redirect(url_for('board'))
        except Exception as e:
            db.session.rollback()
            flash("데이터베이스 저장 중 오류가 발생했습니다.")
            app.logger.error("Error on registration: %s", str(e))
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(error)
    return render_template("register.html", form=form)



@app.route("/board/")
def board():
    name = session.get("name", None)
    user_id = session.get("user_id", None)
    form = BoardForm()  # BoardForm 객체를 생성합니다.

    board = Board.query.order_by(Board.created_dttm.desc()).all()
    return render_template("board.html", data=board, name=name, user_id=user_id, form=form)


@app.route("/user_posts/<user_id>/")
def user_posts(user_id):
    name = session.get("name", None)
    if user_id:
        user_posts = (
            Board.query.filter_by(user_id=user_id)
            .order_by(Board.created_dttm.desc())
            .all()
        )
        return render_template("board.html", data=user_posts, user_id=user_id, name=name)
    else:
        return render_template("error.html", message="유저 아이디가 유효하지 않습니다.")


@app.route("/board_detail/<int:board_id>/")
def board_detail(board_id):
    name = session.get("name", None)
    user_id = session.get("user_id", None)
    board = Board.query.get(board_id)
    reply = Board_Reply.query.filter_by(board_id=board_id).all()
    data = {"board": board, "reply": reply}
    return render_template("board_detail.html", data=data, name=name, user_id=user_id)


@app.route("/board_create", methods=["POST", "GET"])
def board_create():
    user_id = session.get("user_id", None)
    form = BoardForm()

    is_open = False

    if form.validate_on_submit():
        board = Board(
            title=form.title.data,
            content=form.content.data,
            image_url=form.image_url.data,
            user_id=user_id
        )
        db.session.add(board)
        db.session.commit()
        return redirect(url_for("board"))
    else:
        if form.errors:
            for fieldName, errorMessages in form.errors.items():
                
                print(fieldName, errorMessages)
            is_open = True

    boards = Board.query.all()  # 데이터베이스에서 게시물 목록을 가져옴
    return render_template("board.html", data=boards, form=form, is_open=is_open)

@app.route("/board_update/<int:board_id>/", methods=["POST"])
def board_update(board_id):
    title_receive = request.form.get("title")
    content_receive = request.form.get("content")
    image_receive = request.form.get("image_url")

    board = Board.query.get_or_404(board_id)
    board.title = title_receive
    board.content = content_receive
    board.image_url = image_receive

    db.session.commit()

    return redirect(url_for("board"))


@app.route("/board_delete/<int:board_id>/", methods=["POST"])
def board_delete(board_id):
    board = Board.query.get(board_id)
    db.session.delete(board)
    db.session.commit()

    return redirect(url_for("board"))


# 채팅 관련
@app.route('/chat/')
def chat():
    return render_template("chat.html")

# 채팅 메시지를 받는 라우트
@app.route('/send', methods=['POST'])
def send():
    user_id = session.get("user_id", None)
    message = request.form.get('message')
    timestamp = datetime.utcnow()

    new_message = Message(message=message, timestamp=timestamp, user_id=user_id)
    db.session.add(new_message)
    db.session.commit()

    return jsonify({'message': message, 'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),'user_id': user_id})

# 채팅 메시지를 받아오는 폴링 라우트
@app.route('/get_messages')
def get_messages():
    timestamp = request.args.get('timestamp', '2000-01-01 00:00:00')
    timestamp = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')

    new_messages = Message.query.filter(Message.timestamp > timestamp).all()
    latest_timestamp = datetime.utcnow()

    messages = [{'message': msg.message, 'timestamp': msg.timestamp.strftime(
        '%Y-%m-%d %H:%M:%S'), 'user_id': msg.user_id} for msg in new_messages]

    return jsonify({'messages': messages, 'latest_timestamp': latest_timestamp.strftime('%Y-%m-%d %H:%M:%S')})

@app.route('/find_pw/<user_id>')
def find_pw(user_id):
    user=Member.query.filter_by(user_id=user_id).first()
    pwd=user.pwd
    user.fail_count=0
    db.session.commit()
    return render_template('find_pw.html', user_id=user_id,pwd=pwd)


if __name__ == "__main__":
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
    app.run(debug=True, port=8001)  # 디버그 모드로 서버 실행, 포트 8001