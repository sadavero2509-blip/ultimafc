# Diccionario de descripciones de posiciones
POSITIONS_INFO = {
    "GK": "Portero: El guardián del arco. Único jugador autorizado a usar las manos dentro de su área.",
    "CB": "Central: El muro defensivo. Su prioridad es interceptar ataques y despejar el peligro.",
    "LB": "Lateral Izquierdo: Defensor de banda que equilibra la marca con proyecciones ofensivas.",
    "RB": "Lateral Derecho: Defensor de banda encargado de frenar extremos y centrar balones.",
    "CDM": "Pivote: Mediocentro defensivo. El ancla del equipo, recupera balones y cubre a los defensas.",
    "CM": "Mediocentro: El motor del equipo. Distribuye el juego y conecta la defensa con el ataque.",
    "CAM": "Mediapunta: El creador. Jugador de gran visión encargado del último pase y llegada al área.",
    "LW": "Extremo Izquierdo: Velocista de banda. Busca desbordar y enviar centros o diagonales al arco.",
    "RW": "Extremo Derecho: Especialista en velocidad y regate por banda derecha para romper defensas.",
    "ST": "Delantero Centro: El goleador. Su misión principal es finalizar las jugadas y marcar goles.",
    "CF": "Segundo Delantero: Atacante móvil que juega entre líneas, apoyando al punta y creando espacios.",
    "LWB": "Carrilero Izquierdo: Lateral con funciones ofensivas agresivas, cubriendo toda la banda.",
    "RWB": "Carrilero Derecho: Especialista en recorrido largo por banda derecha, defensa y ataque total.",
    "LM": "Interior Izquierdo: Centrocampista de banda que aporta equilibrio y centros desde la izquierda.",
    "RM": "Interior Derecho: Jugador de banda que combina trabajo defensivo con apoyo en construcción."
}

def get_pos_desc(pos):
    return POSITIONS_INFO.get(pos, "Posición táctica en el campo de juego.")
