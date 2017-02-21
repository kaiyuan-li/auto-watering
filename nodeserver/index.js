var net = require('net')

client = new net.Socket();
client.connect(12345,'192.168.1.114',function(){
console.log('connected');
client.write('CHM');
});

client.on('data',function(data){
console.log('Received: '+data);
client.destroy();
});
