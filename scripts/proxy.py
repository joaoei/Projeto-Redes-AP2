# -*- coding: utf-8 -*-
import socket
from threading import Thread
import sys
import json
import urllib2

#           Firewall
#              ^|
#              |v            
# cliente -> proxy -> servidor

firewallConnection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Serve como um servidor para o proxy, mantém as conexões vindas dos clientes
class ClientListener:
	def __init__(self):
		self.ownIP = '10.0.2.2'
		self.ownPort = 11001
		self.serverIP = '10.0.4.2'
		self.serverPort = 11002
		self.firewallIP = '10.0.1.2'
		self.firewallPort = 11003
		self.size = 1024
		self.server = None
		self.listen = 10
		self.connectedClients = []

	def create_socket(self):
		try:
			print "Criando socket..."
			self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.server.bind((self.ownIP, self.ownPort))
			self.server.listen(self.listen)
		except socket.error, (value, message):
			print "Erro de socket: " + message
			sys.exit(1)

	def connect_to_firewall(self):
		firewallConnection.connect((self.firewallIP, self.firewallPort))

	def start_listening(self):
		self.create_socket()
		self.connect_to_firewall()

		while True:
			connection, address = self.server.accept()
			newConnection = ClientConnection(connection, address, self.serverIP, self.serverPort, self.size)
			newConnection.start()
			self.connectedClients.append(newConnection)

class ClientConnection(Thread):
	def __init__(self, connection, address, serverIP, serverPort, size):
		print "Cliente conectado: ", connection, " | endereço: ", address
		Thread.__init__(self)
		self.connection = connection
		self.address = address
		self.serverIP = serverIP
		self.serverPort = serverPort
		self.size = size

	def run(self):
		# Loop infinito até o cliente desconectar
		serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		serverSocket.connect((self.serverIP, self.serverPort))

		while True:
			# Recebe a mensagem do cliente
			clientMessage = self.connection.recv(self.size)

			if clientMessage:
				# Transmite a mensagem ao firewall
				firewallConnection.sendall(self.address[0])
				# Espera resposta do firewall
				message = firewallConnection.recv(self.size)

				# Se recusado pelo firewall, retorne mensagem de conexão negado para o usuário
				if message == "FORBIDDEN":
					json_response = {
							"type" : "response",
							"service" : "",
							"body" : "Access denied! Connections from your IP have been blocked by the firewall!"
						}
					self.connection.sendall(json.dumps(json_response))

				# Se não recusado, continue
				else:
					json_data = json.loads(clientMessage)
					service = json_data["service"]
					
					# Verifica o tipo em busca de uma requisição HTTP
					if service == "http":
						url = json_data["body"]
						contents = urllib2.urlopen(url).read()

						json_response = {
							"type" : "response",
							"service" : "http",
							"body" : contents
						}
						self.connection.sendall(json.dumps(json_response))
					else:
						# Repassa mensagem ao servidor
						serverSocket.sendall(clientMessage)

						# Recebe resposta do servidor e repassa ao usuario
						response = serverSocket.recv(self.size)
						self.connection.sendall(response)

			# Se não recebeu, cancela a conexão
			else:
				self.connection.close()
				break

if __name__ == "__main__":
	s = ClientListener()
	s.start_listening()
