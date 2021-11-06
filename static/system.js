document.addEventListener('DOMContentLoaded', () => {

var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

socket.on('AddChannel', function (data){
    let div= document.getElementById("ChannelList");
    div.innerHTML += '<a class="dropdown-item text-light ChannelLink"  href="/channel/'+ data.Channel  +'">'+data.Channel  +'</a>';
    document.getElementById('NewChannelName').value = '';
    localStorage.setItem('channels', data.channels);
    Print(data.user + ' ha añadido un nuevo canal');
});

socket.on('DataUser', function(data){
    localStorage.setItem('Channel', data.channel);
    Print(bot);
});

socket.on('JoinNow', function (data){
    console.log('joinnow');
    localStorage.setItem('open_channel', data.open_channel);
    console.log('joinnow end');
});

socket.on('GlobalMsg',function(data) {
    Print(data.message);
});

socket.on('Error', function(data){
    alert(data.error);
});

socket.on('muu', function(data){
    alert(data.msg);
    console.log(data.msg);
});

socket.on('AddMsg', function(data){
    PrintMSG(data.msg, data.time, data.user);
});

const BTNsend = document.querySelector('#SendBTN');
if(BTNsend != null){
    BTNsend.addEventListener('click', function(event){
    let timestamp = new Date;
    var h = new Date(timestamp).getHours();
    var m = new Date(timestamp).getMinutes();
    var times = h+ ':' + m;
    console.log(times);
    // const MSG = document.querySelector('#MSGbox').value;
    const MSG = document.querySelector('.emojionearea-editor').innerHTML;
    socket.emit('NewMessage', {'msg': MSG,'time': times});
    console.log(MSG);
    // document.querySelector('#MSGbox').value = '_';
    document.querySelector('.emojionearea-editor').innerHTML = '';
    console.log('emitido: NewChannel');
});
}

const BTNcc = document.querySelector('#CreateChannelBTN');
if(BTNcc != null){
    BTNcc.addEventListener('click', function(event){
    const ChannelName = document.querySelector('#NewChannelName').value;
    socket.emit('NewChannel', {'NewChannelName': ChannelName});
    console.log('emitido: NewChannel');
});
}
var channel;
const BTNcl = document.querySelector('.ChannelLink');
if(BTNcl != null){
    BTNcl.addEventListener('click', function(event){
        console.log(BTNcl.innerHTML);
        channel = BTNcl.innerHTML;
        console.log('emit: Joined');
    });
}
setTimeout(function () {
        console.log(channel);
        socket.emit('Joined', {'channel': channel});
        socket.emit('ChannelsList', {'channels': localStorage.getItem('channels')})
}, 100);

// var channel_left;
// const BTNleft = document.querySelector('.ChannelLeftLink');
// if(BTNleft != null){
//     BTNleft.addEventListener('click', function(event){
//         console.log(BTNcl.innerHTML);
//         channel_left = BTNcl.innerHTML;
//         console.log('emit: left');
//     });
// }
// setTimeout(function () {
//     console.log(channel_left);
//     socket.emit('Joined', {'channel': channel});
// }, 100);

function Print(Text){
    let Chat = document.querySelector("#ChatArea");
    let Element = document.createElement("li");
    Element.innerHTML = Text;
    Chat.appendChild(Element);
    Element.classList.add('Messages-bot');
}

function PrintMSG(Text,Time,User,) {
    let Chat = document.querySelector("#ChatArea");
    if ( Chat != null){
        let Element = document.createElement("li");
        Element.innerHTML = '<small class="msg text-muted">'+Time+ '</small> <strong class="data-msg">' + User +':</strong> <small>' +Text+'</small>';
        Chat.appendChild(Element);
        Element.classList.add('text-light');
        Element.classList.add('msg-bubble');
    }
}

});
