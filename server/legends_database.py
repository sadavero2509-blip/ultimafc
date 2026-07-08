# Base de Datos Maestra del Servidor (Leyendas Completas)
import datetime

# --- LEYENDAS BASE (EL SERVIDOR ES EL PRINCIPAL) ---
LEGENDS_BASE = [
    {'name': 'Maradonna', 'short': 'MAR', 'pot': 97, 'pos': 'CAM', 'nat': 'AR', 's': {'speed': 92, 'shot': 94, 'passing': 95, 'defense': 45, 'gk': 10, 'dribbling': 97, 'physical': 71}},
    {'name': 'Bekenbauer', 'short': 'BEC', 'pot': 94, 'pos': 'CB', 'nat': 'GER', 's': {'speed': 82, 'shot': 75, 'passing': 88, 'defense': 95, 'gk': 10, 'dribbling': 58, 'physical': 82}},
    {'name': 'Cruijff', 'short': 'CRU', 'pot': 94, 'pos': 'CF', 'nat': 'NED', 's': {'speed': 91, 'shot': 92, 'passing': 93, 'defense': 45, 'gk': 10, 'dribbling': 92, 'physical': 85}},
    {'name': 'Peléi', 'short': 'PEL', 'pot': 98, 'pos': 'ST', 'nat': 'BRA', 's': {'speed': 95, 'shot': 96, 'passing': 90, 'defense': 55, 'gk': 10, 'dribbling': 96, 'physical': 88}},
    {'name': 'Kakáh', 'short': 'KAK', 'pot': 91, 'pos': 'CAM', 'nat': 'BRA', 's': {'speed': 91, 'shot': 86, 'passing': 88, 'defense': 45, 'gk': 10, 'dribbling': 91, 'physical': 64}},
    {'name': 'Ronnaldo', 'short': 'R9N', 'pot': 96, 'pos': 'ST', 'nat': 'BRA', 's': {'speed': 97, 'shot': 95, 'passing': 81, 'defense': 45, 'gk': 10, 'dribbling': 93, 'physical': 87}},
    {'name': 'O. Kahn', 'short': 'KHA', 'pot': 92, 'pos': 'GK', 'nat': 'GER', 's': {'speed': 55, 'shot': 15, 'passing': 70, 'defense': 30, 'gk': 93, 'dribbling': 40, 'physical': 75}},
    {'name': 'Casillash', 'short': 'CAS', 'pot': 92, 'pos': 'GK', 'nat': 'ESP', 's': {'speed': 60, 'shot': 10, 'passing': 75, 'defense': 30, 'gk': 92, 'dribbling': 38, 'physical': 72}},
    {'name': 'Cechy', 'short': 'CEC', 'pot': 90, 'pos': 'GK', 'nat': 'CZE', 's': {'speed': 50, 'shot': 10, 'passing': 72, 'defense': 30, 'gk': 91, 'dribbling': 42, 'physical': 71}},
    {'name': 'Cannabaro', 'short': 'CAN', 'pot': 92, 'pos': 'CB', 'nat': 'ITA', 's': {'speed': 82, 'shot': 45, 'passing': 65, 'defense': 95, 'gk': 10, 'dribbling': 56, 'physical': 83}},
    {'name': 'Cafús', 'short': 'CAF', 'pot': 91, 'pos': 'RB', 'nat': 'BRA', 's': {'speed': 91, 'shot': 65, 'passing': 82, 'defense': 88, 'gk': 10, 'dribbling': 69, 'physical': 71}},
    {'name': 'Zanettie', 'short': 'ZAN', 'pot': 90, 'pos': 'RB', 'nat': 'AR', 's': {'speed': 84, 'shot': 60, 'passing': 85, 'defense': 89, 'gk': 10, 'dribbling': 71, 'physical': 69}},
    {'name': 'P. Lahme', 'short': 'LAH', 'pot': 91, 'pos': 'RB', 'nat': 'GER', 's': {'speed': 85, 'shot': 65, 'passing': 88, 'defense': 90, 'gk': 10, 'dribbling': 73, 'physical': 73}},
    {'name': 'R. Carloss', 'short': 'RCA', 'pot': 91, 'pos': 'LB', 'nat': 'BRA', 's': {'speed': 92, 'shot': 89, 'passing': 84, 'defense': 82, 'gk': 10, 'dribbling': 68, 'physical': 73}},
    {'name': 'Maldinni', 'short': 'MAL', 'pot': 94, 'pos': 'CB', 'nat': 'ITA', 's': {'speed': 86, 'shot': 55, 'passing': 75, 'defense': 96, 'gk': 10, 'dribbling': 58, 'physical': 90}},
    {'name': 'Matthaus', 'short': 'MAT', 'pot': 93, 'pos': 'CM', 'nat': 'GER', 's': {'speed': 88, 'shot': 89, 'passing': 90, 'defense': 90, 'gk': 10, 'dribbling': 77, 'physical': 79}},
    {'name': 'Zidanne', 'short': 'ZID', 'pot': 96, 'pos': 'CAM', 'nat': 'FRA', 's': {'speed': 84, 'shot': 91, 'passing': 96, 'defense': 65, 'gk': 10, 'dribbling': 93, 'physical': 73}},
    {'name': 'Ronaldinhu', 'short': 'DHO', 'pot': 94, 'pos': 'LW', 'nat': 'BRA', 's': {'speed': 92, 'shot': 89, 'passing': 91, 'defense': 45, 'gk': 10, 'dribbling': 96, 'physical': 62}},
    {'name': 'Iniestta', 'short': 'INI', 'pot': 91, 'pos': 'CM', 'nat': 'ESP', 's': {'speed': 80, 'shot': 78, 'passing': 92, 'defense': 65, 'gk': 10, 'dribbling': 92, 'physical': 74}},
    {'name': 'Xavi', 'short': 'XAV', 'pot': 91, 'pos': 'CM', 'nat': 'ESP', 's': {'speed': 78, 'shot': 75, 'passing': 94, 'defense': 72, 'gk': 10, 'dribbling': 73, 'physical': 76}},
    {'name': 'G. Mullere', 'short': 'MUL', 'pot': 94, 'pos': 'ST', 'nat': 'GER', 's': {'speed': 82, 'shot': 95, 'passing': 74, 'defense': 40, 'gk': 10, 'dribbling': 81, 'physical': 84}},
    {'name': 'Batistuta', 'short': 'BAT', 'pot': 90, 'pos': 'ST', 'nat': 'AR', 's': {'speed': 86, 'shot': 94, 'passing': 70, 'defense': 40, 'gk': 10, 'dribbling': 77, 'physical': 78}},
    {'name': 'Ashley Cole', 'short': 'COL', 'pot': 89, 'pos': 'LB', 'nat': 'ENG', 's': {'speed': 89, 'shot': 62, 'passing': 80, 'defense': 88, 'gk': 10, 'dribbling': 69, 'physical': 76}},
    {'name': 'Buffonne', 'short': 'BUF', 'pot': 93, 'pos': 'GK', 'nat': 'ITA', 's': {'speed': 58, 'shot': 10, 'passing': 76, 'defense': 30, 'gk': 94, 'dribbling': 43, 'physical': 76}},
    {'name': 'Van Basten', 'short': 'BAS', 'pot': 93, 'pos': 'ST', 'nat': 'NED', 's': {'speed': 84, 'shot': 94, 'passing': 78, 'defense': 40, 'gk': 10, 'dribbling': 79, 'physical': 84}},
    {'name': 'Henrie', 'short': 'HEN', 'pot': 93, 'pos': 'ST', 'nat': 'FRA', 's': {'speed': 94, 'shot': 91, 'passing': 82, 'defense': 50, 'gk': 10, 'dribbling': 89, 'physical': 83}},
    {'name': 'Franco Baresi', 'short': 'BAR', 'pot': 93, 'pos': 'CB', 'nat': 'ITA', 's': {'speed': 78, 'shot': 50, 'passing': 78, 'defense': 95, 'gk': 10, 'dribbling': 56, 'physical': 87}},
    {'name': 'Pirllo', 'short': 'PIR', 'pot': 90, 'pos': 'CM', 'nat': 'ITA', 's': {'speed': 70, 'shot': 80, 'passing': 93, 'defense': 65, 'gk': 10, 'dribbling': 71, 'physical': 72}},
    {'name': 'Raul', 'short': 'RAU', 'pot': 92, 'pos': 'CF', 'nat': 'ESP', 's': {'speed': 86, 'shot': 91, 'passing': 84, 'defense': 50, 'gk': 10, 'dribbling': 77, 'physical': 82}},
    {'name': 'Bobbie More', 'short': 'MOR', 'pot': 92, 'pos': 'CB', 'nat': 'ENG', 's': {'speed': 78, 'shot': 62, 'passing': 80, 'defense': 94, 'gk': 10, 'dribbling': 57, 'physical': 82}},
    {'name': 'Wayner Runi', 'short': 'RUN', 'pot': 91, 'pos': 'ST', 'nat': 'ENG', 's': {'speed': 86, 'shot': 92, 'passing': 82, 'defense': 65, 'gk': 10, 'dribbling': 84, 'physical': 77}},
    {'name': 'Erick Kantonah', 'short': 'KAN', 'pot': 90, 'pos': 'CF', 'nat': 'FRA', 's': {'speed': 82, 'shot': 89, 'passing': 88, 'defense': 45, 'gk': 10, 'dribbling': 85, 'physical': 78}},
    {'name': 'Andri Shevchen', 'short': 'SHE', 'pot': 91, 'pos': 'ST', 'nat': 'UKR', 's': {'speed': 91, 'shot': 93, 'passing': 75, 'defense': 40, 'gk': 10, 'dribbling': 79, 'physical': 80}},
    {'name': 'Hidetoshy Nakathe', 'short': 'NAK', 'pot': 88, 'pos': 'CAM', 'nat': 'JPN', 's': {'speed': 84, 'shot': 80, 'passing': 90, 'defense': 55, 'gk': 10, 'dribbling': 82, 'physical': 67}},
    {'name': 'Alestandro Nestah', 'short': 'NES', 'pot': 92, 'pos': 'CB', 'nat': 'ITA', 's': {'speed': 84, 'shot': 42, 'passing': 68, 'defense': 94, 'gk': 10, 'dribbling': 57, 'physical': 81}},
    {'name': 'Lev Yashinn', 'short': 'YAS', 'pot': 94, 'pos': 'GK', 'nat': 'RUS', 's': {'speed': 62, 'shot': 10, 'passing': 75, 'defense': 30, 'gk': 96, 'dribbling': 41, 'physical': 72}},
    {'name': 'M. Kloze', 'short': 'KLO', 'pot': 89, 'pos': 'ST', 'nat': 'GER', 's': {'speed': 82, 'shot': 90, 'passing': 70, 'defense': 45, 'gk': 10, 'dribbling': 73, 'physical': 81}},
    {'name': 'D. Forlanne', 'short': 'FOR', 'pot': 90, 'pos': 'ST', 'nat': 'URU', 's': {'speed': 85, 'shot': 91, 'passing': 84, 'defense': 42, 'gk': 10, 'dribbling': 78, 'physical': 83}},
    {'name': 'J. Cruyffe', 'short': 'CRU', 'pot': 94, 'pos': 'CAM', 'nat': 'NED', 's': {'speed': 91, 'shot': 89, 'passing': 92, 'defense': 45, 'gk': 10, 'dribbling': 93, 'physical': 68}},
    {'name': 'Gattuzzu', 'short': 'GAT', 'pot': 89, 'pos': 'CDM', 'nat': 'ITA', 's': {'speed': 78, 'shot': 65, 'passing': 78, 'defense': 92, 'gk': 10, 'dribbling': 71, 'physical': 93}},
    {'name': 'Bebetto', 'short': 'BEB', 'pot': 89, 'pos': 'ST', 'nat': 'BRA', 's': {'speed': 88, 'shot': 90, 'passing': 82, 'defense': 40, 'gk': 10, 'dribbling': 86, 'physical': 70}},
    {'name': 'Romarrio', 'short': 'ROM', 'pot': 93, 'pos': 'ST', 'nat': 'BRA', 's': {'speed': 92, 'shot': 95, 'passing': 78, 'defense': 35, 'gk': 10, 'dribbling': 94, 'physical': 76}},
    {'name': 'Rivalddo', 'short': 'RIV', 'pot': 91, 'pos': 'LW', 'nat': 'BRA', 's': {'speed': 89, 'shot': 92, 'passing': 88, 'defense': 45, 'gk': 10, 'dribbling': 91, 'physical': 78}},
    {'name': 'Valderramma', 'short': 'VAL', 'pot': 89, 'pos': 'CAM', 'nat': 'COL', 's': {'speed': 68, 'shot': 78, 'passing': 96, 'defense': 40, 'gk': 10, 'dribbling': 88, 'physical': 62}},
    {'name': 'F. Torress', 'short': 'TOR', 'pot': 89, 'pos': 'ST', 'nat': 'ESP', 's': {'speed': 93, 'shot': 88, 'passing': 78, 'defense': 42, 'gk': 10, 'dribbling': 84, 'physical': 78}},
    {'name': 'D. Villia', 'short': 'VIL', 'pot': 90, 'pos': 'ST', 'nat': 'ESP', 's': {'speed': 89, 'shot': 91, 'passing': 82, 'defense': 40, 'gk': 10, 'dribbling': 85, 'physical': 72}},
    {'name': 'C. Makalele', 'short': 'MAK', 'pot': 89, 'pos': 'CDM', 'nat': 'FRA', 's': {'speed': 82, 'shot': 55, 'passing': 80, 'defense': 92, 'gk': 10, 'dribbling': 76, 'physical': 88}},
    {'name': 'F. Rijkaard', 'short': 'RIJ', 'pot': 90, 'pos': 'CB', 'nat': 'NED', 's': {'speed': 80, 'shot': 75, 'passing': 84, 'defense': 91, 'gk': 10, 'dribbling': 78, 'physical': 89}},
    {'name': 'R. Gullitt', 'short': 'GUL', 'pot': 93, 'pos': 'CF', 'nat': 'NED', 's': {'speed': 86, 'shot': 90, 'passing': 91, 'defense': 82, 'gk': 10, 'dribbling': 88, 'physical': 87}},
    {'name': 'F. Lamparde', 'short': 'LAM', 'pot': 90, 'pos': 'CM', 'nat': 'ENG', 's': {'speed': 78, 'shot': 90, 'passing': 89, 'defense': 75, 'gk': 10, 'dribbling': 82, 'physical': 82}},
    {'name': 'S. Gerrarde', 'short': 'GER', 'pot': 91, 'pos': 'CM', 'nat': 'ENG', 's': {'speed': 82, 'shot': 91, 'passing': 92, 'defense': 78, 'gk': 10, 'dribbling': 84, 'physical': 86}},
    {'name': 'L. Figgo', 'short': 'FIG', 'pot': 90, 'pos': 'RW', 'nat': 'POR', 's': {'speed': 88, 'shot': 85, 'passing': 89, 'defense': 42, 'gk': 10, 'dribbling': 92, 'physical': 78}},
    {'name': 'Euzebio', 'short': 'EUS', 'pot': 93, 'pos': 'ST', 'nat': 'POR', 's': {'speed': 94, 'shot': 94, 'passing': 86, 'defense': 45, 'gk': 10, 'dribbling': 93, 'physical': 82}},
    {'name': 'Dekko', 'short': 'DEC', 'pot': 89, 'pos': 'CAM', 'nat': 'POR', 's': {'speed': 82, 'shot': 84, 'passing': 91, 'defense': 65, 'gk': 10, 'dribbling': 88, 'physical': 75}},
    {'name': 'Passarellah', 'short': 'PAS', 'pot': 91, 'pos': 'CB', 'nat': 'AR', 's': {'speed': 80, 'shot': 85, 'passing': 80, 'defense': 92, 'gk': 10, 'dribbling': 70, 'physical': 88}},
    {'name': 'I. Zamoranno', 'short': 'ZAM', 'pot': 88, 'pos': 'ST', 'nat': 'CHI', 's': {'speed': 84, 'shot': 88, 'passing': 70, 'defense': 45, 'gk': 10, 'dribbling': 76, 'physical': 88}},
    {'name': 'D. Drogbah', 'short': 'DRO', 'pot': 91, 'pos': 'ST', 'nat': 'CIV', 's': {'speed': 88, 'shot': 92, 'passing': 76, 'defense': 48, 'gk': 10, 'dribbling': 82, 'physical': 91}},
    {'name': 'F. Tottih', 'short': 'TOT', 'pot': 92, 'pos': 'CF', 'nat': 'ITA', 's': {'speed': 82, 'shot': 91, 'passing': 93, 'defense': 45, 'gk': 10, 'dribbling': 90, 'physical': 82}},
    {'name': 'D. Beckhame', 'short': 'BEC', 'pot': 89, 'pos': 'RM', 'nat': 'ENG', 's': {'speed': 80, 'shot': 87, 'passing': 95, 'defense': 70, 'gk': 10, 'dribbling': 84, 'physical': 78}},
    {'name': 'S. Eto\'oh', 'short': 'ETO', 'pot': 91, 'pos': 'ST', 'nat': 'CMR', 's': {'speed': 95, 'shot': 91, 'passing': 80, 'defense': 45, 'gk': 10, 'dribbling': 88, 'physical': 82}},
    {'name': 'R. Baggion', 'short': 'BAG', 'pot': 93, 'pos': 'CAM', 'nat': 'ITA', 's': {'speed': 86, 'shot': 90, 'passing': 91, 'defense': 40, 'gk': 10, 'dribbling': 94, 'physical': 65}},
    {'name': 'P. Scholles', 'short': 'SCH', 'pot': 89, 'pos': 'CM', 'nat': 'ENG', 's': {'speed': 74, 'shot': 88, 'passing': 92, 'defense': 72, 'gk': 10, 'dribbling': 80, 'physical': 80}},
    {'name': 'V. der Sarre', 'short': 'VDS', 'pot': 91, 'pos': 'GK', 'nat': 'NED', 's': {'speed': 55, 'shot': 10, 'passing': 84, 'defense': 30, 'gk': 92, 'dribbling': 48, 'physical': 78}},
    {'name': 'M. Platinni', 'short': 'PLA', 'pot': 93, 'pos': 'CAM', 'nat': 'FRA', 's': {'speed': 82, 'shot': 92, 'passing': 94, 'defense': 55, 'gk': 10, 'dribbling': 91, 'physical': 74}},
    {'name': 'F. Riberry', 'short': 'RIB', 'pot': 90, 'pos': 'LW', 'nat': 'FRA', 's': {'speed': 91, 'shot': 85, 'passing': 87, 'defense': 40, 'gk': 10, 'dribbling': 92, 'physical': 68}},
    {'name': 'A. Robbenn', 'short': 'ROB', 'pot': 90, 'pos': 'RW', 'nat': 'NED', 's': {'speed': 93, 'shot': 89, 'passing': 84, 'defense': 35, 'gk': 10, 'dribbling': 92, 'physical': 65}},
    {'name': 'Zicco', 'short': 'ZIC', 'pot': 92, 'pos': 'CAM', 'nat': 'BRA', 's': {'speed': 88, 'shot': 91, 'passing': 92, 'defense': 45, 'gk': 10, 'dribbling': 93, 'physical': 70}},
    {'name': 'P. Nedvedd', 'short': 'NED', 'pot': 91, 'pos': 'LM', 'nat': 'CZE', 's': {'speed': 88, 'shot': 89, 'passing': 90, 'defense': 65, 'gk': 10, 'dribbling': 87, 'physical': 84}},
    {'name': 'P. Vieirra', 'short': 'VIE', 'pot': 91, 'pos': 'CM', 'nat': 'FRA', 's': {'speed': 85, 'shot': 78, 'passing': 84, 'defense': 90, 'gk': 10, 'dribbling': 82, 'physical': 92}},
    {'name': 'L. Thurram', 'short': 'THU', 'pot': 91, 'pos': 'CB', 'nat': 'FRA', 's': {'speed': 86, 'shot': 55, 'passing': 78, 'defense': 92, 'gk': 10, 'dribbling': 72, 'physical': 89}},
    {'name': 'F. Puskash', 'short': 'PUS', 'pot': 94, 'pos': 'CF', 'nat': 'HUN', 's': {'speed': 91, 'shot': 96, 'passing': 91, 'defense': 45, 'gk': 10, 'dribbling': 92, 'physical': 78}},
    {'name': 'J. Stame', 'short': 'STA', 'pot': 89, 'pos': 'CB', 'nat': 'NED', 's': {'speed': 82, 'shot': 50, 'passing': 72, 'defense': 91, 'gk': 10, 'dribbling': 64, 'physical': 94}},
    {'name': 'Y. Tourre', 'short': 'YAY', 'pot': 89, 'pos': 'CM', 'nat': 'CIV', 's': {'speed': 82, 'shot': 86, 'passing': 88, 'defense': 84, 'gk': 10, 'dribbling': 85, 'physical': 91}},
    {'name': 'R. Ferdinnand', 'short': 'FER', 'pot': 90, 'pos': 'CB', 'nat': 'ENG', 's': {'speed': 84, 'shot': 45, 'passing': 74, 'defense': 91, 'gk': 10, 'dribbling': 68, 'physical': 86}},
    {'name': 'R. Koemman', 'short': 'KOE', 'pot': 88, 'pos': 'CB', 'nat': 'NED', 's': {'speed': 72, 'shot': 92, 'passing': 88, 'defense': 87, 'gk': 10, 'dribbling': 68, 'physical': 84}},
    {'name': 'M. Owenn', 'short': 'OWE', 'pot': 88, 'pos': 'ST', 'nat': 'ENG', 's': {'speed': 94, 'shot': 89, 'passing': 70, 'defense': 35, 'gk': 10, 'dribbling': 86, 'physical': 65}},
    {'name': 'W. Sneijdder', 'short': 'SNE', 'pot': 90, 'pos': 'CAM', 'nat': 'NED', 's': {'speed': 80, 'shot': 88, 'passing': 92, 'defense': 55, 'gk': 10, 'dribbling': 87, 'physical': 68}},
    {'name': 'C. Seedorff', 'short': 'SEE', 'pot': 90, 'pos': 'CM', 'nat': 'NED', 's': {'speed': 82, 'shot': 86, 'passing': 90, 'defense': 78, 'gk': 10, 'dribbling': 88, 'physical': 85}},
    {'name': 'Marchello', 'short': 'MAR', 'pot': 89, 'pos': 'LB', 'nat': 'BRA', 's': {'speed': 86, 'shot': 78, 'passing': 88, 'defense': 82, 'gk': 10, 'dribbling': 92, 'physical': 78}},
    {'name': 'Gutty', 'short': 'GUT', 'pot': 88, 'pos': 'CAM', 'nat': 'ESP', 's': {'speed': 78, 'shot': 82, 'passing': 92, 'defense': 55, 'gk': 10, 'dribbling': 89, 'physical': 68}},
    {'name': 'Maiconne', 'short': 'MAI', 'pot': 88, 'pos': 'RB', 'nat': 'BRA', 's': {'speed': 90, 'shot': 78, 'passing': 84, 'defense': 85, 'gk': 10, 'dribbling': 82, 'physical': 88}},
    {'name': 'F. Morienttes', 'short': 'MOR', 'pot': 87, 'pos': 'ST', 'nat': 'ESP', 's': {'speed': 82, 'shot': 88, 'passing': 74, 'defense': 45, 'gk': 10, 'dribbling': 78, 'physical': 84}},
    {'name': 'F. Inzagghi', 'short': 'INZ', 'pot': 88, 'pos': 'ST', 'nat': 'ITA', 's': {'speed': 80, 'shot': 91, 'passing': 65, 'defense': 35, 'gk': 10, 'dribbling': 76, 'physical': 72}},
    {'name': 'Gilbertho S.', 'short': 'GIL', 'pot': 87, 'pos': 'CDM', 'nat': 'BRA', 's': {'speed': 78, 'shot': 65, 'passing': 80, 'defense': 88, 'gk': 10, 'dribbling': 74, 'physical': 84}},
    {'name': 'E. Davidds', 'short': 'DAV', 'pot': 89, 'pos': 'CM', 'nat': 'NED', 's': {'speed': 86, 'shot': 78, 'passing': 82, 'defense': 86, 'gk': 10, 'dribbling': 84, 'physical': 91}},
    {'name': 'X. Alonsho', 'short': 'ALO', 'pot': 89, 'pos': 'CM', 'nat': 'ESP', 's': {'speed': 72, 'shot': 84, 'passing': 92, 'defense': 85, 'gk': 10, 'dribbling': 78, 'physical': 80}},
    {'name': 'R. V. Nistelroy', 'short': 'NIS', 'pot': 90, 'pos': 'ST', 'nat': 'NED', 's': {'speed': 84, 'shot': 92, 'passing': 72, 'defense': 40, 'gk': 10, 'dribbling': 78, 'physical': 85}},
    {'name': 'E. Hazardo', 'short': 'HAZ', 'pot': 90, 'pos': 'LW', 'nat': 'BEL', 's': {'speed': 91, 'shot': 84, 'passing': 86, 'defense': 35, 'gk': 10, 'dribbling': 92, 'physical': 66}},
    {'name': 'E. Petitte', 'short': 'PET', 'pot': 88, 'pos': 'CDM', 'nat': 'FRA', 's': {'speed': 80, 'shot': 75, 'passing': 82, 'defense': 88, 'gk': 10, 'dribbling': 76, 'physical': 86}},
    {'name': 'M. Desaillyh', 'short': 'DES', 'pot': 89, 'pos': 'CB', 'nat': 'FRA', 's': {'speed': 84, 'shot': 50, 'passing': 72, 'defense': 91, 'gk': 10, 'dribbling': 66, 'physical': 90}},
    {'name': 'P. Kluiverte', 'short': 'KLU', 'pot': 88, 'pos': 'ST', 'nat': 'NED', 's': {'speed': 84, 'shot': 88, 'passing': 78, 'defense': 42, 'gk': 10, 'dribbling': 82, 'physical': 82}},
    {'name': 'E. Cambiasso', 'short': 'CAM', 'pot': 88, 'pos': 'CDM', 'nat': 'AR', 's': {'speed': 78, 'shot': 75, 'passing': 84, 'defense': 88, 'gk': 10, 'dribbling': 80, 'physical': 84}},
    {'name': 'D. Bergkampe', 'short': 'BER', 'pot': 92, 'pos': 'CF', 'nat': 'NED', 's': {'speed': 82, 'shot': 91, 'passing': 92, 'defense': 40, 'gk': 10, 'dribbling': 92, 'physical': 78}},
    {'name': 'D. Seamman', 'short': 'SEA', 'pot': 88, 'pos': 'GK', 'nat': 'ENG', 's': {'speed': 55, 'shot': 10, 'passing': 75, 'defense': 30, 'gk': 89, 'dribbling': 44, 'physical': 75}},
    {'name': 'I. Cordobbah', 'short': 'COR', 'pot': 87, 'pos': 'CB', 'nat': 'COL', 's': {'speed': 90, 'shot': 45, 'passing': 68, 'defense': 88, 'gk': 10, 'dribbling': 62, 'physical': 84}},
    {'name': 'René Aguita', 'short': 'HIG', 'pot': 89, 'pos': 'GK', 'nat': 'COL', 's': {'speed': 72, 'shot': 30, 'passing': 82, 'defense': 40, 'gk': 90, 'dribbling': 78, 'physical': 74}},
    {'name': 'Faustino Sprilla', 'short': 'ASP', 'pot': 90, 'pos': 'ST', 'nat': 'COL', 's': {'speed': 94, 'shot': 89, 'passing': 82, 'defense': 40, 'gk': 10, 'dribbling': 92, 'physical': 80}},
    {'name': 'J. S. Parke', 'short': 'PAR', 'pot': 86, 'pos': 'LM', 'nat': 'KOR', 's': {'speed': 88, 'shot': 78, 'passing': 82, 'defense': 78, 'gk': 10, 'dribbling': 82, 'physical': 91}},
    {'name': 'B. Lizarazzu', 'short': 'LIZ', 'pot': 88, 'pos': 'LB', 'nat': 'FRA', 's': {'speed': 88, 'shot': 68, 'passing': 80, 'defense': 88, 'gk': 10, 'dribbling': 78, 'physical': 80}},
    # --- NUEVAS LEYENDAS (Lote 2) ---
    {'name': 'O. Bierhoffe', 'short': 'BIE', 'pot': 88, 'pos': 'ST', 'nat': 'GER', 's': {'speed': 80, 'shot': 89, 'passing': 70, 'defense': 35, 'gk': 10, 'dribbling': 76, 'physical': 88}},
    {'name': 'G. Meazzah', 'short': 'MEA', 'pot': 94, 'pos': 'ST', 'nat': 'ITA', 's': {'speed': 88, 'shot': 93, 'passing': 86, 'defense': 35, 'gk': 10, 'dribbling': 95, 'physical': 74}},
    {'name': 'S. Mazzolah', 'short': 'MZL', 'pot': 91, 'pos': 'CAM', 'nat': 'ITA', 's': {'speed': 84, 'shot': 86, 'passing': 90, 'defense': 48, 'gk': 10, 'dribbling': 91, 'physical': 72}},
    {'name': 'G. Riverah', 'short': 'RVR', 'pot': 92, 'pos': 'CAM', 'nat': 'ITA', 's': {'speed': 82, 'shot': 84, 'passing': 95, 'defense': 42, 'gk': 10, 'dribbling': 93, 'physical': 68}},
    {'name': 'P. Rossih', 'short': 'ROS', 'pot': 90, 'pos': 'ST', 'nat': 'ITA', 's': {'speed': 88, 'shot': 91, 'passing': 76, 'defense': 35, 'gk': 10, 'dribbling': 88, 'physical': 70}},
    {'name': 'D. Zoffe', 'short': 'ZOF', 'pot': 92, 'pos': 'GK', 'nat': 'ITA', 's': {'speed': 55, 'shot': 10, 'passing': 72, 'defense': 30, 'gk': 93, 'dribbling': 40, 'physical': 80}},
    {'name': 'G. Scireah', 'short': 'SCI', 'pot': 93, 'pos': 'CB', 'nat': 'ITA', 's': {'speed': 80, 'shot': 60, 'passing': 84, 'defense': 95, 'gk': 10, 'dribbling': 76, 'physical': 85}},
    {'name': 'G. Bergomih', 'short': 'BGM', 'pot': 90, 'pos': 'CB', 'nat': 'ITA', 's': {'speed': 82, 'shot': 50, 'passing': 70, 'defense': 91, 'gk': 10, 'dribbling': 64, 'physical': 87}},
    {'name': 'Del Pierro', 'short': 'DPI', 'pot': 91, 'pos': 'CF', 'nat': 'ITA', 's': {'speed': 83, 'shot': 89, 'passing': 88, 'defense': 40, 'gk': 10, 'dribbling': 92, 'physical': 68}},
    {'name': 'C. Vierih', 'short': 'VRI', 'pot': 90, 'pos': 'ST', 'nat': 'ITA', 's': {'speed': 84, 'shot': 91, 'passing': 70, 'defense': 38, 'gk': 10, 'dribbling': 80, 'physical': 90}},
    {'name': 'G. Viallih', 'short': 'VIA', 'pot': 89, 'pos': 'ST', 'nat': 'ITA', 's': {'speed': 82, 'shot': 88, 'passing': 76, 'defense': 42, 'gk': 10, 'dribbling': 81, 'physical': 84}},
    {'name': 'R. Donadonih', 'short': 'DON', 'pot': 89, 'pos': 'RM', 'nat': 'ITA', 's': {'speed': 86, 'shot': 78, 'passing': 88, 'defense': 55, 'gk': 10, 'dribbling': 89, 'physical': 72}},
    {'name': 'G. Zolah', 'short': 'ZOL', 'pot': 90, 'pos': 'CF', 'nat': 'ITA', 's': {'speed': 85, 'shot': 86, 'passing': 89, 'defense': 38, 'gk': 10, 'dribbling': 92, 'physical': 64}},
    {'name': 'B. Charltonne', 'short': 'CHA', 'pot': 94, 'pos': 'CAM', 'nat': 'ENG', 's': {'speed': 86, 'shot': 92, 'passing': 91, 'defense': 52, 'gk': 10, 'dribbling': 90, 'physical': 78}},
    {'name': 'G. Linekere', 'short': 'LNK', 'pot': 89, 'pos': 'ST', 'nat': 'ENG', 's': {'speed': 85, 'shot': 91, 'passing': 72, 'defense': 35, 'gk': 10, 'dribbling': 80, 'physical': 76}},
    {'name': 'K. Keeganne', 'short': 'KEE', 'pot': 92, 'pos': 'ST', 'nat': 'ENG', 's': {'speed': 89, 'shot': 90, 'passing': 82, 'defense': 45, 'gk': 10, 'dribbling': 91, 'physical': 78}},
    {'name': 'P. Gascoigneh', 'short': 'GAS', 'pot': 90, 'pos': 'CAM', 'nat': 'ENG', 's': {'speed': 82, 'shot': 84, 'passing': 89, 'defense': 50, 'gk': 10, 'dribbling': 93, 'physical': 80}},
    {'name': 'J. Barnesse', 'short': 'BRN', 'pot': 89, 'pos': 'LW', 'nat': 'ENG', 's': {'speed': 90, 'shot': 82, 'passing': 85, 'defense': 48, 'gk': 10, 'dribbling': 89, 'physical': 78}},
    {'name': 'J. Greavesse', 'short': 'GRE', 'pot': 92, 'pos': 'ST', 'nat': 'ENG', 's': {'speed': 88, 'shot': 93, 'passing': 75, 'defense': 35, 'gk': 10, 'dribbling': 86, 'physical': 72}},
    {'name': 'G. Bestt', 'short': 'BST', 'pot': 93, 'pos': 'RW', 'nat': 'NIR', 's': {'speed': 93, 'shot': 89, 'passing': 84, 'defense': 38, 'gk': 10, 'dribbling': 96, 'physical': 72}},
    {'name': 'D. Lawh', 'short': 'DLW', 'pot': 91, 'pos': 'ST', 'nat': 'SCO', 's': {'speed': 86, 'shot': 91, 'passing': 78, 'defense': 40, 'gk': 10, 'dribbling': 84, 'physical': 79}},
    {'name': 'H. Stoichkove', 'short': 'STO', 'pot': 90, 'pos': 'ST', 'nat': 'BUL', 's': {'speed': 88, 'shot': 91, 'passing': 84, 'defense': 45, 'gk': 10, 'dribbling': 88, 'physical': 82}},
    {'name': 'D. Berbatove', 'short': 'BBT', 'pot': 88, 'pos': 'ST', 'nat': 'BUL', 's': {'speed': 76, 'shot': 88, 'passing': 82, 'defense': 35, 'gk': 10, 'dribbling': 89, 'physical': 74}},
    {'name': 'G. Hagih', 'short': 'HAG', 'pot': 91, 'pos': 'CAM', 'nat': 'ROU', 's': {'speed': 84, 'shot': 90, 'passing': 92, 'defense': 42, 'gk': 10, 'dribbling': 91, 'physical': 70}},
    {'name': 'M. Laudrupe', 'short': 'MLA', 'pot': 92, 'pos': 'CAM', 'nat': 'DEN', 's': {'speed': 86, 'shot': 82, 'passing': 94, 'defense': 45, 'gk': 10, 'dribbling': 93, 'physical': 72}},
    {'name': 'B. Laudrupe', 'short': 'BLA', 'pot': 90, 'pos': 'RW', 'nat': 'DEN', 's': {'speed': 91, 'shot': 84, 'passing': 86, 'defense': 40, 'gk': 10, 'dribbling': 91, 'physical': 70}},
    {'name': 'P. Schmeichele', 'short': 'SMC', 'pot': 92, 'pos': 'GK', 'nat': 'DEN', 's': {'speed': 58, 'shot': 10, 'passing': 78, 'defense': 30, 'gk': 93, 'dribbling': 42, 'physical': 88}},
    {'name': 'Rummeniggeh', 'short': 'RUM', 'pot': 91, 'pos': 'ST', 'nat': 'GER', 's': {'speed': 89, 'shot': 91, 'passing': 82, 'defense': 45, 'gk': 10, 'dribbling': 89, 'physical': 82}},
    {'name': 'A. Brehmeh', 'short': 'BRE', 'pot': 89, 'pos': 'LB', 'nat': 'GER', 's': {'speed': 82, 'shot': 84, 'passing': 88, 'defense': 88, 'gk': 10, 'dribbling': 78, 'physical': 80}},
    {'name': 'J. Klinsmanne', 'short': 'KLI', 'pot': 89, 'pos': 'ST', 'nat': 'GER', 's': {'speed': 86, 'shot': 90, 'passing': 72, 'defense': 38, 'gk': 10, 'dribbling': 80, 'physical': 81}},
    {'name': 'S. Maiere', 'short': 'SMA', 'pot': 90, 'pos': 'GK', 'nat': 'GER', 's': {'speed': 54, 'shot': 10, 'passing': 70, 'defense': 30, 'gk': 91, 'dribbling': 40, 'physical': 76}},
    {'name': 'U. Seelere', 'short': 'USL', 'pot': 90, 'pos': 'ST', 'nat': 'GER', 's': {'speed': 80, 'shot': 90, 'passing': 74, 'defense': 40, 'gk': 10, 'dribbling': 80, 'physical': 86}},
    {'name': 'R. Krolle', 'short': 'KRO', 'pot': 90, 'pos': 'CB', 'nat': 'NED', 's': {'speed': 82, 'shot': 68, 'passing': 84, 'defense': 91, 'gk': 10, 'dribbling': 74, 'physical': 83}},
    {'name': 'J. Neeskensse', 'short': 'NEE', 'pot': 91, 'pos': 'CM', 'nat': 'NED', 's': {'speed': 84, 'shot': 82, 'passing': 86, 'defense': 85, 'gk': 10, 'dribbling': 82, 'physical': 86}},
    {'name': 'M. Overmarsse', 'short': 'OVE', 'pot': 88, 'pos': 'LW', 'nat': 'NED', 's': {'speed': 95, 'shot': 80, 'passing': 80, 'defense': 35, 'gk': 10, 'dribbling': 86, 'physical': 65}},
    {'name': 'Garrinchah', 'short': 'GAR', 'pot': 94, 'pos': 'RW', 'nat': 'BRA', 's': {'speed': 90, 'shot': 85, 'passing': 90, 'defense': 40, 'gk': 10, 'dribbling': 97, 'physical': 68}},
    {'name': 'Jairzinhu', 'short': 'JAI', 'pot': 92, 'pos': 'RW', 'nat': 'BRA', 's': {'speed': 93, 'shot': 89, 'passing': 84, 'defense': 45, 'gk': 10, 'dribbling': 91, 'physical': 82}},
    {'name': 'Djalma Santose', 'short': 'DSA', 'pot': 91, 'pos': 'RB', 'nat': 'BRA', 's': {'speed': 85, 'shot': 62, 'passing': 82, 'defense': 90, 'gk': 10, 'dribbling': 74, 'physical': 84}},
    {'name': 'Nilton Santose', 'short': 'NSA', 'pot': 91, 'pos': 'LB', 'nat': 'BRA', 's': {'speed': 86, 'shot': 72, 'passing': 84, 'defense': 88, 'gk': 10, 'dribbling': 80, 'physical': 80}},
    {'name': 'Tostaoh', 'short': 'TOS', 'pot': 90, 'pos': 'CF', 'nat': 'BRA', 's': {'speed': 84, 'shot': 86, 'passing': 88, 'defense': 42, 'gk': 10, 'dribbling': 90, 'physical': 70}},
    {'name': 'Socratesse', 'short': 'SOC', 'pot': 91, 'pos': 'CAM', 'nat': 'BRA', 's': {'speed': 80, 'shot': 88, 'passing': 92, 'defense': 55, 'gk': 10, 'dribbling': 89, 'physical': 84}},
    {'name': 'Falcaoh', 'short': 'FCO', 'pot': 90, 'pos': 'CM', 'nat': 'BRA', 's': {'speed': 80, 'shot': 80, 'passing': 92, 'defense': 80, 'gk': 10, 'dribbling': 84, 'physical': 80}},
    {'name': 'Carecah', 'short': 'CRC', 'pot': 89, 'pos': 'ST', 'nat': 'BRA', 's': {'speed': 88, 'shot': 90, 'passing': 72, 'defense': 35, 'gk': 10, 'dribbling': 84, 'physical': 80}},
    {'name': 'Taffarele', 'short': 'TAF', 'pot': 89, 'pos': 'GK', 'nat': 'BRA', 's': {'speed': 60, 'shot': 10, 'passing': 70, 'defense': 30, 'gk': 89, 'dribbling': 40, 'physical': 74}},
    {'name': 'H. Sancheze', 'short': 'HSA', 'pot': 90, 'pos': 'ST', 'nat': 'MEX', 's': {'speed': 86, 'shot': 92, 'passing': 74, 'defense': 35, 'gk': 10, 'dribbling': 85, 'physical': 76}},
    {'name': 'R. Marqueze', 'short': 'RMQ', 'pot': 89, 'pos': 'CB', 'nat': 'MEX', 's': {'speed': 74, 'shot': 70, 'passing': 84, 'defense': 90, 'gk': 10, 'dribbling': 72, 'physical': 82}},
    {'name': 'E. Francescolih', 'short': 'FRC', 'pot': 90, 'pos': 'CAM', 'nat': 'URU', 's': {'speed': 84, 'shot': 86, 'passing': 89, 'defense': 42, 'gk': 10, 'dribbling': 91, 'physical': 72}},
    {'name': 'F. Redondoh', 'short': 'RED', 'pot': 90, 'pos': 'CDM', 'nat': 'AR', 's': {'speed': 78, 'shot': 70, 'passing': 88, 'defense': 86, 'gk': 10, 'dribbling': 89, 'physical': 82}},
    {'name': 'J. Saviolah', 'short': 'SAV', 'pot': 87, 'pos': 'ST', 'nat': 'AR', 's': {'speed': 91, 'shot': 84, 'passing': 78, 'defense': 35, 'gk': 10, 'dribbling': 87, 'physical': 60}},
    {'name': 'Riquelmeh', 'short': 'RIQ', 'pot': 91, 'pos': 'CAM', 'nat': 'AR', 's': {'speed': 62, 'shot': 86, 'passing': 96, 'defense': 40, 'gk': 10, 'dribbling': 92, 'physical': 74}},
    {'name': 'G. Weahh', 'short': 'WEA', 'pot': 92, 'pos': 'ST', 'nat': 'LBR', 's': {'speed': 93, 'shot': 91, 'passing': 78, 'defense': 42, 'gk': 10, 'dribbling': 88, 'physical': 89}},
    {'name': 'R. Millah', 'short': 'RML', 'pot': 87, 'pos': 'ST', 'nat': 'CMR', 's': {'speed': 80, 'shot': 86, 'passing': 74, 'defense': 38, 'gk': 10, 'dribbling': 82, 'physical': 80}},
    {'name': 'A. Peléh', 'short': 'APE', 'pot': 89, 'pos': 'CAM', 'nat': 'GHA', 's': {'speed': 89, 'shot': 82, 'passing': 87, 'defense': 40, 'gk': 10, 'dribbling': 90, 'physical': 70}},
    {'name': 'D. Deschampse', 'short': 'DSC', 'pot': 89, 'pos': 'CDM', 'nat': 'FRA', 's': {'speed': 76, 'shot': 65, 'passing': 82, 'defense': 89, 'gk': 10, 'dribbling': 74, 'physical': 85}},
    {'name': 'Y. Djorkaeffe', 'short': 'DJO', 'pot': 88, 'pos': 'CAM', 'nat': 'FRA', 's': {'speed': 82, 'shot': 86, 'passing': 85, 'defense': 45, 'gk': 10, 'dribbling': 87, 'physical': 72}},
]

# --- CARTAS DE EVENTO ---

# Evento 1: Copa del Mundo 2026
WC_RELEASE = datetime.datetime(2026, 6, 11, 12, 0)
WC_END = datetime.datetime(2026, 7, 19, 23, 59) # Activo hasta el 19 de Julio
WC_PLAYERS = [
    # Activos con Boost
    {'name': 'Lionel Messi (WC)', 'short': 'MES', 'pot': 91, 'pos': 'RW', 'nat': 'ARG', 'card_type': 'WORLDCUP', 's': {'speed': 78, 'shot': 92, 'passing': 95, 'defense': 35, 'gk': 10, 'dribbling': 94, 'physical': 72}},
    {'name': 'Vini Jr. (WC)', 'short': 'VIN', 'pot': 92, 'pos': 'LW', 'nat': 'BRA', 'card_type': 'WORLDCUP', 's': {'speed': 98, 'shot': 88, 'passing': 85, 'defense': 35, 'gk': 10, 'dribbling': 95, 'physical': 74}},
    {'name': 'Kylian Mbappé (WC)', 'short': 'MBA', 'pot': 95, 'pos': 'LW', 'nat': 'FRA', 'card_type': 'WORLDCUP', 's': {'speed': 99, 'shot': 93, 'passing': 84, 'defense': 35, 'gk': 10, 'dribbling': 94, 'physical': 78}},
    {'name': 'Lamine Yamal (WC)', 'short': 'LAM', 'pot': 91, 'pos': 'RW', 'nat': 'ESP', 'card_type': 'WORLDCUP', 's': {'speed': 94, 'shot': 85, 'passing': 88, 'defense': 40, 'gk': 10, 'dribbling': 92, 'physical': 64}},
    {'name': 'Jude Bellingham (WC)', 'short': 'BEL', 'pot': 92, 'pos': 'CM', 'nat': 'ENG', 'card_type': 'WORLDCUP', 's': {'speed': 84, 'shot': 86, 'passing': 88, 'defense': 84, 'gk': 10, 'dribbling': 87, 'physical': 82}},
    {'name': 'Cristiano Ronaldo (WC)', 'short': 'CR7', 'pot': 88, 'pos': 'ST', 'nat': 'POR', 'card_type': 'WORLDCUP', 's': {'speed': 80, 'shot': 92, 'passing': 80, 'defense': 35, 'gk': 10, 'dribbling': 84, 'physical': 82}},
    {'name': 'Luis Díaz (WC)', 'short': 'DIA', 'pot': 89, 'pos': 'LW', 'nat': 'COL', 'card_type': 'WORLDCUP', 's': {'speed': 95, 'shot': 85, 'passing': 80, 'defense': 45, 'gk': 10, 'dribbling': 91, 'physical': 76}},
    {'name': 'James Rodríguez (WC)', 'short': 'JAM', 'pot': 88, 'pos': 'CM', 'nat': 'COL', 'card_type': 'WORLDCUP', 's': {'speed': 65, 'shot': 88, 'passing': 94, 'defense': 45, 'gk': 10, 'dribbling': 88, 'physical': 72}},
    
    # Leyendas del Mundial
    {'name': 'Pelé (WC_LEG)', 'short': 'PEL', 'pot': 99, 'pos': 'ST', 'nat': 'BRA', 'card_type': 'WORLDCUP_LEGEND', 's': {'speed': 96, 'shot': 97, 'passing': 91, 'defense': 55, 'gk': 10, 'dribbling': 99, 'physical': 88}},
    {'name': 'Ronaldo (WC_LEG)', 'short': 'R9', 'pot': 97, 'pos': 'ST', 'nat': 'BRA', 'card_type': 'WORLDCUP_LEGEND', 's': {'speed': 98, 'shot': 96, 'passing': 82, 'defense': 45, 'gk': 10, 'dribbling': 98, 'physical': 85}},
    {'name': 'Diego Maradona (WC_LEG)', 'short': 'DIE', 'pot': 98, 'pos': 'CAM', 'nat': 'ARG', 'card_type': 'WORLDCUP_LEGEND', 's': {'speed': 93, 'shot': 95, 'passing': 96, 'defense': 45, 'gk': 10, 'dribbling': 98, 'physical': 78}},
    {'name': 'Zinedine Zidane (WC_LEG)', 'short': 'ZIZ', 'pot': 96, 'pos': 'CAM', 'nat': 'FRA', 'card_type': 'WORLDCUP_LEGEND', 's': {'speed': 85, 'shot': 92, 'passing': 97, 'defense': 65, 'gk': 10, 'dribbling': 92, 'physical': 82}},
    {'name': 'Andrés Iniesta (WC_LEG)', 'short': 'INI', 'pot': 93, 'pos': 'CM', 'nat': 'ESP', 'card_type': 'WORLDCUP_LEGEND', 's': {'speed': 81, 'shot': 79, 'passing': 93, 'defense': 65, 'gk': 10, 'dribbling': 94, 'physical': 70}},
]

# Evento 2: Retro Herencia
HERITAGE_RELEASE = datetime.datetime(2026, 9, 26, 15, 0)
HERITAGE_END = HERITAGE_RELEASE + datetime.timedelta(weeks=4) # 4 semanas de vigencia
HERITAGE_PLAYERS = [
    {'name': 'Erick Kantonah (HERENCIA)', 'short': 'KAN', 'pot': 92, 'pos': 'CF', 'nat': 'FRA', 'card_type': 'RETRO_HERITAGE', 's': {'speed': 84, 'shot': 91, 'passing': 90, 'defense': 48, 'gk': 10, 'dribbling': 76, 'physical': 76}},
    {'name': 'Lev Yashinn (HERENCIA)', 'short': 'YAS', 'pot': 96, 'pos': 'GK', 'nat': 'RUS', 'card_type': 'RETRO_HERITAGE', 's': {'speed': 65, 'shot': 10, 'passing': 78, 'defense': 30, 'gk': 98, 'dribbling': 40, 'physical': 74}},
    {'name': 'Alestandro Nestah (HERENCIA)', 'short': 'NES', 'pot': 94, 'pos': 'CB', 'nat': 'ITA', 'card_type': 'RETRO_HERITAGE', 's': {'speed': 86, 'shot': 42, 'passing': 70, 'defense': 96, 'gk': 10, 'dribbling': 54, 'physical': 84}},
    {'name': 'Bekenbauer (HERENCIA)', 'short': 'BEC', 'pot': 96, 'pos': 'CB', 'nat': 'GER', 'card_type': 'RETRO_HERITAGE', 's': {'speed': 84, 'shot': 78, 'passing': 90, 'defense': 97, 'gk': 10, 'dribbling': 59, 'physical': 89}},
    {'name': 'Peléi (HERENCIA)', 'short': 'PEL', 'pot': 99, 'pos': 'ST', 'nat': 'BRA', 'card_type': 'RETRO_HERITAGE', 's': {'speed': 97, 'shot': 98, 'passing': 92, 'defense': 55, 'gk': 10, 'dribbling': 98, 'physical': 90}}
]

# Evento 3: Flashback (Crónicas del Tiempo)
FLASHBACK_RELEASE = datetime.datetime(2026, 12, 1, 0, 0)
FLASHBACK_END = FLASHBACK_RELEASE + datetime.timedelta(weeks=4) # 4 semanas de vigencia
FLASHBACK_PLAYERS = [
    {'name': 'Lionel Messi (FLASHBACK)', 'short': 'MES', 'pot': 91, 'pos': 'RW', 'nat': 'ARG', 'card_type': 'FLASHBACK', 's': {'speed': 96, 'shot': 90, 'passing': 94, 'defense': 38, 'gk': 10, 'dribbling': 98, 'physical': 68}},
    {'name': 'Kylian Mbappé (FLASHBACK)', 'short': 'MBA', 'pot': 88, 'pos': 'ST', 'nat': 'FRA', 'card_type': 'FLASHBACK', 's': {'speed': 97, 'shot': 85, 'passing': 78, 'defense': 36, 'gk': 10, 'dribbling': 89, 'physical': 72}},
    {'name': 'Lamine Yamal (FLASHBACK)', 'short': 'LAM', 'pot': 90, 'pos': 'RW', 'nat': 'ESP', 'card_type': 'FLASHBACK', 's': {'speed': 94, 'shot': 86, 'passing': 88, 'defense': 45, 'gk': 10, 'dribbling': 93, 'physical': 70}},
    {'name': 'Wayne Rooney (FLASHBACK)', 'short': 'ROO', 'pot': 89, 'pos': 'ST', 'nat': 'ENG', 'card_type': 'FLASHBACK', 'is_legend': True, 's': {'speed': 91, 'shot': 88, 'passing': 78, 'defense': 50, 'gk': 10, 'dribbling': 84, 'physical': 86}},
    {'name': 'Ronaldo (FLASHBACK)', 'short': 'R9', 'pot': 91, 'pos': 'ST', 'nat': 'BRA', 'card_type': 'FLASHBACK', 'is_legend': True, 's': {'speed': 99, 'shot': 87, 'passing': 75, 'defense': 30, 'gk': 10, 'dribbling': 94, 'physical': 75}},
    {'name': 'Diego Maradona (FLASHBACK)', 'short': 'DIE', 'pot': 91, 'pos': 'CAM', 'nat': 'ARG', 'card_type': 'FLASHBACK', 'is_legend': True, 's': {'speed': 97, 'shot': 88, 'passing': 90, 'defense': 40, 'gk': 10, 'dribbling': 98, 'physical': 74}},
    {'name': 'Neymar Jr (FLASHBACK)', 'short': 'NEY', 'pot': 90, 'pos': 'LW', 'nat': 'BRA', 'card_type': 'FLASHBACK', 's': {'speed': 96, 'shot': 88, 'passing': 84, 'defense': 35, 'gk': 10, 'dribbling': 96, 'physical': 80}},
    {'name': 'Cristiano Ronaldo (FLASHBACK)', 'short': 'CR7', 'pot': 91, 'pos': 'LM', 'nat': 'POR', 'card_type': 'FLASHBACK', 's': {'speed': 97, 'shot': 94, 'passing': 80, 'defense': 38, 'gk': 10, 'dribbling': 90, 'physical': 86}},
]

def get_active_legends():
    """Devuelve el pool de jugadores disponibles según la fecha actual y su tiempo de vigencia."""
    now = datetime.datetime.now()
    pool = LEGENDS_BASE.copy()
    
    # Inyectar World Cup (Hasta el 19 de Julio)
    if WC_RELEASE <= now <= WC_END:
        pool.extend(WC_PLAYERS)
        
    # Inyectar Herencia (4 semanas)
    if HERITAGE_RELEASE <= now <= HERITAGE_END:
        pool.extend(HERITAGE_PLAYERS)
        
    # Inyectar Flashback (4 semanas)
    if FLASHBACK_RELEASE <= now <= FLASHBACK_END:
        pool.extend(FLASHBACK_PLAYERS)
        
    return pool

def get_historical_legends():
    """Devuelve el pool COMPLETO de todas las leyendas y eventos históricos (pasados y presentes)."""
    pool = LEGENDS_BASE.copy()
    pool.extend(WC_PLAYERS)
    pool.extend(HERITAGE_PLAYERS)
    pool.extend(FLASHBACK_PLAYERS)
    return pool




