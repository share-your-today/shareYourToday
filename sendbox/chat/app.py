# 필수 라이브러리
'''
0. Flask : 웹서버를 시작할 수 있는 기능. app이라는 이름으로 플라스크를 시작한다
1. render_template : html파일을 가져와서 보여준다
'''
from flask import Flask, render_template, request, redirect, url_for
from flask_socketio import SocketIO
import os
from flask_sqlalchemy import SQLAlchemy


basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
socketio = SocketIO(app,logger=True, engineio_logger=True)

@app.route("/")
def home():
    return render_template('index.html')

# connected_client = {}

@app.route("/chat", methods =["GET", "POST"])
def chat():
    print('-----------client connected------------')
    # name = session.get('name',)
    # id = session.get('id',)
    # if name == None or id == None: # 잘못된 접근일 때
    #     return redirect(url_for('index.html'))
    # context={
    #     'name' : name,
    #     'id' : id
    # }
    # return render_template('chat.html',data = context)
    return render_template('chat.html')

@socketio.on('joined')
def joined():
    # name = session['name']
    # id = session['id']
    # context = {
    #     'msg' : f"{name} + '(' + {id}+ ')'님이 입장했습니다.",
    #     'status' : 'joined'
    # }
    # socketio.emit('joined', context)
    print("------------Server received------------")
    msg = "아무개 님이 입장했습니다"
    socketio.emit('joined', data = msg)
    
@socketio.on('left')
def left():
    # name = session['name']
    # id = session['id']
    # user = f"{name} + '(' + {id}+ ')'"
    # context = {
    #     'msg' : f"{user} 님이 퇴장했습니다.",
    #     'status' : 'left'
    # }
    # socketio.emit('left', context)
    msg = "아무개 님이 입장했습니다"
    socketio.emit('left', data = msg)

@socketio.on('send_msg')
def send_msg(msg):
    # name = session['name']
    # id = session['id']
    # user = f"{name} + '(' + {id} + ')'"
    # msg = ""
    # context = {
    #     'msg' : f"{user} : {msg}",
    #     'status' : 'send_msg'
    # }
    # socketio.emit('send_msg', context)
    send_msg = ">>" + msg
    socketio.emit('send_msg', data = send_msg)

if __name__ == "__main__":
    socketio.run(app, debug=True, port=5000)