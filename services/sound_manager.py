import os

import pygame

from config import settings


class SoundManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SoundManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if getattr(self, "_initialized", False):
            return

        self._initialized = True
        self.sound_on = True

        sound_dir = os.path.join(settings.ASSETS_DIR, "sounds")

        self.button_sound = self._load_sound(sound_dir, "click_button.mp3", volume=0.6)
        self.move_sound = self._load_sound(sound_dir, "chess_move.mp3", volume=0.7)
        self.eat_sound = self._load_sound(sound_dir, "chess_eat.mp3", volume=0.8)

    def _load_sound(self, folder, filename, volume=1.0):
        path = os.path.join(folder, filename)
        if os.path.exists(path):
            sound = pygame.mixer.Sound(path)
            sound.set_volume(volume)
            return sound
        print(f"[SoundManager] Missing sound file: {path}")
        return None

    def play_button(self):
        if self.sound_on and self.button_sound:
            self.button_sound.play()

    def play_move(self):
        if self.sound_on and self.move_sound:
            self.move_sound.play()

    def play_eat(self):
        if self.sound_on and self.eat_sound:
            self.eat_sound.play()

    def toggle_sound(self):
        self.sound_on = not self.sound_on
        return self.sound_on

    def is_sound_on(self):
        return self.sound_on
