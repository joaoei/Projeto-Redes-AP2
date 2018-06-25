# -*- coding: utf-8 -*-
import socket
from datetime import datetime
import sys

#           Firewall
#              ^|
#              |v            
# cliente -> proxy -> servidor

# Ips de exemplo que serão bloqueados pelo servidor por serem maliciosos
ip_block = ['10.0.3.3','178.234.24.15','178.234.24.3']

# horas de exemplo em que o servidor não pode ser acessado
horas_proibidas = [21, 23, 12]

# É um servidor que responde as requisições do proxy
class FirewallServer:
    def __init__(self):
        self.ownIP = '10.0.1.2'
        self.ownPort = 11003
        self.size = 1024
        self.server = None
        self.clientes_conectados = {}
        self.clientes_bloqueados = {}

    def create_socket(self):
        try:
            print "Criando socket..."
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.bind((self.ownIP, self.ownPort))
            self.server.listen(10)
        except socket.error, (value, message):
            print "Erro de socket: " + message
            sys.exit(1)

    def start_listening(self):
        self.create_socket();
        connection, address = self.server.accept()

        while True:
            # Recebe a mensagem do proxy
            clientIp = connection.recv(self.size)
            print "Ip do cliente: ", clientIp

            # Se recebeu
            if clientIp:
                now = datetime.now()
                hora_conexao = str(now).split(" ")[1]
                hora_atual = int(hora_conexao.split(":")[0])

                # Se não tiver se conectado antes, cria a entrada
                if clientIp not in self.clientes_conectados:
                    self.clientes_conectados[clientIp] = []
                    print "primeira conexão de ", clientIp
                self.clientes_conectados[clientIp].append(now)

                negado = False
                # Se for um ip bloqueado ou horas proibidas
                if (clientIp in ip_block) or (hora_atual in horas_proibidas):
                    negado = True

                # Se estiver bloqueado temporariamente a menos de 5 minutos
                if clientIp in self.clientes_bloqueados:
                    print "valor debug ", (now - self.clientes_bloqueados[clientIp]).total_seconds()
                    if (now - self.clientes_bloqueados[clientIp]).total_seconds() < 300:
                        negado = True
                    else:
                        # Se estiver bloqueado temporariamente a mais de 5 minutos, desbloqueia
                        del self.clientes_bloqueados[clientIp]

                # Se realizou 10 conexões nos últimos 5 segundos, bloqueia
                numConnecs = 0
                for timestamp in self.clientes_conectados[clientIp]:
                    if ((now - timestamp).total_seconds() < 5):
                        numConnecs += 1
                        if (numConnecs >= 10):
                            break
                if (numConnecs >= 10):
                    print "blockeado"
                    self.clientes_bloqueados[clientIp] = now
                    negado = True

                # Resposta ao proxy
                msg = ""
                if (negado):
                    msg = "FORBIDDEN"
                else:
                    msg = "ALLOWED"
                
                connection.sendall(msg.encode())

            # Se não recebeu cancela a conexão
            else:
                connection.close()
                break

if __name__ == "__main__":
    fw = FirewallServer()
    fw.start_listening()