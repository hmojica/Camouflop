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
    white_rabbits = []

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
        if self.rabbit == rabbit_id:
            self.rabbit = None
        elif rabbit_id in self.white_rabbits:
            self.white_rabbits.remove(rabbit_id)
        return False

    def no_impact_collision(self, space, arbiter):
        return False

    def collide_white_rabbit_and_halo(self, space, arbiter):
        rabbit_id = arbiter.shapes[0].body.data
        if rabbit_id == self.rabbit:
            return False
        rabbit_entity = self.gameworld.entities[rabbit_id]
        self.stop_rabbit(rabbit_entity)
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
        rabbit_system = {'rabbit_type': rabbit_type}
        create_component_dict = {'cymunk-physics': physics_component, 
        'physics_renderer': rabbit_info['physics_renderer'],}
        component_order = ['cymunk-physics', 'physics_renderer']
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
        physics.add_collision_handler(10, 2, begin_func=rabbit_system.no_impact_collision)
        physics.add_collision_handler(1,10, begin_func=rabbit_system.collide_white_rabbit_and_halo)

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
