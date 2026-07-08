import os, json
DATA_DIR = "server_data"
MARKET_FILE = os.path.join(DATA_DIR, "market.json")
if os.path.exists(MARKET_FILE):
    with open(MARKET_FILE, "r") as f:
        data = json.load(f)
        print(json.dumps(data[:3], indent=2))
else:
    print("Market file not found")
