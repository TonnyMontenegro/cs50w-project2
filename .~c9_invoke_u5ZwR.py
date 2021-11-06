import os

'''
Deque (Doubly Ended Queue) in Python is implemented using the module "collections".
Deque is preferred over list in the cases where we need quicker append and pop operations
from both the ends of container, as deque provides an O(1) time complexity for append and
pop operations as compared to list which provides O(n) time complexity.
'''
from collections import deque

'''
functools is a standard Python module for higher-order functions
(functions that act on or return other functions). wraps() is a decorator
that is applied to the wrapper function of a decorator. It updates the
wrapper function to look like wrapped function by copying attributes such
as __name__, __doc__ (the docstring), etc.
'''
from functools import wraps

from flask import Flask, render_template, request, session, redirect, flash, url_for
from flask_socketio import SocketIO, emit,join_room, leave_room, send

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
socketio = SocketIO(app, cors_allowed_origins='*')

'''Python Storage'''
Users=[]
Channels=[]
Messages= dict()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("username") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

@app.route("/")
@login_required
def index():
    return render_template("channels.html")

@app.route("/login", methods=['GET','POST'])
def login():
    session.clear()
    username = request.form.get("username")

    if request.method == "GET":
        return render_template("login.html")
    else:
        if( len(username) < 3 or username == ''):
            flash("Error, Nombre de usuario no valido,verifique su usuario")
            return render_template("login.html")
        else:
            Users.append(username)
            session['username']= username
            session.permanet=True
            session["Auth"]= True
            return redirect("/create")


@app.route("/logout", methods=['GET','POST'])
@login_required
def logout():
    # se limpia la sesion del usuario
    try:
        Users.remove(session['username'])
        session.clear()
    except:
        session.clear()
    # se le notifica al usuario y se le redirije a la pagina de inicio de sesion
    flash("Sesion cerrada")
    return render_template("login.html")

@app.route("/create", methods=['GET','POST'])
@login_required
def create_channel():
    ListaCanales=Channels
    return render_template("create.html", canales=ListaCanales)

@app.errorhandler(404)
def not_found(e):
  return render_template("404.html")


@app.route("/channel/<channel>", methods=['GET','POST'])
@login_required
def ChannelChat(channel):
    user = session['username']
    session['open_channel']=channel
    if channel not in Channels:
        flash("Lo sentimos ese servidor aun no existe, prueba a crearlo")
        return redirect("/channels")
    else:
        if request.method == "POST":
            return redirect("/channel/" + channel)
        else:
            return render_template("channel.html",user=user,users=Users,channels=Channels,messages=Messages[channel],channel=session['open_channel'])

@socketio.on('NewChannel')
def New_channel(data):
    ChannelName = data['NewChannelName']
    user= session['username']
    if ChannelName in Channels:
        emit('Error', {'error': 'El canal ya se encuentra en la lista de canales'})
    else:
        if len(ChannelName) == 0:
            emit('Error', {'error': 'El canal no puede estar en blanco'})
        else:
            Channels.append(ChannelName)
            Messages[ChannelName] = []
            emit('AddChannel', {'Channel': ChannelName, 'user': user}, broadcast=True)

@socketio.on('Joined')
def Joined(data):
    user = session['username']
    channel= data.channel
    join_room(channel)
    emit('JoinNow', {'open_channel': channel},to=channel)
    emit('GlobalMsg', {'message': 'un@ '+ user +' salvaje ha aparecido!!'},broadcast=True,to=channel)

@socketio.on('connect')
def test_connect():
    send('conectionOn')

if __name__ == '__main__':
    socketio.run(app)