import kivy
import math
import hawk
import boundary
from kivy.app import App
from kivy.properties import StringProperty, NumericProperty
from kivy.uix.widget import Widget
import kivent_cython
from kivent_cython import GameSystem
from kivy.clock import Clock
from kivy.core.window import Window
from math import radians, atan2, degrees, pi
from functools import partial
from random import randint
from kivy.vector import Vector
from kivy.core.image import Image as CoreImage

class RabbitSystem(GameSystem):
    system_id = StringProperty('rabbit_system')
    rabbit = NumericProperty(None, allownone=True)
    white_rabbits = []

    def __init__(self, **kwargs):
        super(RabbitSystem, self).__init__(**kwargs)
        self.setup_rabbit_dicts()

    def update(self, dt):
        for entity_id in self.entity_ids:
            rabbit_entity = self.gameworld.entities[entity_id]
            if rabbit_entity['rabbit_system']['is_safe']:
                self.change_visibility(entity_id, -1)
            else:
                self.change_visibility(entity_id, 2)


    def change_visibility(self, rabbit_id, amount):
        entities = self.gameworld.entities
        rabbit_entity = entities[rabbit_id]
        rabbit_visibility = rabbit_entity['rabbit_system']['visibility']
        rabbit_visibility = rabbit_visibility + amount
        rabbit_entity['rabbit_system']['visibility'] = rabbit_visibility

    def setup_rabbit_dicts(self):
        self.rabbit_dicts = rabbit_dicts = {}
        dark_bunny_physics_renderer = dict(texture='rabbit.png', size=(64, 64))
        white_rabbit_physics_renderer = dict(texture='rabbit.png', size=(64, 64))
        white_rabbit_anim_dict = {'0': 'assets/white_rabbit/WR1.png', '1': 'assets/white_rabbit/WR2.png',
        '2': 'assets/white_rabbit/WR3.png', '3': 'assets/white_rabbit/WR4.png','4': 
        'assets/white_rabbit/WR5.png', '5': 'assets/white_rabbit/WR6.png', 'time_between_frames': .18, 'current_frame': 0,
        'current_frame_time': 0., 'number_of_frames': 6}
        black_rabbit_anim_dict = {'0': 'assets/black_rabbit/BR1.png', '1': 'assets/black_rabbit/BR2.png',
        '2': 'assets/black_rabbit/BR3.png', '3': 'assets/black_rabbit/BR4.png','4': 
        'assets/black_rabbit/BR5.png', '5': 'assets/black_rabbit/BR6.png', 'time_between_frames': .2, 'current_frame': 0,
        'current_frame_time': 0., 'number_of_frames': 6}
        rabbit_dicts['dark_bunny'] = {'outer_radius': 20, 'mass': 50, 'x': 100, 'y': 100,
                                      'angle': 0, 'vel_limit': 250, 'physics_renderer': dark_bunny_physics_renderer, 
                                      'anim_state': black_rabbit_anim_dict}
        rabbit_dicts['white_rabbit_1'] = {'outer_radius': 16, 'mass': 35, 'x': 100, 'y': 400,
                                        'angle': 0, 'vel_limit': 250, 'physics_renderer': white_rabbit_physics_renderer,
                                        'anim_state': white_rabbit_anim_dict}

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
        if self.rabbit == rabbit_id:
            self.rabbit = None
        elif rabbit_id in self.white_rabbits:
            self.white_rabbits.remove(rabbit_id)
        return False

    def enter_shadow(self, space, arbiter):
        rabbit_id = arbiter.shapes[0].body.data
        rabbit_entity = self.gameworld.entities[rabbit_id]
        rabbit_entity['rabbit_system']['shadow_count'] += 1
        is_black = rabbit_id == self.rabbit
        self.update_is_safe(rabbit_entity, is_black)
        return False

    def update_is_safe(self, rabbit_entity, is_black):
        rabbit_system = rabbit_entity['rabbit_system']
        has_camouflage = (rabbit_system['shadow_count'] > 0 and is_black) \
            or (rabbit_system['shadow_count'] == 0 and not is_black)
        if has_camouflage:
            rabbit_system['is_safe'] = True
        elif not rabbit_system['in_log']:
            rabbit_system['is_safe'] = False


    def leave_shadow(self, space, arbiter):
        rabbit_id = arbiter.shapes[0].body.data
        rabbit_entity = self.gameworld.entities[rabbit_id]
        rabbit_entity['rabbit_system']['shadow_count'] -= 1
        is_black = rabbit_id == self.rabbit
        self.update_is_safe(rabbit_entity, is_black)
        return False

    def collide_white_rabbit_and_halo(self, space, arbiter):
        rabbit_id = arbiter.shapes[0].body.data
        if rabbit_id == self.rabbit:
            return False
        rabbit_entity = self.gameworld.entities[rabbit_id]
        self.stop_rabbit(rabbit_entity)
        return False

    def collide_rabbit_and_boundary(self, space, arbiter):
        gameworld = self.gameworld
        entities = gameworld.entities
        rabbit_id = arbiter.shapes[0].body.data
        rabbit_entity = entities[rabbit_id]
        rabbit_body = rabbit_entity['cymunk-physics']['body']
        rabbit_body.reset_forces()
        rabbit_body.velocity = (0, 0)
        rabbit_body.angular_velocity = (0, 0)
        return True

    def add_rabbit(self, rabbit_type):
        rabbit_info = self.rabbit_dicts[rabbit_type]
        x = rabbit_info['x']
        y = rabbit_info['y']
        shape_dict = {'inner_radius': 0, 'outer_radius': rabbit_info['outer_radius'],
            'mass': rabbit_info['mass'], 'offset': (0, 0)}
        col_shape = {'shape_type': 'circle', 'elasticity': .5, 
        'collision_type': 1, 'shape_info': shape_dict, 'friction': 1.0}
        col_shapes = [col_shape]
        if rabbit_type == 'dark_bunny':
            charisma_halo_shape_dict = {'inner_radius': 0, 'outer_radius': rabbit_info['outer_radius'] + 20,
            'mass': rabbit_info['mass'], 'offset': (0, 0)}
            charisma_halo = dict(shape_type='circle', elasticity=.5, collision_type=10,
                                 shape_info=charisma_halo_shape_dict, friction=1.0)
            col_shapes.append(charisma_halo)
        physics_component = {'main_shape': 'circle', 
        'velocity': (0, 0), 
        'position': (x, y), 'angle': rabbit_info['angle'],
        'angular_velocity': 0, 
        'vel_limit': rabbit_info['vel_limit'],
        'ang_vel_limit': radians(200), 
        'mass': 50, 'col_shapes': col_shapes}
        animation_system = {'states': {'running': rabbit_info['anim_state']}, 'current_state': 'running'}
        component_order = ['cymunk-physics', 'physics_renderer', 'rabbit_system', 'animation_system']
        rabbit_system = {'rabbit_type': rabbit_type, 'visibility': 0, 'is_safe': False, 'in_log': False,
                         'shadow_count': 0}
        create_component_dict = {'cymunk-physics': physics_component, 
        'physics_renderer': rabbit_info['physics_renderer'], 'rabbit_system': rabbit_system, 
        'animation_system': animation_system}
        entity_id = self.gameworld.init_entity(create_component_dict, component_order)
        if rabbit_type == 'dark_bunny':
            self.rabbit = entity_id
        else:
            self.white_rabbits.append(entity_id)

    def on_touch_down(self, touch):
        called_rabbit = self.touch_rabbit(touch)
        if not called_rabbit is None:
            if called_rabbit == self.rabbit:
                self.stop_rabbit(self.gameworld.entities[called_rabbit])
            else:
                self.call_rabbit(called_rabbit)
        elif self.rabbit is not None:
            rabbit = self.gameworld.entities[self.rabbit]
            rabbit_position = rabbit['cymunk-physics']['position']
            XDistance =  (rabbit_position[0]) - touch.x
            YDistance =  (rabbit_position[1]) - touch.y
            self.apply_rabbit_force(rabbit, XDistance, YDistance)

    def apply_rabbit_force(self, rabbit, XDistance, YDistance):
        self.stop_rabbit(rabbit)
        rotation = atan2(YDistance, XDistance)
        body = rabbit['cymunk-physics']['body']
        body.angle = (rotation) - pi
        body.angular_velocity = 0
        unit_vector = body.rotation_vector
        force_offset = unit_vector[0] * -1 * 32, unit_vector[1] * -1 * 32
        force = 1000*unit_vector[0], 1000*unit_vector[1]
        body.apply_force(force, force_offset)

    def stop_rabbit(self, rabbit_entity):
        body = rabbit_entity['cymunk-physics']['body']
        body.reset_forces()
        body.velocity = (0, 0)

    def call_rabbit(self, rabbit_id):
        rabbit = self.gameworld.entities[rabbit_id]
        black_rabbit = self.gameworld.entities[self.rabbit]
        black_rabbit_position = black_rabbit['cymunk-physics']['position']
        white_rabbit_position = rabbit['cymunk-physics']['position']
        XDistance = (white_rabbit_position[0]) - (black_rabbit_position[0])
        YDistance = (white_rabbit_position[1]) - (black_rabbit_position[1])
        self.apply_rabbit_force(rabbit, XDistance, YDistance)

    def calculate_desired_vector(self, target, location, ship_data, ship_ai_data):
        g_map = self.gameworld.systems['default_map']
        map_size_x = g_map.map_size[0]/1.9
        map_size_y = g_map.map_size[1]/1.9
        dist_x = math.fabs(target[0] - location[0])
        dist_y = math.fabs(target[1] - location[1])
        ship_ai_data['distance_to_target'] = Vector(target).distance2(location)
        max_speed = ship_data['max_speed']
        v = Vector(target) - Vector(location)
        v = v.normalize()
        v *= max_speed
        if ship_ai_data['ai_state'] == 'flee':
            v *= -1
        if dist_x > map_size_x:
            v[0] *=-1
        if dist_y > map_size_y:
            v[1] *=-1
        return v

    def touch_rabbit(self, touch):
        touch_square = self.query_physics_bb((touch.x,touch.y),5)
        nonplayer_rabbits = self.white_rabbits
        for entity_id in touch_square:
            if entity_id == self.rabbit:
                return entity_id
            if entity_id in nonplayer_rabbits:
                return entity_id
        return None

    def query_physics_bb(self, position, radius):
        physics_system = self.gameworld.systems['cymunk-physics']
        bb_list = [position[0] - radius, position[1] - radius, position[0] + radius, position[1] + radius]
        in_radius = physics_system.query_bb(bb_list)
        return in_radius

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

    def add_tree_shadow(self, position):
        x = position[0]
        y = position[1]
        shape_dict = {'inner_radius': 0, 'outer_radius': 10,
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
            'treeshadow.png', 'size': (200, 200)},}
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
            'green_snow_tree.png', 'size': (80, 80)},}
        component_order = ['cymunk-physics', 'tree_physics_renderer']
        self.gameworld.init_entity(create_component_dict, component_order)



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
        tree_position = (Window.size[0] * 3/8, Window.size[1] * 1/4)
        environment_system.add_tree(tree_position)
        environment_system.add_tree_shadow(tree_position)

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
        screen_width = Window.size[0]
        screen_height = Window.size[1]
        flyover_positions = [
            [0 - screen_width*.1, 0 - screen_height*.1],
            [screen_width / 2, screen_height + (screen_height*.1)],
            [screen_width + screen_width * .1, 0 - screen_height*.1],
            [0 - screen_width*.1, screen_height/4],
            [screen_width * .1, screen_height * 1.1]]
        size = [100, 100]
        hawk_ai_system.spawn_hawk((self.size[0]/2, self.size[1]/2), flyover_positions, size)

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
        physics.add_collision_handler(1,4, begin_func=rabbit_system.enter_shadow,
                                      separate_func=rabbit_system.leave_shadow)
        physics.add_collision_handler(3, 1, begin_func=self.no_impact_collision)
        physics.add_collision_handler(3, 2, begin_func=self.no_impact_collision)
        physics.add_collision_handler(3, 5, begin_func=self.no_impact_collision)
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
