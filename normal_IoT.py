from mininet.topo import Topo
from mininet.net import Mininet
from mininet.link import TCLink
from mininet.log import setLogLevel
from mininet.node import OVSKernelSwitch, RemoteController
from time import sleep

from datetime import datetime
from random import randrange, choice

class MyTopo(Topo):
    def build(self):
        s1 = self.addSwitch('s1', cls=OVSKernelSwitch, protocols='OpenFlow13')
        s2 = self.addSwitch('s2', cls=OVSKernelSwitch, protocols='OpenFlow13')
        s3 = self.addSwitch('s3', cls=OVSKernelSwitch, protocols='OpenFlow13')

        h1 = self.addHost('h1', mac="00:00:00:00:00:01", ip="10.0.0.1/24")
        h2 = self.addHost('h2', mac="00:00:00:00:00:02", ip="10.0.0.2/24")
        h3 = self.addHost('h3', mac="00:00:00:00:00:03", ip="10.0.0.3/24")
        h4 = self.addHost('h4', mac="00:00:00:00:00:04", ip="10.0.0.4/24")

        self.addLink(h1, s1)
        self.addLink(h2, s1)
        self.addLink(h3, s2)
        self.addLink(h4, s2)
        self.addLink(s1, s2)
        self.addLink(s1, s3)
        self.addLink(s2, s3)


def startNetwork():
    topo = MyTopo()
    net = Mininet(topo=topo, link=TCLink, controller=None)

    # Start the controller
    c0 = RemoteController('c0', ip='127.0.0.1', port=6653)
    net.addController(c0)

    # Start the network
    net.start()
    sleep(5)

    # Perform actions with hosts and switches
    h1 = net.get('h1')
    h2 = net.get('h2')
    h3 = net.get('h3')
    h4 = net.get('h4')

    # Add actions for hosts and DDoS attacker
    h1.cmd('ping -c 5 10.0.0.2')  # Ping h2 (DHT11 IoT device)
    h2.cmd('ping -c 5 10.0.0.1') 
    h1.cmd('ping -c 5 10.0.0.3')  # Ping h2 (DHT11 IoT device)
    h2.cmd('ping -c 5 10.0.0.3') 
    h1.cmd('ping -c 5 10.0.0.4')  # Ping h2 (DHT11 IoT device)
    h2.cmd('ping -c 5 10.0.0.4')
    h2.cmd('mosquitto_sub -h 127.0.0.1 -p 1883 -t topic1 > /tmp/temperature.txt &')  # Subscribe to MQTT topic 'topic1' and save the temperature to a file

    # Send ping request from h3 to h1 (IoT coffee maker) and h2 (DHT11 IoT device)
    h3.cmd('ping -c 5 10.0.0.1')
    h3.cmd('ping -c 5 10.0.0.2')
# Send ping request from h4 to h1 (IoT coffee maker) and h2 (DHT11 IoT device)
    h4.cmd('ping -c 5 10.0.0.1')
    h4.cmd('ping -c 5 10.0.0.2')

    # Control coffee maker (h1) from h3
    h3.cmd('mosquitto_pub -h 10.0.0.1 -p 1883 -t control -m "ON"')  # Turn on coffee maker
    sleep(2)
    h3.cmd('mosquitto_pub -h 10.0.0.1 -p 1883 -t control -m "OFF"')  # Turn off coffee maker

  # Control coffee maker (h1) from h4
    h4.cmd('mosquitto_pub -h 10.0.0.1 -p 1883 -t control -m "ON"')  # Turn on coffee maker
    sleep(2)
    h4.cmd('mosquitto_pub -h 10.0.0.1 -p 1883 -t control -m "OFF"')  # Turn off coffee maker

   

    # Start ICMP traffic from h3 to h1, h2, and h4
    h3.cmd('ping -c 10 10.0.0.1 &')
    h3.cmd('ping -c 10 10.0.0.2 &')
    h3.cmd('ping -c 10 10.0.0.4 &')

    # Start TCP traffic from h3 to h1, h2, and h4
    h3.cmd('iperf -c 10.0.0.1 -p 5050 -t 10 &')
    h3.cmd('iperf -c 10.0.0.2 -p 5050 -t 10 &')
    h3.cmd('iperf -c 10.0.0.4 -p 5050 -t 10 &')

    # Start UDP traffic from h3 to h1, h2, and h4
    h3.cmd('iperf -c 10.0.0.1 -u -p 5051 -t 10 &')
    h3.cmd('iperf -c 10.0.0.2 -u -p 5051 -t 10 &')
    h3.cmd('iperf -c 10.0.0.4 -u -p 5051 -t 10 &')

 # Start ICMP traffic from h3 to h1, h2, and h4
    h4.cmd('ping -c 10 10.0.0.1 &')
    h4.cmd('ping -c 10 10.0.0.2 &')
    h4.cmd('ping -c 10 10.0.0.3 &')

    # Start TCP traffic from h3 to h1, h2, and h4
    h4.cmd('iperf -c 10.0.0.1 -p 5050 -t 10 &')
    h4.cmd('iperf -c 10.0.0.2 -p 5050 -t 10 &')
    h4.cmd('iperf -c 10.0.0.3 -p 5050 -t 10 &')

    # Start UDP traffic from h3 to h1, h2, and h4
    h4.cmd('iperf -c 10.0.0.1 -u -p 5051 -t 10 &')
    h4.cmd('iperf -c 10.0.0.2 -u -p 5051 -t 10 &')
    h4.cmd('iperf -c 10.0.0.3 -u -p 5051 -t 10 &')


    # Read temperature data from file on h3
    temperature_file = '/tmp/temperature.txt'
    temperature_data = h3.cmd('cat ' + temperature_file)
    print("Temperature Data:")
    print(temperature_data)

    # Stop the network
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    startNetwork()
