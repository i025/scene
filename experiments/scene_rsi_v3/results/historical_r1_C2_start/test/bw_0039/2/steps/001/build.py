# Reference inventory, normalized image coordinates (approximate):
# - Narrow unfinished room, floor 0.20..0.98 x 0.59..1.00; back wall
#   0.45..1.00 x 0.00..0.72; exposed left wall 0.09..0.47 x 0..0.78.
# - Back window 0.62..0.91 x 0.09..0.43: dark opening, white frame,
#   upper and lower panes, dark exterior. Lower sill partly behind ladder.
# - Aluminum folding ladder 0.57..1.00 x 0.22..0.81, with two sloping
#   front rails, rungs, rear legs and hinge. Rear feet partly occluded.
# - Left wall has dark wood uprights, exposed brick/lath, wiring and a
#   white electrical box at 0.15..0.25 x 0.36..0.50.
# - Warm work lamp at upper left, bright enough to obscure nearby wall.
# - Floor debris includes scattered broken timber, lath and pale rubble,
#   especially foreground 0.28..0.96 x 0.76..1.00.
# - Door jambs frame both sides. Hidden structure outside the room is uncertain.
# Estimated expanded primitives: architecture 60, window 14, ladder 30,
# electrical/lamp 9, debris 105: approximately 218 meshes.

from sceneact import *
import bpy, math, random
from mathutils import Vector

random.seed(17)
scene = Scene('Unfinished room')

brick = (0.31, 0.255, 0.19)
brick_light = (0.38, 0.31, 0.23)
mortar = (0.22, 0.19, 0.15)
wood = (0.24, 0.115, 0.055)
wood_light = (0.43, 0.265, 0.13)
wood_cut = (0.55, 0.37, 0.21)
plaster = (0.52, 0.49, 0.40)
metal = (0.57, 0.59, 0.57)
metal_dark = (0.30, 0.32, 0.31)
white = (0.79, 0.79, 0.72)
dark = (0.035, 0.037, 0.032)

room = Asset('Room shell')
room.include('floor', box((2.75, 5.7, .12), center=(0, .6, -.08), color=(.39,.37,.31)))
room.include('back masonry', box((2.75,.16,3.15), center=(0,3.27,1.575), color=brick))
room.include('left masonry', box((.14,5.7,3.15), center=(-1.39,.55,1.575), color=brick))
room.include('right edge wall', box((.12,5.7,3.15), center=(1.39,.55,1.575), color=(.36,.32,.24)))
# Subtle horizontal masonry courses on the visible back wall.
for i in range(16):
    z = .12 + i*.19
    room.include('back mortar %02d'%i, box((2.72,.012,.014), center=(0,3.175,z), color=mortar))
# Exposed wood lath across lower back wall.
for i in range(13):
    z=.14+i*.075
    room.include('back lath %02d'%i, box((2.66,.035,.042), center=(0,3.13,z), color=wood_light if i%3 else wood))
# Visible left side framing, some members close to the camera.
for i,y in enumerate((-1.45,-.83,-.20,.45,1.12,1.83,2.57,3.05)):
    room.include('left stud %02d'%i, box((.09,.10,3.1), center=(-1.27,y,1.55), color=wood if i%2 else wood_light))
room.include('left bottom plate', box((.12,5.4,.10), center=(-1.26,.5,.08), color=wood))
room.include('back top beam', box((2.7,.12,.12), center=(0,3.09,3.06), color=wood))
room.include('back left stud', box((.09,.10,3.0), center=(-1.17,3.10,1.5), color=wood))
# A few dark lath and brick course marks on the left wall.
for i in range(15):
    z=.18+i*.19
    room.include('left course %02d'%i, box((.012,5.0,.016), center=(-1.305,.55,z), color=mortar))
# Doorway in foreground; the opening itself remains unobstructed.
room.include('left door jamb', box((.17,.18,3.2), center=(-1.33,-2.18,1.55), color=(.62,.54,.36)))
room.include('right door jamb', box((.13,.17,3.2), center=(1.35,-2.18,1.55), color=(.52,.48,.35)))
scene.include('room', room)

window = Asset('White double hung window')
# Dark recess laid in front of masonry, with a thick surrounding dark reveal.
window.include('recess', box((1.03,.035,1.47), center=(.44,3.065,2.05), color=(.035,.037,.032)))
window.include('glass upper', box((.79,.025,.65), center=(.44,3.035,2.37), color=(.12,.18,.19)))
window.include('glass lower', box((.79,.025,.48), center=(.44,3.035,1.79), color=(.035,.10,.16)))
for x in (.015,.865):
    window.include('white side frame %.2f'%x, box((.072,.075,1.32), center=(x,2.99,2.09), color=white))
for z,h in ((1.43,.09),(2.075,.09),(2.75,.09)):
    window.include('white cross frame %.2f'%z, box((.92,.08,h), center=(.44,2.99,z), color=white))
window.include('dark outer left', box((.055,.08,1.52), center=(-.09,3.02,2.08), color=(.10,.075,.045)))
window.include('dark outer right', box((.055,.08,1.52), center=(.97,3.02,2.08), color=(.10,.075,.045)))
window.include('dark lintel', box((1.12,.09,.08), center=(.44,3.02,2.83), color=(.09,.07,.045)))
window.include('sill', box((1.10,.19,.08), center=(.44,2.97,1.39), color=(.36,.32,.23)))
# Thin vertical marks visible behind lower pane.
for i in range(8):
    window.include('lower pane bar %02d'%i, box((.012,.012,.34), center=(.12+i*.09,3.005,1.78), color=(.11,.15,.16)))
scene.include('window', window)

electrical = Asset('Electrical box and cabling')
electrical.include('white box', box((.22,.13,.43), center=(-1.18,-.74,1.35), color=(.79,.79,.72)))
electrical.include('box side', box((.025,.145,.43), center=(-1.055,-.74,1.35), color=(.63,.64,.60)))
electrical.include('red cap', box((.12,.12,.025), center=(-1.16,-.74,1.58), color=(.35,.075,.055)))
electrical.include('conduit', rod(.018, start=(-1.18,-.74,1.12), end=(-1.18,-.74,.15), color=(.43,.43,.40)))
electrical.include('loose cable', sweep_tube(points=[(-1.16,.45,2.9),(-1.16,.45,2.1),(-1.14,.44,1.1),(-1.10,.42,.2)], radius=.012, color=(.11,.12,.11)))
scene.include('electrical', electrical)

# Ladder: front climbing frame runs diagonally toward the window; second
# pair of legs opens toward the right/back. Rungs bridge the front rails.
ladder = Asset('Aluminum folding ladder')
front_bottom = Vector((.12,.30,.10))
front_top = Vector((.78,2.30,2.51))
width = .42
for side in (-1,1):
    off=Vector((side*width/2,0,0))
    a=front_bottom+off
    b=front_top+off
    ladder.include('front rail %s'%side, rod(.045, start=tuple(a), end=tuple(b), color=metal))
    rear_bottom=Vector((1.24+side*.19,2.68,.10))
    ladder.include('rear leg %s'%side, rod(.039, start=tuple(b), end=tuple(rear_bottom), color=metal))
    ladder.include('hinge %s'%side, ball(.072, center=tuple(b), color=metal_dark))
    ladder.include('front foot %s'%side, ball(.057, center=tuple(a), color=(.16,.16,.14)))
for i in range(1,9):
    t=i/10
    mid=front_bottom.lerp(front_top,t)
    a=mid+Vector((-width/2,0,0))
    b=mid+Vector((width/2,0,0))
    ladder.include('rung %02d'%i, rod(.027,start=tuple(a),end=tuple(b),color=(.70,.71,.68)))
# Red label on lower rail, represented by a narrow strip.
a=front_bottom.lerp(front_top,.15)+Vector((-.21,-.035,0))
b=front_bottom.lerp(front_top,.39)+Vector((-.21,-.035,0))
ladder.include('red rail marking', rod(.023,start=tuple(a),end=tuple(b),color=(.63,.10,.07)))
scene.include('ladder', ladder)

lamp = Asset('Warm work light')
lamp.include('bulb', ball(.105,center=(-1.03,.30,2.78),color=(1.0,.91,.67)))
lamp.include('fixture', box((.11,.12,.19),center=(-1.13,.30,2.78),color=(.54,.49,.34)))
scene.include('work light',lamp)

debris = Asset('Construction debris')
# Long laths in a loose overlapping pile at the front of the room.
for i in range(32):
    x=random.uniform(-.75,1.03)
    y=random.uniform(-1.78,.16)
    length=random.uniform(.28,1.05)
    z=random.uniform(.025,.095)
    stick=box((length,random.uniform(.025,.055),random.uniform(.015,.035)),
              center=(x,y,z),color=random.choice([wood,wood_light,wood_cut]))
    stick.turn('+z', random.uniform(-75,75))
    debris.include('broken lath %02d'%i,stick)
# Pale rubble spread over the floor, with larger pieces near the foreground.
for i in range(67):
    x=random.uniform(-1.20,1.20)
    y=random.uniform(-1.95,2.55)
    s=random.uniform(.025,.10)
    frag=box((s*random.uniform(.7,1.7),s,random.uniform(.012,.038)),
             center=(x,y,.015),color=random.choice([(0.58,.55,.46),(.46,.43,.35),(.66,.63,.54),(.35,.32,.27)]))
    frag.turn('+z',random.uniform(0,180))
    debris.include('plaster fragment %02d'%i,frag)
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
background.inputs['Color'].default_value=(.18,.17,.14,1)
background.inputs['Strength'].default_value=.32

set_view((.02,-4.45,1.68),(.03,1.45,1.46),lens=32,sensor=36)
area_emitter((-.95,.25,2.8),power=500,size=.42,target=(0,1.5,1.1),color=(1.0,.72,.42))
area_emitter((.3,-2.0,2.9),power=190,size=3.0,target=(0,1.5,1.2),color=(1.0,.84,.65))
area_emitter((.4,2.9,2.1),power=65,size=1.0,target=(0,0,1.2),color=(.48,.60,1.0))
