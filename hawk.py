from kivy.properties import (StringProperty, ListProperty,
NumericProperty, BooleanProperty, DictProperty)
from kivent_cython import (GameSystem)
from kivy.clock import Clock
from functools import partial
from kivy.vector import Vector
import math

class HawkAISystem(GameSystem):
    updateable = BooleanProperty(True)
    cycles_to_skip = NumericProperty(5)
    cycle_count = NumericProperty(0)

    flyover_positions = [
        [-50, -50],
        [600, 600],
        [0, 300],
        [600, 100]]

    def remove_entity(self, entity_id):
        super(HawkAISystem, self).remove_entity(entity_id)

    def create_component(self, entity_id, entity_component_dict):
        entity_component_dict['distance_to_target'] = 0.
        # entity_component_dict['angle_tolerance'] = 10.
        # entity_component_dict['follow_distance'] = 50
        # entity_component_dict['site_distance'] = 650
        entity_component_dict['state'] = 'hold'
        entity_component_dict['flyover_index'] = 0
        entity_component_dict['target_position'] = [0, 0]
        # entity_component_dict['attack_delay'] = .25

        super(HawkAISystem, self).create_component(entity_id, entity_component_dict)


    # def query_physics_bb(self, position, radius):
    #     physics_system = self.gameworld.systems['cymunk-physics']
    #     bb_list = [position[0] - radius, position[1] - radius, position[0] + radius, position[1] + radius]
    #     in_radius = physics_system.query_bb(bb_list)
    #     return in_radius


    # def calculate_desired_vector(self, target, location, hawk_ai_data):
    #     g_map = self.gameworld.systems['map']
    #     map_size_x = g_map.map_size[0]/1.9
    #     map_size_y = g_map.map_size[1]/1.9
    #     dist_x = math.fabs(target[0] - location[0])
    #     dist_y = math.fabs(target[1] - location[1])
    #     hawk_ai_data['distance_to_target'] = Vector(target).distance2(location)
    #     max_speed = hawk_ai_data['max_speed']
    #     v = Vector(target) - Vector(location)
    #     v = v.normalize()
    #     v *= max_speed
    #     # if ship_ai_data['ai_state'] == 'flee':
    #     #     v *= -1
    #     if dist_x > map_size_x:
    #         v[0] *=-1
    #     if dist_y > map_size_y:
    #         v[1] *=-1
    #     return v

    # def calculate_desired_angle_delta(self, target_vector, unit_vector):
    #     desired_angle_delta = Vector(unit_vector).angle((target_vector[0],
    #         target_vector[1]))
    #     return desired_angle_delta
    #
    # def do_turning(self, target_vector, unit_vector, hawk_ai_data, physics_body):
    #     desired_angle_change = self.calculate_desired_angle_delta(
    #         target_vector, unit_vector)
    #     turn_speed = hawk_ai_data['ang_accel']
    #     desired_multiplier = math.fabs(
    #         desired_angle_change / math.degrees(turn_speed))
    #     hawk_ai_data['turn_speed_multiplier'] = min(1.0, desired_multiplier)
    #     angle_tolerance = hawk_ai_data['angle_tolerance']
    #     if desired_angle_change < -angle_tolerance:
    #         hawk_ai_data['is_turning'] = 'left'
    #     if desired_angle_change > angle_tolerance:
    #         hawk_ai_data['is_turning'] = 'right'
    #     if -angle_tolerance <= desired_angle_change <= angle_tolerance:
    #         hawk_ai_data['is_turning'] = 'zero'
    #         physics_body.angular_velocity = 0
    #     return desired_angle_change
    #
    # def query_view(self, position, unit_vector, site_distance):
    #     unit_vector = Vector(unit_vector)
    #     physics_system = self.gameworld.systems['cymunk-physics']
    #     vec_start = Vector(position) + unit_vector
    #     vec_end = Vector(position) + unit_vector*site_distance
    #     in_view = physics_system.query_segment(vec_start, vec_end)
    #     return in_view

    # def do_thrusting(self, hawk_ai_data, desired_angle):
    #     follow_distance = hawk_ai_data['follow_distance'] * hawk_ai_data['follow_distance']
    #     max_speed = hawk_ai_data['max_speed']
    #     max_speed2 = max_speed * max_speed
    #     distance_to_target = hawk_ai_data['distance_to_target']
    #     desired_multiplier = 1.0
    #     if hawk_ai_data['ai_state'] == 'follow':
    #         if distance_to_target < follow_distance:
    #             desired_multiplier = math.fabs((distance_to_target-follow_distance)/(max_speed2))
    #     hawk_ai_data['engine_speed_multiplier'] = min(1.0, desired_multiplier)
        # if distance_to_target > follow_distance or ship_ai_data['ai_state'] == 'flee':
        #     if -45 <= desired_angle <= 45 and not None:
        #         ship_data['fire_engines'] = True
        #         entity_engine_effect['particle_system_on'] = True
        #     else:
        #         ship_data['fire_engines'] = False
        #         entity_engine_effect['particle_system_on'] = False
        # else:
        #     ship_data['fire_engines'] = False
        #     entity_engine_effect['particle_system_on'] = False

    def update(self, dt):
        if self.cycle_count < self.cycles_to_skip:
            self.cycle_count += 1
        else:
            self.cycle_count = 0

            for entity_id in self.entity_ids:
                hawk = self.gameworld.entities[entity_id]
                hawk_ai_data = hawk['hawk_ai_system']
                physics_data = hawk['cymunk-physics']
                physics_body = physics_data['body']
                hawk_position = physics_data['position']

                if hawk_ai_data['state'] == 'hold':
                    flyover_index = hawk_ai_data['flyover_index']
                    target_position = self.flyover_positions[flyover_index]
                    hawk_ai_data['target_position'] = target_position

                    print 'flying to '
                    print target_position[0]
                    print target_position[1]

                    XDistance = (hawk_position[0] - target_position[0])
                    YDistance = (hawk_position[1] - target_position[1])

                    rotation = math.atan2(YDistance, XDistance)
                    physics_body.reset_forces()
                    physics_body.velocity = (0, 0)
                    physics_body.angle = (rotation) - math.pi
                    unit_vector = physics_body.rotation_vector
                    force_offset = unit_vector[0] * -1 * 32, unit_vector[1] * -1 * 32
                    force = 1000*unit_vector[0], 1000*unit_vector[1]
                    physics_body.apply_force(force, force_offset)

                    hawk_ai_data['state'] = 'fly_over'
                    if flyover_index == len(self.flyover_positions)-1:
                        hawk_ai_data['flyover_index'] = 0
                    else:
                        hawk_ai_data['flyover_index'] += 1

                elif hawk_ai_data['state'] == 'fly_over':
                    target_position = hawk_ai_data['target_position']
                    closex = abs(target_position[0] - hawk_position[0]) < 15
                    closey = abs(target_position[1] - hawk_position[1]) < 15
                    if (closex and closey):
                        print 'reached target position'
                        hawk_ai_data['state'] = 'hold'
                # velocity = physics_data['body'].velocity
                # position = physics_data['position']
                # follow_distance = hawk_ai_data['follow_distance']
                # unit_vector = physics_data['unit_vector']
                # target_position = Vector((-1000, -1000))
                # if target_position == None:
                #     target_position = position
                # dist = Vector(target_position).distance(position)
                # if dist > follow_distance:
                #     hawk_ai_data['ai_state'] = 'follow'
                # desired_vector = self.calculate_desired_vector(target_position, position, hawk_ai_data)
                # desired_vector *= 1.5
                # steering_vector = desired_vector - Vector(velocity)
                # self.steer(steering_vector, hawk)
                # if 'unit_vector' in physics_data:
                #     unit_vector = physics_data['unit_vector']
                #     offset = (hawk_ai_data['offset_distance'] * -unit_vector[0],
                #     hawk_ai_data['offset_distance'] * -unit_vector[1])
                #     force = (hawk_ai_data['engine_speed_multiplier'] * hawk_ai_data['accel']*dt * unit_vector[0],
                #     hawk_ai_data['engine_speed_multiplier'] * hawk_ai_data['accel']*dt * unit_vector[1])
                #     physics_body.apply_impulse(force, offset)
                # if physics_body.is_sleeping:
                #     physics_body.activate()
                # turning = hawk_ai_data['is_turning']
                # if turning == 'left':
                #     physics_body.angular_velocity += hawk_ai_data['turn_speed_multiplier']*hawk_ai_data['ang_accel']*dt
                # elif turning == 'right':
                #     physics_body.angular_velocity -= hawk_ai_data['turn_speed_multiplier']*hawk_ai_data['ang_accel']*dt

    # def steer(self, target_vector, entity):
    #     physics_data = entity['cymunk-physics']
    #     unit_vector = physics_data['unit_vector']
    #     hawk_ai_data = entity['hawk_ai_system']
    #     desired_angle = self.do_turning(target_vector, unit_vector, hawk_ai_data, physics_data['body'])
    #     self.do_thrusting(hawk_ai_data, desired_angle)

    def spawn_hawk(self, position):
        mass = 100
        max_speed = 25000
        acceleration = 25000
        offset_distance = 10
        angular_acceleration = 10
        hawk_width = 100
        hawk_height = 100
        box_dict = {'width': hawk_width, 'height': hawk_height,
         'mass': mass}
        col_shape_dict = {'shape_type': 'box', 'elasticity': .5,
        'collision_type': 3, 'shape_info': box_dict, 'friction': 1.0}
        physics_component_dict = { 'main_shape': 'box',
        'velocity': (0, 0), 'position': position, 'angle': 0,
        'angular_velocity': 0, 'mass': mass, 'vel_limit': 1000,
        'ang_vel_limit': math.radians(1000), 'col_shapes': [col_shape_dict]}
        hawk_ai_system = {'max_speed': max_speed, 'accel': acceleration,
        'offset_distance': offset_distance, 'ang_accel': math.radians(angular_acceleration),
        'is_turning': 'zero',
        'turn_speed_multiplier': 0, 'engine_speed_multiplier': 0}
        create_component_dict = {'cymunk-physics': physics_component_dict,
        'hawk_physics_renderer': {'texture': 'hawk.png', 'size': (hawk_width, hawk_height)},
        'hawk_ai_system': hawk_ai_system}
        component_order = ['cymunk-physics', 'hawk_physics_renderer', 'hawk_ai_system']
        self.gameworld.init_entity(create_component_dict, component_order)

    # def target_bunny(self, dt):
    #     gameworld = self.gameworld
    #     entities = gameworld.entities
    #     character_system = gameworld.systems['player_character']
    #     current_player_character_id = character_system.current_character_id
    #     if current_player_character_id:
    #         current_player_character = entities[current_player_character_id]
    #         target_physics_data = current_player_character['cymunk-physics']
    #         target_position = Vector(target_physics_data['position'])
    #         velocity = Vector(target_physics_data['body'].velocity)
    #         velocity *= dt *self.cycles_to_skip
    #         target_position+= velocity
    #         return target_position
    #     else:
    #         return None

    def no_impact_collision(self, space, arbiter):
        return False
