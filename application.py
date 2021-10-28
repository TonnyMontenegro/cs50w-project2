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
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
socketio = SocketIO(app, cors_allowed_origins='*')



'''Local Storage'''
Users=[]
Channels=[]
Messages= dict()
Channels.append('General')
Messages['General']=deque()

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
    return render_template("index.html")

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
            session['username']=username
            session.permanet=True
            session["Auth"]= True
            socketio.emit('Join_true')
            return redirect("/channels/General")

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

@app.route("/channels/<channel>", methods=['GET','POST'])
@login_required
def channels_list(channel):
    user = session['username']
    session['open_channel']=channel

    if channel not in Channels:
        return redirect("/channels/General")
    else:
        if request.method == "POST":
            return redirect("/")
        else:
            return render_template("channels.html",user=user,users=Users,channels=Channels,messages=Messages[channel],channel=session['open_channel'])


@socketio.on('NewChannel')
def New_channel(data):
    ChannelName = data['NewChannelName']
    if ChannelName in Channels:
        emit('Error', {'error': 'El canal ya se encuentra en la lista de canales'})
    else:
        if len(ChannelName) == 0:
            emit('Error', {'error': 'El canal no puede estar en blanco'})
        else:
            Channels.append(ChannelName)
            Messages[ChannelName] = []
            emit('AddChannel', {'Channel': ChannelName}, broadcast=True)

@socketio.on('Join')
def Join_message(data):
    Username = data['Username']
    Channel = session['open_channel']
    join_room(Channel)
    emit('DataUser', {'user': Username, 'channel': Channel,'bot': '!: un(@)' + Username + ' salvaje ha aparecido'}, room=Channel)

