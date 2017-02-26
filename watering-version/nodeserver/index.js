var net = require('net');
var app = require('express')();
var http = require('http').Server(app);
var io = require('socket.io')(http);


client = new net.Socket();
client.connect(12345,'192.168.1.114',function(){
console.log('connected');

});

client.on('data',function(data){
console.log('Received: ' + data);
client.destroy();
});


app.get('/', function(req, res){
  res.sendFile(__dirname + '/index.html');
});

io.on('connection', function(socket){
  console.log('a user connected');
  socket.on('water', function(msg){
    client.write('WATER');
  });


  socket.on('disconnect', function(){
    console.log('user disconnected');
  });
});

http.listen(3000, function(){
  console.log('listening on *:3000');
});
