from flask import Flask, render_template, request, redirect, url_for
import os

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
app = Flask(__name__)
# DB 연결 코드 만들어야 함

basedir = os.path.abspath(os.path.dirname(__file__))  # 지금 현재 위치
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] =\
        'sqlite:///' + os.path.join(basedir, 'database.db')

db = SQLAlchemy(app)
class Member(db.Model):
    user_id = db.Column(db.String(30), primary_key=True)
    pwd = db.Column(db.String(150), nullable=False)
    name = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f'Member(user_id={self.user_id}, name={self.name})'

class Board(db.Model):
    board_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(300), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_dttm = db.Column(db.DateTime, default=datetime.utcnow)
    updated_dttm = db.Column(db.DateTime, default=datetime.utcnow)
    image_url = db.Column(db.String(300), nullable = True)
    user_id = db.Column(db.String, db.ForeignKey('member.user_id'), nullable=False)
    member = db.relationship('Member', backref=db.backref('boards', lazy=True))

    def __repr__(self):
        return f'Board(title={self.title}, content={self.content}, user_id={self.user_id})'

class Board_Reply(db.Model):
    reply_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    content = db.Column(db.Text, nullable=False)
    created_dttm = db.Column(db.DateTime, default=datetime.utcnow)
    updated_dttm = db.Column(db.DateTime, default=datetime.utcnow)
    board_id = db.Column(db.Integer, db.ForeignKey('board.board_id'), nullable=False)
    board = db.relationship('Board', backref=db.backref('replies', lazy=True))
    user_id = db.Column(db.String, db.ForeignKey('member.user_id'), nullable=False)
    member = db.relationship('Member')

    def __repr__(self):
        return f'BoardReply(content={self.content}, board_id={self.board_id}, user_id={self.user_id})'

with app.app_context():
    db.create_all()

@app.route("/")
def home():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True, port=8001)
