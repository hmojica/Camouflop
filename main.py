import kivy
import math
import levels
import hawk
import boundary
import rabbit
import animation
import environment
import sound
from kivy.app import App
from kivy.properties import StringProperty, NumericProperty, ObjectProperty, ListProperty
from kivy.uix.widget import Widget
import kivent_cython
from kivent_cython import GameSystem
from kivy.clock import Clock
from kivy.core.window import Window
from math import radians, atan2, degrees, pi, ceil, cos, sin


class DarkBunnyGame(Widget):

    def __init__(self, **kwargs):
        super(DarkBunnyGame, self).__init__(**kwargs)
        Clock.schedule_once(self._init_game)

    def _init_game(self, dt):
        try:
            self.init_game(0)
        except:
            print 'failed: rescheduling init'
            Clock.schedule_once(self._init_game)

    def init_game(self, dt):
        self.setup_states()
        self.setup_map()
        self.set_state()

        Clock.schedule_interval(self.update, 1./60.)
        Clock.schedule_once(self.setup_stuff)

    def setup_map(self):
        self.gameworld.currentmap = self.gameworld.systems['map']

    def update(self, dt):
        self.gameworld.update(dt)

    def setup_states(self):
        self.gameworld.add_state(state_name='main', systems_added=[
            'physics_renderer2', 'physics_renderer', 'tree_physics_renderer', 'hawk_physics_renderer'],
            systems_removed=[],
            systems_paused=[], systems_unpaused=[],
            screenmanager_screen='main')

    def no_impact_collision(self, space, arbiter):
        return False

    def setup_collision_callbacks(self):
        systems = self.gameworld.systems
        physics = systems['cymunk-physics']
        rabbit_system = systems['rabbit_system']

        physics.add_collision_handler(1, 2,
            begin_func=rabbit_system.rabbit_collide_with_hole)
        physics.add_collision_handler(10, 2, begin_func=self.no_impact_collision)
        physics.add_collision_handler(1, 10, begin_func=rabbit_system.collide_white_rabbit_and_halo)
        physics.add_collision_handler(3, 2, begin_func=self.no_impact_collision)
        physics.add_collision_handler(3, 10, begin_func=self.no_impact_collision)
        physics.add_collision_handler(3, 11, begin_func=self.no_impact_collision)
        physics.add_collision_handler(1, 11, begin_func=rabbit_system.collide_rabbit_and_boundary)
        physics.add_collision_handler(10, 2, begin_func=self.no_impact_collision)
        physics.add_collision_handler(1,10, begin_func=rabbit_system.collide_white_rabbit_and_halo)
        physics.add_collision_handler(10,4,begin_func=self.no_impact_collision)
        physics.add_collision_handler(1,4, begin_func=rabbit_system.enter_shadow,
                                      separate_func=rabbit_system.leave_shadow)
        physics.add_collision_handler(3, 1, begin_func=self.no_impact_collision)
        physics.add_collision_handler(3, 5, begin_func=self.no_impact_collision)
        physics.add_collision_handler(3, 4, begin_func=self.no_impact_collision)
        physics.add_collision_handler(3, 10, begin_func=self.no_impact_collision)
        physics.add_collision_handler(10, 11, begin_func=self.no_impact_collision)
        physics.add_collision_handler(1, 3, begin_func=self.no_impact_collision,
                                      separate_func=rabbit_system.collide_rabbit_with_hawk)
        physics.add_collision_handler(4, 4, begin_func=self.no_impact_collision)
        physics.add_collision_handler(5, 4, begin_func=self.no_impact_collision)
        physics.add_collision_handler(5, 10, begin_func=self.no_impact_collision)
        physics.add_collision_handler(11, 4, begin_func=self.no_impact_collision)
        physics.add_collision_handler(2, 4, begin_func=self.no_impact_collision)

    def set_state(self):
        self.gameworld.state = 'main'

    def setup_stuff(self, dt):
        systems = self.gameworld.systems
        levels_system = systems['levels_system']
        levels_system.current_level_id = 0
        Clock.schedule_once(levels_system.generate_next_level)
        self.setup_collision_callbacks()
        self.gameworld.music_controller.play_new_song(30)


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

if __name__== '__main__':
    DarkApp().run()
