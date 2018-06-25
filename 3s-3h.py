#!/usr/bin/python

from mininet.net import Mininet
from mininet.node import  OVSController, OVSKernelSwitch, RemoteController, Controller
from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.link import TCLink
import os

def topology():

    "Create a network."
    net = Mininet( controller=RemoteController, link=TCLink, switch=OVSKernelSwitch )
	
    _bw=50
    _latency='5ms'
    _max_queue_size=200
    _use_htb=True
    _ip_remote_control='127.0.0.1'
    _port_remote_control=6653

    adp_USB100MB_MAC = "00:13:3B:85:05:05"

    print "*** Creating Hosts"
    h1 = net.addHost( 'h1', mac="10:60:4b:ea:b9:01", ip='192.168.0.1' )
    h2 = net.addHost( 'h2', mac="c8:cb:b8:c3:fc:3e", ip='192.168.0.2' )
    h3 = net.addHost( 'h3', mac="00:22:19:fd:65:77", ip='192.168.0.3' )

    print "*** Creating Switchs"
    s1 = net.addSwitch( 's1', dpid='00:00:00:00:aa:bb:cc:35' )
    s2 = net.addSwitch( 's2', dpid='00:00:00:00:aa:bb:cc:32' )
    s3 = net.addSwitch( 's3', dpid='00:00:00:00:aa:bb:cc:15' )
    
    print "*** Creating Controller Openflow"
    c0 = Controller( 'c0', port=_port_remote_control )

    print "*** Connecting hosts"
    net.addLink(h1, s1)
    net.addLink(h2, s2)
    net.addLink(h3, s3)

    print "*** Creating connection between switches"
    net.addLink(s1, s2)
    net.addLink(s2, s3)
    
    print "*** Starting network"
    net.build()
    c0.start()
    s1.start( [c0] )
    s2.start( [c0] )
    s3.start( [c0] )
    os.system('sudo ovs-vsctl set Bridge s1 protocols=OpenFlow13')
    os.system('sudo ovs-vsctl set Bridge s2 protocols=OpenFlow13')
    os.system('sudo ovs-vsctl set Bridge s3 protocols=OpenFlow13')

    print "*** Running CLI"
    CLI( net )

    print "*** Stopping network"
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    topology()


