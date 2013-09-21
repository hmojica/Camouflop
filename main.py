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
from kivy.core.image import Image as CoreImage

class RabbitSystem(GameSystem):
    system_id = StringProperty('rabbit_system')
    rabbit = NumericProperty(None, allownone=True)

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

    def add_rabbit(self):
        x = 100
        y = 100
        shape_dict = {'inner_radius': 0, 'outer_radius': 32, 
        'mass': 50, 'offset': (0, 0)}
        col_shape = {'shape_type': 'circle', 'elasticity': .5, 
        'collision_type': 1, 'shape_info': shape_dict, 'friction': 1.0}
        col_shapes = [col_shape]
        physics_component = {'main_shape': 'circle', 
        'velocity': (0, 0), 
        'position': (x, y), 'angle': 0, 
        'angular_velocity': 0, 
        'vel_limit': 250, 
        'ang_vel_limit': radians(200), 
        'mass': 50, 'col_shapes': col_shapes}
        rabbit_system = {''}
        animation_state_dict = {'0': 'assets/white_rabbit/WR1.png', '1': 'assets/white_rabbit/WR2.png',
        '2': 'assets/white_rabbit/WR3.png', '3': 'assets/white_rabbit/WR4.png','4': 
        'assets/white_rabbit/WR5.png', '5': 'assets/white_rabbit/WR6.png', 'time_between_frames': .18, 'current_frame': 0,
        'current_frame_time': 0., 'number_of_frames': 6}
        animation_system = {'states': {'running': animation_state_dict}, 'current_state': 'running'}
        create_component_dict = {'cymunk-physics': physics_component, 
        'physics_renderer': {'texture': 
            'assets/white_rabbit/WR1.png', 'size': (53, 57)},
        'animation_system': animation_system}
        component_order = ['cymunk-physics', 'physics_renderer', 'animation_system']
        entity_id = self.gameworld.init_entity(create_component_dict, component_order)
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

class AnimationSystem(GameSystem):
    '''
    Animation component info looks like: {'states': {dict of state_name, state dicts, 'current_state': state_name}
    state dict looks like: 'number_of_frames': integer, 'frame': 'graphic_str', 
    'current_frame_time': float, 'time_between_frames': float, 'current_frame': int}
    '''
    renderer_to_modify = StringProperty('physics_renderer')
    system_id = StringProperty('animation_system')
    
    def __init__(self, **kwargs):
        super(AnimationSystem, self).__init__(**kwargs)
        self.textures = {}

    def load_texture(self, texture_str):
        textures = self.textures
        if texture_str not in textures:
            textures[texture_str] = CoreImage(texture_str).texture
        texture = textures[texture_str]
        return texture

    def update(self, dt):
        gameworld = self.gameworld
        entities = gameworld.entities
        system_id = self.system_id
        rendering_system = self.renderer_to_modify
        load_texture = self.load_texture
        for entity_id in self.entity_ids:
            entity = entities[entity_id]
            animation_system = entity[system_id]
            rendering_system = entity[rendering_system]
            current_state = animation_system['current_state']
            state_dict = animation_system['states'][current_state]
            state_dict['current_frame_time'] += dt
            if state_dict['current_frame_time'] >= state_dict['time_between_frames']:
                state_dict['current_frame_time'] -= state_dict['time_between_frames']
                state_dict['current_frame'] += 1
                if state_dict['current_frame'] >= state_dict['number_of_frames']:
                    state_dict['current_frame'] = 0
                texture_str = state_dict[str(state_dict['current_frame'])]
                rendering_system['quad'].texture = load_texture(texture_str)
                rendering_system['texture'] = texture_str








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
        rabbit_system.add_rabbit()

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
