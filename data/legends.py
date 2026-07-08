# Sincronización automática: EL SERVIDOR ES EL PRINCIPAL
import sys
import os

# Asegurar que podamos importar desde la carpeta 'server'
root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_path not in sys.path:
    sys.path.append(root_path)

try:
    from server.legends_database import LEGENDS_BASE as LEGENDS
except ImportError:
    # Fallback si el servidor no está accesible o hay problemas de ruta
    print("WARNING: No se pudo conectar con el servidor de leyendas. Usando base vacía.")
    LEGENDS = []

for p in LEGENDS:
    # Asegurar compatibilidad de campos (el local espera 'age' y 'num')
    if 'age' not in p: p['age'] = 28
    if 'num' not in p: p['num'] = 10
    
    p["is_legend"] = True
    from .rosters import calculate_ovr
    p["ovr"] = calculate_ovr(p)
    p["rarity"] = "LEYENDA"
