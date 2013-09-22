import kivy
import math
import hawk
import boundary
import rabbit
from kivy.app import App
from kivy.properties import StringProperty, NumericProperty, ObjectProperty
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
            r_rendering_system = entity[rendering_system]
            current_state = animation_system['current_state']
            state_dict = animation_system['states'][current_state]
            state_dict['current_frame_time'] += dt
            if state_dict['current_frame_time'] >= state_dict['time_between_frames']:
                state_dict['current_frame_time'] -= state_dict['time_between_frames']
                state_dict['current_frame'] += 1
                if state_dict['current_frame'] >= state_dict['number_of_frames']:
                    state_dict['current_frame'] = 0
                texture_str = state_dict[str(state_dict['current_frame'])]
                r_rendering_system['quad'].texture = load_texture(texture_str)
                r_rendering_system['texture'] = texture_str


class EnvironmentSystem(GameSystem):
    system_id = StringProperty('environment_system')

    # def add_hollow_log(self, position, angle):
    #     x = position[0]
    #     y = position[1]
    #     shape_dict = {'width': 69, 'height': 128,
    #     'mass': 100,}
    #     col_shape = {'shape_type': 'box', 'elasticity': .5,
    #     'collision_type': 4, 'shape_info': shape_dict, 'friction': 1.0}
    #     col_shapes = [col_shape]
    #     physics_component = {'main_shape': 'circle',
    #     'velocity': (0, 0),
    #     'position': (x, y), 'angle': angle,
    #     'angular_velocity': 0,
    #     'vel_limit': 0,
    #     'ang_vel_limit': 0,
    #     'mass': 0, 'col_shapes': col_shapes}
    #     create_component_dict = {'cymunk-physics': physics_component,
    #     'tree_physics_renderer': {'texture':
    #         'assets/environment/Passable_Log_Closed.png', 'size': (86, 160)},}
    #     component_order = ['cymunk-physics', 'tree_physics_renderer']
    #     self.gameworld.init_entity(create_component_dict, component_order)
    #
    # def add_passable_log(self, center, angle):
    #     self.add_hollow_log(center, angle)
    #     boundary_system = self.gameworld.systems['boundary_system']
    #     half_width = 36
    #     boundary_system.add_boundary(1, 128, (center[0] + 36*cos(angle), center[1]-36*sin(angle)), angle)
    #     boundary_system.add_boundary(1, 128, (center[0] - 36*cos(angle), center[1]+36*sin(angle)), angle)


    def add_tree_shadow(self, position):
        x = position[0]
        y = position[1]
        shape_dict = {'inner_radius': 0, 'outer_radius': 100,
        'mass': 100, 'offset': (0, 0)}
        col_shape = {'shape_type': 'circle', 'elasticity': .5,
        'collision_type': 4, 'shape_info': shape_dict, 'friction': 1.0}
        col_shapes = [col_shape]
        physics_component = {'main_shape': 'circle',
        'velocity': (0, 0),
        'position': (x, y), 'angle': 0,
        'angular_velocity': 0,
        'vel_limit': 0,
        'ang_vel_limit': 0,
        'mass': 0, 'col_shapes': col_shapes}
        create_component_dict = {'cymunk-physics': physics_component,
        'shadow_renderer': {'texture':
            'assets/environment/GrnTreShadowSM.png', 'size': (146, 144)},}
        component_order = ['cymunk-physics', 'shadow_renderer']
        self.gameworld.init_entity(create_component_dict, component_order)

    def add_tree(self, position):
        x = position[0]
        y = position[1]
        shape_dict = {'inner_radius': 0, 'outer_radius': 10,
        'mass': 100, 'offset': (0, 0)}
        col_shape = {'shape_type': 'circle', 'elasticity': .5,
        'collision_type': 5, 'shape_info': shape_dict, 'friction': 1.0}
        col_shapes = [col_shape]
        physics_component = {'main_shape': 'circle',
        'velocity': (0, 0),
        'position': (x, y), 'angle': 0,
        'angular_velocity': 0,
        'vel_limit': 0,
        'ang_vel_limit': 0,
        'mass': 0, 'col_shapes': col_shapes}
        create_component_dict = {'cymunk-physics': physics_component,
        'tree_physics_renderer': {'texture':
            'assets/environment/green_snow_tree.png', 'size': (80, 80)},}
        component_order = ['cymunk-physics', 'tree_physics_renderer']
        self.gameworld.init_entity(create_component_dict, component_order)


class BackgroundWidget(Widget):
    def __init__(self, **kwargs):
        super(BackgroundWidget, self).__init__(**kwargs)
        Clock.schedule_once(self.setup_background)

    def setup_background(self, dt):
        size = Window.size
        x_repeat_num = int(ceil(size[0]/256.))
        y_repeat_num = int(ceil(size[1]/256.))
        for x in xrange(x_repeat_num):
            for y in xrange(y_repeat_num):
                with self.canvas:
                    Rectangle(pos=(256.*x, 256.*y), size=(256, 256), source='assets/environment/snow_texture.png')


class DarkBunnyGame(Widget):
    bg_texture = ObjectProperty(None)
    
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

    def add_environment(self):
        systems = self.gameworld.systems
        environment_system = systems['environment_system']
        tree_position = (300, 150)
        tree_shadow_position = (325, 125)
        environment_system.add_tree(tree_position)
        environment_system.add_tree_shadow(tree_shadow_position)


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
        physics.add_collision_handler(3, 1, begin_func=self.no_impact_collision)
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

    def set_state(self):
        self.gameworld.state = 'main'

    def setup_stuff(self, dt):
        self.add_rabbit()
        self.add_hole()
        self.add_environment()
        self.setup_collision_callbacks()


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
