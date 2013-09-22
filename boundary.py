from kivent_cython import GameSystem
from kivy.properties import StringProperty
import math


class BoundarySystem(GameSystem):
    system_id = StringProperty('boundary_system')

    def add_boundary(self, width, height, position):
        boundary_system = {}
        shape_dict = {'width': width, 'height': height, 'mass': 0}
        col_shape_dict = {'shape_type': 'box', 'elasticity': .5,
                          'collision_type': 11, 'shape_info': shape_dict, 'friction': 1.0}
        physics_component_dict = {'main_shape': 'box', 'velocity': (0, 0), 'position': position, 'angle':0, 'angular_velocity': 0,
                                  'mass': 0, 'vel_limit': 1000, 'ang_vel_limit': math.radians(1000), 'col_shapes': [col_shape_dict]}
        create_component_dict = {'cymunk-physics': physics_component_dict,
                                 'physics_renderer': {'texture': '', 'size': (width, height)}, 'boundary_system': boundary_system}
        component_order = ['cymunk-physics', 'boundary_system']
        self.gameworld.init_entity(create_component_dict, component_order)

    def add_boundaries(self):
        gamescreen_width = self.size[0]
        gamescreen_height = self.size[1]
        ##left bounding box
        self.add_boundary(gamescreen_height, 5, (0, gamescreen_height/2))
        #bottom bounding box
        self.add_boundary(5, gamescreen_width, (gamescreen_width/2, 0))
        #right bounding box
        self.add_boundary(gamescreen_height, 5, (gamescreen_width, gamescreen_height/2))
        #top bounding box
        self.add_boundary(5, gamescreen_width, (gamescreen_width/2, gamescreen_height))