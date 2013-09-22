from kivy.properties import StringProperty
from kivent_cython import GameSystem



class EnvironmentSystem(GameSystem):
    system_id = StringProperty('environment_system')

    def get_tree_shadow_renderer(self, type):
        if type == 'small':
            return {'texture': 'assets/environment/GrnTreShadowSM2.png', 'size': (128, 122)}
        if type == 'medium':
            return {'texture': 'assets/environment/GrnTreShadowMD2.png', 'size': (156, 150)}
        if type == 'large':
            return {'texture': 'assets/environment/GrnTreShadowLG2.png', 'size': (198, 198)}

    def add_tree_shadow(self, position, type):
        x = position[0] + 50
        y = position[1] - 50
        shadow_renderer = self.get_tree_shadow_renderer(type)
        shape_dict = {'inner_radius': 0, 'outer_radius': shadow_renderer['size'][0]/2,
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
        'shadow_renderer': shadow_renderer}
        component_order = ['cymunk-physics', 'shadow_renderer']
        self.gameworld.init_entity(create_component_dict, component_order)

    def get_cloud_renderer(self, type):
        if type == 'large_feather':
            return {'texture':
            'assets/environment/CloudLGfeather1.png', 'size': (389, 171)}
        if type == 'small_feather':
            return {'texture': 'assets/environment/CloudSMfeather1.png', 'size': (196, 87)}

    def add_cloud(self, position, type, vel_max=30, ang_vel=0, ang_vel_max=0, angle=0):
        if ang_vel_max == 0:
            ang_vel_max = ang_vel
        x = position[0]
        y = position[1]
        renderer = self.get_cloud_renderer(type)
        size = renderer['size']
        shape_dict = {'width': size[0]*.80, 'height': size[1]*.8, 'mass': 100}
        col_shape = {'shape_type': 'box', 'elasticity': .5,
        'collision_type': 4, 'shape_info': shape_dict, 'friction': 1.0}
        col_shapes = [col_shape]
        physics_component = {'main_shape': 'box',
        'velocity': (50, 10),
        'position': (x, y), 'angle': angle,
        'angular_velocity': ang_vel,
        'vel_limit': vel_max,
        'ang_vel_limit': ang_vel_max,
        'mass': 100, 'col_shapes': col_shapes}
        create_component_dict = {'cymunk-physics': physics_component,
        'hawk_physics_renderer': renderer,}
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

    def get_tree_renderer(self, type):
        if type == 'small':
            return {'texture': 'assets/environment/GrnSnwTreSM.png', 'size': (128, 128)}
        if type == 'medium':
            return {'texture': 'assets/environment/GrnSnwTreMD.png', 'size': (176, 176)}
        if type == 'large':
            return {'texture': 'assets/environment/GrnSnwTreLG.png', 'size': (224, 224)}

    def add_tree(self, position, type):
        x = position[0]
        y = position[1]
        physics_renderer = self.get_tree_renderer(type)
        shape_dict = {'inner_radius': 0, 'outer_radius': physics_renderer['size'][0]/8,
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
        'tree_physics_renderer': physics_renderer,}
        component_order = ['cymunk-physics', 'tree_physics_renderer']
        self.gameworld.init_entity(create_component_dict, component_order)
        self.add_tree_shadow(position, type)

    def get_rock_renderer(self, type):
        if type == 'rock':
            return {'texture': 'assets/environment/rock.png', 'size': (70, 70)}

    def add_rock(self, position, type='rock'):
        x = position[0]
        y = position[1]
        renderer = self.get_rock_renderer(type)
        shape_dict = {'inner_radius': 0, 'outer_radius': renderer['size'][0]/2.,
        'mass': 100, 'offset': (0, 0)}
        col_shape_dict = {'shape_type': 'circle', 'elasticity': .5, 'collision_type': 5, 'shape_info': shape_dict, 'friction': 1.0}
        physics_component_dict = {'main_shape': 'circle', 'velocity': (0, 0), 'position': (x, y),
                                  'angle': 0, 'angular_velocity': 0, 'mass': 0, 'vel_limit': 0,
                                  'ang_vel_limit': 0, 'mass': 0, 'col_shapes': [col_shape_dict]}
        create_component_dict = {'cymunk-physics': physics_component_dict,
                                 'physics_renderer': renderer,}
        component_order = ['cymunk-physics', 'physics_renderer']
        self.gameworld.init_entity(create_component_dict, component_order)

    def get_snowtexture_renderer(self, type):
        if type == 'SnowBankA':
            return {'texture': 'assets/environment/SnowBankA.png', 'size': (640, 400)}

    def load_snowtexture(self, type, position):
        create_component_dict = {'position': {'position': position},
        'quadtree_renderer': self.get_snowtexture_renderer(type)}
        component_order = ['position', 'quadtree_renderer']
        self.gameworld.init_entity(create_component_dict, component_order)