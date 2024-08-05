import subprocess
import sys
import importlib

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

required_modules = [
    "customtkinter",
    "psutil",
    "requests",
    "threading",
    "tkinter"
]

for module in required_modules:
    try:
        importlib.import_module(module)
    except ImportError:
        print(f"{module} not found. Installing...")
        install(module)
    else:
        print(f"{module} is already installed.")

import customtkinter as ctk
import psutil
import threading
import os
import time
import requests
import subprocess
from tkinter import filedialog

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class GameInjector:
    @staticmethod
    def download_file(url, destination_path):
        response = requests.get(url)
        if response.status_code == 200:
            with open(destination_path, 'wb') as file:
                file.write(response.content)
            print(f"File downloaded successfully to {destination_path}")
        else:
            print(f"Failed to download file. Status code: {response.status_code}")

    @staticmethod
    def inject(file_path, processid):
        injector_path = os.path.join(os.getcwd(), "assets", "injector.exe")
        os.makedirs(os.path.dirname(injector_path), exist_ok=True)
        if not os.path.exists(injector_path):
            try:
                GameInjector.download_file("https://cdn.ajaxfnc.com/uploads/injector.exe", injector_path)
            except Exception as e:
                print("Download Error", str(e))
                return

        injector_path = os.path.abspath(injector_path)
        file_path = os.path.abspath(file_path)

        command = f'"{injector_path}" "{processid}" "{file_path}"'

        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            print(result.stdout)
            print(result.stderr)
            
            if result.returncode == 0:
                print(f"Injection successful.")
            else:
                print(f"Injection failed with return code: {result.returncode}")
        except Exception as e:
            print(f"Error during injection: {e}")

class App(ctk.CTk):
    HEIGHT, WIDTH = 450, 800
    CHECK_INTERVAL = 3

    def __init__(self):
        super().__init__()
        self.title("EzInjector")
        self.geometry(f"{App.WIDTH}x{App.HEIGHT}")
        self.resizable(False, False)
        self.dll_file = None
        self.fortnite_pid = None

        ctk.CTkFrame(self, width=662, height=124, corner_radius=13).place(x=80, y=0)
        ctk.CTkFrame(self, width=602, height=169, corner_radius=82).place(x=98, y=133)

        ctk.CTkLabel(self, text="EzInjector", bg_color=['gray86', 'gray17'],
                     font=ctk.CTkFont('Burbank', size=76, weight='bold', slant='italic')).place(x=235, y=8)

        self.process_label = ctk.CTkLabel(self, text="Fortnite process not started! you must start fortnite to inject.",
                                         bg_color=['gray86', 'gray17'], font=ctk.CTkFont('Burbank', size=17, weight='bold'))
        self.process_label.place(x=157, y=158)

        self.dll_entry = ctk.CTkEntry(self, width=224, height=41, corner_radius=18, justify="center", 
                                      placeholder_text="DLL Path", bg_color=['gray86', 'gray17'])
        self.dll_entry.place(x=251, y=204)

        ctk.CTkButton(self, text="...", width=52, height=41, corner_radius=15, command=self.browse_dll,
                      bg_color=['gray86', 'gray17']).place(x=483, y=204)

        ctk.CTkButton(self, text="Inject", width=272, height=29, corner_radius=14, font=ctk.CTkFont(
            'Burbank', size=21, weight='bold'), command=self.inject_dll, bg_color=['gray86', 'gray17']).place(x=257, y=263)

        threading.Thread(target=self.check_process, daemon=True).start()

    def browse_dll(self):
        self.dll_file = filedialog.askopenfilename(filetypes=[("DLL Files", "*.dll")])
        if self.dll_file:
            self.dll_entry.delete(0, ctk.END)
            self.dll_entry.insert(0, self.dll_file)

    def check_process(self):
        while True:
            process_info = self.find_fortnite_process()
            if process_info:
                self.fortnite_pid = process_info['pid']
                self.process_label.configure(text=f"Detected Fortnite! {process_info['name']} ({self.fortnite_pid})")
            else:
                self.process_label.configure(text="Fortnite process not started! you must start fortnite to inject.")
            time.sleep(App.CHECK_INTERVAL)

    def find_fortnite_process(self):
        for proc in psutil.process_iter(attrs=['pid', 'name']):
            if proc.info['name'] == 'FortniteClient-Win64-Shipping.exe':
                return proc.info
        return None

    def inject_dll(self):
        if self.dll_file and self.fortnite_pid:
            GameInjector.inject(self.dll_file, self.fortnite_pid)
        else:
            ctk.CTkMessageBox.show_error("Error", "No DLL file selected or Fortnite process not detected.")

if __name__ == "__main__":
    App().mainloop()
