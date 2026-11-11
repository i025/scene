# Reference inventory and approximate image anchors, normalized x/y:
# Raised bed front edge: (0,.60) to (.65,1); straw alley below it.
# Main cow: (.35,.36)-(.83,.85), with dark head at right, broad pale
# flank, irregular black markings, muddy rump, folded legs and trailing tail.
# Several partially occluded cows extend to the left and behind it.
# Galvanized divider loops: approximately (0,.16)-(1,.74); the nearest
# vertical support is around x=.84. Rails overlap cows and background.
# Rear concrete wall and pale upper panels fill the background; blue door
# roughly (.32,0)-(.44,.19); worker partly cropped at the far right.
# Main row edges slope down to the right; cow axes project up to the right.
# Hidden legs, far stall ends and the worker's lower body are uncertain.
#
# Comparison with first render:
# Door reference (.32,.00)-(.44,.19), rendered roughly (.45,.25)-(.53,.47).
# Nearest cow reference (.35,.36)-(.83,.85), rendered cows collectively
# about (.22,.43)-(.73,.72); individual silhouettes are much too small.
# Front curb reference crosses the bottom edge near x=.65; rendered whole
# platform is visible with its front edge around y=.75-.91.
# Rear rails reference begin near y=.17, rendered around y=.36-.54.
# The render shows excessive foreground floor and blank space around the
# platform, a steep downward viewing angle, too-regular small spots, and too
# little dark cow coverage. The person and wall are also too small.
#
# Ranked corrections:
# 1. Lower CAMERA_POS height and increase CAMERA_LENS: raise the background
#    in the frame and enlarge cows, rails and door. Aim near the cows so the
#    foreground curb moves toward and beyond the lower frame edge.
# 2. Move CAMERA_POS farther toward negative y relative to x: reduce the
#    row's edge slope and show more of the cows' long side profiles.
# 3. Increase cow body length and vary body colors and broad markings:
#    enlarge the foreground silhouettes and restore dark/light coverage.
# 4. Keep individual open tubular dividers, concrete bed, wall, door and
#    employee; increase rail prominence while retaining visible gaps.
# A small camera trial below prints separate numerical landmark projections;
# the final image is still needed to judge silhouettes and occlusion.
#
# Approximate expanded primitive count: architecture 16, platform 11,
# divider rails 9*9 + 3 = 84, six cows about 6*22 = 132,
# surface marks 35, employee 7: approximately 285 meshes. No booleans.

import bpy
import math
import random
from mathutils import Vector
from sceneact import *

random.seed(19)

# Camera parameters are independent of scene geometry.
CAMERA_POS = (6.3, -15.8, 4.15)
CAMERA_TARGET = (-0.4, 1.10, 1.25)
CAMERA_LENS = 52
BARN_WIDTH = 19.0
BACK_Y = 5.2
BED_FRONT = -1.35
BED_BACK = 3.7
BED_TOP = .25
STALL_SPACING = 1.62

scene = Scene('Modern dairy free stalls')
steel = (.53, .57, .57)
blue = (.025, .09, .18)
white = (.70, .69, .62)
black = (.025, .029, .026)
mud = (.24, .22, .16)
concrete = (.43, .45, .44)

def put(parent, name, node):
    parent.include(name, node)
    return node

def ellipsoid(parent, name, center, scale, color):
    node = ball(1, center=center, color=color)
    node.resize(scale, pivot=center)
    put(parent, name, node)
    return node

def pipe(parent, name, a, b, radius=.035, color=steel):
    put(parent, name, rod(radius, start=a, end=b, color=color))

# Barn enclosure: wall, upper cladding, columns and the metal double door.
arch = Asset('Barn architecture')
put(arch, 'alley floor', box((BARN_WIDTH, 16, .12),
    center=(0, 0, -.08), color=(.32, .30, .24)))
put(arch, 'rear concrete wall', box((BARN_WIDTH, .20, 2.50),
    center=(0, BACK_Y, 1.25), color=(.40, .43, .43)))
put(arch, 'upper pale wall', box((BARN_WIDTH, .18, 2.50),
    center=(0, BACK_Y, 3.75), color=(.72, .74, .73)))
for i, x in enumerate((-8.7, -6.1, -4.75, -1.9, 1.35, 4.8, 7.6)):
    put(arch, 'blue column %d' % i, box((.14, .23, 5.0),
        center=(x, BACK_Y-.12, 2.5), color=blue))
put(arch, 'door frame', box((1.75, .12, 2.65),
    center=(-2.75, BACK_Y-.16, 1.325), color=blue))
for i, x in enumerate((-3.17, -2.33)):
    put(arch, 'door panel %d' % i, box((.80, .08, 2.40),
        center=(x, BACK_Y-.24, 1.25), color=(.018, .055, .12)))
put(arch, 'door crossbar', box((1.62, .05, .055),
    center=(-2.75, BACK_Y-.29, 1.05), color=(.055, .11, .19)))
put(arch, 'concrete wall seam', box((BARN_WIDTH, .05, .045),
    center=(0, BACK_Y-.13, 2.5), color=(.31, .34, .34)))
scene.include('architecture', arch)

platform = Asset('Raised concrete lying beds')
put(platform, 'bed slab', box((18, BED_BACK-BED_FRONT, BED_TOP),
    center=(0, (BED_FRONT+BED_BACK)/2, BED_TOP/2),
    color=(.49, .50, .48)))
put(platform, 'front curb', box((18, .14, .23),
    center=(0, BED_FRONT-.04, .11), color=(.30, .31, .29)))
put(platform, 'right concrete alley', box((3.2, 9, .12),
    center=(7.8, .1, .02), color=(.46, .47, .45)))
for j, x in enumerate((-7, -5, -3, -1, 1, 3, 5, 7)):
    put(platform, 'bed joint %d' % j, box((.022, 1.6, .008),
        center=(x, -.52, .257), color=(.31, .32, .30)))
scene.include('lying platform', platform)

# Tubes form open-sided divider loops, with individual supports.
rails = Asset('Galvanized stall divider system')
for i in range(10):
    x = -7.35 + i*STALL_SPACING
    points = [(x,3.72,1.27), (x,2.65,1.27), (x,.40,1.27),
              (x,-.12,1.22), (x,-.36,1.09), (x,-.40,.92),
              (x,-.31,.78), (x,.57,.70)]
    for j in range(len(points)-1):
        pipe(rails, 'divider %d loop segment %d' % (i,j),
             points[j], points[j+1], .045)
    pipe(rails, 'divider %d front support' % i,
         (x,-.37,.24), (x,-.37,.95), .046)
    pipe(rails, 'divider %d rear support' % i,
         (x,3.70,.24), (x,3.70,1.27), .040)
for i, y in enumerate((2.36, 3.65)):
    pipe(rails, 'continuous cross rail %d' % i,
         (-8.3,y,1.29), (8.3,y,1.29), .039)
scene.include('stall dividers', rails)

# Low, elongated bodies and tucked limbs. Markings are broad intersecting
# surface shapes; the partly hidden sides and legs remain approximate.
def cow(index, x, y, scale=1.0, variant=0, dark_body=False):
    animal = Asset('Holstein cow %d' % index)
    z = BED_TOP
    def E(name, c, s, color):
        center = (x+c[0]*scale, y+c[1]*scale, z+c[2]*scale)
        return ellipsoid(animal, name, center,
                         tuple(v*scale for v in s), color)
    body_color = black if dark_body else white
    E('broad torso', (0,0,.47), (.65,1.13,.45), body_color)
    E('rounded hindquarters', (0,-.78,.43), (.61,.53,.40), body_color)
    E('shoulder', (.02,.75,.51), (.55,.53,.41), body_color)
    E('neck', (.04,1.12,.55), (.38,.55,.32), black)
    E('head', (.04,1.54,.53), (.30,.37,.25), black)
    E('pale muzzle', (.05,1.83,.44), (.24,.19,.15), (.58,.57,.53))
    E('moist nose', (.05,1.99,.44), (.19,.075,.08), (.12,.12,.11))
    E('left ear', (-.35,1.48,.68), (.22,.14,.07), black)
    E('right ear', (.37,1.48,.68), (.22,.14,.07), black)
    E('left eye', (-.24,1.70,.61), (.03,.035,.03), (.008,.008,.008))
    E('right eye', (.26,1.70,.61), (.03,.035,.03), (.008,.008,.008))
    E('folded left foreleg', (-.42,.30,.17), (.20,.54,.14), body_color)
    E('folded right foreleg', (.42,.32,.17), (.20,.52,.14), body_color)
    E('folded hind leg', (.23,-.82,.17), (.36,.30,.14), (.53,.50,.43))
    E('udder', (.08,-.66,.17), (.28,.27,.13), (.48,.34,.31))
    E('mud on rump', (-.06,-1.03,.40), (.46,.20,.28), mud)
    if not dark_body:
        patches = [
            ((-.43,-.42,.68),(.24,.42,.19)),
            (( .38,-.15,.71),(.23,.35,.17)),
            ((-.25, .33,.81),(.29,.27,.12)),
            (( .45, .45,.58),(.16,.30,.19)),
            (( .12,-.75,.76),(.25,.21,.12)),
            ((-.48, .12,.55),(.12,.23,.16))]
    else:
        patches = [
            ((-.39,-.52,.69),(.22,.32,.14)),
            (( .35, .18,.72),(.20,.30,.13))]
    for j, (c,s) in enumerate(patches):
        if variant % 2:
            c = (-c[0],c[1],c[2])
        E('coat marking %d' % j, c, s, white if dark_body else black)
    pipe(animal, 'tail upper',
         (x,y-1.10*scale,z+.35*scale),
         (x+.08*scale,y-1.39*scale,z+.12*scale),
         .034*scale, mud)
    pipe(animal, 'tail tip',
         (x+.08*scale,y-1.39*scale,z+.12*scale),
         (x+.20*scale,y-1.62*scale,z+.04*scale),
         .026*scale, mud)
    scene.include('cow %d' % index, animal)

cow(1,-5.65,.45,.92,1)
cow(2,-4.03,.33,.98,0)
cow(3,-2.41,.40,1.02,1,True)
cow(4,-.79,.30,1.05,0,True)
cow(5,.83,.30,1.08,1)
cow(6,2.45,.53,1.00,0)

surface = Asset('Bedding and damp surface')
for i in range(28):
    x = random.uniform(-8, 8)
    y = random.uniform(-1.22, 3.4)
    r = random.uniform(.04, .15)
    ellipsoid(surface, 'bed fleck %d' % i, (x,y,.258),
              (r,r*.45,.006), (.35,.32,.24) if i%3 else (.25,.26,.23))
for i in range(7):
    x = random.uniform(4.5, 8.0)
    y = random.uniform(-2.1,1.3)
    ellipsoid(surface, 'damp patch %d' % i, (x,y,.09),
              (random.uniform(.12,.28),random.uniform(.09,.20),.006),
              (.26,.28,.27))
scene.include('bedding and damp patches', surface)

person = Asset('Farm employee')
px, py = 6.35, 4.20
ellipsoid(person, 'head', (px,py,1.67), (.13,.12,.16), (.37,.25,.20))
ellipsoid(person, 'hair', (px,py,1.77), (.14,.12,.09), (.08,.07,.06))
put(person, 'blue jacket', box((.42,.24,.55),
    center=(px,py,1.28), color=(.06,.15,.32)))
pipe(person, 'left arm', (px-.18,py,1.45), (px-.29,py-.17,1.03),
     .085, (.06,.15,.32))
pipe(person, 'right arm', (px+.18,py,1.44), (px+.30,py-.19,1.08),
     .085, (.06,.15,.32))
pipe(person, 'left leg', (px-.10,py,1.03), (px-.11,py,.48),
     .09, (.08,.10,.13))
pipe(person, 'right leg', (px+.10,py,1.03), (px+.18,py,.48),
     .09, (.08,.10,.13))
scene.include('employee', person)

realize(scene)

# Give the rail finish a restrained metallic response and the nose a wet sheen.
for obj in bpy.context.scene.objects:
    if obj.type != 'MESH':
        continue
    for mat in obj.data.materials:
        if not mat or not mat.use_nodes:
            continue
        bsdf = mat.node_tree.nodes.get('Principled BSDF')
        if bsdf is None:
            continue
        c = bsdf.inputs['Base Color'].default_value
        if abs(c[0]-.53)<.02 and abs(c[1]-.57)<.02:
            bsdf.inputs['Metallic'].default_value = .75
            bsdf.inputs['Roughness'].default_value = .29
        elif abs(c[0]-.12)<.015 and abs(c[1]-.12)<.015:
            bsdf.inputs['Roughness'].default_value = .24
        else:
            bsdf.inputs['Roughness'].default_value = .82

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
background.inputs['Color'].default_value = (.65,.70,.76,1)
background.inputs['Strength'].default_value = .46

sc.render.resolution_x = 512
sc.render.resolution_y = 285
sc.render.resolution_percentage = 100
set_view(CAMERA_POS, CAMERA_TARGET, lens=CAMERA_LENS, sensor=36)

# Projection check: compare a small upward aim trial with the chosen camera.
# References describe image features; computed points are explicit geometry
# landmarks and do not establish the visible contours.
landmarks = [
    ('door top left', (-3.625,BACK_Y-.24,2.65), (.32,.02)),
    ('door bottom right', (-1.875,BACK_Y-.24,0), (.44,.20)),
    ('foreground curb', (0,BED_FRONT,.23), (.50,.80)),
    ('rear rail right', (7.1,3.65,1.29), (.98,.31)),
]
def projections():
    bpy.context.view_layer.update()
    camera = sc.camera
    dg = bpy.context.evaluated_depsgraph_get()
    matrix = camera.calc_matrix_camera(dg, x=sc.render.resolution_x,
        y=sc.render.resolution_y, scale_x=sc.render.pixel_aspect_x,
        scale_y=sc.render.pixel_aspect_y)
    values = []
    for name, p, ref in landmarks:
        clip = matrix @ camera.matrix_world.inverted() @ Vector((*p,1.0))
        uv = None if clip.w <= 1e-8 else (
            .5*(clip.x/clip.w+1), .5*(1-clip.y/clip.w))
        values.append(uv)
    return values

chosen = projections()
camera = sc.camera
original_rotation = camera.rotation_euler.copy()
trial_target = Vector((CAMERA_TARGET[0], CAMERA_TARGET[1], CAMERA_TARGET[2]+.15))
camera.rotation_euler = (trial_target-camera.location).to_track_quat('-Z','Y').to_euler()
trial = projections()
camera.rotation_euler = original_rotation
bpy.context.view_layer.update()
print('Landmark reference / chosen projection / upward aim trial')
for (name,p,ref), a, b in zip(landmarks, chosen, trial):
    print(name, ref, a, b)

area_emitter((0,-1,7.5), power=1500, size=8,
             target=(0,1,0), color=(.82,.90,1.0))
area_emitter((-5,2,5.5), power=800, size=6,
             target=(0,1,0), color=(.88,.93,1.0))
