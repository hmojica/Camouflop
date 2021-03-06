from kivent_cython import GameSystem
from math import radians, atan2, pi
from kivy._event import partial
from kivy.clock import Clock
from kivy.properties import StringProperty, NumericProperty, ListProperty, BooleanProperty
import math
from kivy.vector import Vector
from kivy.uix.widget import Widget

class VisibilityBar(Widget):
    current_visibility = NumericProperty(0.)
    max_visibility = NumericProperty(1000.)



class RabbitSystem(GameSystem):
    system_id = StringProperty('rabbit_system')
    rabbit = NumericProperty(None, allownone=True)
    white_rabbits = ListProperty([])
    targeted = NumericProperty(None, allownone=True)
    dead_rabbits = BooleanProperty(False)

    def __init__(self, **kwargs):
        super(RabbitSystem, self).__init__(**kwargs)

    def update(self, dt):
        for entity_id in self.entity_ids:
            entities = self.gameworld.entities
            rabbit_entity = entities[entity_id]
            if (rabbit_entity['rabbit_system']['is_safe'] and 
                rabbit_entity['rabbit_system']['visibility'] > 0):
                self.change_visibility(entity_id, -1)
            elif rabbit_entity['rabbit_system']['visibility'] <= 1000:
                self.change_visibility(entity_id, 2)
            if (rabbit_entity['rabbit_system']['visibility'] > 1000 and 
                self.targeted is None):
                self.targeted = rabbit_entity['id']
                sound_system = self.gameworld.systems['sound_system']
                Clock.schedule_once(
                    partial(sound_system.schedule_play, 'hawkcry'))
            if self.targeted is not None:
                if 'rabbit_system' in entities[self.targeted]:
                    if entities[self.targeted][
                        'rabbit_system']['visibility'] < 800:
                        self.targeted = None
            self.update_visibility_widget(rabbit_entity)

    def collide_rabbit_with_hawk(self, space, arbiter):
        rabbit_id = arbiter.shapes[0].body.data
        if rabbit_id == self.targeted:
            sound_system = self.gameworld.systems['sound_system']
            Clock.schedule_once(
                partial(self.gameworld.timed_remove_entity, self.targeted))
            Clock.schedule_once(
                partial(sound_system.schedule_play, 'rabbit_on_ice'))
            self.dead_rabbits = True
            if self.rabbit == self.targeted:
                self.rabbit = None
                self.gameworld.parent.set_game_over()    
            elif self.targeted in self.white_rabbits:
                self.white_rabbits.remove(self.targeted)
            self.targeted = None
        return False

    def change_visibility(self, rabbit_id, amount):
        entities = self.gameworld.entities
        rabbit_entity = entities[rabbit_id]
        rabbit_visibility = rabbit_entity['rabbit_system']['visibility']
        rabbit_visibility = rabbit_visibility + amount
        rabbit_entity['rabbit_system']['visibility'] = rabbit_visibility

    def rabbit_collide_with_hole(self, space, arbiter):
        gameworld = self.gameworld
        entities = gameworld.entities
        rabbit_id = arbiter.shapes[0].body.data
        hole_id = arbiter.shapes[1].body.data
        rabbit_entity = entities[rabbit_id]
        hole_entity = entities[hole_id]
        rabbit_position = rabbit_entity['cymunk-physics']['position']
        hole_position = hole_entity['cymunk-physics']['position']
        Clock.schedule_once(partial(gameworld.timed_remove_entity, rabbit_id))
        if rabbit_id == self.targeted:
            self.targeted = None
        if self.rabbit == rabbit_id:
            self.rabbit = None
            time_offset = 10.
            gameworld.gamescreenmanager.main_screen.add_timer()
            Clock.schedule_once(
                gameworld.systems['levels_system'].clear_level, time_offset) 
        elif rabbit_id in self.white_rabbits:
            self.white_rabbits.remove(rabbit_id)
        if self.rabbit == None and self.white_rabbits == []:
            sound_system = gameworld.systems['sound_system']
            Clock.schedule_once(
                partial(sound_system.schedule_play, 'rabbit_victory'))
        return False

    def enter_shadow(self, space, arbiter):
        rabbit_id = arbiter.shapes[0].body.data
        rabbit_entity = self.gameworld.entities[rabbit_id]
        rabbit_entity['rabbit_system']['shadow_count'] += 1
        is_black = rabbit_id == self.rabbit
        self.update_is_safe(rabbit_entity, is_black)
        return False

    def update_is_safe(self, rabbit_entity, is_black):
        rabbit_system = rabbit_entity['rabbit_system']
        has_camouflage = (rabbit_system['shadow_count'] > 0 and is_black) \
            or (rabbit_system['shadow_count'] == 0 and not is_black)
        if has_camouflage:
            rabbit_system['is_safe'] = True
        elif not rabbit_system['in_log']:
            rabbit_system['is_safe'] = False


    def leave_shadow(self, space, arbiter):
        rabbit_id = arbiter.shapes[0].body.data
        rabbit_entity = self.gameworld.entities[rabbit_id]
        rabbit_entity['rabbit_system']['shadow_count'] -= 1
        is_black = rabbit_id == self.rabbit
        self.update_is_safe(rabbit_entity, is_black)
        return False

    def collide_white_rabbit_and_halo(self, space, arbiter):
        rabbit_id = arbiter.shapes[0].body.data
        if rabbit_id == self.rabbit:
            return False
        rabbit_entity = self.gameworld.entities[rabbit_id]
        self.stop_rabbit(rabbit_entity)
        return False

    def collide_rabbit_and_boundary(self, space, arbiter):
        gameworld = self.gameworld
        entities = gameworld.entities
        boundary_id = arbiter.shapes[1].body.data
        rabbit_id = arbiter.shapes[0].body.data
        rabbit_entity = entities[rabbit_id]
        rabbit_body = rabbit_entity['cymunk-physics']['body']
        return True

    def get_rabbit_dict(self, rabbit_type):
        if rabbit_type == 'white_rabbit':
            white_rabbit_physics_renderer = {
            'texture': 'assets/white_rabbit/WR1.png', 'size': (64, 64)}
            white_rabbit_anim_dict = {'0': 'assets/white_rabbit/WR1.png', 
            '1': 'assets/white_rabbit/WR2.png',
            '2': 'assets/white_rabbit/WR3.png', 
            '3': 'assets/white_rabbit/WR4.png',
            '4': 'assets/white_rabbit/WR5.png', 
            '5': 'assets/white_rabbit/WR6.png', 
            'time_between_frames': .18, 'current_frame': 0,
            'current_frame_time': 0., 'number_of_frames': 6}
            return {'outer_radius': 12, 'mass': 35,
                    'angle': 0, 'vel_limit': 250,
                    'physics_renderer': white_rabbit_physics_renderer,
                    'anim_state': white_rabbit_anim_dict}
        else:
            dark_bunny_physics_renderer = {
                'texture': 'assets/black_rabbit/BR1.png', 'size': (64, 64)}
            black_rabbit_anim_dict = {
                '0': 'assets/black_rabbit/BR1.png', 
                '1': 'assets/black_rabbit/BR2.png',
                '2': 'assets/black_rabbit/BR3.png', 
                '3': 'assets/black_rabbit/BR4.png',
                '4':'assets/black_rabbit/BR5.png', 
                '5': 'assets/black_rabbit/BR6.png', 
                'time_between_frames': .2, 'current_frame': 0,
                'current_frame_time': 0., 'number_of_frames': 6}
            return {'outer_radius': 16, 'mass': 50,
                    'angle': 0, 'vel_limit': 250, 
                    'physics_renderer': dark_bunny_physics_renderer,
                    'anim_state': black_rabbit_anim_dict}


    def add_rabbit(self, rabbit_type, position):
        rabbit_info = self.get_rabbit_dict(rabbit_type)
        x = position[0]
        y = position[1]
        shape_dict = {'inner_radius': 0, 
            'outer_radius': rabbit_info['outer_radius'],
            'mass': rabbit_info['mass'], 'offset': (0, 0)}
        col_shape = {'shape_type': 'circle', 'elasticity': .5,
        'collision_type': 1, 'shape_info': shape_dict, 'friction': 1.0}
        col_shapes = [col_shape]
        if rabbit_type == 'dark_bunny':
            charisma_halo_shape_dict = {'inner_radius': 0, 
            'outer_radius': rabbit_info['outer_radius'] + 20,
            'mass': rabbit_info['mass'], 'offset': (0, 0)}
            charisma_halo = {'shape_type': 'circle', 'elasticity': .5, 
                'collision_type': 10, 'shape_info': charisma_halo_shape_dict, 
                'friction': 1.0}
            col_shapes.append(charisma_halo)
        physics_component = {'main_shape': 'circle',
        'velocity': (0, 0),
        'position': (x, y), 'angle': rabbit_info['angle'],
        'angular_velocity': 0,
        'vel_limit': rabbit_info['vel_limit'],
        'ang_vel_limit': radians(200),
        'mass': 50, 'col_shapes': col_shapes}
        animation_system = {'states': {'running': rabbit_info['anim_state']}, 
            'current_state': 'running'}
        component_order = ['cymunk-physics', 'environment_system', 
            'physics_renderer', 'rabbit_system', 'animation_system']
        is_safe = not rabbit_type == 'dark_bunny'
        rabbit_visibility_widget = VisibilityBar(
            current_visibility = 0, size = (75, 10), pos=(-50, -25))
        self.add_widget(rabbit_visibility_widget)
        rabbit_system = {'rabbit_type': rabbit_type, 'visibility': 0, 
                         'is_safe': is_safe, 'in_log': False,
                         'shadow_count': 0, 'acceleration': 1000, 
                         'touch_effect_radius': 5, 'impulse_accel': 250,
                         'visibility_widget': rabbit_visibility_widget,}
        create_component_dict = {'cymunk-physics': physics_component,
            'physics_renderer': rabbit_info['physics_renderer'], 
            'rabbit_system': rabbit_system,
            'animation_system': animation_system, 'environment_system': {}}
        entity_id = self.gameworld.init_entity(
                        create_component_dict, component_order)
        if rabbit_type == 'dark_bunny':
            self.rabbit = entity_id
        else:
            self.white_rabbits.append(entity_id)
        return entity_id

    def update_visibility_widget(self, rabbit_entity):
        rabbit_system = rabbit_entity['rabbit_system']
        camera_pos = self.gameworld.systems['default_gameview'].camera_pos
        visibility_widget = rabbit_system['visibility_widget']
        current_position = rabbit_entity['cymunk-physics']['position']
        current_visibility = rabbit_system['visibility']
        visibility_widget.current_visibility = current_visibility
        visibility_widget.pos = (current_position[0] + camera_pos[0] - 40, 
            current_position[1] + camera_pos[1] - 40)

    def on_touch_down(self, touch):
        camera_pos = self.gameworld.systems['default_gameview'].camera_pos
        touch.x -= camera_pos[0]
        touch.y -= camera_pos[1]
        if self.gameworld.state == 'main' or 'main_editor':
            called_rabbit = self.touch_rabbit(touch)
            if not called_rabbit is None:
                if called_rabbit == self.rabbit:
                    self.stop_rabbit(self.gameworld.entities[called_rabbit])
                elif self.rabbit is not None:
                    self.call_rabbit(called_rabbit)
                    sound_system = self.gameworld.systems['sound_system']
                    Clock.schedule_once(partial(sound_system.schedule_play, 'white_rabbits'), .5)
            elif self.rabbit is not None:
                rabbit = self.gameworld.entities[self.rabbit]
                rabbit_position = rabbit['cymunk-physics']['position']
                XDistance =  (rabbit_position[0]) - touch.x
                YDistance =  (rabbit_position[1]) - touch.y
                self.apply_rabbit_force(rabbit, XDistance, YDistance)

    def apply_rabbit_force(self, rabbit, XDistance, YDistance):
        if 'rabbit_system' in rabbit:
            rotation = atan2(YDistance, XDistance)
            body = rabbit['cymunk-physics']['body']
            body.angle = (rotation) - pi
            body.reset_forces()
            body.angular_velocity = 0
            unit_vector = body.rotation_vector
            rabbit_type = rabbit['rabbit_system']['rabbit_type']
            rabbit_info = self.get_rabbit_dict(rabbit_type)
            outer_radius = rabbit_info['outer_radius']
            force_offset = (unit_vector[0] * -1 * outer_radius, 
                unit_vector[1] * -1 * outer_radius)
            acceleration = rabbit['rabbit_system']['acceleration']
            impulse_accel = rabbit['rabbit_system']['impulse_accel']
            force = (acceleration * unit_vector[0], 
                acceleration * unit_vector[1])
            impulse_force = (impulse_accel * unit_vector[0], 
                impulse_accel * unit_vector[1])
            body.apply_impulse(force, force_offset)
            body.apply_force(force, force_offset)

    def stop_rabbit(self, rabbit_entity):
        body = rabbit_entity['cymunk-physics']['body']
        body.reset_forces()
        body.velocity = (0, 0)

    def call_rabbit(self, rabbit_id):
        sound_system = self.gameworld.systems['sound_system']
        Clock.schedule_once(partial(sound_system.schedule_play, 'rabbit'))
        rabbit = self.gameworld.entities[rabbit_id]
        black_rabbit = self.gameworld.entities[self.rabbit]
        black_rabbit_position = black_rabbit['cymunk-physics']['position']
        white_rabbit_position = rabbit['cymunk-physics']['position']
        XDistance = (white_rabbit_position[0]) - (black_rabbit_position[0])
        YDistance = (white_rabbit_position[1]) - (black_rabbit_position[1])
        self.apply_rabbit_force(rabbit, XDistance, YDistance)

    def touch_rabbit(self, touch):
        touch_effect_radius = 16
        touch_square = self.query_physics_bb(
                (touch.x, touch.y), touch_effect_radius)
        nonplayer_rabbits = self.white_rabbits
        for entity_id in touch_square:
            if entity_id == self.rabbit:
                return entity_id
            if entity_id in nonplayer_rabbits:
                return entity_id
        return None

    def query_physics_bb(self, position, radius):
        physics_system = self.gameworld.systems['cymunk-physics']
        bb_list = [position[0] - radius, position[1] - radius, 
            position[0] + radius, position[1] + radius]
        in_radius = physics_system.query_bb(bb_list)
        return in_radius

    def clear_rabbits(self):
        self.targeted = None
        self.white_rabbits = []
        for entity_id in self.entity_ids:
            Clock.schedule_once(
                partial(self.gameworld.timed_remove_entity, entity_id))

    def remove_entity(self, entity_id):
        entities = self.gameworld.entities
        rabbit_entity = entities[entity_id]
        rabbit_system = rabbit_entity['rabbit_system']
        visibility_widget = rabbit_system['visibility_widget']
        self.remove_widget(visibility_widget)
        rabbit_system['visibility_widget'] = None
        super(RabbitSystem, self).remove_entity(entity_id)

