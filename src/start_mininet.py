from mininet.net import Mininet
from mininet.cli import CLI
from mininet.node import Controller, OVSKernelSwitch
from mininet.link import TCLink
import time
import sys
import os

def start_network(num_switches):
    net = Mininet(controller=Controller, switch=OVSKernelSwitch, link=TCLink)

    # Add controller with explicit executable
    net.addController("c0", controller=Controller, command="ovs-testcontroller")

    # Add hosts and switch (usar rutas absolutas)
   
    #base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    
    h1 = net.addHost("h1", ip="10.0.0.1")
    h2 = net.addHost("h2", ip="10.0.0.2")
    h3 = net.addHost("h3", ip="10.0.0.3")
    h4 = net.addHost("h4", ip="10.0.0.4")

    s1 = net.addSwitch("s1")
    s2 = net.addSwitch("s2")

    #crear switches y unirlos

    switches = []
    for i in range(num_switches):
        sw = net.addSwitch(f"s_mid{i+1}")
        switches.append(sw)

    previous = s1
    for sw in switches:
        net.addLink(previous, sw)
        previous = sw
    net.addLink(previous, s2)


    #conectar los 2 primeros hosts con un switch
    net.addLink(h1, s1)
    net.addLink(h2, s1)
    
    #conectar los otros 2 hosts con el "ultimo" switch
    net.addLink(h3, s2)
    net.addLink(h4, s2)
    
    
    net.start()
    net.pingAll()

    # Usar rutas absolutas para los comandos
    # server_path = os.path.join(base_path, "src/lib", "server")
    # client_path = os.path.join(base_path, "src/lib", "client")
    


    # Levantar servidor primero y esperar un poco para que el servidor se inicie
    h1.cmd(f'xterm -hold &') 
    time.sleep(2)
    
    # Ejecutar las terminales
    h2.cmd(f'xterm -hold &')
    h3.cmd(f'xterm -hold &')
    h4.cmd(f'xterm -hold &')

    print(f"\n=== Red iniciada ===")
    print(f"Presiona 'exit' en la CLI de Mininet para terminar\n")
    
    CLI(net)
    
    print("\n=== Terminando red ===")
    h1.cmd("killall xterm")
    h2.cmd("killall xterm")
    h3.cmd("killall xterm")
    h4.cmd("killall xterm")

    net.stop()


if __name__ == "__main__":
    num_switches = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    start_network(num_switches)