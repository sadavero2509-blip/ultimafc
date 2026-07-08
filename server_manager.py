import subprocess
import os
import sys
import time

def is_server_running():
    """Comprueba si el servidor ya está corriendo con un timeout corto.
    Verifica tanto el puerto del config como el puerto local fijo (25565)
    para detectar correctamente cuando se usa un túnel público."""
    from server_cfg import SERVER_PORT
    import socket
    # Puertos a verificar: el del config Y el puerto local del servidor (25565)
    ports_to_check = list(set([SERVER_PORT, 25565]))
    for port in ports_to_check:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.1)
                if s.connect_ex(('localhost', port)) == 0:
                    return True
        except:
            pass
    return False

def start_server():
    """Lanza el servidor Flask en un proceso independiente si no está ya corriendo."""
    if is_server_running():
        return None

    import sys
    if getattr(sys, 'frozen', False):
        exe_dir = os.path.dirname(sys.executable)
        server_exe = os.path.join(exe_dir, "server.exe")
        if not os.path.exists(server_exe):
            server_exe = os.path.join(os.getcwd(), "server.exe")
        
        if os.path.exists(server_exe):
            try:
                creationflags = 0
                if sys.platform == "win32":
                    creationflags = subprocess.CREATE_NO_WINDOW
                process = subprocess.Popen(
                    [server_exe],
                    creationflags=creationflags,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                return process
            except Exception as e:
                print(f"Error al iniciar server.exe: {e}")
                return None
        else:
            print("No se encontró server.exe para iniciar en modo offline.")
            return None
    else:
        server_path = os.path.join(os.getcwd(), "server", "app.py")
        if not os.path.exists(server_path):
            return None

        try:
            creationflags = 0
            if sys.platform == "win32":
                creationflags = subprocess.CREATE_NO_WINDOW

            process = subprocess.Popen(
                [sys.executable, server_path],
                creationflags=creationflags,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            return process
        except Exception as e:
            return None

def stop_server(process):
    """Cierra el proceso del servidor."""
    if process:
        try:
            process.terminate()
        except:
            pass

if __name__ == "__main__":
    start_server()
