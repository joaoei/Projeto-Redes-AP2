# -*- coding: utf-8 -*-
import socket
import json
import datetime

#           Firewall
#              ^|
#              |v            
# cliente -> proxy -> servidor

HOST = '10.0.4.2'              # Server IP
PORT = 11002     		        # Server Port
SIZE = 1024            			# Buffer size

tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
orig = (HOST, PORT)
tcp.bind(orig)
tcp.listen(5)

print 'Server running on port ', PORT, '\n'

reqs_count = 0
while True:
    con, client = tcp.accept()
    print '>>> Connection established with ', client

    while True:
        msg = con.recv(SIZE)
        if not msg: break

        reqs_count += 1
        json_data = json.loads(msg)
        print client, json_data
        service = json_data["service"]

        if service == "time":
        	curr_date = datetime.datetime.now().strftime("%H:%M %d-%m-%Y")
        	json_response = {
        		"type" : "response",
        		"service" : "time",
        		"body" : curr_date
        	}
        	con.send(json.dumps(json_response))
        elif service == "server-reqs":
        	json_response = {
        		"type" : "response",
        		"service" : "time",
        		"body" : str(reqs_count)
        	}
        	con.send(json.dumps(json_response))
    	else:
    		json_response = {
        		"type" : "response",
        		"service" : "",
        		"body" : "Request not supported!"
        	}
        	con.send(json.dumps(json_response))

    print '>>> Closing connection with client ', client
    con.close()
