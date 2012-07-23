var app = require('express').createServer();

app.get('/', function(req, res){
  res.send('hello world');
});

app.listen(3000);

var ldap = require('ldapjs');

var server = ldap.createServer();

server.listen(1389, function() {
  console.log('/etc/passwd LDAP server up at: %s', server.url);
});
