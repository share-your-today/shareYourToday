from flask import session, Blueprint, redirect, render_template, request, flash, url_for
from forms import BoardForm
from models import db, Board, Board_Reply
from datetime import datetime

bp = Blueprint("board", __name__, url_prefix="/board")


@bp.route("/")
def board():
    name = session.get("name", None)
    user_id = session.get("user_id", None)
    form = BoardForm()  # BoardForm 객체를 생성합니다.

    board = Board.query.order_by(Board.created_dttm.desc()).all()
    return render_template(
        "board.html", data=board, name=name, user_id=user_id, form=form
    )


@bp.route("/board_detail/<int:board_id>/")
def board_detail(board_id):
    name = session.get("name", None)
    user_id = session.get("user_id", None)
    board = Board.query.get(board_id)
    reply = Board_Reply.query.filter_by(board_id=board_id).all()
    data = {"board": board, "reply": reply}
    return render_template("board_detail.html", data=data, name=name, user_id=user_id)


@bp.route("/board_create", methods=["POST"])
def board_create():
    user_id = session.get("user_id", None)
    form = BoardForm()

    is_open = False

    if form.validate_on_submit():
        board = Board(
            title=form.title.data,
            content=form.content.data,
            image_url=form.image_url.data,
            user_id=user_id,
        )
        try:
            db.session.add(board)
            db.session.commit()
            print(f"정상 commit 후 formdata {form.title.data}")
            # return render_template("board.html", data=boards, form=form)
            return redirect(url_for("board.board"))
        except:
            flash("데이터베이스 저장 중 오류가 발생했습니다.")
    else:
        is_open = True  # 모달 새로열기
        boards = Board.query.all()  # 데이터베이스에서 게시물 목록을 가져옴
        # 1차시기
        # form.data["title"] = ""
        # form.data["image_url"] = ""
        # form.data["content"] = ""

        # 2차 시기
        # form = BoardForm(formdata=None)
        return redirect(url_for("board.board"))
        # return render_template("board.html", data=boards, form=form)


@bp.route("/board_update/<int:board_id>/", methods=["POST"])
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


@bp.route("/board_delete/<int:board_id>/", methods=["POST"])
def board_delete(board_id):
    board = Board.query.get(board_id)
    db.session.delete(board)
    db.session.commit()

    return redirect(url_for("board"))


@bp.route("/user_posts/<user_id>/")
def user_posts(user_id):
    form = BoardForm() 
    name = session.get("name", None)

    if user_id:
        user_posts = (
            Board.query.filter_by(user_id=user_id)
            .order_by(Board.created_dttm.desc())
            .all()
        )
        return render_template(
            "board.html", data=user_posts, user_id=user_id, name=name, form=form
        )
    else:
        return render_template("error.html", message="유저 아이디가 유효하지 않습니다.")


# 댓글 추가,수정,삭제
@bp.route("/add_reply/<int:board_id>/", methods=["GET", "POST"])
def add_reply(board_id):
    user_id = session.get("user_id", "")
    if user_id == "":
        return render_template("login.html")

    text = request.form.get("reply_text")

    if text == None:
        return redirect(url_for("board.board_detail", board_id=board_id))

    elif text != "":
        board_reply = Board_Reply(content=text, board_id=board_id, user_id=user_id)

        db.session.add(board_reply)
        db.session.commit()

        return redirect(url_for("board.board_detail", board_id=board_id))


# @handle_error("수정 실패했습니다. 어ㅓ쭊구")
@bp.route("/edit_reply/<int:board_id>/<int:reply_id>", methods=["GET", "POST"])
def edit_reply(reply_id, board_id):
    reply = Board_Reply.query.get_or_404(reply_id)
    msg = request.form.get("edited_reply")

    reply.content = msg
    reply.updated_dttm = datetime.utcnow()
    try:
        db.session.commit()
    except Exception as e:
        return
    return redirect(url_for("board.board_detail", board_id=board_id))


@bp.route("/del_reply/<int:board_id>/<int:reply_id>/", methods=["GET", "POST"])
def del_reply(reply_id, board_id):
    reply = Board_Reply.query.get_or_404(reply_id)
    db.session.delete(reply)
    db.session.commit()
    return redirect(url_for("board.board_detail", board_id=board_id))
