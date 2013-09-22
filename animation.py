from kivy.core.image import Image as CoreImage
from kivy.properties import StringProperty
from kivent_cython import GameSystem

class AnimationSystem(GameSystem):
    '''
    Animation component info looks like: {'states': {dict of state_name, state dicts, 'current_state': state_name}
    state dict looks like: 'number_of_frames': integer, 'frame': 'graphic_str',
    'current_frame_time': float, 'time_between_frames': float, 'current_frame': int}
    '''
    renderer_to_modify = StringProperty('physics_renderer')
    system_id = StringProperty('animation_system')

    def __init__(self, **kwargs):
        super(AnimationSystem, self).__init__(**kwargs)
        self.textures = {}

    def load_texture(self, texture_str):
        textures = self.textures
        if texture_str not in textures:
            textures[texture_str] = CoreImage(texture_str).texture
        texture = textures[texture_str]
        return texture

    def update(self, dt):
        gameworld = self.gameworld
        entities = gameworld.entities
        system_id = self.system_id
        rendering_system = self.renderer_to_modify
        load_texture = self.load_texture
        for entity_id in self.entity_ids:
            entity = entities[entity_id]
            animation_system = entity[system_id]
            r_rendering_system = entity[rendering_system]
            current_state = animation_system['current_state']
            state_dict = animation_system['states'][current_state]
            state_dict['current_frame_time'] += dt
            if state_dict['current_frame_time'] >= state_dict['time_between_frames']:
                state_dict['current_frame_time'] -= state_dict['time_between_frames']
                state_dict['current_frame'] += 1
                if state_dict['current_frame'] >= state_dict['number_of_frames']:
                    state_dict['current_frame'] = 0
                texture_str = state_dict[str(state_dict['current_frame'])]
                r_rendering_system['quad'].texture = load_texture(texture_str)
                r_rendering_system['texture'] = texture_str