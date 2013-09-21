import kivy
from kivy.app import App
from kivy.properties import StringProperty
from kivy.uix.widget import Widget
import kivent_cython
from kivy.clock import Clock
from kivy.core.window import Window

class DarkBunnyGame(Widget):

    def init_game(self, dt):
        self.setup_states()
        self.set_state()
        Clock.schedule_interval(self.update, 1./60.)

    def update(self, dt):
        self.gameworld.update(dt) 

    def setup_states(self):
        self.gameworld.add_state(state_name='main', systems_added=[], 
            systems_removed=[], 
            systems_paused=[], systems_unpaused=[],
            screenmanager_screen='main')

    def set_state(self):
        self.gameworld.state = 'main'


class DebugPanel(Widget):
    fps = StringProperty(None)

    def __init__(self, **kwargs):
        super(DebugPanel, self).__init__(**kwargs)
        Clock.schedule_interval(self.update_fps, .1)

    def update_fps(self,dt):
        self.fps = str(int(Clock.get_fps()))

class DarkApp(App):

    def build(self):
    	pass

if __name__== '__main__': DarkApp().run()