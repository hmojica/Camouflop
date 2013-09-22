from kivy.properties import (StringProperty, ListProperty,
NumericProperty, BooleanProperty, DictProperty)
from kivent_cython import (GameSystem)
from kivy.clock import Clock
from functools import partial
from kivy.vector import Vector
import math
from kivy.core.window import Window
from random import random

class HawkAISystem(GameSystem):
    updateable = BooleanProperty(True)

    def remove_entity(self, entity_id):
        super(HawkAISystem, self).remove_entity(entity_id)

    def calculate_desired_angle_delta(self, target_vector, unit_vector):
        desired_angle_delta = Vector(unit_vector).angle((target_vector[0], 
            target_vector[1]))
        return desired_angle_delta

    def query_physics_bb(self, position, radius):
        physics_system = self.gameworld.systems['cymunk-physics']
        bb_list = [position[0] - radius, position[1] - radius, position[0] + radius, position[1] + radius]
        in_radius = physics_system.query_bb(bb_list)
        return in_radius

    def avoid_obstacles_vector(self, entity_id, position):
        entities = self.gameworld.entities
        obstacles_to_avoid = self.query_physics_bb(position, 100)
        sum_avoidance = Vector(0, 0)
        ob_count = 0
        for obstacle in obstacles_to_avoid:
            if obstacle != entity_id:
                obstacle = entities[obstacle]
                ob_location = obstacle['cymunk-physics']['position']
                dist = Vector(ob_location).distance(position)
                scale_factor = (150.-dist)/150.
                avoidance_vector = Vector(position) - Vector(ob_location)
                avoidance_vector = avoidance_vector.normalize()
                avoidance_vector *= scale_factor
                sum_avoidance += avoidance_vector
                ob_count += 1
        if ob_count > 0:
            sum_avoidance /= float(ob_count)
        sum_avoidance *= entities[entity_id][self.system_id]['max_speed']
        return sum_avoidance

    def create_component(self, entity_id, entity_component_dict):
        entity_component_dict['fire_engines'] = False
        entity_component_dict['follow_distance'] = 10
        entity_component_dict['ai_state'] = 'follow'
        entity_component_dict['angle_tolerance'] = 10.
        #entity_component_dict['max_speed'] = 300
        super(HawkAISystem, self).create_component(entity_id, entity_component_dict)

    def calculate_desired_vector(self, target, location, system_data):
        #g_map = self.gameworld.systems['default_map']
        #map_size_x = g_map.map_size[0]/1.9
        #map_size_y = g_map.map_size[1]/1.9
        dist_x = math.fabs(target[0] - location[0])
        dist_y = math.fabs(target[1] - location[1])
        system_data['distance_to_target'] = Vector(target).distance2(location)
        max_speed = system_data['max_speed']
        v = Vector(target) - Vector(location)
        v = v.normalize()
        v *= max_speed
        if system_data['ai_state'] == 'flee':
            v *= -1
        #if dist_x > map_size_x:
        #    v[0] *=-1
        #if dist_y > map_size_y:
        #    v[1] *=-1
        return v

    def update_steering(self, dt):
        gameworld = self.gameworld
        entities = gameworld.entities
        system_id = self.system_id
        for entity_id in self.entity_ids:
            entity = entities[entity_id]
            physics_data = entity['cymunk-physics']
            system_data = entity[system_id]
            velocity = physics_data['body'].velocity
            position = physics_data['position']
            follow_distance = system_data['follow_distance']
            unit_vector = physics_data['unit_vector']
            target_position = self.target_player(dt)
            if target_position == None:
                size = Window.size
                target_position = (random()*size[0], random()*size[1])
            dist = Vector(target_position).distance(position)
            if dist > follow_distance and system_data['ai_state'] == 'flee': 
                system_data['ai_state'] = 'follow'
            if dist < 5 and system_data['ai_state'] == 'follow':
                system_data['ai_state'] = 'flee'
            desired_vector = self.calculate_desired_vector(target_position, 
                position, system_data)
            desired_vector *= 1.5
            #avoidance_vector = self.avoid_obstacles_vector(entity_id, position)
            #avoidance_vector *= .25
            #desired_vector = (desired_vector + avoidance_vector)
            steering_vector = desired_vector - Vector(velocity)
            self.steer(steering_vector, entity)

    def steer(self, target_vector, entity):
        physics_data = entity['cymunk-physics']
        system_data = entity[self.system_id]
        unit_vector = physics_data['unit_vector']
        desired_angle = self.do_turning(target_vector, unit_vector, 
            system_data, physics_data['body'])
        self.do_thrusting(system_data, desired_angle)

    def do_thrusting(self, system_data, desired_angle):
        follow_distance = system_data['follow_distance'] * system_data['follow_distance']
        max_speed = system_data['max_speed']
        max_speed2 = max_speed * max_speed
        distance_to_target = system_data['distance_to_target']
        desired_multiplier = 1.0
        if system_data['ai_state'] == 'follow':
            if distance_to_target < follow_distance:
                desired_multiplier = math.fabs((distance_to_target-follow_distance)/(max_speed2))
        system_data['engine_speed_multiplier'] = min(1.0, desired_multiplier)
        if distance_to_target > follow_distance or system_data['ai_state'] == 'flee':
            if -45 <= desired_angle <= 45 and not None:
                system_data['fire_engines'] = True
            else: 
                system_data['fire_engines'] = False
        else: 
            system_data['fire_engines'] = False

    def do_turning(self, target_vector, unit_vector, system_data, physics_body):
        desired_angle_change = self.calculate_desired_angle_delta(
            target_vector, unit_vector)
        turn_speed = system_data['ang_accel']
        desired_multiplier = math.fabs(
            desired_angle_change / math.degrees(turn_speed))
        system_data['turn_speed_multiplier'] = min(1.0, desired_multiplier)
        angle_tolerance = system_data['angle_tolerance']
        if desired_angle_change < -angle_tolerance:
            system_data['is_turning'] = 'left'
        if desired_angle_change > angle_tolerance:
            system_data['is_turning'] = 'right'
        if -angle_tolerance <= desired_angle_change <= angle_tolerance:
            system_data['is_turning'] = 'zero'
            physics_body.angular_velocity = 0
        return desired_angle_change

    def target_player(self, dt):
        gameworld = self.gameworld
        entities = gameworld.entities
        systems = gameworld.systems
        rabbit_system = systems['rabbit_system']
        current_player_character_id = rabbit_system.targeted
        if current_player_character_id:
            current_player_character = entities[current_player_character_id]
            target_physics_data = current_player_character['cymunk-physics']
            target_position = Vector(target_physics_data['position'])
            velocity = Vector(target_physics_data['body'].velocity)
            velocity *= dt
            target_position += velocity
            return target_position
        else:
            return None

    def update(self, dt):
        gameworld = self.gameworld
        systems = gameworld.systems
        rabbit_system = systems['rabbit_system']
        entities = gameworld.entities
        self.update_steering(dt)
        for entity_id in self.entity_ids:
            character = self.gameworld.entities[entity_id]
            physics_data = character['cymunk-physics']
            physics_body = physics_data['body']
            system_data = character[self.system_id]
            if system_data['fire_engines'] and 'unit_vector' in physics_data:   
                unit_vector = physics_data['unit_vector']
                offset = (system_data['offset_distance'] * -unit_vector[0], 
                system_data['offset_distance'] * -unit_vector[1])
                force = (system_data['engine_speed_multiplier'] * system_data['accel']*dt * unit_vector[0], 
                system_data['engine_speed_multiplier'] * system_data['accel']*dt * unit_vector[1])
                physics_body.apply_impulse(force, offset)
            if physics_body.is_sleeping:
                physics_body.activate()
            turning = system_data['is_turning']
            if turning == 'left':
                physics_body.angular_velocity += system_data['turn_speed_multiplier']*system_data['ang_accel']*dt
            elif turning == 'right':
                physics_body.angular_velocity -= system_data['turn_speed_multiplier']*system_data['ang_accel']*dt


    def spawn_hawk(self, position):
        mass = 100
        max_speed = 200
        acceleration = 5000
        offset_distance = 10
        angular_acceleration = 10
        hawk_width = 172
        hawk_height = 86
        box_dict = {'width': 70, 'height': 80,
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
        'hawk_physics_renderer': {'texture': 'assets/hawk/HawkLG.png', 'size': (hawk_width, hawk_height)},
        'hawk_ai_system': hawk_ai_system}
        component_order = ['cymunk-physics', 'hawk_physics_renderer', 'hawk_ai_system']
        self.gameworld.init_entity(create_component_dict, component_order)

