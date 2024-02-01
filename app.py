from flask import Flask, render_template, request, redirect, url_for ,session, flash
import os
from forms import RegisterForm, LoginForm
from flask_wtf.csrf import CSRFProtect
from flask_sqlalchemy import SQLAlchemy
from models import db,  Member, Board, Board_Reply
from datetime import datetime

app = Flask(__name__)
# DB 연결 설정 

@app.route("/")
def home():
    #세연에서 사용자 이름을 가져옴, 없으면 None
    name = session.get('name', None)
    user_id=session.get('user_id',None)
    if name is None:
        return redirect('/login') #로그인하지 않은 사용자는 로그인 페이지로 리디렉션
    return render_template("index.html",name=name,user_id=user_id) #로그인한 사용자에게 메잊 페이지(index.html) 표시

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Member.query.filter_by(user_id=form.user_id.data).first()
        # 이 시점에서 사용자가 존재하고 비밀번호가 맞다고 가정할 수 있음
        session['user_id'] = user.user_id
        session['name'] = user.name
        return redirect('/')
    # 폼 에러(검증 에러 포함)는 템플릿에서 사용할 수 있음
    return render_template('login.html', form=form)



@app.route('/logout',methods=['GET'])
def logout():
    session.pop('userid',None)
    return redirect('/login')

@app.route('/register', methods=['GET','POST'])  
def register(): 
    form = RegisterForm()
    if request.method == 'POST' and form.validate():
        user_id = form.user_id.data
        name = form.name.data
        pwd = form.pwd.data
        
        # Check if user already exists
        if Member.query.filter_by(user_id=user_id).first() is not None:
            flash('이미 존재하는 사용자 아이디입니다.')
            return redirect(url_for('register'))
        try:
            member = Member(user_id=user_id, name=name, pwd=pwd)
            db.session.add(member)
            db.session.commit()
            flash("회원가입이 성공했습니다! ")
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash('데이터베이스 저장 중 오류가 발생했습니다.')
            app.logger.error('Error on registration: %s', str(e))
    else:
        for field, errors in form.errors.items():
            print(errors)
            for error in errors:
                flash(error)
    return render_template('register.html', form=form)

@app.route("/board/")
def board():
    board = Board.query.all()
    return render_template("board.html",data=board)


@app.route("/board_detail/<int:board_id>/")
def board_detail(board_id):
    board = Board.query.get(board_id)
    reply = Board_Reply.query.filter_by(board_id=board_id).all()
    data = {
        'board': board,
        'reply': reply
    }
    return render_template("board_detail.html", data=data)


@app.route("/board_create")
def board_create():
    title_receive = request.args.get("title")
    content_receive = request.args.get("content")
    image_receive = request.args.get("image_url")

    board = Board(
        title=title_receive,
        content=content_receive,
        image_url=image_receive,
        user_id="dummy_user_id",
    )
    db.session.add(board)
    db.session.commit()
    return redirect(url_for("board"))


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


if __name__ == "__main__":
    basedir = os.path.abspath(os.path.dirname(__file__)) #현재 파일의 절대 경로
    dbfile = os.path.join(basedir, 'db.sqlite')#데이터베이스 파일 경로 설정

    #애플리케이션 설정
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + dbfile   
    app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True #요청 종료 시 자동 커밋
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  #수정사항 추적 비활성화
    app.config['SECRET_KEY'] = 'wcsfeufhwiquehfdx' # CSRF 및 세션을 위한 비밀 키
    app.config['SESSION_PERMANENT'] = False 


    db.init_app(app)
    with app.app_context():
        db.create_all() #DB 초기화
    app.run(debug=True, port=8001) #디버그 모드로 서버 실행, 포트 8001
