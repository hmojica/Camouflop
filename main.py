import kivy
from kivy.app import App
from kivy.properties import StringProperty, NumericProperty
from kivy.uix.widget import Widget
import kivent_cython
from kivent_cython import GameSystem
from kivy.clock import Clock
from kivy.core.window import Window
from math import radians, atan2, degrees, pi
from functools import partial
from kivy.vector import Vector

class RabbitSystem(GameSystem):
    system_id = StringProperty('rabbit_system')
    rabbit = NumericProperty(None, allownone=True)

    def __init__(self, **kwargs):
        super(RabbitSystem, self).__init__(**kwargs)
        self.setup_rabbit_dicts()

    def setup_rabbit_dicts(self):
        self.rabbit_dicts = rabbit_dicts = {}
        dark_bunny_physics_renderer = dict(texture='rabbit.png', size=(64, 64))
        white_rabbit_physics_renderer = dict(texture='rabbit.png', size=(64, 64))
        rabbit_dicts['dark_bunny'] = {'outer_radius': 32, 'mass': 50, 'x': 100, 'y': 100,
                                      'angle': 0, 'vel_limit': 250, 'physics_renderer': dark_bunny_physics_renderer}
        rabbit_dicts['white_rabbit_1'] = {'outer_radius': 32, 'mass': 50, 'x': 100, 'y': 400,
                                        'angle': 0, 'vel_limit': 250, 'physics_renderer': white_rabbit_physics_renderer}

    def rabbit_collide_with_hole(self, space, arbiter):
        gameworld = self.gameworld
        entities = gameworld.entities
        rabbit_id = arbiter.shapes[0].body.data
        hole_id = arbiter.shapes[1].body.data
        rabbit_entity = entities[rabbit_id]
        hole_entity = entities[hole_id]
        rabbit_position = rabbit_entity['cymunk-physics']['position']
        hole_position = hole_entity['cymunk-physics']['position']
        Clock.schedule_once(partial(gameworld.timed_remove_entity, rabbit_id))
        self.rabbit = None
        return False

    def add_rabbit(self, rabbit_type):
        rabbit_info = self.rabbit_dicts[rabbit_type]
        x = rabbit_info['x']
        y = rabbit_info['y']
        shape_dict = {'inner_radius': 0, 'outer_radius': rabbit_info['outer_radius'],
            'mass': rabbit_info['mass'], 'offset': (0, 0)}
        col_shape = {'shape_type': 'circle', 'elasticity': .5, 
        'collision_type': 1, 'shape_info': shape_dict, 'friction': 1.0}
        col_shapes = [col_shape]
        physics_component = {'main_shape': 'circle', 
        'velocity': (0, 0), 
        'position': (x, y), 'angle': rabbit_info['angle'],
        'angular_velocity': 0, 
        'vel_limit': rabbit_info['vel_limit'],
        'ang_vel_limit': radians(200), 
        'mass': 50, 'col_shapes': col_shapes}
        rabbit_system = {''}
        create_component_dict = {'cymunk-physics': physics_component, 
        'physics_renderer': rabbit_info['physics_renderer'],}
        component_order = ['cymunk-physics', 'physics_renderer']
        entity_id = self.gameworld.init_entity(create_component_dict, component_order)
        if rabbit_type == 'dark_bunny':
            self.rabbit = entity_id

    def on_touch_down(self, touch):
        if self.rabbit != None:
            rabbit = self.gameworld.entities[self.rabbit]
            rabbit_position = rabbit['cymunk-physics']['position']
            XDistance =  (rabbit_position[0]) - touch.x
            YDistance =  (rabbit_position[1]) - touch.y
            rotation = atan2(YDistance, XDistance) 
            body = rabbit['cymunk-physics']['body']
            body.reset_forces()
            body.velocity = (0, 0)
            body.angle = (rotation) - pi
            unit_vector = body.rotation_vector
            force_offset = unit_vector[0] * -1 * 32, unit_vector[1] * -1 * 32
            force = 1000*unit_vector[0], 1000*unit_vector[1]
            body.apply_force(force, force_offset)

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
        x = 500
        y = 100
        shape_dict = {'inner_radius': 0, 'outer_radius': 10, 
        'mass': 100, 'offset': (0, 0)}
        col_shape = {'shape_type': 'circle', 'elasticity': .5, 
        'collision_type': 2, 'shape_info': shape_dict, 'friction': 1.0}
        col_shapes = [col_shape]
        physics_component = {'main_shape': 'circle', 
        'velocity': (0, 0), 
        'position': (x, y), 'angle': 0, 
        'angular_velocity': 0, 
        'vel_limit': 250, 
        'ang_vel_limit': radians(200), 
        'mass': 0, 'col_shapes': col_shapes}
        create_component_dict = {'cymunk-physics': physics_component, 
        'physics_renderer2': {'texture': 
            'hole.png', 'size': (80, 80)},}
        component_order = ['cymunk-physics', 'physics_renderer2']
        self.gameworld.init_entity(create_component_dict, component_order)

    def add_rabbit(self):
        systems = self.gameworld.systems
        rabbit_system = systems['rabbit_system']
        rabbit_system.add_rabbit('dark_bunny')
        rabbit_system.add_rabbit('white_rabbit_1')

    def init_game(self, dt):
        self.setup_states()
        self.setup_map()
        self.set_state()
        self.setup_collision_callbacks()
        Clock.schedule_interval(self.update, 1./60.)
        Clock.schedule_once(self.setup_stuff)

    def setup_map(self):
        self.gameworld.currentmap = self.gameworld.systems['map']

    def update(self, dt):
        self.gameworld.update(dt) 

    def setup_states(self):
        self.gameworld.add_state(state_name='main', systems_added=[
            'physics_renderer2', 'physics_renderer'], 
            systems_removed=[], 
            systems_paused=[], systems_unpaused=[],
            screenmanager_screen='main')

    def setup_collision_callbacks(self):
        systems = self.gameworld.systems
        physics = systems['cymunk-physics']
        rabbit_system = systems['rabbit_system']
        physics.add_collision_handler(1, 2, 
            begin_func=rabbit_system.rabbit_collide_with_hole)

    def set_state(self):
        self.gameworld.state = 'main'

    def setup_stuff(self, dt):
        self.add_rabbit()
        self.add_hole()


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
