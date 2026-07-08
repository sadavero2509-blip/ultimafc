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
            pygame.mixer.set_num_channels(8)
            self.ch_sfx = pygame.mixer.Channel(0)
            self.ch_crowd = pygame.mixer.Channel(1)
            self.ch_whistle = pygame.mixer.Channel(2)
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
            "walkout": "walkout.wav"
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
        track = random.choice(self.playlist)
        try:
            pygame.mixer.music.load(track)
            pygame.mixer.music.set_volume(0.6)
            pygame.mixer.music.play(0) # Play once, endevent will trigger next
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
