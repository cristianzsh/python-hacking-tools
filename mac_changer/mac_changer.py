import optparse
import re
import subprocess

def get_arguments():
    parser = optparse.OptionParser()
    parser.add_option("-i", "--interface", dest = "interface", help = "Interface to change its MAC address.")
    parser.add_option("-m", "--mac", dest = "new_mac", help = "New MAC address.")
    (options, arguments) = parser.parse_args()

    if not options.interface:
        parser.error("[-] Please specify an interface, use --help for more info.")
    elif not options.new_mac:
        parser.error("[-] Please specify a new MAC, use --help for more info.")

    return options

def change_mac(interface, new_mac):
    print("\033[92m[+]\033[0m Changing MAC address for {} to {}".format(interface, new_mac))
    subprocess.call(["ifconfig", interface, "down"])
    subprocess.call(["ifconfig", interface, "hw", "ether", new_mac])
    subprocess.call(["ifconfig", interface, "up"])

def get_current_mac(interface):
    ifconfig_result = subprocess.check_output(["ifconfig", interface])
    mac_address_result = re.search(r"\w\w:\w\w:\w\w:\w\w:\w\w:\w\w", ifconfig_result)

    if mac_address_result:
        return mac_address_result.group(0)
    else:
        print("\033[91m[-]\033[0m Could not read MAC address.")

options = get_arguments()
current_mac = get_current_mac(options.interface)
print("[+] Current MAC = " + str(current_mac))
change_mac(options.interface, options.new_mac)
current_mac = get_current_mac(options.interface)

if current_mac == options.new_mac:
    print("\033[92m[+]\033[0m MAC address was successfully changed to: " + current_mac)
else:
    print("\033[91m[-]\033[0m MAC address did not get changed.")
