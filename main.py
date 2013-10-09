import kivy
import math
import levels
import hawk
import boundary
import rabbit
import animation
import environment
import sound
from kivy.app import App
from kivy.properties import (StringProperty, NumericProperty, 
    ObjectProperty, ListProperty, BooleanProperty, DictProperty)
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
import kivent_cython
from kivent_cython import GameSystem, GameScreen
from kivy.clock import Clock
from kivy.core.window import Window
from math import radians, atan2, degrees, pi, ceil, cos, sin
from functools import partial


class Editor(Widget):
    edit_mode = StringProperty('no')
    object_type = StringProperty('none')
    dark_rabbit_added = NumericProperty(None, allownone=True)
    hole_entity = NumericProperty(None, allownone=True)
    current_entity_list = ObjectProperty(None, allownone=True)
    entity_layouts = DictProperty({})
    touch_radius = NumericProperty(10.)
    currently_selected = ListProperty([])
    trees = ['small_tree', 'med_tree', 'large_tree']
    rocks = ['small_rock', 'med_rock', 'large_rock']
    rabbits = ['dark_bunny', 'white_rabbit']
    clouds = ['small_feather', 'large_feather']
    holes = ['hole1']

    def __init__(self, **kwargs):
        super(Editor, self).__init__(**kwargs)
        self.setup_buttons()

    def setup_buttons(self):
        entity_lists = {'place_tree': self.trees, 'place_rock': self.rocks,
            'place_rabbit': self.rabbits, 'place_clouds': self.clouds, 
            'place_hole': self.holes}
        for entity_group in entity_lists:
            layout = BoxLayout(orientation='horizontal', size_hint=(.75, .15),
                pos_hint={'x': .25, 'y': 0.})
            self.entity_layouts[entity_group] = layout
            for entity_type in entity_lists[entity_group]:
                button = Button(text=entity_type, 
                    on_press=self.set_edit_mode)
                button.entity_tuple = (entity_type, entity_group)
                layout.add_widget(button)

    def open_entity_list(self, entity_group):
        current_selected_widget = self.current_entity_list
        if current_selected_widget:
            self.root_layout.remove_widget(current_selected_widget)
            self.current_entity_list = None
        if current_selected_widget != self.entity_layouts[entity_group]:
            layout = self.entity_layouts[entity_group]
            self.current_entity_list = layout
            self.root_layout.add_widget(layout)

    def set_edit_mode(self, instance):
        entity_info = instance.entity_tuple
        self.edit_mode = entity_info[1]
        self.object_type = entity_info[0]

    def query_touch(self, touch):
        gameworld = self.gameworld
        physics_system = gameworld.systems['cymunk-physics']
        touch_radius = self.touch_radius
        query_box = [touch.x-touch_radius, touch.y-touch_radius, 
            touch.x+touch_radius, touch.y+touch_radius]
        touched = physics_system.query_bb(query_box)
        touched = list(set(touched))
        return touched

    def on_touch_move(self, touch):
        entities = self.gameworld.entities
        currently_selected = self.currently_selected
        if self.edit_mode == 'move':
            for entity_id in currently_selected:
                entity = entities[entity_id]
                if 'shadow_renderer' in entity and not entity[
                    'environment_system']['linked_tree'] in currently_selected:
                        continue
                self.update_position(entity_id, touch.dx, touch.dy)

    def on_touch_up(self, touch):
        gameworld = self.gameworld
        entities = gameworld.entities
        currently_selected = self.currently_selected
        if self.edit_mode == 'move':
            for entity_id in currently_selected:
                entity = entities[entity_id]
                if 'environment_system' in entity:
                    entity['environment_system']['color'] = (1., 1., 1., 1.)
        elif self.edit_mode == 'delete':
            for entity_id in currently_selected:
                entity = entities[entity_id]
                if 'shadow_renderer' in entity and not entity[
                    'environment_system']['linked_tree'] in currently_selected:
                        continue
                if 'environment_system' in entity and 'hole' in entity[
                    'environment_system']:
                    self.hole_entity = None
                if 'rabbit_system' in entity and entity[
                    'rabbit_system']['rabbit_type'] == 'dark_bunny':
                    print 'removing dark_rabbit'
                    self.dark_rabbit_added = None
                Clock.schedule_once(
                    partial(gameworld.timed_remove_entity, entity_id))
        self.currently_selected = []

    def on_touch_down(self, touch):
        gameworld = self.gameworld

        if not super(Editor, self).on_touch_down(touch):
            camera_pos = gameworld.systems['default_gameview'].camera_pos
            touch.x -= camera_pos[0]
            touch.y -= camera_pos[1]
            if self.edit_mode == 'place_tree':
                self.add_tree((touch.x, touch.y), self.object_type)
            elif self.edit_mode == 'place_rock':
                self.add_rock((touch.x, touch.y), self.object_type)
            elif self.edit_mode == 'place_rabbit':
                self.add_rabbit((touch.x, touch.y), self.object_type)
            elif self.edit_mode == 'place_clouds':
                self.add_clouds((touch.x, touch.y), self.object_type)
            elif self.edit_mode == 'place_hole':
                self.add_hole((touch.x, touch.y), self.object_type)
            elif self.edit_mode == 'move':
                touched = self.query_touch(touch)
                entities = gameworld.entities
                self.currently_selected = touched
                for entity_id in touched:
                    entity = entities[entity_id]
                    if 'environment_system' in entity:
                        entity['environment_system']['color'] = (0., 1., 0., 1.)
            elif self.edit_mode == 'delete':
                entities = gameworld.entities
                touched = self.query_touch(touch)
                self.currently_selected = touched
                for entity_id in touched:
                    entity = entities[entity_id]
                    if 'environment_system' in entity:
                        entity['environment_system']['color'] = (1., 0., 0., 1.)
 

    def add_hole(self, position, hole_type):
        gameworld = self.gameworld
        systems = gameworld.systems
        if self.hole_entity == None:
            environment_system = systems['environment_system']
            hole_id = environment_system.add_hole(position)
            self.hole_entity = hole_id
        else:
            self.set_position(self.hole_entity, position)

    def update_position(self, entity_id, dx, dy):
        gameworld = self.gameworld
        systems = gameworld.systems
        entities = gameworld.entities
        entity = entities[entity_id]
        physics_body = entity['cymunk-physics']['body']
        current_position = physics_body.position
        physics_body.position = (current_position[0] + dx, 
            current_position[1] + dy)
        physics_system = systems['cymunk-physics']
        space = physics_system.space
        for shape in entity['cymunk-physics']['shapes']:
            space.reindex_shape(shape)

    def set_position(self, entity_id, position):
        gameworld = self.gameworld
        systems = gameworld.systems
        entities = gameworld.entities
        entity = entities[entity_id]
        physics_body = entity['cymunk-physics']['body']
        physics_body.position = position
        physics_system = systems['cymunk-physics']
        space = physics_system.space
        for shape in entity['cymunk-physics']['shapes']:
            space.reindex_shape(shape)

    def add_tree(self, position, tree_type):
        environment_system = self.gameworld.systems['environment_system']
        environment_system.add_tree(position, tree_type)

    def add_rock(self, position, rock_type):
        environment_system = self.gameworld.systems['environment_system']
        environment_system.add_rock(position, rock_type)

    def add_clouds(self, position, cloud_type):
        environment_system = self.gameworld.systems['environment_system']
        environment_system.add_cloud(position, 
                cloud_type, vel_max=50)

    def add_rabbit(self, position, rabbit_type):
        gameworld = self.gameworld
        systems = gameworld.systems
        rabbit_system = systems['rabbit_system']
        if rabbit_type == 'dark_bunny':
            if self.dark_rabbit_added == None:
                rabbit = rabbit_system.add_rabbit('dark_bunny', position)
                self.dark_rabbit_added = rabbit
            else:
                self.set_position(self.dark_rabbit_added, position)

        else:
            rabbit_system.add_rabbit(rabbit_type, position)


class SliderSetting(Widget):
    slider_name = StringProperty('default')
    slider_value = NumericProperty(1.)


class Timer(Widget):
    timer_count = NumericProperty(10)

    def start_timer(self):
        Clock.schedule_once(self.decrement_timer, 1.0)

    def decrement_timer(self, dt):
        if self.timer_count > 0:
            self.timer_count -= 1
            Clock.schedule_once(self.decrement_timer, 1.0)
        else:
            self.timer_count = 10
        

class MainScreen(GameScreen):
    timer = ObjectProperty(None)
    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)

    def add_timer(self):
        if not self.timer:
            self.timer = Timer()
        self.layout.add_widget(self.timer)
        self.timer.start_timer()
        Clock.schedule_once(self.remove_timer, 10.)
        self.timer.pos_hint = {'x': .4, 'y': .4}
        self.timer.size_hint = (.2, .2)

    def remove_timer(self, dt):
        self.layout.remove_widget(self.timer)


class DarkBunnyGame(Widget):
    
    def __init__(self, **kwargs):
        super(DarkBunnyGame, self).__init__(**kwargs)
        Clock.schedule_once(self._init_game)

    def _init_game(self, dt):
        try:
            self.init_game(0)
        except:
            print 'failed: rescheduling init'
            Clock.schedule_once(self._init_game)

    def init_game(self, dt):
        self.setup_states()
        self.setup_map()
        self.set_state()

        Clock.schedule_interval(self.update, 1./60.)
        Clock.schedule_once(self.setup_stuff)

    def setup_map(self):
        self.gameworld.currentmap = self.gameworld.systems['map']

    def update(self, dt):
        self.gameworld.update(dt)

    def setup_states(self):
        self.gameworld.add_state(state_name='main', systems_added=[
            'physics_renderer2', 
            'rabbit_system', 'physics_renderer', 'shadow_renderer',
            'tree_physics_renderer', 'hawk_physics_renderer',],
            systems_removed=[],
            systems_paused=[], systems_unpaused=['cymunk-physics', 
            'physics_renderer2', 'physics_renderer', 
            'tree_physics_renderer', 'hawk_physics_renderer',
            'animation_system', 'shadow_renderer', 'hawk_ai_system', 
            'rabbit_system', 'default_gameview'],
            screenmanager_screen='main')
        self.gameworld.add_state(state_name='menu', systems_added=[],
            systems_removed=['physics_renderer2', 'physics_renderer', 
            'tree_physics_renderer', 'hawk_physics_renderer', 
            'shadow_renderer', 'rabbit_system'],
            systems_paused=['cymunk-physics', 'physics_renderer2', 
            'physics_renderer', 'tree_physics_renderer', 
            'hawk_physics_renderer', 
            'shadow_renderer', 'animation_system', 'hawk_ai_system', 
            'rabbit_system'], systems_unpaused=[],
            screenmanager_screen='menu')
        self.gameworld.add_state(state_name='settings', systems_added=[],
            systems_removed=['physics_renderer2', 'physics_renderer', 
            'tree_physics_renderer', 'hawk_physics_renderer', 
            'shadow_renderer', 'rabbit_system'],
            systems_paused=['cymunk-physics', 'physics_renderer2', 
            'physics_renderer', 'tree_physics_renderer', 
            'hawk_physics_renderer', 
            'shadow_renderer', 'animation_system', 'hawk_ai_system', 
            'rabbit_system'], systems_unpaused=[],
            screenmanager_screen='settings')
        self.gameworld.add_state(state_name='gameover', systems_added=[],
            systems_removed=['physics_renderer2', 'physics_renderer', 
            'tree_physics_renderer', 'hawk_physics_renderer', 
            'shadow_renderer', 'rabbit_system'],
            systems_paused=['cymunk-physics', 'physics_renderer2', 
            'physics_renderer', 'tree_physics_renderer', 
            'hawk_physics_renderer', 
            'shadow_renderer', 'animation_system', 'hawk_ai_system', 
            'rabbit_system'], systems_unpaused=[],
            screenmanager_screen='gameover')
        self.gameworld.add_state(state_name='pause', systems_added=[],
            systems_removed=['physics_renderer2', 'physics_renderer', 
            'tree_physics_renderer', 'hawk_physics_renderer', 
            'shadow_renderer', 'rabbit_system'],
            systems_paused=['cymunk-physics', 'physics_renderer2', 
            'physics_renderer', 'tree_physics_renderer', 
            'hawk_physics_renderer', 
            'shadow_renderer', 'animation_system', 'hawk_ai_system', 
            'rabbit_system'], systems_unpaused=[],
            screenmanager_screen='pause')
        self.gameworld.add_state(state_name='credits', systems_added=[],
            systems_removed=['physics_renderer2', 'physics_renderer', 
            'tree_physics_renderer', 'hawk_physics_renderer', 
            'shadow_renderer', 'rabbit_system'],
            systems_paused=['cymunk-physics', 'physics_renderer2', 
            'physics_renderer', 'tree_physics_renderer', 
            'hawk_physics_renderer', 'shadow_renderer', 
            'animation_system', 'hawk_ai_system', 
            'rabbit_system'], systems_unpaused=[],
            screenmanager_screen='credits')
        self.gameworld.add_state(state_name='editor', systems_added=[
            'physics_renderer2', 'physics_renderer', 'shadow_renderer', 
            'tree_physics_renderer', 'hawk_physics_renderer',],
            systems_removed=['rabbit_system'],
            systems_paused=['animation_system', 'hawk_ai_system', 
            'rabbit_system'], systems_unpaused=['cymunk-physics', 
            'physics_renderer2', 'physics_renderer', 
            'tree_physics_renderer', 'hawk_physics_renderer', 
            'shadow_renderer',],
            screenmanager_screen='editor')

    def no_impact_collision(self, space, arbiter):
        return False

    def start_game(self):
        self.gameworld.state = 'main'
        systems = self.gameworld.systems
        gameview = systems['default_gameview']
        gameview.focus_entity = True
        
    def pause_game(self):
        self.gameworld.state = 'pause'

    def open_editor(self):
        systems = self.gameworld.systems
        levels_system = systems['levels_system']
        self.gameworld.state = 'editor'
        levels_system.clear_gameworld_objects()
        gameview = systems['default_gameview']
        gameview.focus_entity = False

    def set_game_over(self):
        self.gameworld.state = 'gameover'
        systems = self.gameworld.systems
        levels_system = systems['levels_system']
        levels_system.current_level_id = 0
        
    def setup_collision_callbacks(self):
        systems = self.gameworld.systems
        physics = systems['cymunk-physics']
        rabbit_system = systems['rabbit_system']
        physics.add_collision_handler(1, 2,
            begin_func=rabbit_system.rabbit_collide_with_hole)
        physics.add_collision_handler(
            10, 2, begin_func=self.no_impact_collision)
        physics.add_collision_handler(
            1, 10, begin_func=rabbit_system.collide_white_rabbit_and_halo)
        physics.add_collision_handler(
            3, 2, begin_func=self.no_impact_collision)
        physics.add_collision_handler(
            3, 10, begin_func=self.no_impact_collision)
        physics.add_collision_handler(
            3, 11, begin_func=self.no_impact_collision)
        physics.add_collision_handler(
            1, 11, begin_func=rabbit_system.collide_rabbit_and_boundary)
        physics.add_collision_handler(
            10, 2, begin_func=self.no_impact_collision)
        physics.add_collision_handler(
            1,10, begin_func=rabbit_system.collide_white_rabbit_and_halo)
        physics.add_collision_handler(
            10,4,begin_func=self.no_impact_collision)
        physics.add_collision_handler(
            1,4, begin_func=rabbit_system.enter_shadow,
            separate_func=rabbit_system.leave_shadow)
        physics.add_collision_handler(
            3, 1, begin_func=self.no_impact_collision)
        physics.add_collision_handler(
            3, 5, begin_func=self.no_impact_collision)
        physics.add_collision_handler(
            3, 4, begin_func=self.no_impact_collision)
        physics.add_collision_handler(
            3, 10, begin_func=self.no_impact_collision)
        physics.add_collision_handler(
            10, 11, begin_func=self.no_impact_collision)
        physics.add_collision_handler(
            1, 3, begin_func=self.no_impact_collision,
            separate_func=rabbit_system.collide_rabbit_with_hawk)
        physics.add_collision_handler(
            4, 4, begin_func=self.no_impact_collision)
        physics.add_collision_handler(
            5, 4, begin_func=self.no_impact_collision)
        physics.add_collision_handler(
            5, 10, begin_func=self.no_impact_collision)
        physics.add_collision_handler(
            11, 4, begin_func=self.no_impact_collision)
        physics.add_collision_handler(
            2, 4, begin_func=self.no_impact_collision)

    def set_state(self):
        self.gameworld.state = 'menu'

    def open_settings(self):
        self.gameworld.state = 'settings'

    def open_credits(self):
        self.gameworld.state = 'credits'

    def setup_stuff(self, dt):
        systems = self.gameworld.systems
        levels_system = systems['levels_system']
        levels_system.current_level_id = 0
        self.setup_collision_callbacks()
        self.gameworld.music_controller.play_new_song(30)

    def generate_level(self):
        systems = self.gameworld.systems
        levels_system = systems['levels_system']
        Clock.schedule_once(levels_system.generate_next_level)


class DebugPanel(Widget):
    fps = StringProperty(None)

    def __init__(self, **kwargs):
        super(DebugPanel, self).__init__(**kwargs)
        Clock.schedule_interval(self.update_fps, .1)

    def update_fps(self,dt):
        self.fps = str(int(Clock.get_fps()))


class DarkApp(App):
    music_level = NumericProperty(1.)
    sound_level = NumericProperty(1.)

    def build(self):
        pass

if __name__== '__main__':

    DarkApp().run()

