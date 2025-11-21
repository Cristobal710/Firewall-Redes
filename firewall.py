from pox.core import core
import json, os
from pox.lib.revent import EventHalt

log = core.getLogger()

fw_rules = []
firewall_switch = "s1"  # The switch to enforce firewall rules on

def load_rules(path=None):
    global fw_rules, firewall_switch

    if path is None:
        base = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(base))
        path = os.path.join(project_root, "config/reglas_firewall.json")
    else:
        path = os.path.abspath(path)

    try:
        with open(path) as f:
            config = json.load(f)
            fw_rules = config.get("reglas", [])
            firewall_switch = config.get("firewall_switch", None)

        # log.info("Firewall loaded (%d rules) from %s", len(fw_rules), path)
        # log.info("Target firewall switch: %s", firewall_switch)
        # for i, rule in enumerate(fw_rules, 1):
        #     log.info("  Rule %d: %s", i, rule.get("name", "Sin nombre"))

    except FileNotFoundError:
        # log.warning("Firewall rules file not found: %s", path)
        fw_rules = []
    except json.JSONDecodeError as e:
        # log.error("Error parsing firewall rules JSON: %s", e)
        fw_rules = []



def packet_to_dict(packet):
    """Convert a packet into a dict of relevant attributes for comparison."""
    pkt_dict = {}

    # MAC addresses
    pkt_dict["mac_origen"] = str(packet.src).lower()
    pkt_dict["mac_destino"] = str(packet.dst).lower()

    # IP info
    ip = packet.find("ipv4")
    if ip:
        pkt_dict["ip_origen"] = str(ip.srcip)
        pkt_dict["ip_destino"] = str(ip.dstip)
        pkt_dict["protocolo"] = None
        tcp = packet.find("tcp")
        udp = packet.find("udp")
        if tcp:
            pkt_dict["protocolo"] = "tcp"
            pkt_dict["puerto_destino"] = tcp.dstport
        elif udp:
            pkt_dict["protocolo"] = "udp"
            pkt_dict["puerto_destino"] = udp.dstport

    # ARP info
    arp = packet.find("arp")
    if arp:
        pkt_dict["ip_tipo"] = "arp"

    #IPv6 info
    ipv6 = packet.find("ipv6")
    if ipv6:
        pkt_dict["ip_tipo"] = "ipv6"
    return pkt_dict


def packet_matches_rule(packet, rule):
    pkt_dict = packet_to_dict(packet)
    
    for key, value in rule.items():
        if key == "name":
            continue
        if key not in pkt_dict or pkt_dict[key] != value:
            return False
    return True

def on_packet_in(event):
    # Only enforce rules on the firewall switch
    dpid = event.connection.dpid
    switch_name = f"s{dpid}"  # assumes Mininet uses "s<dpid>" names
    if switch_name != firewall_switch:
        return  # Not the firewall switch

    packet = event.parsed
    if not packet:
        return

    for rule in fw_rules:
        if packet_matches_rule(packet, rule):
            log.warning("Firewall DROP: matched rule '%s'", rule.get("name", ""))
            return EventHalt

    # If no rule matches, do nothing; l2_learning handles forwarding

def launch(reglas=None, switch_objetivo=None):
    load_rules(reglas)
    global firewall_switch
    if switch_objetivo:
        firewall_switch = switch_objetivo

    core.openflow.addListenerByName("PacketIn", on_packet_in)
    #log.info("Firewall module loaded (coexisting with forwarding.l2_learning)")
