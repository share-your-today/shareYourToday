from flask import Flask, render_template, request, redirect, url_for ,session
import os
from forms import RegisterForm, LoginForm
from flask_wtf.csrf import CSRFProtect
from flask_sqlalchemy import SQLAlchemy
from models import db,  Member, Board, Board_Reply
from datetime import datetime
app = Flask(__name__)
# DB 연결 코드 만들어야 함

basedir = os.path.abspath(os.path.dirname(__file__))  # 지금 현재 위치
app.config['SQLALCHEMY_DATABASE_URI'] =\
        'sqlite:///' + os.path.join(basedir, 'database.db')




@app.route("/")
def home():
    name = session.get('name', None)
    if name is None:
        return redirect('/login')
    return render_template("index.html",name=name)

@app.route('/login', methods=['GET','POST'])  
def login():  
    form = LoginForm() #로그인 폼 생성
    if form.validate_on_submit(): #유효성 검사
        session.clear()
        user= Member.query.filter_by(user_id=form.data.get('user_id')).first()
        if user:
            session['user_id'] = user.user_id
            session['name'] = user.name  #form에서 가져온 userid를 session에 저장
            return redirect('/') #로그인에 성공하면 홈화면으로 redirect
        else:
            #사용자가 없을 떄의 처리
            pass
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET','POST'])  #겟, 포스트 메소드 둘다 사용
def register():   #get 요청 단순히 페이지 표시 post요청 회원가입-등록을 눌렀을때 정보 가져오는것
    form = RegisterForm()
    if form.validate_on_submit(): # POST검사의 유효성검사가 정상적으로 되었는지 확인할 수 있다. 입력 안한것들이 있는지 확인됨.
        #비밀번호 = 비밀번호 확인 -> EqulaTo
        try:
            member = Member()  #models.py에 있는 Fcuser 
            member.user_id = form.data.get('user_id')
            member.name = form.data.get('name')
            member.pwd = form.data.get('pwd')
            db.session.add(member)  # id, name 변수에 넣은 회원정보 DB에 저장
            db.session.commit()  #커밋
            return "가입 완료" #post요청일시는 '/'주소로 이동. (회원가입 완료시 화면이동)
        except Exception as e:
            print("데이터베이스 저장 중 오류 발생: ",str(e))
            return "데이터베이스 저장 오류" +str(e)
    else:
        print("폼 유효성 검사 실패: ",form.errors)
    return render_template('register.html', form=form)

@app.route("/board/")
def board():
    board = Board.query.all()
    return render_template("board.html",data=board)


@app.route("/board_detail/<int:board_id>/")
def board_detail(board_id):
    board = Board.query.get(board_id)
    print(board.board_id)
    return render_template("board_detail.html", data=board)


if __name__ == "__main__":
    basedir = os.path.abspath(os.path.dirname(__file__)) #db파일을 절대경로로 생성
    dbfile = os.path.join(basedir, 'db.sqlite')#db파일을 절대경로로 생성

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + dbfile   
#sqlite를 사용함. (만약 mysql을 사용한다면, id password 등... 더 필요한게많다.)
    app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True 
#사용자 요청의 끝마다 커밋(데이터베이스에 저장,수정,삭제등의 동작을 쌓아놨던 것들의 실행명령)을 한다.
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 
#수정사항에 대한 track을 하지 않는다. True로 한다면 warning 메시지유발
    app.config['SECRET_KEY'] = 'wcsfeufhwiquehfdx'
    app.config['SESSION_PERMANENT'] = False
    csrf = CSRFProtect()
    csrf.init_app(app)

    db.init_app(app)
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=8001)
