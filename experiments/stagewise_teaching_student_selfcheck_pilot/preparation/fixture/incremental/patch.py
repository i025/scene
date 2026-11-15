import bpy
from sceneact import *
cube = bpy.data.objects['red_cube_geometry']
cube.location.x += .75
scene = Scene('FixtureAddition')
second = box((.6, .6, 1.4), center=(-1.2, 0, .7), color=(.03, .1, .8))
second.name = 'blue_block_geometry'
scene.include('blue_block_group', second)
realize(scene, clear=False)
