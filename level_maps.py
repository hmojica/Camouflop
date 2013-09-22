class LevelMaps:
    levels = [
        #level 1
        {
            'dark_bunny': {'position': (.145, .4)},
            'white_bunnies': [
                {'position': (.15, .8)}
            ],
            'trees': [
                {'position': (.1, .5), 'type': 'small'},
                {'position': (.8, .3), 'type': 'small'}
            ],
            'rocks': [
                {'position': (.25, .85)},
                {'position': (.25, .74)},
                {'position': (.5, .5)},
                {'position': (.5, .39)},
                {'position': (.5, .28)},
                {'position': (.5, .17)},
                {'position': (.5, .06)},
                {'position': (.75, .75)},
                {'position': (.75, .64)},
                {'position': (.75, .86)}
            ],
            'clouds': [],
            'hole': {'position': (.90, .75)}
        },
        #level 2
        {
            'dark_bunny': {'position': (.125, .167)},
            'white_bunnies': [
                {'position': (.125, .67)}
            ],
            'trees': [
                {'position': (.5, .25), 'type': 'small'},
                {'position': (.25, .75), 'type': 'small'},
                {'position': (.75, .75), 'type': 'small'}
            ],
            'rocks': [
                {'position': (.9, .4)},
                {'position': (.85, .5)},
                {'position': (.55, .9)},
                {'position': (.55, .8)},
                {'position': (.55, .7)}
            ],
            'clouds': [
                {'position': (.3, .2), 'type': 'large_feather', 'vel_max': 50, 'ang_vel': -.15},
                {'position': (.6, .8), 'type': 'small_feather', 'vel_max': 30, 'ang_vel': .1}
            ],
            'hole': {'position': (.95, .5)}
        }
    ]