from flask import Flask, render_template, request, redirect, url_for
import os

app = Flask(__name__)
# DB 연결 코드 만들어야 함

basedir = os.path.abspath(os.path.dirname(__file__))  # 지금 현재 위치
app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True, port=8001)
