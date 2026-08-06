# ⚽ Ultima FC 27

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Engine](https://img.shields.io/badge/Engine-Pygame--CE-green.svg)](https://pyga.me/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Ultima FC 27** is a feature-packed 2D football (soccer) simulation and arcade game built from the ground up in Python. Combining retro top-down arcade action with modern career simulation mechanics, custom team building, intelligent scaling AI, and online capabilities, **Ultima FC 27** delivers an immersive football experience.

---

## 🌟 Key Features

### 🧠 Progressive AI Escalation System (Levels 1–10)
- **Dynamic Difficulty**: Scales from *Aficionado* (Level 1) to *Legend* (Level 10).
- **CPU Offense**: High-level CPU opponents execute smart through-balls, one-touch passing under pressure, evasive dribbling cuts, and clinical shots placed into net corners.
- **Goalkeeper Intelligence**: Dynamic reaction times (down to 0.015s), dive speed boosts, catch bonuses, and aggressive 1v1 rush logic to close down shooting angles.
- **Multi-Player Pressing**: High difficulty triggers up to 4 simultaneous active CPU pressers with an expanded pressing radius (up to 530px).

### 📋 Custom Roster & Team Editor
- **Default Formations**: Change default tactical formations for any team (`4-3-3`, `4-4-2`, `4-2-3-1`, `3-5-2`, `5-3-2`, etc.).
- **Starting 11 Customization**: Swap starters and reserves for any club or national team in the game database.
- **Confirmation Modal**: Interactive overlay ensures explicit approval before persisting changes to disk.
- **Player Creator**: Create custom players with personalized stats, age, positions, and ratings.

### 👑 Interactive Career Mode (Player & Manager)
- **Interactive DM System**: Receive direct messages from managers, agents, and national team coaches.
- **Captaincy Milestone**: Accept or decline captaincy offers for both club and national teams via interactive choices.
- **Social Media & Sports News Feed**: Dynamic news articles, newspaper covers, and fan reactions following key career milestones and match results.
- **Transfer Market & Negotiations**: Buy, sell, contract negotiations, and wage management.

### 🃏 Ultimate Team Mode
- **Squad Building Challenges (SBCs)**: Exchange player cards to earn high-tier rewards.
- **Card Packs & Store**: Open packs to collect rare players, icons, and special items.
- **Custom Squad Management**: Chemistry, formations, and squad rating management.

---

## 🎮 Game Modes

1. **Quick Match (Amistoso)**: Instant exhibition matches with custom difficulty, teams, and match lengths.
2. **Career Mode (Modo Carrera)**: Play as a custom player or manager, leading your team through seasons, trophies, and transfer windows.
3. **Roster Editor (Modo Planteles)**: Manage starting lineups, default formations, and custom created players.
4. **Ultimate Team**: Build your dream team through card packs, SBCs, and squad optimization.
5. **Tournament & League Modes**: Compete in structured cups, leagues, and knockout competitions.

---

## 🛠️ Technology Stack

- **Core Engine**: [Pygame / Pygame-CE](https://pyga.me/) (2D rendering, event handling, sound system).
- **Language**: Python 3.10+.
- **Physics & Math**: `pygame.math.Vector2` for custom ball trajectory, player momentum, collision detection, and shooting physics.
- **Online Infrastructure**: Socket.IO & REST server components for online matchmaking and live updates.
- **Packaging & Executables**: PyInstaller with live hot-patching capabilities (`dist/UltimaFC27.exe`).

---

## 🎮 Controls & Keybindings

| Action | Keyboard Input |
| :--- | :--- |
| **Movement / Direction** | Arrow Keys / `W`, `A`, `S`, `D` |
| **Pass / Ground Pass** | `A` or `S` |
| **Through Ball** | `W` |
| **Shoot / Power Shot** | `D` or `Spacebar` |
| **Sprint** | `Left Shift` |
| **Tackle / Press** | `S` or `Spacebar` |
| **Player Switch / Team Switch** | `Q` / `E` |
| **Confirm / Select** | `Enter` |
| **Back / Pause / Menu** | `ESC` |

---

## 🚀 How to Run & Play

### Option 1: Standalone Launcher (Windows)
Run the included launcher script:
```cmd
JUGAR.bat
```

### Option 2: Run from Source
1. Clone the repository:
   ```bash
   git clone https://github.com/sadavero2509-blip/ultimafc.git
   cd ultimafc
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate   # On Windows
   # source .venv/bin/activate  # On Linux/macOS
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Launch the game:
   ```bash
   python main.py
   ```

### Option 3: Pre-compiled Executable
Run the pre-compiled executable directly from the `dist/` directory:
```cmd
dist\UltimaFC27.exe
```

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for details.
