from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import OVSKernelSwitch, RemoteController
from mininet.link import TCLink
from mininet.log import setLogLevel
from datetime import datetime
from random import randrange, choice
from time import sleep

class MyTopo(Topo):
    def build(self):
        # Create switches
        s1 = self.addSwitch('s1', cls=OVSKernelSwitch, protocols='OpenFlow13')
        s2 = self.addSwitch('s2', cls=OVSKernelSwitch, protocols='OpenFlow13')
        s3 = self.addSwitch('s3', cls=OVSKernelSwitch, protocols='OpenFlow13')

        # Create hosts
        h1 = self.addHost('h1', mac="00:00:00:00:00:01", ip="10.0.0.1/24")
        h2 = self.addHost('h2', mac="00:00:00:00:00:02", ip="10.0.0.2/24")
        h3 = self.addHost('h3', mac="00:00:00:00:00:03", ip="10.0.0.3/24")
        h4 = self.addHost('h4', mac="00:00:00:00:00:04", ip="10.0.0.4/24")

        # Add links
        self.addLink(h1, s1)
        self.addLink(h2, s1)
        self.addLink(h3, s2)
        self.addLink(h4, s2)
        self.addLink(s1, s2)
        self.addLink(s1, s3)
        self.addLink(s2, s3)

def ip_generator():
    # Generate a random IP address in the range 10.0.0.1 - 10.0.0.4
    ip = ".".join(["10", "0", "0", str(randrange(1, 5))])
    return ip

def startNetwork():
    topo = MyTopo()
    c0 = RemoteController('c0', ip='192.168.0.101', port=6653)
    net = Mininet(topo=topo, link=TCLink, controller=c0)
    net.start()

    h1 = net.get('h1')
    h2 = net.get('h2')
    h3 = net.get('h3')
    h4 = net.get('h4')

    # Set up web server on h1
    h1.cmd('cd /home/mininet/webserver')
    h1.cmd('python -m SimpleHTTPServer 80 &')

    # ICMP (Ping) Flood
    for _ in range(5):
        src = choice([h1, h2])
        dst = ip_generator()
        src.cmd("timeout 20s hping3 -1 -V -d 120 -w 64 -p 80 --rand-source --flood {}".format(dst))
        sleep(10)

    # UDP Flood
    for _ in range(5):
        src = choice([h1, h2])
        dst = ip_generator()
        src.cmd("timeout 20s hping3 -2 -V -d 120 -w 64 --rand-source --flood {}".format(dst))
        sleep(10)

    # TCP-SYN Flood
    for _ in range(5):
        src = choice([h1, h2])
        dst = ip_generator()
        src.cmd('timeout 20s hping3 -S -V -d 120 -w 64 --rand-source --flood {}'.format(dst))
        sleep(10)

    # LAND Attack
    src = choice([h1, h2])
    dst = ip_generator()
    src.cmd('timeout 20s hping3 -S -a {} -p 80 --flood {}'.format(dst, dst))
    sleep(10)

    # DNS Amplification
    src = choice([h1, h2])
    dst = ip_generator()
    src.cmd('timeout 20s hping3 -2 -s 53 -d 120 -w 64 --rand-source --flood {}'.format(dst))
    sleep(10)

    # CoAP Flood
    for _ in range(5):
        src = choice([h1, h2])
        dst = ip_generator()
        src.cmd('timeout 20s hping3 -2 -s 5683 -d 120 -w 64 --rand-source --flood {}'.format(dst))
        sleep(10)

    # SYN-ACK Flood
    for _ in range(5):
        src = choice([h1, h2])
        dst = ip_generator()
        src.cmd('timeout 20s hping3 -2 -s 80 -d 120 -w 64 --rand-source --flood {}'.format(dst))
        sleep(10)

    # Slowloris DDoS Attack
    for _ in range(5):
        src = choice([h1, h2])
        dst = ip_generator()
        src.cmd('timeout 20s slowloris -dns {} -port 1883 -timeout 200'.format(dst))
        sleep(10)

    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    startNetwork()
