from mininet.net import Mininet
from mininet.cli import CLI
from mininet.node import OVSKernelSwitch, RemoteController
from mininet.link import TCLink
import sys
import time
import os
from datetime import datetime

def iniciar_red(cantidad_switches, ip_controlador="127.0.0.1", puerto_controlador=6633):
    # Crear carpeta de capturas si no existe
    carpeta_capturas = os.path.join(os.path.dirname(os.path.dirname(__file__)), "capturas")
    os.makedirs(carpeta_capturas, exist_ok=True)
    
    # Crear nombre de archivo con timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    red = Mininet(controller=RemoteController, switch=OVSKernelSwitch, link=TCLink)
    red.addController("c0", controller=RemoteController, ip=ip_controlador, port=puerto_controlador)
    h1 = red.addHost("h1", ip="10.0.0.1", mac="00:00:00:00:00:01")
    h2 = red.addHost("h2", ip="10.0.0.2", mac="00:00:00:00:00:02")
    h3 = red.addHost("h3", ip="10.0.0.3", mac="00:00:00:00:00:03")
    h4 = red.addHost("h4", ip="10.0.0.4", mac="00:00:00:00:00:04")
    
    # Crear switches
    extremo_izquierdo = red.addSwitch("s1", dpid="1")
    num_switch_derecho = cantidad_switches + 2
    extremo_derecho = red.addSwitch(f"s{num_switch_derecho}", dpid=str(num_switch_derecho))
    intermedios = []
    for indice in range(cantidad_switches):
        num_switch = indice + 2
        intermedios.append(red.addSwitch(f"s_cadena{num_switch}", dpid=str(num_switch)))
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
    
    # Iniciar captura de tráfico en cada host
    print("\nIniciando captura de tráfico en hosts...")
    procesos_captura = []
    hosts = [h1, h2, h3, h4]
    
    for host in hosts:
        nombre_host = host.name
        archivo_captura = os.path.join(carpeta_capturas, f"HOST_{nombre_host}.pcap")
        # Capturar en la interfaz principal del host
        interfaz = f"{nombre_host}-eth0"
        cmd = f"tcpdump -i {interfaz} -w {archivo_captura} -q"
        proceso = host.popen(cmd, shell=True)
        procesos_captura.append(("host", host, proceso, archivo_captura))
        print(f"Capturando tráfico de {nombre_host} en {archivo_captura}")
    
    # Iniciar captura de tráfico en cada switch
    print("\nIniciando captura de tráfico en switches...")
    todos_switches = [extremo_izquierdo] + intermedios + [extremo_derecho]
    
    for switch in todos_switches:
        nombre_switch = switch.name
        archivo_captura = os.path.join(carpeta_capturas, f"SWITCH_{nombre_switch}.pcap")
        
        # Obtener IP y MAC del switch (de la primera interfaz disponible)
        ip_switch = switch.cmd("ip addr show | grep 'inet ' | head -1 | awk '{print $2}' | cut -d/ -f1").strip()
        mac_switch = switch.cmd("ip addr show | grep 'link/ether' | head -1 | awk '{print $2}'").strip()
        
        if not ip_switch:
            ip_switch = "N/A"
        if not mac_switch:
            mac_switch = "N/A"
        
        # Capturar en todas las interfaces del switch usando 'any'
        cmd = f"echo '[Switch: {nombre_switch}, IP: {ip_switch}, MAC: {mac_switch}]' && tcpdump -i any -w {archivo_captura} -q 2>/dev/null"
        proceso = switch.popen(cmd, shell=True)
        procesos_captura.append(("switch", switch, proceso, archivo_captura))
        print(f"Capturando tráfico de {nombre_switch} (IP: {ip_switch}, MAC: {mac_switch}) en {archivo_captura}")
    
    red.pingAll()

    print("\nRed iniciada")
    print(f"Controlador remoto: {ip_controlador}:{puerto_controlador}")
    print(f"Capturas guardadas en: {carpeta_capturas}")
    print("Escribe exit en la CLI para finalizar")
    CLI(red)
    
    # Detener capturas antes de detener la red
    print("\nDeteniendo capturas de tráfico...")
    for tipo, nodo, proceso, archivo in procesos_captura:
        proceso.terminate()
        proceso.wait()
        print(f"Captura de {nodo.name} ({tipo}) guardada en: {archivo}")
    
    red.stop()


if __name__ == "__main__":
    cantidad_switches = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    ip_controlador = sys.argv[2] if len(sys.argv) > 2 else "127.0.0.1"
    puerto_controlador = int(sys.argv[3]) if len(sys.argv) > 3 else 6633
    iniciar_red(cantidad_switches, ip_controlador, puerto_controlador)