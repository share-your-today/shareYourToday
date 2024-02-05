from flask import session, Blueprint, redirect, render_template, request, flash, url_for
from forms import LoginForm, RegisterForm
from models import db, Member

bp = Blueprint("users", __name__, url_prefix="/users")


@bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    fail_count = 0
    user_id = ""
    if form.validate_on_submit():
        user = Member.query.filter_by(user_id=form.user_id.data).first()
        if user:
            # 로그인 성공 처리
            user.fail_count = 0
            db.session.commit()
            session["user_id"] = user.user_id
            session["name"] = user.name
            return redirect("/board")
    else:
        # 로그인 실패시 해당 유저가 있는지 확인
        user = Member.query.filter_by(user_id=form.user_id.data).first()
        if user:
            user_id = user.user_id
            user.fail_count += 1
            fail_count = user.fail_count
            db.session.commit()
            if user.fail_count >= 5:
                if form.validate_on_submit():
                    return render_template(
                        "login.html", form=form, fail_count=fail_count, user_id=user_id
                    )
    return render_template(
        "login.html", form=form, fail_count=fail_count, user_id=user_id
    )


@bp.route("/logout", methods=["GET"])
def logout():
    session.clear()
    return redirect("/login")


@bp.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if request.method == "POST" and form.validate():
        user_id = form.user_id.data
        name = form.name.data
        pwd = form.pwd.data

        if Member.query.filter_by(user_id=user_id).first() is not None:
            flash("이미 존재하는 사용자 아이디입니다.")
            return redirect(url_for("register"))

        try:
            member = Member(user_id=user_id, name=name, pwd=pwd)
            db.session.add(member)
            db.session.commit()
            flash("회원가입이 성공했습니다! ")

            # 자동 로그인을 위한 세션 설정
            session["user_id"] = user_id
            session["name"] = name

            return redirect(url_for("board"))
        except Exception as e:
            db.session.rollback()
            flash("데이터베이스 저장 중 오류가 발생했습니다.")
            # app.logger.error("Error on registration: %s", str(e)) #TODO: app-logger 옮기기
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(error)
    return render_template("register.html", form=form)


@bp.route("/find_pw/<user_id>")
def find_pw(user_id):
    user = Member.query.filter_by(user_id=user_id).first()
    pwd = user.pwd
    user.fail_count = 0
    db.session.commit()
    return render_template("find_pw.html", user_id=user_id, pwd=pwd)
