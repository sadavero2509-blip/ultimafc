try:
    import requests
    import socketio
except ImportError:
    requests = None
    socketio = None

import threading
import json

def _safe_json(response):
    """Intenta parsear JSON de una respuesta HTTP de forma segura.
    Si el cuerpo no es JSON válido (ej. error HTML de Serveo), devuelve None."""
    try:
        return response.json()
    except (json.JSONDecodeError, ValueError):
        return None

class NetworkManager:
    """Sistema de comunicación con el servidor central."""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(NetworkManager, cls).__new__(cls)
            cls._instance.init_vars()
        return cls._instance

    def init_vars(self):
        from server_cfg import SERVER_IP, SERVER_PORT, SERVER_URL
        self.server_ip = SERVER_IP
        self.server_port = SERVER_PORT
        self.server_url = SERVER_URL
        self.is_remote_server = False  # True solo si conecta al servidor real (no local)
        self._check_url_and_fallback()
        print(f"[NET] Usando URL: {self.server_url} (remoto={self.is_remote_server})")
        
        self.sio = None
        if socketio:
            try:
                self.sio = socketio.Client()
            except:
                print("Error inicializando SocketIO. Modo offline.")
                
        self.connected = False
        self.username = None
        self.online_players = []
        self.chat_messages = []
        
        # Callbacks para la UI
        self.on_message_received = None
        self.on_players_updated = None
        self.on_match_received = None
        self.on_match_found = None
        self.on_system_message = None
 
        self.setup_handlers()

    def _check_url_and_fallback(self):
        """Verifica conexión al servidor remoto/público.
        Si la conexión es exitosa, marca is_remote_server=True (siempre que no sea localhost).
        No realiza fallback a localhost si el servidor real no está disponible."""
        if not requests:
            self.is_remote_server = False
            return
        
        try:
            res = requests.get(self.server_url, timeout=2.5)
            if res.status_code == 200:
                if "localhost" in self.server_ip or "127.0.0.1" in self.server_ip:
                    print(f"[NET] Conexión local detectada en '{self.server_url}' (no cuenta como servidor remoto real).")
                    self.is_remote_server = False
                else:
                    print(f"[NET] Servidor REMOTO detectado en '{self.server_url}'. Modos online disponibles.")
                    self.is_remote_server = True
                return
        except Exception as e:
            print(f"[NET] Servidor remoto '{self.server_url}' no alcanzable: {e}")
        
        self.is_remote_server = False

    def refresh_config(self):
        """Vuelve a leer la IP del servidor desde el archivo de configuración."""
        import server_cfg
        server_cfg.reload()
        self.server_ip = server_cfg.SERVER_IP
        self.server_port = server_cfg.SERVER_PORT
        self.server_url = server_cfg.SERVER_URL
        self._check_url_and_fallback()
        print(f"[NET] Usando URL: {self.server_url} (remoto={self.is_remote_server})")

    def setup_handlers(self):
        if not self.sio: return
        
        @self.sio.event
        def connect():
            self.connected = True
            print("Conectado al servidor.")

        @self.sio.event
        def disconnect():
            self.connected = False
            print("Desconectado del servidor.")

        @self.sio.on('new_message')
        def on_new_message(data):
            self.chat_messages.append(data)
            if self.on_message_received:
                self.on_message_received(data)

        @self.sio.on('system_message')
        def on_system_msg(data):
            if self.on_system_message:
                self.on_system_message(data)

        @self.sio.on('update_players')
        def on_update_players(data):
            self.online_players = data
            if self.on_players_updated:
                self.on_players_updated(data)

        @self.sio.on('incoming_match')
        def on_incoming_match(data):
            if self.on_match_received:
                self.on_match_received(data)

        @self.sio.on('match_found')
        def on_match_found_handler(data):
            if self.on_match_found:
                self.on_match_found(data)

    def connect(self, username):
        if not self.sio:
            print("SocketIO no está instalado. Modo Offline forzado.")
            return False
        self.username = username
        try:
            # Conectar en un hilo separado para no bloquear el juego
            threading.Thread(target=self._run_socket, daemon=True).start()
            return True
        except Exception as e:
            print(f"Error de conexión: {e}")
            return False

    def start_matchmaking(self):
        if self.connected:
            self.sio.emit('start_matchmaking', {})

    def cancel_matchmaking(self):
        if self.connected:
            self.sio.emit('cancel_matchmaking', {})

    def _run_socket(self):
        import time as _time
        urls_to_try = [self.server_url]
        
        for attempt in range(3):
            for url in urls_to_try:
                try:
                    # Recrear el cliente SIO para evitar estado corrupto de intentos previos
                    self.sio = socketio.Client()
                    self.setup_handlers()
                    self.sio.connect(url, wait_timeout=3)
                    self.server_url = url  # Recordar la URL que funcionó
                    print(f"[NET] SocketIO conectado a {url}")
                    self.sio.emit('login', {"username": self.username})
                    self.sio.wait()
                    return
                except Exception as e:
                    print(f"[NET] Intento {attempt+1}/3 fallido para {url}: {e}")
                    try: self.sio.disconnect()
                    except: pass
            _time.sleep(1)
        
        print("[NET] No se pudo conectar al servidor tras 3 intentos.")
        self.connected = False

    def send_chat(self, msg):
        if self.connected:
            self.sio.emit('chat_message', {"msg": msg})

    def request_match(self, target_user):
        if self.connected:
            self.sio.emit('match_request', {"target": target_user})

    # --- AUTH API ---

    def register(self, username, password):
        if not requests: return False, "Librería requests no disponible"
        self.refresh_config()
        try:
            res = requests.post(f"{self.server_url}/api/auth/register", 
                                json={"username": username, "password": password}, timeout=5)
            print(f"[NET] Register response: status={res.status_code}, content-type={res.headers.get('content-type','?')}, body={res.text[:150]}")
            body = _safe_json(res)
            if body is None:
                return False, "Servidor no disponible (respuesta inválida)"
            if res.status_code == 200:
                return True, "Registro exitoso"
            return False, body.get("error", f"Error del servidor ({res.status_code})")
        except requests.exceptions.ConnectionError:
            return False, "Servidor no alcanzado. ¿Está encendido?"
        except requests.exceptions.Timeout:
            return False, "Servidor tardó demasiado en responder"
        except Exception as e:
            print(f"[NET] Register exception: {e}")
            return False, f"Error de conexión"

    def login(self, username, password):
        if not requests: return False, "Librería requests no disponible"
        self.refresh_config()
        try:
            res = requests.post(f"{self.server_url}/api/auth/login", 
                                json={"username": username, "password": password}, timeout=5)
            print(f"[NET] Login response: status={res.status_code}, content-type={res.headers.get('content-type','?')}, body={res.text[:150]}")
            body = _safe_json(res)
            if body is None:
                return False, "Servidor no disponible (respuesta inválida)"
            if res.status_code == 200:
                self.username = username
                self.connect(username)
                return True, "Login exitoso"
            return False, body.get("error", f"Error del servidor ({res.status_code})")
        except requests.exceptions.ConnectionError:
            return False, "Servidor offline"
        except requests.exceptions.Timeout:
            return False, "Servidor tardó demasiado en responder"
        except Exception as e:
            print(f"[NET] Login exception: {e}")
            return False, f"Error de conexión"

    # --- API HTTP ---

    def save_cloud(self, save_data):
        """Guarda la partida en la nube."""
        if not requests: return False
        try:
            response = requests.post(
                f"{self.server_url}/api/save",
                json={"username": self.username, "save_data": save_data}
            )
            return response.status_code == 200
        except:
            return False

    def load_cloud(self):
        """Carga la partida de la nube."""
        if not requests: return None
        try:
            response = requests.get(f"{self.server_url}/api/load/{self.username}", timeout=5)
            if response.status_code == 200:
                data = _safe_json(response)
                return data
            return None
        except:
            return None

    def get_leaderboard(self):
        """Obtiene el top mundial."""
        if not requests: return []
        try:
            response = requests.get(f"{self.server_url}/api/leaderboard")
            if response.status_code == 200:
                try:
                    return response.json()
                except (ValueError, Exception):
                    return []
            return []
        except:
            return []

    def post_score(self, score, team_name):
        """Sube una puntuación al ranking mundial."""
        try:
            requests.post(
                f"{self.server_url}/api/leaderboard",
                json={"username": self.username, "score": score, "team": team_name}
            )
        except:
            pass
