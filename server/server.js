#! /usr/bin/env nodejs
var http = require('http');
var express = require('express');
var app = express();
var toobusy = require('toobusy-js');
var port = process.env.PORT || 3000;
var server = require('http').createServer(app);
var io = require('socket.io')(server);
var yargs = require('yargs')

toobusy.onLag(function(currentlag){
	console.log(" Event loop lag detected! Latency: "+ currentlag);
});

app.use(function(req, res, next){
	if(toobusy()) {
		res.send(503, "servidor esta sobrecarregado");
	} else {
		next();
	}
});

app.get('/', function(req,res) {
	res.send('requisicao via http aceita! Host: ' + yargs.argv.url);
});

io.on('connection', function(socket){
	socket.emit('helloprotocol',{ msg: 'requisicao via socket aceita' } );
});

server.listen(port);

process.on('SIGINT', function() {
	server.close();
	toobusy.shutdown();
	process.exit();
});
