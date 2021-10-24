import os

from flask import Flask, render_template,request
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
socketio = SocketIO(app)


'''Local Storage'''
Users={}
Chanels={}
Messages={}

@app.route("/")
def index():
    session= False
    return render_template("index.html")

@app.route("/main")
def main():
    session= True
    return render_template("main.html")
