from kivy.properties import StringProperty
from kivent_cython import GameSystem


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
