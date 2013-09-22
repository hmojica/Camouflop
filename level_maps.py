class LevelMaps:
    levels = [
        #level 1
        {
            'trees': [
                {'position': (.5, .5), 'type': 'small'}
            ],
            'rocks': [],
            'clouds': [],
            'hole': {'position': (.95, .5)}
        },
        #level 2
        {
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