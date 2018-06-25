#!/usr/bin/python

"""
This example creates a multi-controller network from semi-scratch by
using the net.add*() API and manually starting the switches and controllers.

This is the "mid-level" API, which is an alternative to the "high-level"
Topo() API which supports parametrized topology classes.

Note that one could also create a custom switch class and pass it into
the Mininet() constructor.
"""


from mininet.net import Mininet
from mininet.node import Controller, OVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info

def multiControllerNet():
    "Create a network from semi-scratch with multiple controllers."

    net = Mininet( controller=Controller, switch=OVSSwitch )

    info( "*** Creating (reference) controllers\n" )
    c1 = net.addController( 'c1', port=6633 )
    c2 = net.addController( 'c2', port=6634 )
    c3 = net.addController( 'c3', port=6635 )
    c4 = net.addController( 'c4', port=6636 )

    info( "*** Creating switches\n" )
    s_clientes = net.addSwitch( 's1' )
    s_proxy = net.addSwitch( 's2' )
    s_servidores = net.addSwitch( 's3' )
    s_firewall = net.addSwitch( 's4' )
#    s_centro = net.addSwitch( 's5' )

    info( "*** Creating hosts\n" )
    clientes = [ net.addHost('cliente'), net.addHost('cliente2') ]
    proxy = [ net.addHost('proxy') ]
    servidores = [ net.addHost('servidor'), net.addHost('servidor2') ]
    firewall = [ net.addHost('firewall') ]


    info( "*** Creating links\n" )
    for h in clientes:
        net.addLink( s_clientes, h )
    for h in proxy:
        net.addLink( s_proxy, h )
    for h in servidores:
        net.addLink( s_servidores, h )
    for h in firewall:
        net.addLink( s_firewall, h )

    net.addLink( s_clientes, s_proxy )
    net.addLink( s_servidores, s_firewall )
#    net.addLink( s_firewall )
    net.addLink( s_proxy, s_servidores )
#    net.addLink( s_proxy, s_firewall )
#    net.addLink( s_clientes, s_servidores )

    info( "*** Starting network\n" )
    net.build()
    c1.start()
    c2.start()
    c3.start()
    c4.start()

#    s_centro.start( [ c3 ] )
    s_servidores.start( [ c3 ] )
    s_firewall.start( [ c3 ] )
    s_proxy.start( [ c2 ] )
    s_clientes.start( [ c1 ] )

    info( "*** Testing network\n" )
    net.pingAll()

    info( "*** Running CLI\n" )
    CLI( net )

    info( "*** Stopping network\n" )
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )  # for CLI output
    multiControllerNet()