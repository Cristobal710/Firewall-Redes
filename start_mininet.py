from mininet.net import Mininet
from mininet.cli import CLI
from mininet.node import OVSKernelSwitch, RemoteController
from mininet.link import TCLink
import sys
import time

def iniciar_red(cantidad_switches, ip_controlador="127.0.0.1", puerto_controlador=6633):
    red = Mininet(controller=RemoteController, switch=OVSKernelSwitch, link=TCLink)
    red.addController("c0", controller=RemoteController, ip=ip_controlador, port=puerto_controlador)
    h1 = red.addHost("h1", ip="10.0.0.1")
    h2 = red.addHost("h2", ip="10.0.0.2")
    h3 = red.addHost("h3", ip="10.0.0.3")
    h4 = red.addHost("h4", ip="10.0.0.4")
    extremo_izquierdo = red.addSwitch("s1", dpid="1")
    extremo_derecho = red.addSwitch(f"s{cantidad_switches+2}")
    intermedios = []
    for indice in range(cantidad_switches):
        intermedios.append(red.addSwitch(f"s_cadena{indice+2}"))
    anterior = extremo_izquierdo
    for nodo in intermedios:
        red.addLink(anterior, nodo)
        anterior = nodo
    red.addLink(anterior, extremo_derecho)
    red.addLink(h1, extremo_izquierdo)
    red.addLink(h2, extremo_izquierdo)
    red.addLink(h3, extremo_derecho)
    red.addLink(h4, extremo_derecho)
    red.start()
    red.pingAll()

    print("Red iniciada")
    print(f"Controlador remoto: {ip_controlador}:{puerto_controlador}")
    print("Escribe exit en la CLI para finalizar")
    CLI(red)
    red.stop()


if __name__ == "__main__":
    cantidad_switches = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    ip_controlador = sys.argv[2] if len(sys.argv) > 2 else "127.0.0.1"
    puerto_controlador = int(sys.argv[3]) if len(sys.argv) > 3 else 6633
    iniciar_red(cantidad_switches, ip_controlador, puerto_controlador)