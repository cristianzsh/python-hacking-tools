import argparse
import scapy.all as scapy
import subprocess
import time

def get_arguments():
    parser = argparse.ArgumentParser("Script for detecting ARP spoofing")
    parser.add_argument("-i", "--interface", dest = "interface", help = "Interface")
    args = parser.parse_args()

    if not args.interface:
        parser.error("[-] Please specify an interface, use --help for more info.")

    return args

def get_mac(ip):
    arp_request = scapy.ARP(pdst = ip)
    broadcast = scapy.Ether(dst = "ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast / arp_request
    answered_list = scapy.srp(arp_request_broadcast, timeout = 1, verbose = False)[0]

    return answered_list[0][1].hwsrc

def sniff(interface):
    scapy.sniff(iface = interface, store = False, prn = process_sniffed_packet)

def process_sniffed_packet(packet):
    if packet.haslayer(scapy.ARP) and packet[scapy.ARP].op == 2:
        try:
            real_mac = get_mac(packet[scapy.ARP].psrc)
            response_mac = packet[scapy.ARP].hwsrc

            if real_mac != response_mac:
                print("\033[93m[+]\033[0m You are under attack!")
                subprocess.Popen(["notify-send"], "You are under attack!")
                time.sleep(5)
        except:
            pass

args = get_arguments()
sniff(args.interface)
