import kivy
import math
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
from functools import partial
from random import randint
from kivy.vector import Vector
from kivy.core.image import Image as CoreImage
from kivy.graphics import Rectangle


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

    def add_hole(self):
        position = [Window.size[0]*.95, Window.size[1]/2]
        shape_dict = {'inner_radius': 0, 'outer_radius': 10,
        'mass': 100, 'offset': (0, 0)}
        col_shape = {'shape_type': 'circle', 'elasticity': .5,
        'collision_type': 2, 'shape_info': shape_dict, 'friction': 1.0}
        col_shapes = [col_shape]
        physics_component = {'main_shape': 'circle',
        'velocity': (0, 0),
        'position': position, 'angle': 0,
        'angular_velocity': 0,
        'vel_limit': 250,
        'ang_vel_limit': radians(200),
        'mass': 0, 'col_shapes': col_shapes}
        create_component_dict = {'cymunk-physics': physics_component,
        'physics_renderer2': {'texture':
            'assets/environment/RabbitHole.png', 'size': (80, 80)},}
        component_order = ['cymunk-physics', 'physics_renderer2']
        self.gameworld.init_entity(create_component_dict, component_order)

    def add_rabbit(self):
        systems = self.gameworld.systems
        rabbit_system = systems['rabbit_system']
        rabbit_system.add_rabbit('dark_bunny')
        rabbit_system.add_rabbit('white_rabbit_1')

    def add_environment(self):
        systems = self.gameworld.systems

        environment_system = systems['environment_system']
        tree_position1 = (Window.size[0] * .5, Window.size[1] * .25)
        environment_system.add_tree(tree_position1, 'small')

        tree_position2 = (Window.size[0] * .25, Window.size[1] * .75)
        environment_system.add_tree(tree_position2, 'small')

        tree_position3 = (Window.size[0] * .75, Window.size[1] * .75)
        environment_system.add_tree(tree_position3, 'small')

        rock_position1 = (Window.size[0] * .90, Window.size[1] * .40)
        environment_system.add_rock(rock_position1)

        rock_position2 = (Window.size[0] * .85, Window.size[1] * .50)
        environment_system.add_rock(rock_position2)

        rock_position3 = (Window.size[0] * .55, Window.size[1] * .90)
        environment_system.add_rock(rock_position3)

        rock_position4 = (Window.size[0] * .55, Window.size[1] * .80)
        environment_system.add_rock(rock_position4)

        rock_position5 = (Window.size[0] * .55, Window.size[1] * .70)
        environment_system.add_rock(rock_position5)

        cloud_position1 = (Window.size[0] * .30, Window.size[1] * .20)
        environment_system.add_cloud(cloud_position1, 'large_feather', vel_max=50)

        cloud_position2 = (Window.size[0] * .60, Window.size[1] * .80)
        environment_system.add_cloud(cloud_position2, 'small_feather', vel_max=30)

        snow_position1 = (Window.size[0] * .50, Window.size[1] * .50)
        environment_system.load_snowtexture('SnowBankA', snow_position1)



    def init_game(self, dt):
        self.setup_states()
        self.setup_map()
        self.set_state()
        

        Clock.schedule_interval(self.update, 1./60.)
        Clock.schedule_once(self.setup_boundaries)
        Clock.schedule_once(self.setup_hawk)
        Clock.schedule_once(self.setup_stuff)

    def setup_hawk(self, dt):
        hawk_ai_system = self.gameworld.systems['hawk_ai_system']
        hawk_ai_system.spawn_hawk((500, 500))

    def setup_boundaries(self, dt):
        boundary_system = self.gameworld.systems['boundary_system']
        boundary_system.add_boundaries()

    def setup_map(self):
        self.gameworld.currentmap = self.gameworld.systems['map']

    def update(self, dt):
        self.gameworld.update(dt) 

    def setup_states(self):
        self.gameworld.add_state(state_name='main', systems_added=[
            'physics_renderer2', 'physics_renderer',  'tree_physics_renderer', 'hawk_physics_renderer'],
            systems_removed=[], 
            systems_paused=[], systems_unpaused=[],
            screenmanager_screen='main')

    def no_impact_collision(self, space, arbiter):
        return False

    def setup_collision_callbacks(self):
        systems = self.gameworld.systems
        physics = systems['cymunk-physics']
        rabbit_system = systems['rabbit_system']
        hawk_ai_system = systems['hawk_ai_system']
        boundary_system = systems['boundary_system']
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
        self.add_rabbit()
        self.add_hole()
        self.add_environment()
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
