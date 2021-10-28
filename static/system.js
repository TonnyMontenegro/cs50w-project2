var socket = io();

document.addEventListener('DOMContentLoaded', function() {

    socket.on('connect', ()=>{
        socket.emit('Joined');
    })

});

function NewChannelFunc() {
    const ChannelName = document.querySelector('#NewChannelName').value;
    socket.emit('NewChannel', {'NewChannelName': ChannelName});
}

function OpenModalChannel() {
    $('#ChannelModal').modal('show');
}

function CloseModalChannel() {
    $('#ChannelModal').modal('hide');
    $('body').removeClass('modal-open');
    $('.modal-backdrop').remove();
     $("#NewChannelName").val("");
}


function Print(Text, Class){
    let Chat = document.querySelector("#ChatArea");
    let Element = document.createElement("li");
    Element.innerHTML = Text;
    Chat.appendChild(Element)
    Chat.classList.add(Class);
}

socket.on('AddChannel', function (data) {
    let div= document.getElementById("ChannelList");
    div.innerHTML += '<a class="dropdown-item text-light" href="#">'+data.Channel  +'</a>'
    CloseModalChannel();
    Print('Añadiste un nuevo canal','Messages-bot')
});

socket.on('DataUser', function(data){
    localStorage.setItem('Channel', data.channel)
    Print(bot,'Messages-bot')
});
