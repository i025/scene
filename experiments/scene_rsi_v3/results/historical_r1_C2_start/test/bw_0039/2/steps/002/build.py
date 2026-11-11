# Reference inventory, approximate normalized image bounds:
# - Narrow unfinished room: exposed left wall x=.10-.47, rear wall x=.45-1,
#   dusty floor x=.24-1, y=.62-1. Rear wall and ceiling continue beyond frame.
# - White double-hung window x=.62-.91, y=.09-.43, dark reveal, two panes,
#   horizontal sash, dark blue exterior and vertical lower-pane marks.
# - Aluminum folding ladder x=.57-1, y=.22-.81. Two inclined front rails,
#   rungs, rear support, hinges, dark feet and red rail marking. Right support
#   and parts of its feet are occluded by the image boundary and debris.
# - Dark timber studs and lath over rough masonry at left; white electrical
#   box x=.15-.25, y=.36-.50, conduit and loose wires.
# - Bright warm work light near x=.39, y=.13; some nearby detail is obscured.
# - Broken wooden lath and plaster/brick rubble concentrated across the
#   foreground. Door jambs border the scene. Hidden construction is uncertain.
#
# Render comparison: the first view showed too much blank right wall and black
# space above the room; the rear window and ladder appeared too small and low.
# The reference has a darker, rougher wall, a stronger work light, and a more
# diagonally presented ladder. This revision tightens the view, extends the
# walls above the frame, moves the ladder toward the right, and adds restrained
# surface variation.
# Estimated expanded primitive count: room 68, window 23, ladder 23,
# electrical and light 14, debris 120: approximately 248 meshes.

from sceneact import *
import bpy, math, random
from mathutils import Vector

random.seed(17)
scene = Scene('Unfinished room')

brick = (0.25, 0.205, 0.145)
mortar = (0.19, 0.155, 0.115)
wood = (0.19, 0.085, 0.038)
wood_light = (0.37, 0.215, 0.105)
wood_cut = (0.49, 0.31, 0.16)
metal = (0.43, 0.46, 0.44)
metal_dark = (0.22, 0.24, 0.23)
white = (0.77, 0.77, 0.70)

room = Asset('Room shell')
room.include('dusty floor', box((2.75, 5.7, .12), center=(0, .6, -.08),
                                color=(.35,.33,.27)))
room.include('rear exposed masonry', box((2.75,.16,4.5),
                                        center=(0,3.27,2.25), color=brick))
room.include('left exposed masonry', box((.14,5.7,4.5),
                                        center=(-1.39,.55,2.25), color=(.23,.18,.13)))
# The right wall is mostly outside the photographed field of view.
room.include('right wall', box((.12,5.7,4.5), center=(1.39,.55,2.25),
                               color=(.27,.23,.17)))
for i in range(22):
    z = .12 + i*.19
    room.include('rear masonry joint %02d'%i,
                 box((2.72,.012,.011), center=(0,3.175,z), color=mortar))
for i in range(13):
    z=.14+i*.075
    room.include('rear exposed lath %02d'%i,
                 box((2.66,.035,.043), center=(0,3.13,z),
                     color=wood_light if i%3 else wood))
for i,y in enumerate((-1.45,-.83,-.20,.45,1.12,1.83,2.57,3.05)):
    room.include('left vertical stud %02d'%i,
                 box((.09,.10,4.5), center=(-1.27,y,2.25),
                     color=wood if i%2 else wood_light))
room.include('left bottom plate', box((.12,5.4,.10),
                                     center=(-1.26,.5,.08), color=wood))
room.include('rear left stud', box((.09,.10,4.5),
                                  center=(-1.17,3.10,2.25), color=wood))
for i in range(20):
    z=.18+i*.19
    room.include('left masonry joint %02d'%i,
                 box((.012,5.0,.012), center=(-1.305,.55,z), color=mortar))
room.include('left doorway jamb', box((.17,.18,4.5),
                                     center=(-1.33,-2.18,2.25),
                                     color=(.48,.40,.24)))
room.include('right doorway jamb', box((.13,.17,4.5),
                                      center=(1.35,-2.18,2.25),
                                      color=(.45,.41,.29)))
scene.include('room', room)

window = Asset('White double hung window')
window.include('dark recess', box((1.03,.035,1.47),
                                  center=(.44,3.065,2.05), color=(.025,.028,.025)))
window.include('upper glass', box((.79,.025,.65),
                                 center=(.44,3.035,2.37), color=(.09,.14,.15)))
window.include('lower glass', box((.79,.025,.48),
                                 center=(.44,3.035,1.79), color=(.018,.055,.12)))
for x in (.015,.865):
    window.include('white side frame %.2f'%x,
                   box((.072,.075,1.32), center=(x,2.99,2.09), color=white))
for z in (1.43,2.075,2.75):
    window.include('white sash %.2f'%z,
                   box((.92,.08,.09), center=(.44,2.99,z), color=white))
for x in (-.09,.97):
    window.include('dark outer trim %.2f'%x,
                   box((.055,.08,1.52), center=(x,3.02,2.08),
                       color=(.075,.055,.035)))
window.include('dark lintel', box((1.12,.09,.08), center=(.44,3.02,2.83),
                                 color=(.075,.055,.035)))
window.include('sill', box((1.10,.19,.08), center=(.44,2.97,1.39),
                           color=(.28,.25,.19)))
for i in range(8):
    window.include('lower pane bar %02d'%i,
                   box((.012,.012,.34), center=(.12+i*.09,3.005,1.78),
                       color=(.10,.13,.14)))
scene.include('window', window)

electrical = Asset('Electrical box and wiring')
electrical.include('white box', box((.22,.13,.43),
                                    center=(-1.18,-.74,1.35), color=(.76,.76,.69)))
electrical.include('box side', box((.025,.145,.43),
                                   center=(-1.055,-.74,1.35), color=(.58,.59,.55)))
electrical.include('red cap', box((.12,.12,.025),
                                  center=(-1.16,-.74,1.58), color=(.33,.06,.04)))
electrical.include('conduit', rod(.018, start=(-1.18,-.74,1.12),
                                  end=(-1.18,-.74,.15), color=(.37,.37,.34)))
electrical.include('loose dark cable',
                   sweep_tube(points=[(-1.16,.45,3.4),(-1.16,.45,2.1),
                                      (-1.14,.44,1.1),(-1.10,.42,.2)],
                              radius=.012, color=(.08,.085,.08)))
electrical.include('pale hanging wire',
                   sweep_tube(points=[(-1.17,1.18,2.8),(-1.16,1.18,1.9),
                                      (-1.11,1.16,.8),(-1.12,1.13,.3)],
                              radius=.009, color=(.35,.34,.29)))
scene.include('electrical', electrical)

# The climber is positioned diagonally, with the top closer to the rear
# wall and the feet toward the foreground. The right support is partly cropped.
ladder = Asset('Aluminum folding ladder')
front_bottom = Vector((.29,.24,.10))
front_top = Vector((1.02,2.32,2.54))
width = .48
for side in (-1,1):
    off=Vector((side*width/2,0,0))
    a=front_bottom+off
    b=front_top+off
    ladder.include('front rail %s'%side,
                   rod(.047, start=tuple(a), end=tuple(b), color=metal))
    rear_bottom=Vector((1.34+side*.19,2.74,.10))
    ladder.include('rear support %s'%side,
                   rod(.040, start=tuple(b), end=tuple(rear_bottom), color=metal))
    ladder.include('hinge %s'%side, ball(.065, center=tuple(b), color=metal_dark))
    ladder.include('front foot %s'%side,
                   ball(.055, center=tuple(a), color=(.13,.13,.12)))
for i in range(1,9):
    t=i/10
    mid=front_bottom.lerp(front_top,t)
    a=mid+Vector((-width/2,0,0))
    b=mid+Vector((width/2,0,0))
    ladder.include('rung %02d'%i,
                   rod(.026, start=tuple(a), end=tuple(b), color=(.59,.60,.57)))
a=front_bottom.lerp(front_top,.15)+Vector((-.24,-.04,0))
b=front_bottom.lerp(front_top,.40)+Vector((-.24,-.04,0))
ladder.include('red rail marking',
               rod(.022,start=tuple(a),end=tuple(b),color=(.55,.055,.035)))
scene.include('ladder', ladder)

lamp = Asset('Warm work light')
lamp.include('bright bulb', ball(.12,center=(-1.03,.30,2.78),
                                color=(1.0,.88,.60)))
lamp.include('fixture', box((.11,.12,.19),center=(-1.13,.30,2.78),
                            color=(.43,.38,.25)))
scene.include('work light',lamp)

debris = Asset('Construction debris')
for i in range(38):
    x=random.uniform(-.65,1.14)
    y=random.uniform(-1.80,.25)
    length=random.uniform(.27,1.05)
    z=random.uniform(.025,.11)
    stick=box((length,random.uniform(.025,.055),random.uniform(.015,.035)),
              center=(x,y,z),color=random.choice([wood,wood_light,wood_cut]))
    stick.turn('+z',random.uniform(-85,85))
    debris.include('broken timber lath %02d'%i,stick)
for i in range(82):
    x=random.uniform(-1.20,1.20)
    y=random.uniform(-1.95,2.65)
    s=random.uniform(.025,.095)
    frag=box((s*random.uniform(.7,1.7),s,random.uniform(.012,.038)),
             center=(x,y,.015),
             color=random.choice([(.49,.46,.37),(.37,.34,.27),
                                  (.57,.53,.43),(.29,.26,.21)]))
    frag.turn('+z',random.uniform(0,180))
    debris.include('plaster and brick fragment %02d'%i,frag)
scene.include('debris', debris)

realize(scene)

sc=bpy.context.scene
if sc.world is None:
    sc.world=bpy.data.worlds.new('SceneWorld')
sc.world.use_nodes=True
background=sc.world.node_tree.nodes.get('Background')
if background is None:
    background=sc.world.node_tree.nodes.new('ShaderNodeBackground')
output=sc.world.node_tree.nodes.get('World Output')
if output is None:
    output=sc.world.node_tree.nodes.new('ShaderNodeOutputWorld')
sc.world.node_tree.links.new(background.outputs['Background'],output.inputs['Surface'])
background.inputs['Color'].default_value=(.15,.14,.11,1)
background.inputs['Strength'].default_value=.25

# Add small-scale material variation to the shared generated finishes.
# This does not change silhouettes or use an external texture.
for mat in bpy.data.materials:
    if not mat.use_nodes:
        continue
    nodes=mat.node_tree.nodes
    bsdf=nodes.get('Principled BSDF')
    if bsdf is None:
        continue
    base=bsdf.inputs['Base Color'].default_value[:]
    noise=nodes.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value=55.0
    noise.inputs['Detail'].default_value=2.0
    ramp=nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].position=.15
    ramp.color_ramp.elements[0].color=(base[0]*.68,base[1]*.68,base[2]*.68,1)
    ramp.color_ramp.elements[1].position=.85
    ramp.color_ramp.elements[1].color=(min(base[0]*1.14,1),
                                        min(base[1]*1.14,1),
                                        min(base[2]*1.14,1),1)
    mat.node_tree.links.new(noise.outputs['Fac'],ramp.inputs['Fac'])
    mat.node_tree.links.new(ramp.outputs['Color'],bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value=.84

set_view((.02,-4.45,1.68),(.43,1.45,1.28),lens=44,sensor=36)
area_emitter((-.95,.25,2.8),power=440,size=.25,
             target=(0,1.5,1.1),color=(1.0,.72,.42))
area_emitter((.3,-2.0,2.9),power=95,size=3.0,
             target=(0,1.5,1.2),color=(1.0,.84,.65))
area_emitter((.4,2.9,2.1),power=40,size=1.0,
             target=(0,0,1.2),color=(.48,.60,1.0))
