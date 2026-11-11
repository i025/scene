# Reference inventory, normalized image coordinates (x right, y down):
# Concrete wall and white panels span the upper image; blue door approximately
# (0.31, 0.00)-(0.44, 0.20), worker approximately (0.94, 0.12)-(1.00, 0.43).
# Raised concrete beds, front curb, and straw-covered aisle occupy the lower image.
# The curb descends from about (0.00, 0.60) toward (0.66, 1.00).
# Foremost cow occupies approximately (0.35, 0.40)-(0.83, 0.94); its rump is
# in front of its black neck and head, and the rail overlaps the neck.
# Several partially hidden cows extend leftward and backward. Their hidden limbs
# and exact count are uncertain. Rounded steel divider loops overlap the cows.
#
# Comparison with the successful render:
# 1. The entire scene is too small: the wall ends at the top and sides, while the
#    reference wall fills the frame. The foreground cow rendered around
#    (0.29, 0.53)-(0.56, 0.75), much smaller than the reference cow.
# 2. The door rendered around (0.37, 0.23)-(0.47, 0.50), versus the reference
#    (0.31, 0.00)-(0.44, 0.20). Its bottom correspondence is uncertain because
#    rails obscure the reference door.
# 3. The front curb rendered across approximately (0.00, 0.65)-(1.00, 0.96).
#    The reference curb has a stronger diagonal and exits the lower edge earlier.
# 4. Rendered cows look like small spotted balls and occupy too little of the
#    image. The foreground animal needs a longer torso, broad irregular dark
#    patches, folded limbs, and a readable head.
# 5. The rail assembly has excessive long straight horizontal lines through the
#    animals. The reference shows distinct, larger rounded divider loops and gaps.
# The printed original projections agree approximately with the rendered door
# and curb, but the former muzzle anchor did not identify the visible muzzle.
# The worker is present and occluded; no duplicate is added.
#
# Revision: move the camera closer and lower and point it toward the foreground
# cow. This should enlarge foreground contours, push the curb down and out of
# frame, and move the door up and left. The camera is also turned slightly more
# along the row so that the curb slopes down toward the right. The foreground
# cow is locally enlarged and moved right, increasing its image width; the
# door is shortened at its base to reflect the visible upper wall opening.
# Rail loops are shortened locally so the visible rounded returns and gaps remain.
# Camera perturbations are evaluated below with fixed geometry before selecting
# the candidate. Diagnostics are geometric projections, not visibility tests.
#
# Expanded primitive estimate: architecture 20 boxes; 6 dividers x 2 loops x
# (8 rods + 7 bend balls) plus 6 posts and 2 cross rails = 188; 9 cows x about
# 20 primitives = 180; worker 7; bedding 25. Total approximately 420 meshes.

import math
import random
import bpy
from mathutils import Vector
from sceneact import *

random.seed(13)
IMAGE_WIDTH, IMAGE_HEIGHT = 512, 285

# Scene dimensions and camera are deliberately independent.
BED_TOP = .22
BACK_WALL_Y = 3.3
BED_LENGTH = 15.0
BED_DEPTH = 5.5
RAIL_HEIGHT = 1.25
STALL_YS = [-2.35, -1.35, -.35, .65, 1.65, 2.65]

CAMERA_POSITION = (3.0, -7.5, 3.0)
CAMERA_TARGET = (.0, -.30, .90)
CAMERA_LENS = 39

concrete = (.43, .44, .42)
bed_color = (.51, .52, .50)
wall_gray = (.39, .41, .41)
panel_white = (.77, .79, .78)
blue = (.025, .11, .27)
dark_blue = (.012, .045, .12)
steel = (.48, .51, .50)
black = (.018, .020, .018)
white = (.71, .70, .62)
muzzle = (.35, .29, .27)
straw = (.42, .35, .21)

scene = Scene('Dairy barn free stalls')

def add_box(parent, name, size, center, color):
    parent.include(name, box(size=size, center=center, color=color))

def add_ball(parent, name, center, radii, color):
    node = ball(1, center=center, color=color)
    node.resize(radii)
    parent.include(name, node)

def add_rod(parent, name, a, b, radius, color):
    parent.include(name, rod(radius=radius, start=a, end=b, color=color))

def path(parent, name, points, radius, color):
    for i in range(len(points)-1):
        add_rod(parent, name + ' segment %d' % i,
                points[i], points[i+1], radius, color)
    for i, p in enumerate(points[1:-1]):
        add_ball(parent, name + ' bend %d' % i, p,
                 (radius, radius, radius), color)

building = Asset('Barn architecture')
add_box(building, 'lower concrete wall', (22, .18, 1.48),
        (0, BACK_WALL_Y, .74), wall_gray)
add_box(building, 'upper white wall panels', (22, .16, 3.5),
        (0, BACK_WALL_Y, 3.23), panel_white)
add_box(building, 'raised bed slab', (BED_LENGTH, BED_DEPTH, BED_TOP),
        (0, -.05, BED_TOP/2), bed_color)
add_box(building, 'front bed curb', (BED_LENGTH, .16, .26),
        (0, -2.82, .12), concrete)
add_box(building, 'foreground aisle', (24, 12, .10),
        (0, -8.84, -.08), (.31, .29, .22))
add_box(building, 'rear aisle', (22, 1.0, .10),
        (0, 2.95, -.04), concrete)

# The lower part of the doorway is obscured in the reference.
add_box(building, 'blue door panel', (1.55, .08, 1.35),
        (-2.45, BACK_WALL_Y-.13, 1.28), dark_blue)
add_box(building, 'door left jamb', (.11, .11, 1.45),
        (-3.25, BACK_WALL_Y-.19, 1.28), blue)
add_box(building, 'door right jamb', (.11, .11, 1.45),
        (-1.65, BACK_WALL_Y-.19, 1.28), blue)
add_box(building, 'door header', (1.72, .11, .12),
        (-2.45, BACK_WALL_Y-.19, 2.00), blue)
add_box(building, 'door central seam', (.025, .035, 1.32),
        (-2.45, BACK_WALL_Y-.24, 1.28), blue)
for i, x in enumerate([-5.8, 2.9, 6.6]):
    add_box(building, 'blue structural post %d' % i, (.18, .20, 5),
            (x, BACK_WALL_Y-.16, 2.5), blue)
for i, x in enumerate([-5.0, -3.8, -1.0, .2, 1.4, 4.0, 5.2, 7.0]):
    add_box(building, 'upper panel seam %d' % i, (.018, .02, 3.4),
            (x, BACK_WALL_Y-.10, 3.2), (.57, .59, .58))
scene.include('architecture', building)

rails = Asset('Galvanized steel stall dividers')
for j, y in enumerate(STALL_YS):
    divider = Asset('stall divider %02d' % j)
    for k, base_x in enumerate([-5.8, -1.3, 3.2]):
        end = base_x + 3.9
        points = [
            (base_x, y, .25),
            (base_x, y, 1.03),
            (base_x+.07, y, 1.18),
            (base_x+.23, y, RAIL_HEIGHT),
            (end-.20, y, RAIL_HEIGHT),
            (end-.05, y, 1.17),
            (end, y, .96),
            (end-.06, y, .73),
            (end-.25, y, .70),
        ]
        path(divider, 'rounded loop %d' % k, points, .036, steel)
        add_rod(divider, 'lower return %d' % k,
                (end-.25, y, .70), (base_x+.45, y, .85), .036, steel)
    add_rod(divider, 'upright support', (3.2, y, .22),
            (3.2, y, 1.25), .045, steel)
    rails.include('divider %02d' % j, divider)
for i, z in enumerate([1.25, 1.12]):
    add_rod(rails, 'rear cross rail %d' % i, (-7.3, 2.75-i*.24, z),
            (7.3, 2.75-i*.24, z), .035, steel)
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

    ell('broad torso', -.12, 0, .52, 1.08, .49, .46, white)
    ell('hindquarter', -.84, -.01, .42, .48, .44, .36, white)
    ell('chest', .61, 0, .47, .45, .43, .38, white)
    ell('black neck', 1.00, 0, .64, .43, .32, .30, black)
    ell('head', 1.31, -.02, .65, .34, .25, .25, black)
    ell('white forehead blaze', 1.46, -.20, .67, .13, .065, .15, white)
    ell('moist muzzle', 1.58, -.01, .53, .20, .21, .13, muzzle)
    ell('near ear', 1.12, -.28, .79, .19, .10, .07, black)
    ell('far ear', 1.12, .26, .79, .19, .10, .07, black)
    ell('near eye', 1.42, -.24, .72, .03, .024, .03, (.005,.005,.005))
    ell('folded hind leg', -.58, -.30, .21, .43, .18, .15, white)
    ell('rear hoof', -.90, -.32, .16, .16, .14, .09, (.16,.14,.12))
    ell('folded foreleg', .53, -.29, .21, .39, .16, .13, white)
    ell('front hoof', .85, -.30, .16, .15, .13, .08, (.16,.14,.12))
    ell('udder', -.37, -.28, .20, .31, .18, .13, (.58,.41,.36))

    patterns = [
        [(-.77,-.40,.53,.32,.065,.25),(-.40,-.45,.65,.30,.055,.23),
         (.08,-.46,.62,.22,.055,.18),(.43,-.39,.52,.20,.07,.23),
         (-.18,-.25,.90,.38,.19,.07)],
        [(-.70,-.40,.54,.39,.06,.27),(-.28,-.45,.58,.30,.055,.25),
         (.26,-.43,.65,.32,.06,.22),(.63,-.34,.51,.19,.07,.20),
         (-.32,-.21,.91,.40,.19,.07)],
        [(-.70,-.40,.53,.30,.06,.26),(-.32,-.44,.67,.34,.06,.22),
         (.19,-.45,.56,.25,.06,.23),(.57,-.34,.66,.20,.07,.17),
         (.06,-.20,.92,.35,.18,.07)]
    ]
    for i, patch in enumerate(patterns[variation % len(patterns)]):
        ell('hide patch %d' % i, *patch, black)
    limb('tail', (-1.00,.05,.43), (-1.24,-.06,.06), .035, white)
    ell('tail tuft', -1.25, -.06, .05, .10, .065, .07, black)
    return cow

cows = Asset('Reclining Holstein cows')
for i, spec in enumerate([
    (.20, -1.95, 1.28, 0),
    (-2.05, -1.00, 1.10, 1),
    (-4.00, -.08, .98, 2),
    (-.95, .05, 1.00, 2),
    (-3.00, 1.04, .92, 0),
    (.35, 1.12, .90, 1),
    (-4.60, 2.05, .82, 1),
    (-1.50, 2.05, .84, 2),
    (1.65, 2.05, .82, 0)
]):
    cows.include('cow %02d' % i, make_cow('Holstein %02d' % i, *spec))
scene.include('cows', cows)

person = Asset('Barn employee')
px, py, pz = 4.25, 2.95, .05
add_ball(person, 'head', (px,py,pz+1.60), (.115,.105,.14), (.43,.29,.23))
add_ball(person, 'hair', (px-.015,py+.015,pz+1.69),
         (.12,.11,.075), (.06,.055,.05))
add_box(person, 'blue jacket', (.40,.24,.53), (px,py,pz+1.22), (.055,.16,.38))
add_rod(person, 'left sleeve', (px-.18,py,1.40), (px-.30,py-.05,1.08),
        .075, (.055,.16,.38))
add_rod(person, 'right sleeve', (px+.18,py,1.40), (px+.29,py-.08,1.08),
        .075, (.055,.16,.38))
add_rod(person, 'left trouser leg', (px-.10,py,.99), (px-.11,py,.48),
        .095, (.07,.09,.13))
add_rod(person, 'right trouser leg', (px+.10,py,.99), (px+.13,py,.48),
        .095, (.07,.09,.13))
scene.include('employee', person)

bedding = Asset('Scattered straw')
for i in range(25):
    x = random.uniform(-6, 6)
    y = random.uniform(-5, 2.4)
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
background.inputs['Strength'].default_value = .55

set_view(CAMERA_POSITION, CAMERA_TARGET, lens=CAMERA_LENS, sensor=36)
area_emitter((0, -1, 7), power=1300, size=8, target=(0,0,0),
             color=(.83,.90,1.0))
area_emitter((-5, -2, 4.5), power=500, size=5, target=(-1,0,.4),
             color=(.91,.95,1.0))

for mat in bpy.data.materials:
    if not mat.use_nodes:
        continue
    bsdf = mat.node_tree.nodes.get('Principled BSDF')
    if bsdf is None:
        continue
    rgb = tuple(bsdf.inputs['Base Color'].default_value[:3])
    if sum(abs(rgb[i]-steel[i]) for i in range(3)) < .08:
        bsdf.inputs['Metallic'].default_value = .78
        bsdf.inputs['Roughness'].default_value = .28
    elif sum(abs(rgb[i]-muzzle[i]) for i in range(3)) < .06:
        bsdf.inputs['Roughness'].default_value = .23
    else:
        bsdf.inputs['Roughness'].default_value = .82

# Four to eight identifiable points, including background and foreground.
# Door lower edge is uncertain due to occlusion, and the cow muzzle anchor is
# the front tip of the muzzle rather than its center.
anchors = [
    ('door top left', (-3.25, BACK_WALL_Y-.19, 2.00), (.31,.03)),
    ('door top right', (-1.65, BACK_WALL_Y-.19, 2.00), (.43,.03)),
    ('door lower right', (-1.65, BACK_WALL_Y-.19,.56), (.43,.20)),
    ('front curb left', (-5.4,-2.90,.25), (.00,.60)),
    ('front curb right', (5.4,-2.90,.25), (.76,.99)),
    ('near rail bend', (2.40,-2.35,1.25), (.80,.32)),
    ('fore cow muzzle', (2.48,-1.96,.90), (.82,.55)),
    ('fore cow rump', (-1.49,-1.95,.76), (.36,.67)),
]

cam = sc.camera
depsgraph = bpy.context.evaluated_depsgraph_get()

def projections():
    bpy.context.view_layer.update()
    projection = cam.calc_matrix_camera(depsgraph, x=IMAGE_WIDTH, y=IMAGE_HEIGHT,
                                        scale_x=1, scale_y=1)
    view = cam.matrix_world.inverted()
    result = []
    for name, point, ref in anchors:
        clip = projection @ view @ Vector((point[0],point[1],point[2],1))
        if clip.w <= 0:
            result.append((name, ref, None))
        else:
            result.append((name, ref, (.5*(clip.x/clip.w+1),
                                       .5*(1-clip.y/clip.w))))
    return result

# Test small target shifts with fixed geometry. Restore the selected pose after
# comparing aggregate residuals; uncertain features are not forced into place.
base_location = cam.location.copy()
base_rotation = cam.rotation_euler.copy()
base_lens = cam.data.lens

def set_candidate(position, target, lens):
    cam.location = Vector(position)
    cam.rotation_euler = (Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler()
    cam.data.lens = lens
    bpy.context.view_layer.update()

candidates = [
    (CAMERA_POSITION, CAMERA_TARGET, CAMERA_LENS),
    (CAMERA_POSITION, (CAMERA_TARGET[0]-.3, CAMERA_TARGET[1], CAMERA_TARGET[2]), CAMERA_LENS),
    (CAMERA_POSITION, (CAMERA_TARGET[0], CAMERA_TARGET[1], CAMERA_TARGET[2]+.25), CAMERA_LENS),
    (CAMERA_POSITION, CAMERA_TARGET, CAMERA_LENS-2),
]
scores = []
for position, target, lens in candidates:
    set_candidate(position, target, lens)
    projected = projections()
    score = 0.0
    for name, ref, uv in projected:
        if uv is not None:
            weight = .35 if name in ('door lower right','front curb right','near rail bend') else 1.0
            score += weight*((uv[0]-ref[0])**2+(uv[1]-ref[1])**2)
    scores.append(score)

best = min(range(len(scores)), key=lambda i: scores[i])
set_candidate(*candidates[best])
rows = []
for name, ref, uv in projections():
    if uv is None:
        rows.append('{"name":"%s","reference":[%.4f,%.4f],'
                    '"projection":null,"status":"behind camera"}' %
                    (name,ref[0],ref[1]))
    else:
        rows.append('{"name":"%s","reference":[%.4f,%.4f],'
                    '"projection":[%.4f,%.4f],"residual":[%.4f,%.4f]}' %
                    (name,ref[0],ref[1],uv[0],uv[1],
                     uv[0]-ref[0],uv[1]-ref[1]))
print('CAMERA_CANDIDATE_SCORES ' + str([round(s,5) for s in scores]) +
      ' chosen=' + str(best))
print('ANCHOR_DIAGNOSTICS [' + ','.join(rows) + ']')
