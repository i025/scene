from sceneact import *
scene = Scene('FixtureRoom')
floor = box((6, 6, .1), center=(0, 0, -.05), color=(.55, .55, .55))
floor.name = 'floor_geometry'
scene.include('floor_group', floor)
cube = box((1, 1, 1), center=(0, 0, .5), color=(.75, .05, .03))
cube.name = 'red_cube_geometry'
scene.include('red_cube_group', cube)
realize(scene)
set_view((4, -6, 4), (0, 0, .5), lens=45)
area_emitter((0, -3, 6), power=1200, size=5, target=(0, 0, 0))
