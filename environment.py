from math import radians
from kivy.properties import StringProperty
from kivent_cython import GameSystem, Clock, partial


class EnvironmentSystem(GameSystem):
    system_id = StringProperty('environment_system')
    images = {
        'small_tree': ('assets/environment/GrnSnwTreSM.png',128,128),
        'med_tree': ('assets/environment/GrnSnwTreMD.png',176,176),
        'large_tree': ('assets/environment/GrnSnwTreLG.png', 180, 180),
        'small_tree_shadow': ('assets/environment/GrnTreShadowSM2.png',164,154),
        'med_tree_shadow': ('assets/environment/GrnTreShadowMD2.png',156,150),
        'large_tree_shadow': ('assets/environment/GrnTreShadowLG2.png',220,220),
        'small_rock': ('assets/environment/rockSM.png',34,33),
        'med_rock': ('assets/environment/rockMD.png',58,56),
        'large_rock': ('assets/environment/rockLG.png',70,70),
        'snow_bank_a': ('assets/environment/SnowBankA.png',160,200),
        'snow_bank_b': ('assets/environment/SnowBankB.png',160,100),
        'snow_crack_a': ('assets/environment/SnowCrackA.png',160,100),
        'snow_crack_b': ('assets/environment/SnowCrackB.png',126,76),
        'snow_drift_a': ('assets/environment/SnowDriftA.png',184,112),
        'snow_drift_b': ('assets/environment/SnowDriftB.png',160,100),
        'snow_hill_a': ('assets/environment/SnowHillA.png',160,100),
        'snow_hill_b': ('assets/environment/SnowHillB.png',160,100)
    }

    def create_component(self, entity_id, entity_component_dict):
        entity_component_dict['color'] = (1., 1., 1., 1.)

        super(EnvironmentSystem, self).create_component(entity_id, entity_component_dict)

    def get_renderer(self, type):
        image = self.images[type]
        return {'texture': image[0], 'size': (image[1], image[2])}

    def add_tree_shadow(self, position, type, entity_id):
        offsets = {'small_tree_shadow': (25, -25), 
            'large_tree_shadow': (50, -50), 'med_tree_shadow': (35, -35)}
        offset = offsets[type]
        x = position[0] + offset[0]
        y = position[1] + offset[1]
        shadow_renderer = self.get_renderer(type)
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
        'shadow_renderer': shadow_renderer, 'environment_system': {'linked_tree': entity_id}}
        component_order = ['cymunk-physics', 'environment_system', 'shadow_renderer']
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
        'hawk_physics_renderer': renderer, 'environment_system': {}}
        component_order = ['cymunk-physics', 'environment_system', 'hawk_physics_renderer']
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
        return cloud_id

    def add_tree(self, position, type):
        x = position[0]
        y = position[1]
        physics_renderer = self.get_renderer(type)
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
        'tree_physics_renderer': physics_renderer, 'environment_system': {}}
        component_order = ['cymunk-physics', 'environment_system', 'tree_physics_renderer']
        entity_id = self.gameworld.init_entity(create_component_dict, component_order)
        type = type + '_shadow'
        self.add_tree_shadow(position, type, entity_id)
        return entity_id

    def add_rock(self, position, type='large_rock'):
        x = position[0]
        y = position[1]
        renderer = self.get_renderer(type)
        shape_dict = {'inner_radius': 0, 'outer_radius': renderer['size'][0]/2.,
        'mass': 100, 'offset': (0, 0)}
        col_shape_dict = {'shape_type': 'circle', 'elasticity': .5, 'collision_type': 5, 'shape_info': shape_dict,
                          'friction': 1.0}
        physics_component_dict = {'main_shape': 'circle', 'velocity': (0, 0), 'position': (x, y),
                                  'angle': 0, 'angular_velocity': 0, 'mass': 0, 'vel_limit': 0,
                                  'ang_vel_limit': 0, 'mass': 0, 'col_shapes': [col_shape_dict]}
        create_component_dict = {'cymunk-physics': physics_component_dict,
                                 'physics_renderer': renderer, 'environment_system': {}}
        component_order = ['cymunk-physics', 'environment_system', 'physics_renderer']
        entity_id = self.gameworld.init_entity(create_component_dict, component_order)
        return entity_id

    def load_snowtexture(self, type, position):
        create_component_dict = {'position': {'position': position},
        'quadtree_renderer': self.get_renderer(type)}
        component_order = ['position', 'quadtree_renderer']
        self.gameworld.init_entity(create_component_dict, component_order)

    def add_hole(self, position):
        shape_dict = {'inner_radius': 0, 'outer_radius': 20,
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
            'assets/environment/RabbitHole.png', 'size': (80, 80)}, 'environment_system': {'hole': True}}
        component_order = ['cymunk-physics', 'environment_system', 'physics_renderer2']
        entity_id = self.gameworld.init_entity(create_component_dict, component_order)
        return entity_id

    def get_wooden_log_renderer(self, type):
        if type == 'log':
            return {'texture': 'assets/environment/Log.png', 'size': (93, 179)}

    def add_wooden_logs(self, position, type='log'):
        x = position[0]
        y = position[1]
        renderer = self.get_wooden_log_renderer(type)
        size = renderer['size']
        shape_dict = {'width': size[0]*.80, 'height': size[1]*.8, 'mass': 100}
        col_shape_dict = {'shape_type': 'box', 'elasticity': .5, 'collision_type': 5, 'shape_info': shape_dict,
                          'friction': 1.0}
        physics_component_dict = {'main_shape': 'box', 'velocity': (0, 0), 'position': (x, y),
                                  'angle': 0, 'angular_velocity': 0, 'mass': 0, 'vel_limit': 0,
                                  'ang_vel_limit': 0, 'mass': 0, 'col_shapes': [col_shape_dict]}
        create_component_dict = {'cymunk-physics': physics_component_dict,
                                 'physics_renderer': renderer,
                                 'environment_system': {},}
        component_order = ['cymunk-physics', 'environment_system', 'physics_renderer']
        entity_id = self.gameworld.init_entity(create_component_dict, component_order)
        return entity_id

    def clear_objects(self):
        for entity_id in self.entity_ids:
            Clock.schedule_once(partial(self.gameworld.timed_remove_entity, entity_id))
