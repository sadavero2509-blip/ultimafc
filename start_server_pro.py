import os
import sys
import socket
import json
import subprocess

def get_local_ip():
    """Obtiene la dirección IP local de esta máquina."""
    try:
        # Crea un socket temporal para determinar la IP de red activa
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def update_config(ip):
    """Actualiza server_config.json con la IP local detectada (solo si no se está usando un dominio de túnel como playit.gg)."""
    config_path = os.path.join(os.getcwd(), "server_config.json")
    
    # Si ya existe un dominio de túnel en el config, no lo sobrescribimos automáticamente
    if os.path.exists(config_path):
        try:
            with open(config_path, "r") as f:
                old = json.load(f)
                existing_ip = old.get("ip", "")
                # Si contiene letras (no es una IP pura) o contiene playit, no sobrescribimos
                has_letters = any(c.isalpha() for c in existing_ip)
                if "playit" in existing_ip or ".gg" in existing_ip or has_letters:
                    print(f"[CONFIG] Detectado túnel o dominio '{existing_ip}'. No se sobrescribirá server_config.json.")
                    return
                port = int(old.get("port", 5001))
        except:
            port = 5001
    else:
        port = 5001

    config_data = {
        "ip": ip,
        "port": port
    }
    with open(config_path, "w") as f:
        json.dump(config_data, f, indent=4)
    print(f"[CONFIG] server_config.json actualizado con IP: {ip}:{port}")

def check_dependencies():
    """Verifica e instala dependencias necesarias para el servidor."""
    print("[SERVER] Verificando dependencias...")
    try:
        import flask
        import flask_socketio
        import flask_cors
        print("[SERVER] Dependencias OK.")
    except ImportError:
        print("[SERVER] Instalando dependencias faltantes...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "flask", "flask-socketio", "flask-cors", "eventlet"])

def run_server():
    """Inicia el servidor Flask."""
    from server_cfg import SERVER_PORT
    server_path = os.path.join(os.getcwd(), "server", "app.py")
    if not os.path.exists(server_path):
        print(f"[ERROR] No se encontró el archivo del servidor en {server_path}")
        return

    print("\n" + "="*50)
    print("      ULTIMA FC - SERVIDOR CENTRAL (PRO)")
    print("="*50)
    print(f" HOST: {get_local_ip()}")
    print(" PORT: 25565 (Mapeado a tu túnel de Playit)")
    print("-" * 50)
    print(" NOTA: Si quieres que otros entren desde fuera de tu WiFi,")
    print(" debes abrir el puerto 25565 en tu router si no usas Playit (Port Forwarding).")
    print("="*50 + "\n")

    # Ejecutar el servidor
    # Usamos eventlet si está disponible para mejor rendimiento en SocketIO
    try:
        import eventlet
        print("[SERVER] Usando motor de red Eventlet (Alto rendimiento)")
    except ImportError:
        print("[SERVER] Usando motor de red Flask estándar")

    subprocess.call([sys.executable, server_path])

if __name__ == "__main__":
    local_ip = get_local_ip()
    update_config(local_ip)
    # check_dependencies() # Descomentar si se quiere auto-instalar
    run_server()
