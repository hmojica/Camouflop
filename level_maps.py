class LevelMaps:
    levels = [
	#level 0
	{
	    'dark_bunny': {'position': (.9, .145)},
            'white_bunnies': [
                {'position': (.95, .9)},
 		{'position': (.1, .1)},
		{'position': (.2, .65)}
            ],
            'trees': [
                {'position': (.1, .5), 'type': 'small_tree'},
                {'position': (.8, .5), 'type': 'small_tree'},
		{'position': (.6, .4), 'type': 'large_tree'},
		{'position': (.2, .8), 'type': 'large_tree'},
		{'position': (.2, .3), 'type': 'med_tree'},
		{'position': (.35, .47), 'type': 'med_tree'},
		{'position': (.55, .1), 'type': 'small_tree'},
		{'position': (.05, .2), 'type': 'small_tree'}
            ],
            'rocks': [
                {'position': (.9, .78), 'type': 'large_rock'},
                {'position': (.95, .74), 'type': 'large_rock'},
                {'position': (.98, .8), 'type': 'med_rock'},
                {'position': (.85, .8), 'type': 'large_rock'},
		{'position': (.3, .2), 'type': 'med_rock'},
            ],
            'clouds': [{'position': (.6, .8), 'type': 'small_feather', 'vel_max': 30, 'ang_vel': .1}],
            'holes': [{'position': (.90, .25)}],
            'wooden_log': []	
	},
        #level 1
        {
            'dark_bunny': {'position': (.145, .4)},
            'white_bunnies': [
                {'position': (.15, .8)},
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
            'holes': [{'position': (.90, .75)}],
            'wooden_log': [{'position': (.5, .8)}]
        },
        #level 2
        {
            'dark_bunny': {'position': (.8, .8)},
            'white_bunnies': [
                {'position': (.1, .6)},
                {'position': (.9, .05)}
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
            'holes': [{'position': (.1, .9)}],
            'wooden_log': []
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
            'holes': [{'position': (.95, .5)}],
            'wooden_log': []
        },
        #level 4
        {
            'dark_bunny': {'position': (.5, .5)},
                'white_bunnies': [
                    {'position': (.1, .7)},
            {'position': (.3, .3)},
            {'position': (.7, .7)}
                ],
                'trees': [
                    {'position': (.4, .2), 'type': 'small_tree'},
                    {'position': (.6, .4), 'type': 'small_tree'},
            {'position': (.4, .4), 'type': 'small_tree'}

                ],
                'rocks': [
                    {'position': (.1, .6), 'type': 'large_rock'},
                    {'position': (.2, .6), 'type': 'large_rock'},
                    {'position': (.3, .6), 'type': 'med_rock'},
                    {'position': (.4, .5), 'type': 'large_rock'},
            {'position': (.4, .4), 'type': 'med_rock'},
            {'position': (.5, .3), 'type': 'med_rock'},
            {'position': (.6, .6), 'type': 'med_rock'},
            {'position': (.6, .5), 'type': 'med_rock'}
                ],
                'clouds': [],
                'holes': [{'position': (.9, .1)}],
                'wooden_log': []
        },
        #level 5
        {
            'dark_bunny': {'position': (.9, .9)},
            'white_bunnies': [
                {'position': (.1, .125)},
                {'position': (.1, .25)},
                {'position': (.1, .375)},
                {'position': (.1, .5)},
                {'position': (.1, .625)},
                {'position': (.1, .75)}
            ],
            'trees': [],
            'rocks': [],
            'clouds':[],
            'holes': [
                {'position': (.7, .125)},
                {'position': (.9, .25)},
                {'position': (.8, .375)},
                {'position': (.7, .5)},
                {'position': (.9, .625)},
                {'position': (.7, .75)}
            ],
            'wooden_log': []
        }
    ]
