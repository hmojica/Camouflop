from kivy.clock import Clock
from kivy.properties import StringProperty, BooleanProperty, NumericProperty
import random
from kivy.core.audio import SoundLoader
from kivy.uix.widget import Widget
from kivent_cython import (GameSystem)


class SoundSystem(GameSystem):
    sound_dir = StringProperty('assets/sound_fx/')
    volume = NumericProperty(1.)

    def __init__(self, **kwargs):
        super(SoundSystem, self).__init__(**kwargs)
        self.sound_dict = {}
        self.sound_names = ['bunny_eats_something', 'bunny_powerup', 'hawk_diving',
        'hawk_diving', 'hawk_victory', 'rabbit', 'rabbit_in_snow', 'rabbit_on_ice',
        'rabbit_on_wood', 'rabbit_victory', 'white_rabbits', 'wind_in_the_background', 
        'hawkcry']
        self.load_music(0)

    def on_volume(self, instance, value):
        for track in self.sound_names:
            self.sound_dict[track].volume = value
        
    def load_music(self, dt):
        sound_names = self.sound_names
        sound_dict = self.sound_dict
        sound_dir = self.sound_dir
        reset_sound_position = self.reset_sound_position
        for sound_name in sound_names:
            sound_dict[sound_name] = SoundLoader.load(sound_dir + sound_name + '.ogg')
            sound_dict[sound_name].seek(0)
            sound_dict[sound_name].bind(on_stop=reset_sound_position)

    def reset_sound_position(self, value):
        value.seek(0)

    def schedule_play(self, sound_name, dt):
        self.play(sound_name)

    def play(self, sound_name):
        sound_dict = self.sound_dict
        if sound_name in sound_dict:
            sound_dict[sound_name].play()
        else:
            print "file",sound_name,"not found in", self.sound_dir

    def stop(self, sound_name):
        sound_dict = self.sound_dict
        if sound_name in sound_dict:
            sound_dict[sound_name].stop()
        else:
            print "file", sound_name, "not found in", self.sound_dir

class MusicController(Widget):
    music_dir = StringProperty('assets/music/')
    song_is_playing = BooleanProperty(False)
    volume = NumericProperty(1.)

    def __init__(self, **kwargs):
        super(MusicController, self).__init__(**kwargs)
        self.music_dict = {}
        self.track_names = ['rabbittrack1', 'rabbittrack2', 'rabbittrack3', 'rabbittrack4']
        self.load_music(0)

    def on_volume(self, instance, value):
        for track in self.track_names:
            self.music_dict[track].volume = value
        
    def load_music(self, dt):
        track_names = self.track_names
        music_dict = self.music_dict
        for track_name in track_names:
            music_dict[track_name] = SoundLoader.load(self.music_dir + track_name + '.ogg')
            music_dict[track_name].seek(0)

    def check_if_songs_are_playing(self):
        music_dict = self.music_dict
        for track in music_dict:
            if music_dict[track].state == 'play':
                return True
        else: 
            return False

    def play_new_song(self, dt):
        if not self.check_if_songs_are_playing():
            self.play(random.choice(self.track_names))

    def schedule_choose_new_song(self, value):
        start_delay = random.random() * 20.0
        value.seek(0)
        Clock.schedule_once(self.play_new_song, start_delay)
        
    def play(self, sound_name):
        if sound_name in self.music_dict:
            self.music_dict[sound_name].play()
            self.music_dict[sound_name].bind(on_stop=self.schedule_choose_new_song)
        else:
            print "file",sound_name,"not found in", self.music_dir

    def stop(self, sound_name):
        if sound_name in self.music_dict:
            self.music_dict[sound_name].stop()
        else:
            print "file", sound_name, "not found in", self.music_dir
