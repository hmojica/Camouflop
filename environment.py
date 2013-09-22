from kivy.properties import StringProperty
from kivent_cython import GameSystem


class EnvironmentSystem(GameSystem):
    system_id = StringProperty('environment_system')

    # def add_hollow_log(self, position, angle):
    # x = position[0]
    # y = position[1]
    # shape_dict = {'width': 69, 'height': 128,
    # 'mass': 100,}
    # col_shape = {'shape_type': 'box', 'elasticity': .5,
    # 'collision_type': 4, 'shape_info': shape_dict, 'friction': 1.0}
    # col_shapes = [col_shape]
    # physics_component = {'main_shape': 'circle',
    # 'velocity': (0, 0),
    # 'position': (x, y), 'angle': angle,
    # 'angular_velocity': 0,
    # 'vel_limit': 0,
    # 'ang_vel_limit': 0,
    # 'mass': 0, 'col_shapes': col_shapes}
    # create_component_dict = {'cymunk-physics': physics_component,
    # 'tree_physics_renderer': {'texture':
    # 'assets/environment/Passable_Log_Closed.png', 'size': (86, 160)},}
    # component_order = ['cymunk-physics', 'tree_physics_renderer']
    # self.gameworld.init_entity(create_component_dict, component_order)
    #
    # def add_passable_log(self, center, angle):
    # self.add_hollow_log(center, angle)
    # boundary_system = self.gameworld.systems['boundary_system']
    # half_width = 36
    # boundary_system.add_boundary(1, 128, (center[0] + 36*cos(angle), center[1]-36*sin(angle)), angle)
    # boundary_system.add_boundary(1, 128, (center[0] - 36*cos(angle), center[1]+36*sin(angle)), angle)


    def add_tree_shadow(self, position):
        x = position[0] + 50
        y = position[1] - 50
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

    def add_cloud(self, position, img, image_size_w, image_size_h, vel_max ):
        x = position[0]
        y = position[1]
        width = image_size_w
        height = image_size_h
        shape_dict = {'width': width*.80, 'height': height*.8, 'mass': 100}
        col_shape = {'shape_type': 'box', 'elasticity': .5,
        'collision_type': 4, 'shape_info': shape_dict, 'friction': 1.0}
        col_shapes = [col_shape]
        physics_component = {'main_shape': 'box',
        'velocity': (50, 10),
        'position': (x, y), 'angle': 0,
        'angular_velocity': 0,
        'vel_limit': vel_max,
        'ang_vel_limit': 0,
        'mass': 100, 'col_shapes': col_shapes}
        create_component_dict = {'cymunk-physics': physics_component,
        'hawk_physics_renderer': {'texture':
            img, 'size': (width, height)},}
        component_order = ['cymunk-physics', 'hawk_physics_renderer']
        cloud_id = self.gameworld.init_entity(create_component_dict, component_order)
        cloud = self.gameworld.entities[cloud_id]
        physics_data = cloud['cymunk-physics']
        physics_body = physics_data['body']
        physics_body.reset_forces()
        physics_body.velocity = (0, 0)
        unit_vector = [0, 100]
        force_offset = unit_vector[0] * -1 * 100, unit_vector[1] * -1 * 100
        force = 1000 * unit_vector[0], 1000 * unit_vector[1]
        physics_body.apply_force(force, force_offset)


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

    def add_rock(self, position):
        x = position[0]
        y = position[1]
        shape_dict = {'inner_radius': 0, 'outer_radius': 10,
        'mass': 100, 'offset': (0, 0)}
        col_shape_dict = {'shape_type': 'circle', 'elasticity': .5, 'collision_type': 5, 'shape_info': shape_dict, 'friction': 1.0}
        physics_component_dict = {'main_shape': 'circle', 'velocity': (0, 0), 'position': (x, y),
                                  'angle': 0, 'angular_velocity': 0, 'mass': 0, 'vel_limit': 0,
                                  'ang_vel_limit': 0, 'mass': 0, 'col_shapes': [col_shape_dict]}
        create_component_dict = {'cymunk-physics': physics_component_dict,
                                 'physics_renderer': {'texture': 'assets/environment/rock.png', 'size': (50, 50)},}
        component_order = ['cymunk-physics', 'physics_renderer']
        self.gameworld.init_entity(create_component_dict, component_order)