"""
Módulo centralizador de configuración del servidor.
Lee server_config.json UNA sola vez y expone ip, port y url de forma ultra-robusta.
Soporta URLs completas (http/https), dominios de túnel (Serveo, Playit, Ngrok) o IPs locales.
"""

import os
import json

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))

def _find_config():
    """Busca server_config.json."""
    import sys
    if getattr(sys, 'frozen', False):
        exe_dir = os.path.dirname(sys.executable)
        candidate = os.path.join(exe_dir, "server_config.json")
        if os.path.exists(candidate):
            return candidate
        candidate = os.path.join(os.getcwd(), "server_config.json")
        if os.path.exists(candidate):
            return candidate

    search = _THIS_DIR
    for _ in range(5):
        candidate = os.path.join(search, "server_config.json")
        if os.path.exists(candidate):
            return candidate
        search = os.path.dirname(search)
    return os.path.join(_THIS_DIR, "server_config.json")

_CONFIG_PATH = _find_config()

def _load():
    """Carga y normaliza la configuración desde el JSON."""
    try:
        with open(_CONFIG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        url_input = data.get("url", "").strip()
        ip_input = data.get("ip", data.get("server_ip", "localhost")).strip()
        port_input = data.get("port", 80)
        
        target = url_input if url_input else ip_input
        
        if not target.startswith("http://") and not target.startswith("https://"):
            proto = "https" if port_input == 443 else "http"
            target = f"{proto}://{target}"
            
        proto = "https" if target.startswith("https://") else "http"
        clean = target.replace("http://", "").replace("https://", "").split("/")[0]
        
        if ":" in clean:
            parts = clean.split(":")
            ip = parts[0]
            try:
                port = int(parts[1])
            except:
                port = 80
        else:
            ip = clean
            port = int(port_input)
            
        if (port == 80 and proto == "http") or (port == 443 and proto == "https"):
            url = f"{proto}://{ip}"
        else:
            url = f"{proto}://{ip}:{port}"
            
        return ip, port, url
    except Exception as e:
        print(f"[server_cfg] Error cargando {_CONFIG_PATH}: {e}")
        return "localhost", 25565, "http://localhost:25565"

SERVER_IP, SERVER_PORT, SERVER_URL = _load()

def reload():
    """Recarga la configuración desde disco."""
    global SERVER_IP, SERVER_PORT, SERVER_URL
    SERVER_IP, SERVER_PORT, SERVER_URL = _load()
