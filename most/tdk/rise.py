from flask import Flask, render_template, request, session
from pathlib import Path
import os
from flask_socketio import SocketIO, emit
from flask_session import Session
from icecream import ic
from datetime import datetime
from random import random
from uuid import uuid4

app = Flask(
    __name__,
    template_folder="build",
    static_folder="build",
    root_path=Path(os.getcwd()) / "most",
)

app.config['SECRET_KEY'] = 'secret!'
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

flow = dict()

socketio = SocketIO(
    app,
    message_queue='amqp://justatom:fate@rabbitmq:5672',
    logger=True,
    engineio_logger=True,
    cors_allowed_origins="*",
    manage_session=False,
)


@app.route('/')
def index():
    return render_template('index.html')


def rock_n_roll():
    while True:
        socketio.emit('updateData', {'date': datetime.now().strftime("%H:%M:%S"), "value": round(random() * 100, 3)})
        socketio.sleep(1)


@socketio.on("message")
def message(data):
    ic(data)
    emit('updateData', {'date': datetime.now().strftime("%H:%M:%S"), "value": round(random() * 100, 3)})


@socketio.on("connect")
def connect():
    # TODO: Add new way to broadcast the messages back to the client(s)
    ic(session)
    thread, sid = socketio.start_background_task(rock_n_roll), str(uuid4())
    session["sid"] = sid
    flow[sid] = thread  # atomic operation => thread safe on builtin type(s)


@socketio.on('disconnect')
def disconnect():
    thread, sid = flow[session["sid"]], session["sid"]
    thread.join()
    del flow[session["sid"]]
    print(f'Client {sid} disconnected')


if __name__ == '__main__':
    socketio.run(app, debug=False, host="0.0.0.0", port=2222)
