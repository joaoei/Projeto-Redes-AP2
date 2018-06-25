#!/usr/bin/python

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Node
from mininet.log import setLogLevel, info
from mininet.cli import CLI

class LinuxRouter( Node ):
    "A Node with IP forwarding enabled."

    def config( self, **params ):
        super( LinuxRouter, self).config( **params )
        # Enable forwarding on the router
        self.cmd( 'sysctl net.ipv4.ip_forward=1' )

    def terminate( self ):
        self.cmd( 'sysctl net.ipv4.ip_forward=0' )
        super( LinuxRouter, self ).terminate()


class NetworkTopo( Topo ):
    "A LinuxRouter connecting three IP subnets"

    def build( self, **_opts ):

        defaultIP = '10.0.1.1/24'  # IP address for r0-eth1
        router = self.addNode( 'r0', cls=LinuxRouter, ip=defaultIP )

        #FIREWALL
        firewall = self.addHost( 'firewall', ip='10.0.1.2/24', defaultRoute='via 10.0.1.1' )
        #PROXY
        proxy = self.addHost( 'proxy', ip='10.0.2.2/24', defaultRoute='via 10.0.2.1' )
        
        cliente1 = self.addHost( 'cliente1', ip='10.0.3.2/24', defaultRoute='via 10.0.3.1' )
        cliente2 = self.addHost( 'cliente2', ip='10.0.3.3/24', defaultRoute='via 10.0.3.1' )

        servidor1 = self.addHost( 'servidor1', ip='10.0.4.2/24', defaultRoute='via 10.0.4.1' )
        servidor2 = self.addHost( 'servidor2', ip='10.0.4.3/24', defaultRoute='via 10.0.4.1' )

        #FIREWALL
        s1 = self.addSwitch('s1')
        #PROXY
        s2 = self.addSwitch('s2')
        #CLIENTES
        s3 = self.addSwitch('s3')
        #SERVIDORES
        s4 = self.addSwitch('s4')


        #Linkando os dois switches, firewall e proxy ao roteador
        self.addLink( s1, router, intfName2='r0-eth1', params2={ 'ip' : '10.0.1.1/24' } )
        self.addLink( s2, router, intfName2='r0-eth2', params2={ 'ip' : '10.0.2.1/24' } )
        self.addLink( s3, router, intfName2='r0-eth3', params2={ 'ip' : '10.0.3.1/24' } )
        self.addLink( s4, router, intfName2='r0-eth4', params2={ 'ip' : '10.0.4.1/24' } )

        #Linkando host firewall ao switch
        self.addLink(firewall, s1)

        #Linkando host proxy ao switch
        self.addLink(proxy, s2)

        #Linkando hosts clientes ao switch
        self.addLink(cliente1, s3)
        self.addLink(cliente2, s3)

        #Linkando hosts servidores ao switch
        self.addLink(servidor1, s4)
        self.addLink(servidor2, s4)

        #Linkando clientes a proxy
        self.addLink(s3, s2)
        #Linkando servidores a firewall
        self.addLink(s1, s4)



def run():
    "Test linux router"
    topo = NetworkTopo()
    net = Mininet( topo=topo ) 
    net.start()
    info( '*** Routing Table on Router:\n' )
    print net[ 'r0' ].cmd( 'route' )
    CLI( net )
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    run()