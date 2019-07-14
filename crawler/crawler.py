import optparse
import requests

def request(url):
    try:
        return requests.get("http://" + url)
    except requests.exceptions.ConnectionError:
        pass

parser = optparse.OptionParser()
parser.add_option("-t", "--target", dest = "target", help = "Target URL.")
(options, arguments) = parser.parse_args()

if not options.target:
    parser.error("[-] Please specify an target, use --help for more info.")

with open("subdomains-wordlist.txt", "r") as wordlist:
    for line in wordlist:
        word = line.strip()
        test_url = word + "." + options.target
        response = request(test_url)
        if response:
            print("[+] Discovered subdomain --> " + test_url)

with open("files-and-dirs-wordlist.txt", "r") as wordlist:
    for line in wordlist:
        word = line.strip()
        test_url = options.target + "/" + word
        response = request(test_url)

        if response:
            print("[+] Discovered URL --> " + test_url)
