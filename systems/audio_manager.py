import pygame
import os
import random

MUSIC_END_EVENT = pygame.USEREVENT + 1

class AudioManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AudioManager, cls).__new__(cls)
            cls._instance._init()
        return cls._instance
        
    def _init(self):
        self.enabled = True
        try:
            # Init mixer explicitly just in case
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        except:
            self.enabled = False
            print("Warning: pygame.mixer could not be initialized. Audio is disabled.")
            
        self.sounds = {}
        self.playlist = []
        self.music_playing = False
        
        # Audio channels
        if self.enabled:
            pygame.mixer.set_num_channels(16)
            self.ch_sfx = pygame.mixer.Channel(0)
            self.ch_crowd = pygame.mixer.Channel(1)
            self.ch_whistle = pygame.mixer.Channel(2)
            self.ch_kick = pygame.mixer.Channel(3)
            self.ch_ui = pygame.mixer.Channel(4)
            self.ch_ambient = pygame.mixer.Channel(5)
            pygame.mixer.music.set_endevent(MUSIC_END_EVENT)
            
        self.load_all_sounds()

    def load_all_sounds(self):
        import sys
        if getattr(sys, 'frozen', False):
            exe_dir = os.path.dirname(sys.executable)
            audio_dir = os.path.join(exe_dir, "assets", "audio")
            if not os.path.exists(audio_dir):
                audio_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "audio")
        else:
            audio_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "audio")
        
        sound_files = {
            "move": "menu_move.wav",
            "select": "menu_select.wav",
            "whistle": "whistle.wav",
            "crowd": "crowd_bg.wav",
            "goal": "goal_cheer.wav",
            "walkout": "walkout.wav",
            "kick": "kick.wav",
            "pass_short": "pass_short.wav",
            "tackle": "tackle.wav",
            "post_hit": "post_hit.wav",
            "save": "save.wav",
            "card_yellow": "card_yellow.wav",
            "card_red": "card_red.wav",
            "foul_whistle": "foul_whistle.wav",
            "coin_spend": "coin_spend.wav",
            "pack_open": "pack_open.wav",
            "card_flip": "card_flip.wav",
            "error": "error.wav",
            "success": "success.wav",
            "notification": "notification.wav",
            "countdown": "countdown.wav",
            "transition": "transition.wav",
            "crowd_chant": "crowd_chant.wav",
            "crowd_boo": "crowd_boo.wav",
            "stadium_ambience": "stadium_ambience.wav",
        }
        
        for key, filename in sound_files.items():
            path = os.path.join(audio_dir, filename)
            if os.path.exists(path):
                try:
                    self.sounds[key] = pygame.mixer.Sound(path)
                except Exception as e:
                    print(f"Failed to load sound {path}: {e}")
                    
        # Load playlist (any file starting with menu_music_)
        if os.path.exists(audio_dir):
            for f in os.listdir(audio_dir):
                if f.startswith("menu_music_") and f.endswith(".wav"):
                    self.playlist.append(os.path.join(audio_dir, f))
        
        # Add original menu_music.wav if it exists
        orig_music = os.path.join(audio_dir, "menu_music.wav")
        if os.path.exists(orig_music) and orig_music not in self.playlist:
            self.playlist.append(orig_music)

    def play_sfx(self, name, volume=1.0):
        if not self.enabled or name not in self.sounds: return
        self.sounds[name].set_volume(volume)
        self.ch_sfx.play(self.sounds[name])

    def play_kick(self, volume=1.0):
        if not self.enabled or "kick" not in self.sounds: return
        self.sounds["kick"].set_volume(volume)
        self.ch_kick.play(self.sounds["kick"])

    def play_pass(self, volume=1.0):
        if not self.enabled or "pass_short" not in self.sounds: return
        self.sounds["pass_short"].set_volume(volume)
        self.ch_kick.play(self.sounds["pass_short"])

    def play_tackle(self, volume=1.0):
        if not self.enabled or "tackle" not in self.sounds: return
        self.sounds["tackle"].set_volume(volume)
        self.ch_sfx.play(self.sounds["tackle"])

    def play_post_hit(self, volume=1.0):
        if not self.enabled or "post_hit" not in self.sounds: return
        self.sounds["post_hit"].set_volume(volume)
        self.ch_sfx.play(self.sounds["post_hit"])

    def play_save(self, volume=1.0):
        if not self.enabled or "save" not in self.sounds: return
        self.sounds["save"].set_volume(volume)
        self.ch_sfx.play(self.sounds["save"])

    def play_card(self, card_type, volume=1.0):
        name = "card_yellow" if card_type.lower() == "yellow" else "card_red"
        if not self.enabled or name not in self.sounds: return
        self.sounds[name].set_volume(volume)
        self.ch_ui.play(self.sounds[name])

    def play_foul_whistle(self, volume=0.8):
        if not self.enabled or "foul_whistle" not in self.sounds: return
        self.sounds["foul_whistle"].set_volume(volume)
        self.ch_whistle.play(self.sounds["foul_whistle"])

    def play_ui(self, name, volume=1.0):
        if not self.enabled or name not in self.sounds: return
        self.sounds[name].set_volume(volume)
        self.ch_ui.play(self.sounds[name])

    def play_crowd_reaction(self, react_type, volume=0.8):
        name = "crowd_chant" if react_type.lower() == "chant" else "crowd_boo"
        if not self.enabled or name not in self.sounds: return
        self.sounds[name].set_volume(volume)
        self.ch_crowd.play(self.sounds[name])

    def play_stadium_ambience(self, volume=0.5):
        if not self.enabled or "stadium_ambience" not in self.sounds: return
        self.sounds["stadium_ambience"].set_volume(volume)
        self.ch_ambient.play(self.sounds["stadium_ambience"], loops=-1, fade_ms=1500)

    def stop_stadium_ambience(self):
        if not self.enabled: return
        self.ch_ambient.fadeout(1000)
        
    def play_whistle(self):
        if not self.enabled or "whistle" not in self.sounds: return
        self.sounds["whistle"].set_volume(0.8)
        self.ch_whistle.play(self.sounds["whistle"])

    def play_goal_cheer(self):
        if not self.enabled or "goal" not in self.sounds: return
        self.sounds["goal"].set_volume(0.9)
        self.ch_crowd.play(self.sounds["goal"])

    def start_crowd_bg(self):
        if not self.enabled or "crowd" not in self.sounds: return
        self.sounds["crowd"].set_volume(0.4)
        # Fade in crowd over 2 seconds
        self.ch_crowd.play(self.sounds["crowd"], loops=-1, fade_ms=2000)

    def stop_crowd_bg(self):
        if not self.enabled: return
        # Fade out over 1 second
        self.ch_crowd.fadeout(1000)

    def play_menu_music(self):
        if not self.enabled or not self.playlist: return
        if self.music_playing: return
        self.play_next_song()
        
    def play_next_song(self):
        if not self.enabled or not self.playlist: return
        # Filter out match/tension music from the random menu music selection
        valid_tracks = [t for t in self.playlist if "match_music_" not in os.path.basename(t)]
        if not valid_tracks:
            valid_tracks = self.playlist
        track = random.choice(valid_tracks)
        try:
            pygame.mixer.music.load(track)
            pygame.mixer.music.set_volume(0.6)
            pygame.mixer.music.play(0) # Play once, endevent will trigger next
            self.music_playing = True
        except: pass

    def play_match_tension(self):
        if not self.enabled: return
        # Find tension music track
        tension_track = None
        for t in self.playlist:
            if "match_music_tension" in os.path.basename(t):
                tension_track = t
                break
        if tension_track:
            try:
                pygame.mixer.music.load(tension_track)
                pygame.mixer.music.set_volume(0.7)
                pygame.mixer.music.play(-1) # Loop indefinitely
                self.music_playing = True
            except: pass

    def stop_menu_music(self):
        if not self.enabled or not self.music_playing: return
        try:
            pygame.mixer.music.fadeout(1000)
            self.music_playing = False
        except: pass

# Global instance
audio_manager = AudioManager()
