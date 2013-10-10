import kivy
import math
import levels
import hawk
import boundary
import rabbit
import editor
import animation
import numpad
import environment
import sound
from kivy.app import App
from kivy.properties import (StringProperty, NumericProperty, 
    ObjectProperty, ListProperty, BooleanProperty, DictProperty)
from kivy.uix.widget import Widget
from kivy.uix.label import Label
import kivent_cython
from kivent_cython import GameSystem, GameScreen
from kivy.clock import Clock
from kivy.core.window import Window
from math import radians, atan2, degrees, pi, ceil, cos, sin


class SliderSetting(Widget):
    slider_name = StringProperty('default')
    slider_value = NumericProperty(1.)


class Timer(Widget):
    timer_count = NumericProperty(10)

    def start_timer(self):
        Clock.schedule_once(self.decrement_timer, 1.0)

    def decrement_timer(self, dt):
        if self.timer_count > 0:
            self.timer_count -= 1
            Clock.schedule_once(self.decrement_timer, 1.0)
        else:
            self.timer_count = 10
        

class MainScreen(GameScreen):
    timer = ObjectProperty(None)
    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)

    def add_timer(self):
        if not self.timer:
            self.timer = Timer()
        self.layout.add_widget(self.timer)
        self.timer.start_timer()
        Clock.schedule_once(self.remove_timer, 10.)
        self.timer.pos_hint = {'x': .4, 'y': .4}
        self.timer.size_hint = (.2, .2)

    def remove_timer(self, dt):
        self.layout.remove_widget(self.timer)


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
            'physics_renderer2', 
            'rabbit_system', 'physics_renderer', 'shadow_renderer',
            'tree_physics_renderer', 'hawk_physics_renderer',],
            systems_removed=[],
            systems_paused=[], systems_unpaused=['cymunk-physics', 
            'physics_renderer2', 'physics_renderer', 
            'tree_physics_renderer', 'hawk_physics_renderer',
            'animation_system', 'shadow_renderer', 'hawk_ai_system', 
            'rabbit_system', 'default_gameview'],
            screenmanager_screen='main')
        self.gameworld.add_state(state_name='menu', systems_added=[],
            systems_removed=['physics_renderer2', 'physics_renderer', 
            'tree_physics_renderer', 'hawk_physics_renderer', 
            'shadow_renderer', 'rabbit_system'],
            systems_paused=['cymunk-physics', 'physics_renderer2', 
            'physics_renderer', 'tree_physics_renderer', 
            'hawk_physics_renderer', 
            'shadow_renderer', 'animation_system', 'hawk_ai_system', 
            'rabbit_system'], systems_unpaused=[],
            screenmanager_screen='menu')
        self.gameworld.add_state(state_name='settings', systems_added=[],
            systems_removed=['physics_renderer2', 'physics_renderer', 
            'tree_physics_renderer', 'hawk_physics_renderer', 
            'shadow_renderer', 'rabbit_system'],
            systems_paused=['cymunk-physics', 'physics_renderer2', 
            'physics_renderer', 'tree_physics_renderer', 
            'hawk_physics_renderer', 
            'shadow_renderer', 'animation_system', 'hawk_ai_system', 
            'rabbit_system'], systems_unpaused=[],
            screenmanager_screen='settings')
        self.gameworld.add_state(state_name='gameover', systems_added=[],
            systems_removed=['physics_renderer2', 'physics_renderer', 
            'tree_physics_renderer', 'hawk_physics_renderer', 
            'shadow_renderer', 'rabbit_system'],
            systems_paused=['cymunk-physics', 'physics_renderer2', 
            'physics_renderer', 'tree_physics_renderer', 
            'hawk_physics_renderer', 
            'shadow_renderer', 'animation_system', 'hawk_ai_system', 
            'rabbit_system'], systems_unpaused=[],
            screenmanager_screen='gameover')
        self.gameworld.add_state(state_name='pause', systems_added=[],
            systems_removed=['physics_renderer2', 'physics_renderer', 
            'tree_physics_renderer', 'hawk_physics_renderer', 
            'shadow_renderer', 'rabbit_system'],
            systems_paused=['cymunk-physics', 'physics_renderer2', 
            'physics_renderer', 'tree_physics_renderer', 
            'hawk_physics_renderer', 
            'shadow_renderer', 'animation_system', 'hawk_ai_system', 
            'rabbit_system'], systems_unpaused=[],
            screenmanager_screen='pause')
        self.gameworld.add_state(state_name='credits', systems_added=[],
            systems_removed=['physics_renderer2', 'physics_renderer', 
            'tree_physics_renderer', 'hawk_physics_renderer', 
            'shadow_renderer', 'rabbit_system'],
            systems_paused=['cymunk-physics', 'physics_renderer2', 
            'physics_renderer', 'tree_physics_renderer', 
            'hawk_physics_renderer', 'shadow_renderer', 
            'animation_system', 'hawk_ai_system', 
            'rabbit_system'], systems_unpaused=[],
            screenmanager_screen='credits')
        self.gameworld.add_state(state_name='editor', systems_added=[
            'physics_renderer2', 'physics_renderer', 'shadow_renderer', 
            'tree_physics_renderer', 'hawk_physics_renderer',],
            systems_removed=['rabbit_system'],
            systems_paused=['animation_system', 'hawk_ai_system', 
            'rabbit_system'], systems_unpaused=['cymunk-physics', 
            'physics_renderer2', 'physics_renderer', 
            'tree_physics_renderer', 'hawk_physics_renderer', 
            'shadow_renderer',],
            screenmanager_screen='editor')

    def no_impact_collision(self, space, arbiter):
        return False

    def start_game(self):
        self.gameworld.state = 'main'
        systems = self.gameworld.systems
        gameview = systems['default_gameview']
        gameview.focus_entity = True
        
    def pause_game(self):
        self.gameworld.state = 'pause'

    def open_editor(self):
        systems = self.gameworld.systems
        levels_system = systems['levels_system']
        self.gameworld.state = 'editor'
        levels_system.clear_gameworld_objects()
        gameview = systems['default_gameview']
        gameview.focus_entity = False

    def set_game_over(self):
        self.gameworld.state = 'gameover'
        systems = self.gameworld.systems
        levels_system = systems['levels_system']
        levels_system.current_level_id = 0
        
    def setup_collision_callbacks(self):
        systems = self.gameworld.systems
        physics = systems['cymunk-physics']
        rabbit_system = systems['rabbit_system']
        physics.add_collision_handler(1, 2,
            begin_func=rabbit_system.rabbit_collide_with_hole)
        physics.add_collision_handler(
            10, 2, begin_func=self.no_impact_collision)
        physics.add_collision_handler(
            1, 10, begin_func=rabbit_system.collide_white_rabbit_and_halo)
        physics.add_collision_handler(
            3, 2, begin_func=self.no_impact_collision)
        physics.add_collision_handler(
            3, 10, begin_func=self.no_impact_collision)
        physics.add_collision_handler(
            3, 11, begin_func=self.no_impact_collision)
        physics.add_collision_handler(
            1, 11, begin_func=rabbit_system.collide_rabbit_and_boundary)
        physics.add_collision_handler(
            10, 2, begin_func=self.no_impact_collision)
        physics.add_collision_handler(
            1,10, begin_func=rabbit_system.collide_white_rabbit_and_halo)
        physics.add_collision_handler(
            10,4,begin_func=self.no_impact_collision)
        physics.add_collision_handler(
            1,4, begin_func=rabbit_system.enter_shadow,
            separate_func=rabbit_system.leave_shadow)
        physics.add_collision_handler(
            3, 1, begin_func=self.no_impact_collision)
        physics.add_collision_handler(
            3, 5, begin_func=self.no_impact_collision)
        physics.add_collision_handler(
            3, 4, begin_func=self.no_impact_collision)
        physics.add_collision_handler(
            3, 10, begin_func=self.no_impact_collision)
        physics.add_collision_handler(
            10, 11, begin_func=self.no_impact_collision)
        physics.add_collision_handler(
            1, 3, begin_func=self.no_impact_collision,
            separate_func=rabbit_system.collide_rabbit_with_hawk)
        physics.add_collision_handler(
            4, 4, begin_func=self.no_impact_collision)
        physics.add_collision_handler(
            5, 4, begin_func=self.no_impact_collision)
        physics.add_collision_handler(
            5, 10, begin_func=self.no_impact_collision)
        physics.add_collision_handler(
            11, 4, begin_func=self.no_impact_collision)
        physics.add_collision_handler(
            2, 4, begin_func=self.no_impact_collision)

    def set_state(self):
        self.gameworld.state = 'menu'

    def open_settings(self):
        self.gameworld.state = 'settings'

    def open_credits(self):
        self.gameworld.state = 'credits'

    def setup_stuff(self, dt):
        systems = self.gameworld.systems
        levels_system = systems['levels_system']
        levels_system.current_level_id = 0
        self.setup_collision_callbacks()
        #self.gameworld.music_controller.play_new_song(30)

    def generate_level(self):
        systems = self.gameworld.systems
        levels_system = systems['levels_system']
        Clock.schedule_once(levels_system.generate_next_level)


class DebugPanel(Widget):
    fps = StringProperty(None)

    def __init__(self, **kwargs):
        super(DebugPanel, self).__init__(**kwargs)
        Clock.schedule_interval(self.update_fps, .1)

    def update_fps(self,dt):
        self.fps = str(int(Clock.get_fps()))


class DarkApp(App):
    music_level = NumericProperty(1.)
    sound_level = NumericProperty(1.)

    def build(self):
        pass

if __name__== '__main__':

    DarkApp().run()

