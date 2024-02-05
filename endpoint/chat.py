from flask import session, Blueprint, render_template, request, flash, url_for, jsonify
from datetime import datetime, timezone, timedelta
from models import db, Message
from exception import db_commit_error_handler

bp = Blueprint("chat", __name__, url_prefix="/chat")

@bp.route("/")
def chat():
    name = session.get("name", None)
    return render_template("chat.html")


# 채팅 메시지를 받는 라우트
@bp.route("/send", methods=["POST"])
@db_commit_error_handler
def send():
    user_id = session.get("user_id", None)
    message = request.form.get("message")

    utc_now = datetime.utcnow()
    kst = timezone(timedelta(hours=9))
    kst_now = utc_now.replace(tzinfo=timezone.utc).astimezone(kst)
    timestamp = kst_now

    new_message = Message(message=message, timestamp=timestamp, user_id=user_id)
    db.session.add(new_message)
    db.session.commit()

    return jsonify(
        {
            "message": message,
            "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "user_id": user_id,
        }
    )


# 채팅 메시지를 받아오는 폴링 라우트
@bp.route("/get_messages")
def get_messages():
    client_timestamp_str = request.args.get("timestamp", "2000-01-01 00:00:00")
    client_timestamp = datetime.strptime(client_timestamp_str, "%Y-%m-%d %H:%M:%S")

    utc_now = datetime.utcnow()
    kst = timezone(timedelta(hours=9))
    latest_timestamp = utc_now.replace(tzinfo=timezone.utc).astimezone(kst)

    new_messages = Message.query.filter(Message.timestamp > client_timestamp).all()

    messages = [
        {
            "message": msg.message,
            "timestamp": msg.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "user_id": msg.user_id,
        }
        for msg in new_messages
    ]

    return jsonify(
        {
            "messages": messages,
            "latest_timestamp": latest_timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        }
    )
