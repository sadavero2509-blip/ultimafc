"""
Módulo centralizador de configuración del servidor.
Lee server_config.json UNA sola vez y expone ip, port y url.
Todos los archivos del proyecto importan de aquí.

Uso:
    from server_cfg import SERVER_IP, SERVER_PORT, SERVER_URL
"""

import os
import json

# ── Localizar server_config.json sin importar desde dónde se ejecute ──
# Estrategia: subir desde este archivo hasta encontrar server_config.json
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
    for _ in range(5):  # máximo 5 niveles hacia arriba
        candidate = os.path.join(search, "server_config.json")
        if os.path.exists(candidate):
            return candidate
        search = os.path.dirname(search)
    # Fallback: junto a este archivo
    return os.path.join(_THIS_DIR, "server_config.json")

_CONFIG_PATH = _find_config()

def _load():
    """Carga la configuración desde el JSON."""
    try:
        with open(_CONFIG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        ip = data.get("ip", "localhost")
        port = int(data.get("port", 5001))
        return ip, port
    except Exception:
        return "localhost", 5001

SERVER_IP, SERVER_PORT = _load()
SERVER_URL = f"http://{SERVER_IP}:{SERVER_PORT}"

def reload():
    """Recarga la configuración desde disco (útil tras editar el JSON)."""
    global SERVER_IP, SERVER_PORT, SERVER_URL
    SERVER_IP, SERVER_PORT = _load()
    SERVER_URL = f"http://{SERVER_IP}:{SERVER_PORT}"
