# Reference inventory and image anchors (normalized image coordinates, x right/y down):
# - Raised concrete beds: foreground edge runs from (0.00, .60) to (.60, 1.00);
#   right-hand bed extends toward (.99, .65). Thin straw and dark damp marks.
# - Holstein cows occupy roughly (0, .28)-(.87, .90), overlapping the rails.
#   The nearest cow has a broad white flank with black patches, muddy hindquarters,
#   folded legs, a black neck and head pointing right; farther cows are partly occluded.
# - Galvanized divider rails form repeated open loops across (.00, .17)-(1.00, .75).
#   Foreground rails rise above the cows and end in vertical posts by the bed edge.
# - Rear concrete wall spans the upper image, with blue door near (.32, .00)-(.44, .19),
#   pale wall panels, blue columns, and a partly visible worker at far right.
# - Main rail and bed edges slope gently down to the right; foreground bed edge
#   slopes more steeply down to the right. The cows obscure lower parts of the rails.
# - Hidden stall ends, cow legs, and the worker's lower body are uncertain.
#
# Approximate expanded primitive count: architecture 15, beds 8, rails 110,
# five cows including patches and limbs 125, worker 12, bedding marks 45:
# approximately 315 primitive meshes, without fillet boxes or Boolean operations.

import bpy
import math
import random
from mathutils import Vector
from sceneact import *

random.seed(12)

# Independent camera and major scene dimensions.
CAM_POS = (8.7, -13.0, 6.4)
CAM_TARGET = (0.0, 1.1, 1.05)
CAM_LENS = 36
BARN_WIDTH = 15.5
BACK_Y = 5.2
BED_FRONT = -1.35
BED_BACK = 3.7
BED_TOP = 0.25
STALL_SPACING = 1.65

scene = Scene('Modern dairy free stalls')
gray = (.48, .49, .47)
concrete = (.49, .50, .49)
bedgray = (.56, .57, .55)
steel = (.62, .66, .66)
blue = (.035, .12, .25)
white = (.77, .76, .69)
black = (.035, .038, .035)
mud = (.29, .27, .20)
straw = (.43, .39, .27)

def add(parent, name, node):
    parent.include(name, node)
    return node

def ellipsoid(parent, name, center, scale, color):
    node = ball(1, center=center, color=color)
    node.resize(scale, pivot=center)
    add(parent, name, node)
    return node

def segment(parent, name, a, b, radius, color):
    add(parent, name, rod(radius, start=a, end=b, color=color))

# Architecture: enclosed rear wall, blue columns, blue double door and upper panels.
arch = Asset('Barn architecture')
add(arch, 'floor', box((BARN_WIDTH, 13, .12), center=(0, .0, -.08), color=(.36,.35,.30)))
add(arch, 'rear concrete wall', box((BARN_WIDTH, .20, 2.5), center=(0, BACK_Y, 1.25), color=(.47,.49,.49)))
add(arch, 'upper pale wall', box((BARN_WIDTH, .18, 2.1), center=(0, BACK_Y, 3.55), color=(.75,.77,.76)))
for i, x in enumerate((-7.25,-4.75,-1.9,1.35,4.8,7.25)):
    add(arch, 'blue wall column %d'%i, box((.14,.22,4.7), center=(x,BACK_Y-.12,2.35), color=blue))
add(arch, 'door frame', box((1.75,.12,2.65), center=(-2.75,BACK_Y-.15,1.325), color=blue))
add(arch, 'door left', box((.80,.08,2.40), center=(-3.17,BACK_Y-.23,1.25), color=(.025,.075,.15)))
add(arch, 'door right', box((.80,.08,2.40), center=(-2.33,BACK_Y-.23,1.25), color=(.025,.075,.15)))
add(arch, 'door crossbar', box((1.62,.05,.05), center=(-2.75,BACK_Y-.28,1.05), color=(.07,.15,.25)))
add(arch, 'upper wall seam', box((BARN_WIDTH,.05,.055), center=(0,BACK_Y-.14,2.5), color=(.36,.39,.40)))
scene.include('architecture', arch)

# Raised continuous platform with a visible front riser and concrete walking alley.
platform = Asset('Raised concrete lying beds')
add(platform, 'bed slab', box((14.5, BED_BACK-BED_FRONT, BED_TOP),
    center=(0,(BED_FRONT+BED_BACK)/2,BED_TOP/2), color=bedgray))
add(platform, 'front dark curb', box((14.5,.14,.23),
    center=(0,BED_FRONT-.04,.11), color=(.35,.36,.34)))
add(platform, 'right concrete alley', box((3.0,8.0,.12),
    center=(6.9,.1,.02), color=(.53,.54,.52)))
# Visible floor seams.
for j, x in enumerate((-6,-4,-2,0,2,4,6)):
    add(platform, 'slab joint %d'%j, box((.025,1.7,.008),
        center=(x,-.52,.257), color=(.35,.36,.34)))
scene.include('lying platform', platform)

# A stall divider is a galvanized pipe loop in the longitudinal direction.
# The horizontal pipe is high at the back, drops and curves towards the front.
rails = Asset('Galvanized free stall divider system')
for i in range(9):
    x = -6.7 + i*STALL_SPACING
    p = [
        (x,3.70,1.25), (x,2.8,1.25), (x,.35,1.25),
        (x,-.15,1.19), (x,-.39,1.02), (x,-.39,.84),
        (x,-.22,.72), (x,.55,.72)
    ]
    for j in range(len(p)-1):
        segment(rails,'divider %d curved tube %d'%(i,j),p[j],p[j+1],.036,steel)
    segment(rails,'divider %d front post'%i,(x,-.35,.22),(x,-.35,.89),.042,steel)
    segment(rails,'divider %d rear post'%i,(x,3.69,.24),(x,3.69,1.27),.039,steel)
# Two continuous longitudinal cross rails provide a recognisable row.
for j, y in enumerate((2.35,3.62)):
    segment(rails,'continuous rail %d'%j,(-7.1,y,1.29),(7.1,y,1.29),.033,steel)
scene.include('stall dividers',rails)

# Cows lie lengthwise along the stalls, tails toward the viewer, heads toward rear.
# Model each as individually editable broad masses, black patches and tucked limbs.
def cow(index, x, y, scale=1.0, variant=0):
    a = Asset('Holstein cow %d'%index)
    z = BED_TOP
    def E(name,c,s,col):
        return ellipsoid(a,name,(x+c[0]*scale,y+c[1]*scale,z+c[2]*scale),
                         tuple(v*scale for v in s),col)
    E('body', (0,0,.48),(.61,1.06,.48),white)
    E('rump', (0,-.72,.45),(.60,.55,.43),white)
    E('shoulders', (0,.66,.56),(.53,.54,.45),white)
    E('neck', (.04,1.06,.57),(.37,.58,.34),black)
    E('head', (.04,1.49,.53),(.30,.38,.28),black)
    E('white muzzle', (.06,1.75,.43),(.25,.19,.15),(.67,.65,.59))
    E('wet nose', (.06,1.89,.43),(.20,.075,.085),(.18,.17,.16))
    E('left ear', (-.36,1.45,.69),(.22,.13,.07),black)
    E('right ear', (.38,1.45,.69),(.22,.13,.07),black)
    E('left eye', (-.24,1.65,.62),(.035,.035,.035),(.015,.015,.015))
    E('right eye', (.27,1.65,.62),(.035,.035,.035),(.015,.015,.015))
    E('folded left leg', (-.42,.15,.19),(.20,.54,.15),white)
    E('folded right leg', (.42,.28,.19),(.20,.53,.15),white)
    E('rear folded leg', (.20,-.79,.18),(.37,.28,.15),(.60,.58,.50))
    E('udder', (.08,-.66,.19),(.28,.27,.14),(.59,.44,.41))
    E('muddy rump', (-.08,-.99,.45),(.44,.20,.30),mud)
    # Surface patches intersect the body to make irregular black areas.
    patches = [
        ((-.43,-.38,.70),(.20,.42,.20)),
        ((.36,-.12,.76),(.25,.31,.18)),
        ((-.27,.38,.82),(.26,.24,.15)),
        ((.45,.48,.60),(.15,.30,.20)),
        ((.12,-.70,.82),(.24,.18,.12)),
    ]
    if variant % 2:
        patches = [((-p[0][0],p[0][1],p[0][2]),p[1]) for p in patches]
    for j,(c,s) in enumerate(patches):
        E('black flank patch %d'%j,c,s,black)
    # Tail trails from the rump onto the concrete.
    segment(a,'tail', (x,y-1.05*scale,z+.38*scale),
            (x+.18*scale,y-1.40*scale,z+.12*scale),.035*scale,mud)
    scene.include('cow %d'%index,a)

# Five overlapping cows in neighboring bays.
cow(1,-4.95,.60, .88,1)
cow(2,-3.27,.35, .96,0)
cow(3,-1.62,.42,1.00,1)
cow(4,.05,.31,1.02,0)
cow(5,1.73,.33,1.05,1)
cow(6,3.40,.65,.93,0)

# Sparse bedding and damp patches; keep the surface mostly bare.
surface = Asset('Scattered bedding and damp patches')
for i in range(38):
    x = random.uniform(-7,7)
    y = random.uniform(-1.22,3.5)
    s = random.uniform(.035,.12)
    ellipsoid(surface,'bedding mark %d'%i,(x,y,.258),(s,s*.45,.006),
              straw if i%3 else (.31,.31,.28))
for i in range(7):
    x = random.uniform(4.7,7.1)
    y = random.uniform(-2.1,1.4)
    ellipsoid(surface,'damp mark %d'%i,(x,y,.09),
              (random.uniform(.12,.27),random.uniform(.09,.20),.006),(.31,.33,.32))
scene.include('surface marks',surface)

# Background employee, scaled to an adult and partly obscured by the rail system.
person = Asset('Farm employee')
px, py = 6.35, 4.20
ellipsoid(person,'head',(px,py,1.67),(.13,.12,.16),(.42,.30,.23))
ellipsoid(person,'hair',(px,py,1.77),(.14,.12,.09),(.10,.09,.08))
add(person,'blue work jacket',box((.42,.24,.55),center=(px,py,1.28),color=(.08,.20,.41)))
segment(person,'left arm',(px-.18,py,1.45),(px-.29,py-.17,1.03),.085,(.08,.20,.41))
segment(person,'right arm',(px+.18,py,1.44),(px+.30,py-.19,1.08),.085,(.08,.20,.41))
segment(person,'left leg',(px-.10,py,1.03),(px-.11,py,.48),.09,(.10,.13,.18))
segment(person,'right leg',(px+.10,py,1.03),(px+.18,py,.48),.09,(.10,.13,.18))
scene.include('employee',person)

realize(scene)

# Set metallic response for the shared galvanized steel material where available.
for obj in bpy.context.scene.objects:
    if obj.type == 'MESH':
        for mat in obj.data.materials:
            if mat and mat.use_nodes:
                bsdf = mat.node_tree.nodes.get('Principled BSDF')
                if bsdf:
                    c = bsdf.inputs['Base Color'].default_value
                    if abs(c[0]-.62)<.025 and abs(c[1]-.66)<.025:
                        bsdf.inputs['Metallic'].default_value = .72
                        bsdf.inputs['Roughness'].default_value = .27
                    else:
                        bsdf.inputs['Roughness'].default_value = .83

sc = bpy.context.scene
if sc.world is None:
    sc.world = bpy.data.worlds.new('SceneWorld')
sc.world.use_nodes = True
background = sc.world.node_tree.nodes.get('Background')
if background is None:
    background = sc.world.node_tree.nodes.new('ShaderNodeBackground')
output = sc.world.node_tree.nodes.get('World Output')
if output is None:
    output = sc.world.node_tree.nodes.new('ShaderNodeOutputWorld')
sc.world.node_tree.links.new(background.outputs['Background'], output.inputs['Surface'])
background.inputs['Color'].default_value = (.65,.71,.78,1)
background.inputs['Strength'].default_value = .55

sc.render.resolution_x = 512
sc.render.resolution_y = 285
sc.render.resolution_percentage = 100
set_view(CAM_POS, CAM_TARGET, lens=CAM_LENS, sensor=36)
area_emitter((0,-1,7.5),power=1800,size=8,target=(0,1,0),color=(.82,.90,1.0))
area_emitter((-5,2,5.5),power=1000,size=6,target=(0,1,0),color=(.89,.94,1.0))

# Projection check uses identifiable geometry landmarks. References are estimates.
bpy.context.view_layer.update()
cam = sc.camera
dg = bpy.context.evaluated_depsgraph_get()
projection = cam.calc_matrix_camera(dg, x=sc.render.resolution_x,
    y=sc.render.resolution_y, scale_x=sc.render.pixel_aspect_x,
    scale_y=sc.render.pixel_aspect_y)
landmarks = [
    ('door top left', (-3.625,BACK_Y-.23,2.65), (.32,.02)),
    ('door bottom right', (-1.875,BACK_Y-.23,0), (.44,.20)),
    ('front curb near center', (0,BED_FRONT,.23), (.50,.80)),
    ('rear rail right end', (7.1,3.62,1.29), (.98,.31)),
]
print('Reference / projected landmarks (normalized image coordinates)')
for name,p,ref in landmarks:
    clip = projection @ cam.matrix_world.inverted() @ Vector((*p,1.0))
    uv = None if clip.w <= 1e-8 else (
        .5*(clip.x/clip.w+1), .5*(1-clip.y/clip.w))
    print(name, 'reference', ref, 'projected', uv)
