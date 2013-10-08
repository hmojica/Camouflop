from kivent_cython import GameSystem, Clock, partial
from kivy.core.window import Window
from math import radians
from kivy.properties import StringProperty, NumericProperty
import hawk
import boundary
import level_maps
import rabbit
import animation
import environment


class LevelsSystem(GameSystem):

    levels = level_maps.LevelMaps.levels

    system_id = StringProperty('levels_system')
    current_level_id = NumericProperty(0)

    def clear_level(self, dt):
        self.gameworld.parent.state = 'pause'
        self.clear_gameworld_objects()
        self.cleared = False
        Clock.schedule_once(self.check_clear)

    def check_clear(self, dt):
        systems = self.gameworld.systems
        systems_to_check = ['rabbit_system', 'hawk_ai_system', 
        'environment_system']
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
        print 'clearing level'
        systems = self.gameworld.systems
        systems['rabbit_system'].clear_rabbits()
        systems['environment_system'].clear_objects()
        systems['hawk_ai_system'].clear_hawk()

    def add_trees(self, trees):
        environment_system = self.gameworld.systems['environment_system']
        for tree in trees:
            tree_position1 = (Window.size[0] * tree['position'][0], 
                Window.size[1] * tree['position'][1])
            environment_system.add_tree(tree_position1, tree['type'])

    def add_rocks(self, rocks):
        environment_system = self.gameworld.systems['environment_system']
        for rock in rocks:
            rock_position = (Window.size[0] * rock['position'][0], 
                Window.size[1] * rock['position'][1])
            environment_system.add_rock(rock_position, type=rock['type'])

    def add_clouds(self, clouds):
        environment_system = self.gameworld.systems['environment_system']
        for cloud in clouds:
            cloud_position = (Window.size[0] * cloud['position'][0], 
                Window.size[1] * cloud['position'][1])
            cloud_type = cloud['type']
            environment_system.add_cloud(cloud_position, 
                cloud_type, vel_max=50)

    def add_holes(self, holes):
        environment_system = self.gameworld.systems['environment_system']
        for hole in holes:
            hole_position = (Window.size[0] * hole['position'][0], 
                Window.size[1] * hole['position'][1])
            environment_system.add_hole(hole_position)

    def add_wooden_logs(self, wooden_logs):
        environment_system = self.gameworld.systems['environment_system']
        for wooden_log in wooden_logs:
            print wooden_log['position'][0]
            log_position = (Window.size[0] * wooden_log['position'][0], 
                Window.size[1] * wooden_log['position'][1])
            environment_system.add_wooden_logs(log_position)

    def add_environments(self, level_map):
        self.add_trees(level_map['trees'])
        self.add_rocks(level_map['rocks'])
        self.add_clouds(level_map['clouds'])
        self.add_holes(level_map['holes'])
        self.add_wooden_logs(level_map['wooden_log'])

    def get_window_position(self, position):
        return Window.size[0] * position[0], Window.size[1] * position[1]

    def add_rabbits(self, level_map):
        systems = self.gameworld.systems
        rabbit_system = systems['rabbit_system']
        rabbit_system.add_rabbit('dark_bunny', 
            self.get_window_position(level_map['dark_bunny']['position']))
        for white_bunny in level_map['white_bunnies']:
            rabbit_system.add_rabbit('white_rabbit', 
                self.get_window_position(white_bunny['position']))

    def add_hawk(self):
        hawk_ai_system = self.gameworld.systems['hawk_ai_system']
        hawk_ai_system.spawn_hawk((500, 500))

    def add_boundaries(self):
        boundary_system = self.gameworld.systems['boundary_system']
        boundary_system.add_boundaries()

    def generate_level(self, level_id):
        self.add_rabbits(self.levels[level_id])
        self.add_boundaries()
        self.add_hawk()
        self.add_environments(self.levels[level_id])

    def generate_next_level(self, dt):
        if self.current_level_id >= len(self.levels):
            self.gameworld.state = 'menu'
            self.current_level_id = 0
        self.clear_level(dt)
        self.add_rabbits(self.levels[self.current_level_id])
        self.add_boundaries()
        self.add_hawk()
        self.add_environments(self.levels[self.current_level_id])
        self.current_level_id += 1

