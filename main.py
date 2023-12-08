from flask import Flask, render_template
from flask_socketio import SocketIO
from datetime import datetime
from dateutil.parser import parse, ParserError
from json import loads, JSONDecodeError

from os import environ

environ["TZ"] = "Europe/London"

app = Flask(__name__, static_folder="static", template_folder="templates")
socketio = SocketIO(app)

dates = []


def __updateDates():
    global dates
    try:
        dates = [parse(x, dayfirst=True) for x in loads(open("dates.json", "r").read())]
    except (JSONDecodeError, ParserError, OverflowError):
        dates = []


def __GetTimeLeft():
    current = datetime.now()
    datesFiltered = [x for x in dates if x >= current]

    if len(datesFiltered) == 0:
        return "No dates left"

    target = min(datesFiltered)

    return str(target - current).split(".")[0]


@app.route("/")
def root():
    return render_template("root.jinja")


@socketio.on("connect")
def connect():
    socketio.emit("time", __GetTimeLeft())


def emitTask():
    while True:
        socketio.emit("time", __GetTimeLeft())
        socketio.sleep(1)


def updateTask():
    while True:
        __updateDates()
        socketio.sleep(300)


if __name__ == "__main__":
    socketio.start_background_task(target=emitTask)
    socketio.start_background_task(target=updateTask)

    socketio.run(app, "0.0.0.0", 5444, debug=True, allow_unsafe_werkzeug=True)
