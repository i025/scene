# Reference inventory and approximate image anchors (normalized x right, y down):
# Raised concrete beds and curb: (0.00, 0.51)-(1.00, 1.00); front curb edge
# descends from left toward the lower right. Brown bedding passage fills foreground.
# Foreground reclining Holstein: (0.35, 0.40)-(0.83, 0.94), partly overlapped by
# steel stall loops. Other partly occluded cows occupy left and middle beds.
# Galvanized dividers: (0.00, 0.15)-(1.00, 0.70); rounded loops and horizontal
# rails overlap the animals. Their parallel edges recede through the scene.
# Gray concrete rear wall and pale panels: upper part of image; dark blue door
# approximately (0.31, 0.00)-(0.44, 0.19), blue structural posts, distant worker
# at (0.94, 0.12)-(1.00, 0.43). Hidden legs and distant cows are uncertain.
#
# Estimated primitive count: architecture 21 boxes; stall equipment 242 rods and
# 108 bend balls; cows about 198 balls and rods; employee 7; bedding 35 rods:
# approximately 611 meshes. All assets and meaningful child parts remain editable.

import math
import random
import bpy
from mathutils import Vector
from sceneact import *

random.seed(13)

BED_LENGTH = 10.8
BED_DEPTH = 5.5
BED_TOP = 0.22
BACK_WALL_Y = 3.3
STALL_X0 = -4.7
STALL_YS = [-2.35, -1.35, -0.35, 0.65, 1.65, 2.65]
RAIL_HEIGHT = 1.25

CAMERA_POSITION = (4.1, -10.8, 4.3)
CAMERA_TARGET = (0.0, 0.15, 0.95)
CAMERA_LENS = 36
IMAGE_WIDTH, IMAGE_HEIGHT = 512, 285

concrete = (0.47, 0.48, 0.47)
concrete_light = (0.58, 0.59, 0.57)
wall_gray = (0.44, 0.46, 0.46)
panel_white = (0.82, 0.84, 0.83)
blue = (0.035, 0.13, 0.31)
dark_blue = (0.015, 0.055, 0.16)
steel = (0.56, 0.60, 0.60)
black = (0.025, 0.028, 0.026)
white = (0.78, 0.77, 0.69)
muzzle = (0.42, 0.35, 0.32)
straw = (0.45, 0.38, 0.22)

scene = Scene('Modern dairy free-stall barn')

def add_box(parent, name, size, center, color):
    parent.include(name, box(size=size, center=center, color=color))

def add_ball(parent, name, center, radii, color):
    node = ball(1, center=center, color=color)
    node.resize(radii)
    parent.include(name, node)

def add_rod(parent, name, a, b, radius, color):
    parent.include(name, rod(radius=radius, start=a, end=b, color=color))

def path(parent, name, points, radius=0.035, color=steel):
    for i in range(len(points)-1):
        add_rod(parent, name + '_segment_' + str(i),
                points[i], points[i+1], radius, color)
    for i, p in enumerate(points[1:-1]):
        add_ball(parent, name + '_bend_' + str(i), p,
                 (radius, radius, radius), color)

building = Asset('Barn architecture')
add_box(building, 'lower rear concrete wall', (14, .18, 1.48),
        (0, BACK_WALL_Y, .74), wall_gray)
add_box(building, 'upper pale wall panels', (14, .16, 1.75),
        (0, BACK_WALL_Y, 2.35), panel_white)
add_box(building, 'raised concrete bed slab', (BED_LENGTH, BED_DEPTH, BED_TOP),
        (0, -.05, BED_TOP/2), concrete_light)
add_box(building, 'front bed curb', (BED_LENGTH, .16, .26),
        (0, -2.82, .12), concrete)
add_box(building, 'foreground walkway', (16, 7, .10),
        (0, -6.34, -.08), (0.37, 0.34, 0.27))
add_box(building, 'rear walkway', (14, 1.0, .10),
        (0, 2.95, -.04), concrete)
add_box(building, 'blue doorway panel', (1.55, .08, 2.25),
        (-2.45, BACK_WALL_Y-.13, 1.13), dark_blue)
add_box(building, 'door left jamb', (.11, .11, 2.32),
        (-3.25, BACK_WALL_Y-.19, 1.16), blue)
add_box(building, 'door right jamb', (.11, .11, 2.32),
        (-1.65, BACK_WALL_Y-.19, 1.16), blue)
add_box(building, 'door header', (1.72, .11, .12),
        (-2.45, BACK_WALL_Y-.19, 2.27), blue)
add_box(building, 'door center seam', (.025, .035, 2.1),
        (-2.45, BACK_WALL_Y-.24, 1.11), blue)
for i, x in enumerate([-5.8, 2.9, 6.6]):
    add_box(building, 'blue structural column %d' % i, (.18, .20, 3.25),
            (x, BACK_WALL_Y-.16, 1.63), blue)
for i, x in enumerate([-5.0, -3.8, -1.0, .2, 1.4, 4.0, 5.2]):
    add_box(building, 'upper panel seam %d' % i, (.018, .02, 1.7),
            (x, BACK_WALL_Y-.10, 2.35), (0.60, .63, .63))
scene.include('architecture', building)

rails = Asset('Galvanized steel stall dividers')
for j, y in enumerate(STALL_YS):
    divider = Asset('stall divider %02d' % j)
    for k, base_x in enumerate([STALL_X0, .10]):
        end = base_x + 4.55
        points = [
            (base_x, y, .30), (base_x, y, 1.02),
            (base_x+.06, y, 1.17), (base_x+.20, y, RAIL_HEIGHT),
            (end-.20, y, RAIL_HEIGHT), (end-.06, y, 1.20),
            (end, y, 1.08), (end, y, .78),
            (end-.10, y, .69), (end-.28, y, .70),
            (base_x+.52, y, .89)
        ]
        path(divider, 'loop %d' % k, points, .036)
    add_rod(divider, 'upright support', (4.62, y, .22),
            (4.62, y, 1.30), .045, steel)
    rails.include('divider %02d' % j, divider)
for j, z in enumerate([1.25, 1.12]):
    add_rod(rails, 'cross rail %d' % j, (-5.3, 2.75-j*.24, z),
            (5.3, 2.75-j*.24, z), .035, steel)
scene.include('stall equipment', rails)

def make_cow(name, x, y, scale=1.0, variation=0):
    cow = Asset(name)
    s = scale
    z = BED_TOP
    def ell(n, dx, dy, dz, rx, ry, rz, col):
        add_ball(cow, n, (x+dx*s, y+dy*s, z+dz*s),
                 (rx*s, ry*s, rz*s), col)
    def limb(n, a, b, r, col):
        add_rod(cow, n,
                (x+a[0]*s, y+a[1]*s, z+a[2]*s),
                (x+b[0]*s, y+b[1]*s, z+b[2]*s), r*s, col)
    ell('broad torso', -.12, 0, .52, 1.05, .48, .46, white)
    ell('hindquarter', -.83, -.01, .42, .47, .43, .35, white)
    ell('chest', .62, 0, .47, .44, .43, .38, white)
    ell('neck', .93, 0, .64, .43, .31, .30, black)
    ell('head', 1.24, -.02, .65, .34, .25, .25, black)
    ell('white forehead blaze', 1.39, -.19, .67, .14, .075, .16, white)
    ell('moist muzzle', 1.52, -.01, .53, .20, .22, .13, muzzle)
    ell('near ear', 1.05, -.28, .79, .20, .10, .075, black)
    ell('far ear', 1.05, .26, .79, .20, .10, .075, black)
    ell('near eye', 1.35, -.235, .72, .035, .025, .035, (.006,.006,.005))
    ell('folded rear leg', -.60, -.28, .21, .43, .18, .15, white)
    ell('rear hoof', -.91, -.31, .16, .16, .15, .09, (.18,.16,.13))
    ell('folded front leg', .53, -.25, .21, .39, .15, .13, white)
    ell('front hoof', .85, -.27, .16, .15, .13, .08, (.18,.16,.13))
    ell('udder', -.36, -.23, .20, .31, .18, .13, (.65,.48,.43))
    patterns = [
        [(-.78,-.411,.52,.29,.055,.26),(-.40,-.455,.67,.27,.05,.24),
         (.08,-.455,.63,.22,.05,.18),(.42,-.39,.51,.20,.07,.24),
         (-.18,-.28,.90,.38,.16,.07)],
        [(-.72,-.40,.54,.36,.06,.28),(-.27,-.45,.58,.25,.05,.26),
         (.29,-.43,.66,.31,.06,.21),(.65,-.34,.51,.18,.07,.20),
         (-.35,-.22,.91,.40,.18,.07)],
        [(-.70,-.40,.53,.28,.06,.26),(-.32,-.44,.67,.34,.06,.22),
         (.19,-.45,.56,.23,.06,.23),(.57,-.34,.66,.20,.07,.17),
         (.06,-.20,.92,.35,.18,.07)]
    ]
    for i, p in enumerate(patterns[variation % len(patterns)]):
        ell('black hide patch %d' % i, *p, black)
    limb('tail', (-1.00,.05,.43), (-1.22,-.02,.12), .035, white)
    ell('tail tuft', -1.23, -.02, .10, .10, .065, .07, black)
    return cow

cows = Asset('Reclining Holstein cows')
for i, spec in enumerate([
    (-.25, -1.93, 1.02, 0),
    (-1.75, -.98, .96, 1),
    (-3.35, -.05, .91, 2),
    (-.65, .12, .91, 2),
    (-2.65, 1.12, .83, 0),
    (.40, 1.13, .83, 1),
    (-4.1, 2.10, .76, 1),
    (-1.35, 2.10, .77, 2),
    (1.6, 2.03, .76, 0)
]):
    cows.include('cow %02d' % i, make_cow('Holstein %02d' % i, *spec))
scene.include('cows', cows)

person = Asset('Barn employee')
px, py, pz = 4.25, 2.95, .05
add_ball(person, 'head', (px,py,pz+1.60), (.115,.105,.14), (.48,.32,.25))
add_ball(person, 'dark hair', (px-.015,py+.015,pz+1.69),
         (.12,.11,.075), (.08,.07,.06))
add_box(person, 'blue work jacket', (.40,.24,.53),
        (px,py,pz+1.22), (.07,.20,.44))
add_rod(person, 'left sleeve', (px-.18,py,1.40), (px-.30,py-.05,1.08),
        .075, (.07,.20,.44))
add_rod(person, 'right sleeve', (px+.18,py,1.40), (px+.29,py-.08,1.08),
        .075, (.07,.20,.44))
add_rod(person, 'left trouser leg', (px-.10,py,.99), (px-.11,py,.48),
        .095, (.08,.10,.15))
add_rod(person, 'right trouser leg', (px+.10,py,.99), (px+.13,py,.48),
        .095, (.08,.10,.15))
scene.include('employee', person)

bedding = Asset('Scattered straw bedding')
for i in range(35):
    x = random.uniform(-5, 5)
    y = random.uniform(-4.8, 2.4)
    z = .235 if y > -2.75 else -.015
    length = random.uniform(.06, .18)
    angle = random.uniform(0, math.tau)
    add_rod(bedding, 'straw %02d' % i, (x,y,z),
            (x+length*math.cos(angle), y+length*math.sin(angle), z+.005),
            .008, straw)
scene.include('bedding', bedding)

realize(scene)

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
background.inputs['Color'].default_value = (.71, .78, .83, 1)
background.inputs['Strength'].default_value = .65

set_view(CAMERA_POSITION, CAMERA_TARGET, lens=CAMERA_LENS, sensor=36)
area_emitter((0, -1, 7), power=1600, size=8, target=(0,0,0),
             color=(.83, .90, 1.0))
area_emitter((-5, -2, 4.5), power=650, size=5, target=(-1,0,.4),
             color=(.91, .95, 1.0))

for mat in bpy.data.materials:
    if not mat.use_nodes:
        continue
    bsdf = mat.node_tree.nodes.get('Principled BSDF')
    if bsdf is None:
        continue
    rgba = bsdf.inputs['Base Color'].default_value
    rgb = tuple(rgba[:3])
    if sum(abs(rgb[i] - steel[i]) for i in range(3)) < .08:
        bsdf.inputs['Metallic'].default_value = .78
        bsdf.inputs['Roughness'].default_value = .28
    elif sum(abs(rgb[i] - muzzle[i]) for i in range(3)) < .08:
        bsdf.inputs['Roughness'].default_value = .24
    else:
        bsdf.inputs['Roughness'].default_value = .82

# Projection diagnostics use actual geometry points and the supplied image aspect.
# Estimates are not calibration or a visibility test.
anchors = [
    ('door top left', (-3.25, BACK_WALL_Y-.19, 2.27), (.31, .03)),
    ('door top right', (-1.65, BACK_WALL_Y-.19, 2.27), (.43, .03)),
    ('door lower right', (-1.65, BACK_WALL_Y-.19, 0.0), (.43, .20)),
    ('front curb left', (-5.4, -2.90, .25), (.00, .60)),
    ('front curb right', (5.4, -2.90, .25), (.76, .99)),
    ('near rail high bend', (4.45, -2.35, 1.25), (.80, .32)),
    ('fore cow muzzle', (1.30, -1.94, .76), (.82, .55)),
    ('fore cow rump', (-1.35, -1.94, .65), (.36, .67)),
]
bpy.context.view_layer.update()
cam = sc.camera
depsgraph = bpy.context.evaluated_depsgraph_get()
projection = cam.calc_matrix_camera(depsgraph, x=IMAGE_WIDTH, y=IMAGE_HEIGHT,
                                    scale_x=1, scale_y=1)
view = cam.matrix_world.inverted()
rows = []
for name, point, ref in anchors:
    clip = projection @ view @ Vector((point[0], point[1], point[2], 1))
    if clip.w <= 0:
        rows.append('{"name":"%s","reference":[%.4f,%.4f],'
                    '"projection":null,"status":"behind camera"}' %
                    (name, ref[0], ref[1]))
    else:
        u = .5*(clip.x/clip.w+1)
        v = .5*(1-clip.y/clip.w)
        rows.append('{"name":"%s","reference":[%.4f,%.4f],'
                    '"projection":[%.4f,%.4f],"residual":[%.4f,%.4f]}' %
                    (name, ref[0], ref[1], u, v, u-ref[0], v-ref[1]))
print('ANCHOR_DIAGNOSTICS [' + ','.join(rows) + ']')
