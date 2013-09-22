class LevelMaps:
    levels = [
        #level 1
        {
            'dark_bunny': {'position': (.145, .4)},
            'white_bunnies': [
                {'position': (.15, .8)}
            ],
            'trees': [
                {'position': (.1, .5), 'type': 'small_tree'},
                {'position': (.8, .3), 'type': 'small_tree'}
            ],
            'rocks': [
                {'position': (.25, .85), 'type': 'large_rock'},
                {'position': (.25, .74), 'type': 'large_rock'},
                {'position': (.5, .5), 'type': 'med_rock'},
                {'position': (.5, .39), 'type': 'large_rock'},
                {'position': (.5, .28), 'type': 'large_rock'},
                {'position': (.5, .17), 'type': 'med_rock'},
                {'position': (.5, .06), 'type': 'large_rock'},
                {'position': (.75, .75), 'type': 'med_rock'},
                {'position': (.75, .64), 'type': 'large_rock'},
                {'position': (.75, .86), 'type': 'small_rock'}
            ],
            'clouds': [],
            'hole': {'position': (.90, .75)}
        },
        #level 2
        {
            'dark_bunny': {'position': (.8, .8)},
            'white_bunnies': [
                {'position': (.1, .6)}
                # {'position': (.8, .5)}
            ],
            'trees': [
                {'position': (.5, .7), 'type': 'small_tree'},
                {'position': (.2, .4), 'type': 'small_tree'},
                {'position': (.5, .22), 'type': 'small_tree'}
            ],
            'rocks': [
                {'position': (.65, .85), 'type': 'large_rock'},
                {'position': (.7, .74), 'type': 'large_rock'},
                {'position': (.1, .15), 'type': 'large_rock'},
                {'position': (.18, .14), 'type': 'large_rock'},
                {'position': (.9, .15), 'type': 'large_rock'},
                {'position': (.8, .14), 'type': 'large_rock'}
            ],
            'clouds': [
                {'position': (.5, .5), 'type': 'large_feather', 'vel_max': 0, 'ang_vel': 0}
            ],
            'hole': {'position': (.1, .9)}
        },
        #level 3
        {
            'dark_bunny': {'position': (.125, .167)},
            'white_bunnies': [
                {'position': (.125, .67)}
            ],
            'trees': [
                {'position': (.5, .25), 'type': 'small_tree'},
                {'position': (.25, .75), 'type': 'small_tree'},
                {'position': (.75, .75), 'type': 'small_tree'}
            ],
            'rocks': [
                {'position': (.9, .4), 'type': 'large_rock'},
                {'position': (.85, .5), 'type': 'large_rock'},
                {'position': (.55, .9), 'type': 'large_rock'},
                {'position': (.55, .8), 'type': 'large_rock'},
                {'position': (.55, .7), 'type': 'large_rock'}
            ],
            'clouds': [
                {'position': (.3, .2), 'type': 'large_feather', 'vel_max': 50, 'ang_vel': -.15},
                {'position': (.6, .8), 'type': 'small_feather', 'vel_max': 30, 'ang_vel': .1}
            ],
            'hole': {'position': (.95, .5)}
        }
    ]