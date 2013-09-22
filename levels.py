from kivent_cython import GameSystem, Clock, partial
from kivy.core.window import Window
from math import radians
from kivy.properties import StringProperty, NumericProperty
import hawk
import boundary
import rabbit
import animation
import environment


class LevelsSystem(GameSystem):

    levels = [
        #level 1
        {
            'trees': [
                {'position': (.5, .5)}
            ],
            'rocks': [],
            'clouds': []
        },
        #level 2
        {
            'trees': [
                {'position': (.5, .25)},
                {'position': (.25, .75)},
                {'position': (.75, .75)}
            ],
            'rocks': [
                {'position': (.9, .4)},
                {'position': (.85, .5)},
                {'position': (.55, .9)},
                {'position': (.55, .8)},
                {'position': (.55, .7)}
            ],
            'clouds': [
                {'position': (.3, .2), 'size': 'LARGE'},
                {'position': (.6, .8), 'size': 'SMALL'}
            ]
        }
    ]

    system_id = StringProperty('levels_system')
    current_level_id = NumericProperty(0)

    def clear_level(self, dt):
        self.clear_gameworld_objects()
        self.cleared = False
        Clock.schedule_once(self.check_clear)

    def check_clear(self, dt):
        systems = self.gameworld.systems
        systems_to_check = ['rabbit_system', 'hawk_ai_system', 'environment_system']
        num_entities = 0
        self.check_clear_counter = 0
        for system in systems_to_check:
            num_entities += len(systems[system].entity_ids)
        if num_entities > 0:
            self.check_clear_counter += 1
            if self.check_clear_counter > 10:
                self.clear_gameworld_objects()
            Clock.schedule_once(self.check_clear, .01)
        else:
            self.cleared = True
            self.generate_next_level(dt)

    def clear_gameworld_objects(self):
        systems = self.gameworld.systems
        systems['rabbit_system'].clear_rabbits()
        systems['environment_system'].clear_objects()
        systems['hawk_ai_system'].clear_hawk()
        ##clear hole
        for entity_id in self.entity_ids:
            Clock.schedule_once(partial(self.gameworld.timed_remove_entity, entity_id))

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

    def add_objects(self, elements, callback):
        for element in elements:
            position = (Window.size[0] * element['position'][0], Window.size[1] * element['position'][1])
            callback(position)

    def add_trees(self, trees):
        environment_system = self.gameworld.systems['environment_system']
        for tree in trees:
            tree_position1 = (Window.size[0] * tree['position'][0], Window.size[1] * tree['position'][1])
            environment_system.add_tree(tree_position1)
            environment_system.add_tree_shadow(tree_position1)

    def add_rocks(self, rocks):
        environment_system = self.gameworld.systems['environment_system']
        for rock in rocks:
            rock_position = (Window.size[0] * rock['position'][0], Window.size[1] * rock['position'][1])
            environment_system.add_rock(rock_position)

    def add_clouds(self, clouds):
        environment_system = self.gameworld.systems['environment_system']
        for cloud in clouds:
            cloud_position = (Window.size[0] * cloud['position'][0], Window.size[1] * cloud['position'][1])
            cloud_size = cloud['size']
            texture = ''
            img_w = 0
            img_h = 0
            max_vel = 0
            if cloud_size == 'SMALL':
                texture = 'assets/environment/CloudSMfeather1.png'
                img_w = 196
                img_h = 87
                max_vel = 30
            elif cloud_size == 'LARGE':
                texture = 'assets/environment/CloudLGfeather1.png'
                img_w = 389
                img_h = 171
                max_vel = 50
            environment_system.add_cloud(cloud_position, texture, img_w, img_h, max_vel)

    def add_environments(self, level_map):
        self.add_trees(level_map['trees'])
        self.add_rocks(level_map['rocks'])
        self.add_clouds(level_map['clouds'])

    def add_rabbits(self):
        systems = self.gameworld.systems
        rabbit_system = systems['rabbit_system']
        rabbit_system.add_rabbit('dark_bunny')
        rabbit_system.add_rabbit('white_rabbit_1')

    def add_hawk(self):
        hawk_ai_system = self.gameworld.systems['hawk_ai_system']
        hawk_ai_system.spawn_hawk((500, 500))

    def add_boundaries(self):
        boundary_system = self.gameworld.systems['boundary_system']
        boundary_system.add_boundaries()

    def generate_next_level(self, dt):
        # if self.current_level_id > 0:
        #     self.clear_level()
        self.add_rabbits()
        self.add_hole()
        self.add_boundaries()
        self.add_hawk()
        self.add_environments(self.levels[self.current_level_id])
        self.current_level_id += 1

