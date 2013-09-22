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
    system_id = StringProperty('levels_system')
    current_level_id = NumericProperty(0)

    def clear_level(self):
        self.clear_gameworld_objects()
        self.cleared = False
        Clock.schedule_once(self.check_clear)

    def check_clear(self, dt):
        systems = self.gameworld.systems
        systems_to_check = ['rabbit_system']
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
            self.generate_next_level()

    def clear_gameworld_objects(self):
        systems = self.gameworld.systems
        systems['rabbit_system'].clear_rabbits()
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

    def add_environments(self):
        systems = self.gameworld.systems
        environment_system = systems['environment_system']
        tree_position1 = (Window.size[0] * .5, Window.size[1] * .25)
        environment_system.add_tree(tree_position1)
        environment_system.add_tree_shadow(tree_position1)

        tree_position2 = (Window.size[0] * .25, Window.size[1] * .75)
        environment_system.add_tree(tree_position2)
        environment_system.add_tree_shadow(tree_position2)

        tree_position3 = (Window.size[0] * .75, Window.size[1] * .75)
        environment_system.add_tree(tree_position3)
        environment_system.add_tree_shadow(tree_position3)

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
        environment_system.add_cloud(cloud_position1, 'assets/environment/CloudLGfeather1.png', 389, 171, 50)

        cloud_position2 = (Window.size[0] * .60, Window.size[1] * .80)
        environment_system.add_cloud(cloud_position2, 'assets/environment/CloudSMfeather1.png', 196, 87, 30)

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

        if self.current_level_id == 0:
            self.add_rabbits()
            self.add_hole()
            self.add_boundaries()
        elif self.current_level_id == 1:
            self.clear_level()
            self.add_rabbits()
            self.add_hole()
            self.add_environments()
            self.add_boundaries()
            self.add_hawk()

        self.current_level_id += 1

