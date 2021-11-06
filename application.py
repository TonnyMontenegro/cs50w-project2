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
from flask_socketio import SocketIO, emit, join_room, leave_room, send

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
socketio = SocketIO(app, cors_allowed_origins='*', manage_session=False)

'''Python Storage'''
Users=[]
ChannelList=[]
Messages= dict()
limite = 10

#inicio de sesion requerido y proteccion de vistas
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("username") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

#ruta pre definida que carga la pantalla de create y opcionalmente carga un boton que te dirije al ultimo canal usado
@app.route("/")
@login_required
def index():
    session['open_channel'] = 'NoNe_CHannEL'
    Lastchannel=session['last_channel']
    return render_template("create.html", ChannelList= ChannelList, Lastchannel = Lastchannel)

#pantalla de login
@app.route("/login", methods=['GET','POST'])
def login():
    session.clear()
    session['last_channel']= 'NoNe_CHannEL'
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

#pantalla de logout
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

#ruta pre definida que carga la pantalla de create y opcionalmente carga un boton que te dirije al ultimo canal usado
@app.route("/create", methods=['GET','POST'])
@login_required
def create_channel():
    ListaCanales=ChannelList
    Lastchannel=session['last_channel']
    print("hello")
    session['open_channel'] = 'NoNe_CHannEL'
    print(ChannelList)
    return render_template("create.html", ChannelList=ListaCanales, Lastchannel = Lastchannel)

#pagina personalizada de error 404
@app.errorhandler(404)
def not_found(e):
  return render_template("404.html")

#ruta de cada canal
@app.route("/channel/<channel>", methods=['GET','POST'])
@login_required
def ChannelChat(channel):
    user = session['username']
    session['open_channel']=channel
    session['last_channel']=channel
    if channel not in ChannelList:
        flash("Lo sentimos ese servidor aun no existe, prueba a crearlo")
        return redirect("/create")
    else:
        if request.method == "POST":
            return redirect("/channel/" + channel)
        else:
            return render_template("channel.html",user=user,users=Users,ChannelList=ChannelList,messages=Messages[channel],channel=session['open_channel'])

@socketio.on('NewChannel')
def New_channel(data):
    print("hello")
    ChannelName = data['NewChannelName']
    user= session['username']
    if ChannelName in ChannelList:
        emit('Error', {'error': 'El canal ya se encuentra en la lista de canales'})
    else:
        if len(ChannelName) == 0:
            emit('Error', {'error': 'El canal no puede estar en blanco'})
        else:
            ChannelList.append(ChannelName)
            Messages[ChannelName] = deque(maxlen=100)
            emit('AddChannel', {'Channel': ChannelName, 'user': user, 'channels': ChannelList}, broadcast=True)

@socketio.on('Joined')
def Joined(data):
    print("Joined")
    user = session['username']
    channel=session['open_channel']
    if (session['open_channel'] != 'NoNe_CHannEL'):
        print('te has unido a '+ channel)
        join_room(channel)
        emit('JoinNow', {'open_channel': channel}, to = channel)
        emit('GlobalMsg', {'message': 'un '+ user +' salvaje ha aparecido!!'},to=channel)
        print("Joined end")

# @socketio.on('Leaved')
# def Leaved(data):
#     print("leaved")
#     user = session['username']
#     channel=session['open_channel']
#     emit('GlobalMsg', {'message': user +' hizo despawn del servidor'},to=channel)
#     leave_room(channel)
#     print('te has salido de '+ channel)


@socketio.on('NewMessage')
def NewMessage(data):
    Channel = session['open_channel']
    username = session['username']
    time = data['time']
    msg = data['msg']
    Messages[Channel].append([time ,username,msg])
    # if(len(Messages[Channel]) > limite):
    #     Messages[Channel].pop(10)
    print(Channel)
    emit('AddMsg',{'user': username, 'time':time, 'msg':msg }, to = Channel)
    print("NewMessage End")
if __name__ == "__main__":
    socketio.run(app)