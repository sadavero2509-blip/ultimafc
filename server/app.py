import os
import json
import time
import sys
import threading
import socket

# Forzar UTF-8 en stdout/stderr para evitar errores de codificación charmap en Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room, leave_room

# El servidor importa datos directamente de la carpeta del cliente (fuente única de verdad)
if getattr(sys, 'frozen', False):
    _PROJECT_ROOT = os.path.dirname(sys.executable)
else:
    _PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

def get_active_legends():
    """Importa las leyendas directamente de la base de datos maestra del servidor."""
    try:
        from server.legends_database import get_active_legends as get_legends
        base_list = get_legends()
    except ImportError:
        print("ERROR: No se pudo cargar la base de datos maestra en el servidor.")
        base_list = []
    
    from data.rosters import calculate_ovr
    legends = []
    for l in base_list:
        # Limpiar datos para el tráfico de red (el servidor no suele enviar edad/número)
        entry = {k: v for k, v in l.items() if k not in ('age', 'num')}
        if "is_legend" not in entry: entry["is_legend"] = True
        entry["ovr"] = calculate_ovr(entry)
        legends.append(entry)
    return legends



_LEGENDS_BASE = get_active_legends()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ultima_fc_secret_key_2026'
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# --- CONFIGURACIÓN DE VERSIÓN Y ACTUALIZACIÓN DEL SERVIDOR ---
# SERVER_VERSION y SERVER_UPDATE_TYPE se leen automáticamente del archivo de configuración del juego.
try:
    from settings import GAME_VERSION, UPDATE_TYPE
    SERVER_VERSION = GAME_VERSION
    SERVER_UPDATE_TYPE = UPDATE_TYPE
except ImportError:
    SERVER_VERSION = "1.1.0"
    SERVER_UPDATE_TYPE = "minor"



# Rutas de persistencia
_SERVER_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(_PROJECT_ROOT, "server_data")
SAVES_DIR = os.path.join(DATA_DIR, "saves")
LEADERBOARD_FILE = os.path.join(DATA_DIR, "leaderboard.json")
MARKET_FILE = os.path.join(DATA_DIR, "market.json")
USERS_FILE = os.path.join(DATA_DIR, "users.json")
UPDATE_DIR = _PROJECT_ROOT  # Raiz del proyecto (maneja frozen correctamente via _PROJECT_ROOT)

for d in [DATA_DIR, SAVES_DIR]:
    if not os.path.exists(d):
        os.makedirs(d)

# Si algún archivo JSON está corrupto (por ejemplo, con NUL bytes tras un fallo de escritura/cierre),
# lo reinicializamos con el valor por defecto.
def _check_and_fix_json_file(path, default_val):
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                json.load(f)
        except Exception:
            print(f"[SERVER WARNING] Archivo corrupto detectado en {path}. Reinicializando...")
            with open(path, "w", encoding="utf-8") as f:
                json.dump(default_val, f)
    else:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(default_val, f)

_check_and_fix_json_file(MARKET_FILE, [])
_check_and_fix_json_file(USERS_FILE, {})
_check_and_fix_json_file(LEADERBOARD_FILE, [])

# --- RUTAS API ---

# IDs autorizados para inyectar monedas (El de tu PC y el que uses en móvil)
ADMIN_IDS = ["sadav", "AndroidUser"]

# --- AUTH ROUTES ---

@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.json
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()
    
    if not username or not password:
        return jsonify({"error": "Usuario y contraseña requeridos"}), 400
    
    with open(USERS_FILE, "r") as f:
        users = json.load(f)
        
    if username in users:
        return jsonify({"error": "El nombre de usuario ya existe"}), 409
        
    users[username] = password
    with open(USERS_FILE, "w") as f:
        json.dump(users, f)
        
    return jsonify({"success": True, "message": "Registro exitoso"})

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()
    
    with open(USERS_FILE, "r") as f:
        users = json.load(f)
        
    if username not in users or users[username] != password:
        return jsonify({"error": "Credenciales inválidas"}), 401
        
    return jsonify({"success": True, "username": username})

@app.route('/')
def index():
    return jsonify({
        "status": "online",
        "game": "ULTIMA FC Server",
        "version": SERVER_VERSION,
        "update_type": SERVER_UPDATE_TYPE,
        "server_time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "message": "Servidor Central de ULTIMA FC - Conexión Abierta"
    })

@app.route('/api/news', methods=['GET'])
def get_news():
    """Devuelve noticias dinámicas del servidor para el cliente."""
    return jsonify({
        "headline": "¡EVENTO MUNDIAL ACTIVO!",
        "sub": "Las cartas de la Copa del Mundo ya están disponibles en sobres y mercado.",
        "active_events": ["WorldCup2026", "LegendsPack"],
        "server_msg": "Bienvenido al ecosistema real de ULTIMA FC."
    })

@app.route('/api/save', methods=['POST'])
def save_game():
    data = request.json
    username = data.get("username")
    save_data = data.get("save_data")
    
    if not username or not save_data:
        return jsonify({"error": "Faltan datos"}), 400
    
    file_path = os.path.join(SAVES_DIR, f"{username}.json")
    
    # SISTEMA ANTI-CHEAT (Protección contra inyección local en WiFi)
    if os.path.exists(file_path) and username not in ADMIN_IDS:
        try:
            with open(file_path, "r") as f:
                old_data = json.load(f)
                
            old_coins = old_data.get("coins", 0)
            new_coins = save_data.get("coins", 0)
            
            # Si alguien no autorizado se suma más de 50.000 monedas de golpe, se bloquea.
            if new_coins > old_coins + 50000:
                save_data["coins"] = old_coins # Se le devuelve al valor original
                print(f"ANTI-CHEAT ACTIVO: Intento de inyección de monedas bloqueado para {username}.")
        except Exception as e:
            pass

    with open(file_path, "w") as f:
        json.dump(save_data, f)
        
    return jsonify({"message": "Partida guardada en la nube con éxito."})

@app.route('/api/admin/add_coins', methods=['POST'])
def admin_add_coins():
    data = request.json
    username = data.get("username")
    amount = data.get("amount", 1000000)
    
    if username not in ADMIN_IDS:
        return jsonify({"error": "Acceso denegado"}), 403
        
    # RESPUESTA TURBO: Respondemos al cliente inmediatamente
    # y procesamos la escritura en disco en un hilo separado
    def _background_save(user, qty):
        file_path = os.path.join(SAVES_DIR, f"{user}.json")
        if os.path.exists(file_path):
            try:
                with open(file_path, "r") as f:
                    save_data = json.load(f)
                save_data["coins"] = save_data.get("coins", 0) + qty
                with open(file_path, "w") as f:
                    json.dump(save_data, f)
                print(f"[SERVER ADMIN] {qty} monedas inyectadas a {user} (Background)")
            except: pass

    import threading
    threading.Thread(target=_background_save, args=(username, amount), daemon=True).start()
    
    return jsonify({"success": True, "message": "Petición admin procesada al instante"})

@app.route('/api/load/<username>', methods=['GET'])
def load_game(username):
    file_path = os.path.join(SAVES_DIR, f"{username}.json")
    if not os.path.exists(file_path):
        return jsonify({"error": "No hay partidas guardadas para este usuario"}), 404
        
    with open(file_path, "r") as f:
        save_data = json.load(f)
        
    return jsonify(save_data)

@app.route('/api/leaderboard', methods=['GET'])
def get_leaderboard():
    with open(LEADERBOARD_FILE, "r") as f:
        data = json.load(f)
    # Devolver top 10
    sorted_data = sorted(data, key=lambda x: x['score'], reverse=True)[:10]
    return jsonify(sorted_data)

@app.route('/api/leaderboard', methods=['POST'])
def update_leaderboard():
    new_entry = request.json # {username, score, team}
    if not new_entry.get("username") or not new_entry.get("score"):
        return jsonify({"error": "Datos inválidos"}), 400
        
    with open(LEADERBOARD_FILE, "r") as f:
        data = json.load(f)
        
    # Actualizar si existe o añadir
    found = False
    for entry in data:
        if entry["username"] == new_entry["username"]:
            if new_entry["score"] > entry["score"]:
                entry["score"] = new_entry["score"]
                entry["team"] = new_entry.get("team", entry["team"])
            found = True
            break
    
    if not found:
        data.append(new_entry)
        
    with open(LEADERBOARD_FILE, "w") as f:
        json.dump(data, f)
        
    return jsonify({"message": "Leaderboard actualizado."})
    
# --- ULTIMATE TEAM SECURE ENDPOINTS ---

@app.route('/api/ultimate/load/<username>', methods=['GET'])
def ultimate_load(username):
    file_path = os.path.join(SAVES_DIR, f"ut_{username}.json")
    if not os.path.exists(file_path):
        return jsonify({"new_user": True})
    with open(file_path, "r") as f:
        return jsonify(json.load(f))

import datetime
import random

@app.route('/api/ultimate/christmas_gift', methods=['POST'])
def christmas_gift():
    data = request.json
    username = data.get("username")
    if not username:
        return jsonify({"error": "Usuario no proporcionado"}), 400
        
    # Verificar fecha: 24 de Dic 00:00 hasta 26 de Dic 21:00 (9 PM ET)
    # Nota: Usamos la hora del sistema. 9 PM ET es aprox 02:00 UTC del día siguiente.
    now = datetime.datetime.now()
    start = datetime.datetime(2026, 12, 24, 0, 0)
    end = datetime.datetime(2026, 12, 26, 21, 0)
    
    if not (start <= now <= end):
        return jsonify({"error": "El regalo de Navidad solo está disponible entre el 24 y el 26 de diciembre hasta las 9 PM ET."}), 403

    # Cargar datos del usuario
    file_path = os.path.join(SAVES_DIR, f"ut_{username}.json")
    if not os.path.exists(file_path):
        return jsonify({"error": "Debes tener un club creado para recibir el regalo."}), 404
        
    with open(file_path, "r") as f:
        save_data = json.load(f)
        
    if save_data.get("christmas_gift_2026_claimed"):
        return jsonify({"error": "Ya has reclamado tu regalo de Navidad."}), 400
        
    # Generar Pick de 5 leyendas históricas
    from server.legends_database import get_historical_legends
    all_legends = get_historical_legends()
    
    # Elegir 5 aleatorias
    options = random.sample(all_legends, min(5, len(all_legends)))
    
    # Guardamos el estado "reclamado" y las opciones para evitar re-rolls
    save_data["christmas_gift_2026_claimed"] = True
    save_data["pending_gift_options"] = options
    
    with open(file_path, "w") as f:
        json.dump(save_data, f)
        
    return jsonify({
        "success": True, 
        "message": "¡Feliz Navidad! Elige tu Repetición Histórica:",
        "options": options
    })

@app.route('/api/ultimate/choose_gift', methods=['POST'])
def choose_gift():
    data = request.json
    username = data.get("username")
    chosen_index = data.get("index") # 0-4
    
    if username is None or chosen_index is None:
        return jsonify({"error": "Datos inválidos"}), 400
        
    file_path = os.path.join(SAVES_DIR, f"ut_{username}.json")
    if not os.path.exists(file_path):
        return jsonify({"error": "Usuario no encontrado"}), 404
        
    with open(file_path, "r") as f:
        save_data = json.load(f)
        
    options = save_data.get("pending_gift_options")
    if not options or chosen_index >= len(options):
        return jsonify({"error": "No hay opciones de regalo pendientes o el índice es inválido."}), 400
        
    chosen_player = options[chosen_index]
    
    # Añadir al club (asegurando que existe la lista de jugadores)
    if "players" not in save_data: save_data["players"] = []
    
    # Clonamos para evitar referencias si es necesario y añadimos
    new_player = chosen_player.copy()
    save_data["players"].append(new_player)
    
    # Limpiar opciones pendientes para cerrar el ciclo
    save_data["pending_gift_options"] = None
    
    with open(file_path, "w") as f:
        json.dump(save_data, f)
        
    return jsonify({
        "success": True, 
        "message": f"¡{chosen_player['name']} se ha unido a tu club!",
        "player": chosen_player
    })

@app.route('/api/ultimate/save', methods=['POST'])

def ultimate_save():
    data = request.json
    username = data.get("username")
    club_data = data.get("club_data")
    if not username or not club_data:
        return jsonify({"error": "Datos inválidos"}), 400
    
    file_path = os.path.join(SAVES_DIR, f"ut_{username}.json")
    with open(file_path, "w") as f:
        json.dump(club_data, f)
    return jsonify({"success": True})

# Lock para evitar colisiones en Windows al acceder a archivos
market_lock = threading.Lock()

@app.route('/api/ultimate/market', methods=['GET'])
def get_market():
    """Devuelve todas las subastas activas en el mercado global."""
    with market_lock:
        with open(MARKET_FILE, "r") as f:
            return jsonify(json.load(f))

@app.route('/api/ultimate/market/list', methods=['POST'])
def list_item():
    """Añade un item al mercado global."""
    new_auction = request.json
    with market_lock:
        with open(MARKET_FILE, "r") as f:
            market = json.load(f)
        
        market.append(new_auction)
        with open(MARKET_FILE, "w") as f:
            json.dump(market, f)
    return jsonify({"success": True})

@app.route('/api/ultimate/market/buy', methods=['POST'])
def buy_item():
    """Procesa la compra de un item en el mercado global."""
    data = request.json
    auction_id = data.get("auction_id")
    
    with market_lock:
        with open(MARKET_FILE, "r") as f:
            market = json.load(f)
        
        # Encontrar y eliminar la subasta
        updated_market = [auc for auc in market if auc["id"] != auction_id]
        if len(updated_market) == len(market):
            return jsonify({"error": "Subasta no encontrada o ya vendida"}), 404
            
        with open(MARKET_FILE, "w") as f:
            json.dump(updated_market, f)
    return jsonify({"success": True})

@app.route('/api/ultimate/market/bid', methods=['POST'])
def bid_item():
    """Procesa una oferta de puja en el mercado global."""
    data = request.json
    auction_id = data.get("auction_id")
    bid_amount = data.get("bid_amount")
    bidder = data.get("bidder")
    
    if not auction_id or not bid_amount or not bidder:
        return jsonify({"error": "Datos incompletos para procesar la puja"}), 400
        
    with market_lock:
        with open(MARKET_FILE, "r") as f:
            market = json.load(f)
            
        # Buscar la subasta
        found = False
        for auc in market:
            if auc["id"] == auction_id:
                found = True
                current_bid = auc.get("current_bid", 0)
                if bid_amount <= current_bid:
                    return jsonify({"error": f"La puja debe ser mayor que la puja actual ({current_bid})"}), 400
                
                # Reembolsar al postor anterior si existe
                prev_bidder = auc.get("last_bidder")
                prev_bid = auc.get("current_bid", 0)
                if prev_bidder and prev_bid > 0:
                    prev_user_path = os.path.join(SAVES_DIR, f"ut_{prev_bidder}.json")
                    if os.path.exists(prev_user_path):
                        try:
                            with open(prev_user_path, "r") as f_prev:
                                prev_data = json.load(f_prev)
                            prev_data["coins"] = prev_data.get("coins", 0) + prev_bid
                            with open(prev_user_path, "w") as f_prev:
                                json.dump(prev_data, f_prev)
                            print(f"[SERVER MARKET] Reembolso de {prev_bid} monedas entregado a {prev_bidder} al ser superada su puja.")
                        except Exception as ex:
                            print(f"[SERVER ERROR] Falló reembolso a {prev_bidder}: {ex}")
                
                # Actualizar la subasta con la nueva puja
                auc["current_bid"] = bid_amount
                auc["last_bidder"] = bidder
                break
                
        if not found:
            return jsonify({"error": "Subasta no encontrada"}), 404
            
        with open(MARKET_FILE, "w") as f:
            json.dump(market, f)
            
    return jsonify({"success": True})

@app.route('/api/ultimate/open_pack', methods=['POST'])
def ultimate_open_pack():
    # El servidor genera los items y resta la moneda seleccionada
    data = request.json
    username = data.get("username")
    pack_id = data.get("pack_id")
    currency = data.get("currency", "COINS")
    
    if currency == "FC_POINTS":
        current_points = data.get("current_points", 0)
        pack_price_points = data.get("pack_price_points", 0)
        if current_points < pack_price_points:
            return jsonify({"error": "Puntos FC insuficientes"}), 400
        return jsonify({"approved": True, "new_points_balance": current_points - pack_price_points})
    else:
        current_coins = data.get("current_coins", 0)
        pack_price = data.get("pack_price", 0)
        if current_coins < pack_price:
            return jsonify({"error": "Monedas insuficientes"}), 400
        return jsonify({"approved": True, "new_balance": current_coins - pack_price})

@app.route('/api/ultimate/legends', methods=['GET'])
def ultimate_get_legends():
    """Devuelve la lista de leyendas activas en el servidor."""
    return jsonify(get_active_legends())

# --- SISTEMA DE AUTO-ACTUALIZACIÓN ---

@app.route('/api/update/check', methods=['GET'])
def update_check():
    """Genera un manifiesto de todos los archivos críticos del cliente para auto-sincronización total."""
    import glob
    import hashlib
    
    # Directorios base a ignorar
    ignore_dirs = [".venv", "venv", "__pycache__", "server", "server_data", "saves", "scratch", ".vscode", ".git"]
    
    files_to_check = []
    
    # Escaneo dinámico recursivo de todo el proyecto (excepto lo ignorado)
    for root, dirs, files in os.walk(UPDATE_DIR):
        # Filtrar directorios ignorados en vivo
        dirs[:] = [d for d in dirs if d not in ignore_dirs and not d.startswith('.')]
        
        for file in files:
            # Extensiones a sincronizar (código, imágenes, sonidos, fuentes)
            valid_exts = (".py", ".png", ".jpg", ".ttf", ".wav", ".mp3", ".json")
            if file.endswith(valid_exts):
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, UPDATE_DIR).replace("\\", "/")
                # Ignorar el propio server, dependencias, o saves locales del cliente
                if not rel_path.startswith("server") and not rel_path.startswith("scratch") and "saves" not in rel_path and "server_data" not in rel_path:
                    files_to_check.append(rel_path)
    
    manifest = {}
    for rel_path in files_to_check:
        full_path = os.path.join(UPDATE_DIR, rel_path)
        if os.path.exists(full_path):
            with open(full_path, "rb") as f:
                file_hash = hashlib.md5(f.read()).hexdigest()
                manifest[rel_path] = file_hash
                
    return jsonify({
        "version": SERVER_VERSION,
        "update_type": SERVER_UPDATE_TYPE,
        "manifest": manifest
    })

@app.route('/api/update/download/<path:filepath>', methods=['GET'])
def update_download(filepath):
    """Sirve un archivo específico del proyecto."""
    from flask import send_from_directory
    directory = os.path.abspath(os.path.join(UPDATE_DIR, os.path.dirname(filepath)))
    filename = os.path.basename(filepath)
    return send_from_directory(directory, filename)

def _find_best_exe_path():
    """Busca dinámicamente el ejecutable NeoFutbolArcade.exe en las rutas de desarrollo y distribución."""
    candidate_paths = [
        os.path.join(UPDATE_DIR, "dist", "NeoFutbolArcade_Release", "NeoFutbolArcade.exe"),
        os.path.join(UPDATE_DIR, "dist", "NeoFutbolArcade.exe"),
        os.path.join(UPDATE_DIR, "NeoFutbolArcade.exe"),
        # Respaldos relativos al archivo actual
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "dist", "NeoFutbolArcade_Release", "NeoFutbolArcade.exe"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "dist", "NeoFutbolArcade.exe"),
    ]
    for path in candidate_paths:
        norm_path = os.path.normpath(path)
        if os.path.exists(norm_path):
            return norm_path
    return None

@app.route('/api/update/exe_info', methods=['GET'])
def update_exe_info():
    """Devuelve el hash MD5 del ejecutable NeoFutbolArcade.exe para la auto-actualización del .exe."""
    import hashlib
    exe_path = _find_best_exe_path()
    if not exe_path:
        return jsonify({"error": "Ejecutable no encontrado en el servidor"}), 404
    with open(exe_path, "rb") as f:
        exe_hash = hashlib.md5(f.read()).hexdigest()
    return jsonify({
        "version": SERVER_VERSION,
        "md5": exe_hash,
        "update_type": SERVER_UPDATE_TYPE
    })

@app.route('/api/update/download_exe', methods=['GET'])
def update_download_exe():
    """Sirve el ejecutable NeoFutbolArcade.exe para auto-actualización del cliente."""
    from flask import send_from_directory
    exe_path = _find_best_exe_path()
    if not exe_path:
        return jsonify({"error": "Ejecutable no encontrado"}), 404
    return send_from_directory(
        os.path.dirname(exe_path),
        os.path.basename(exe_path),
        as_attachment=True,
        mimetype="application/octet-stream"
    )

# --- EVENTOS SOCKET.IO (TIEMPO REAL) ---

online_users = {}
matchmaking_queue = []

@socketio.on('connect')
def handle_connect():
    print(f"Cliente conectado: {request.sid}")

@socketio.on('login')
def handle_login(data):
    username = data.get("username")
    online_users[request.sid] = username
    emit('system_message', {"msg": f"{username} se ha unido al lobby."}, broadcast=True)
    emit('update_players', list(online_users.values()), broadcast=True)

@socketio.on('chat_message')
def handle_chat(data):
    username = online_users.get(request.sid, "Anónimo")
    msg = data.get("msg")
    emit('new_message', {"user": username, "msg": msg, "time": time.strftime("%H:%M")}, broadcast=True)

@socketio.on('start_matchmaking')
def handle_start_matchmaking(data):
    if request.sid not in matchmaking_queue:
        matchmaking_queue.append(request.sid)
        print(f"Usuario en cola: {online_users.get(request.sid)}")
        
    # Intentar emparejar
    if len(matchmaking_queue) >= 2:
        p1_sid = matchmaking_queue.pop(0)
        p2_sid = matchmaking_queue.pop(0)
        
        p1_name = online_users.get(p1_sid)
        p2_name = online_users.get(p2_sid)
        
        # Enviar información del partido a ambos
        emit('match_found', {"opponent": p2_name, "is_host": True}, to=p1_sid)
        emit('match_found', {"opponent": p1_name, "is_host": False}, to=p2_sid)

@socketio.on('cancel_matchmaking')
def handle_cancel_matchmaking():
    if request.sid in matchmaking_queue:
        matchmaking_queue.remove(request.sid)

@socketio.on('match_request')
def handle_match_request(data):
    target_user = data.get("target")
    sender_user = online_users.get(request.sid)
    
    # Encontrar el sid del target
    target_sid = None
    for sid, name in online_users.items():
        if name == target_user:
            target_sid = sid
            break
            
    if target_sid:
        emit('incoming_match', {"from": sender_user}, to=target_sid)

@socketio.on('disconnect')
def handle_disconnect():
    if request.sid in matchmaking_queue:
        matchmaking_queue.remove(request.sid)
    if request.sid in online_users:
        user = online_users.pop(request.sid)
        emit('system_message', {"msg": f"{user} ha salido del lobby."}, broadcast=True)
        emit('update_players', list(online_users.values()), broadcast=True)

# --- MARKET BOT (Lógica en Servidor) ---

def simulate_market_tick():
    """El servidor maneja el mercado global de forma autónoma."""
    import random
    try:
        import datetime
        from data.event_flashback import FLASHBACK_PLAYERS
        from data.event_worldcup import WORLDCUP_PLAYERS
        from data.rosters import all_rosters as ROSTERS
        
        # Configuración de Fechas de Evento
        FB_RELEASE = datetime.datetime(2026, 12, 1, 19, 0)  # 1 de Dic
        WC_RELEASE = datetime.datetime(2026, 6, 11, 12, 0)   # 11 de Junio (Fecha oficial del Mundial)
        now = datetime.datetime.now()
        
        with market_lock:
            with open(MARKET_FILE, "r") as f:
                market = json.load(f)
            
            # --- RESOLVER SUBASTAS EXPIRADAS ---
            now_ms = int(time.time() * 1000)
            expired_auctions = [auc for auc in market if auc.get("expires", 0) <= now_ms]
            market = [auc for auc in market if auc.get("expires", 0) > now_ms]
            
            for auc in expired_auctions:
                bidder = auc.get("last_bidder")
                if bidder:
                    player = auc.get("player_data")
                    if player:
                        user_save_path = os.path.join(SAVES_DIR, f"ut_{bidder}.json")
                        if os.path.exists(user_save_path):
                            try:
                                with open(user_save_path, "r") as f_user:
                                    user_data = json.load(f_user)
                                if "club_items" not in user_data:
                                    user_data["club_items"] = {}
                                if "players" not in user_data["club_items"]:
                                    user_data["club_items"]["players"] = []
                                
                                # Entregar la carta al ganador
                                user_data["club_items"]["players"].append(player)
                                
                                with open(user_save_path, "w") as f_user:
                                    json.dump(user_data, f_user)
                                print(f"[SERVER BOT] Subasta expirada. {player.get('name')} entregado al ganador {bidder} por {auc.get('current_bid')} monedas.")
                            except Exception as ex:
                                print(f"[SERVER ERROR] No se pudo entregar jugador {player.get('name')} a {bidder}: {ex}")
                else:
                    p_name = auc.get("player_data", {}).get("name", "Item")
                    print(f"[SERVER BOT] Subasta expirada sin ofertas para {p_name}. Eliminada.")

            # 1. BOT COMPRADOR: El servidor compra cartas baratas de usuarios para generar liquidez
            for auc in market[:]:
                if auc.get("is_bot"): continue
                # El bot compra si la carta es una ganga (menos de 30% de su OVR en miles) o aleatorio (5%)
                price_threshold = auc['player_data'].get('ovr', 70) * 1200
                if auc["buy_now"] < price_threshold or random.random() < 0.05:
                    market.remove(auc)
                    print(f"[SERVER BOT] Comprada carta {auc['player_data']['name']} para control de liquidez.")

            # 2. BOT VENDEDOR: El servidor inyecta cartas nuevas para mantener el stock
            if len(market) < 450 and random.random() < 0.60:
                new_auc = _generate_bot_auction(now)
                if new_auc:
                    market.append(new_auc)

            with open(MARKET_FILE, "w") as f:
                json.dump(market, f)
    except Exception as e:
        print(f"Error en Market Bot: {e}")

def _generate_bot_auction(now=None):
    if now is None:
        now = datetime.datetime.now()
    import random
    from data.rosters import all_rosters as ROSTERS
    # Configuración de Fechas de Evento
    FB_RELEASE = datetime.datetime(2026, 12, 1, 19, 0)
    WC_RELEASE = datetime.datetime(2026, 6, 11, 12, 0)
    
    is_special_roll = random.random() < 0.20
    p_data = None
    bid = 0
    
    if is_special_roll:
        # Pool Especial (Mundial o Leyendas)
        special_pool = []
        if now >= WC_RELEASE:
            from data.event_worldcup import get_event_cards
            special_pool.extend(get_event_cards())
        if now >= FB_RELEASE:
            from data.event_flashback import get_flashback_cards
            special_pool.extend(get_flashback_cards())
        
        # Añadir Leyendas Base
        special_pool.extend(get_active_legends())
        
        if special_pool:
            p_data = random.choice(special_pool).copy()
            # Precio premium para especiales
            bid = random.randint(20000, 100000)
            if p_data.get("ovr", 0) >= 90: bid += 150000
            
    if not p_data:
        # Inyección de Jugador Base
        team_ids = list(ROSTERS.keys())
        t_id = random.choice(team_ids)
        team_players = ROSTERS[t_id]
        if team_players:
            from data.rosters import calculate_ovr
            p_data = random.choice(team_players).copy()
            p_data["ovr"] = calculate_ovr(p_data)
        bid = random.randint(500, 5000)
        
    if p_data:
        buy = bid + int(bid * 0.1) + 200
        return {
            "id": f"auc_srv_{int(time.time()*1000)}_{random.randint(10000, 99999)}",
            "seller_id": "SERVER_SYSTEM",
            "player_data": p_data,
            "current_bid": bid,
            "buy_now": buy,
            "expires": int(time.time()*1000) + (6 * 3600 * 1000),
            "is_bot": True
        }
    return None

def seed_market_if_low():
    """Rellena el mercado en el arranque con un stock mínimo si hay pocas cartas."""
    try:
        with market_lock:
            with open(MARKET_FILE, "r") as f:
                market = json.load(f)
            
            current_count = len(market)
            target = 80
            if current_count < 60:
                print(f"[SERVER BOT] Inicializando mercado. Stock actual: {current_count}. Generando {target - current_count} cartas de stock...")
                now = datetime.datetime.now()
                for _ in range(target - current_count):
                    auc = _generate_bot_auction(now)
                    if auc:
                        market.append(auc)
                with open(MARKET_FILE, "w") as f:
                    json.dump(market, f)
                print(f"[SERVER BOT] Inicialización completada. Total cartas en mercado: {len(market)}")
    except Exception as e:
        print(f"Error inicializando mercado: {e}")

# Hilo para que el mercado respire solo
import threading
def market_loop():
    while True:
        simulate_market_tick()
        time.sleep(30) # Tick cada 30 segundos

threading.Thread(target=market_loop, daemon=True).start()

if __name__ == '__main__':
    # El servidor local siempre corre en el puerto 25565 para recibir el túnel de Playit
    bind_port = 25565
    seed_market_if_low()
    print("\n" + "*"*60)
    print("      SERVIDOR ULTIMA FC - INICIALIZACIÓN COMPLETA")
    print("*"*60)
    print(f" URL BASE: http://127.0.0.1:{bind_port}")
    print(f" IP LAN:   http://{socket.gethostbyname(socket.gethostname())}:{bind_port}")
    print(f" DIRECTORIO DE DATOS: {DATA_DIR}")
    print("*"*60 + "\n")
    socketio.run(app, host='0.0.0.0', port=bind_port, debug=False, log_output=True, allow_unsafe_werkzeug=True)

