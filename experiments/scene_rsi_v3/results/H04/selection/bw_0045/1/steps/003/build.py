# Reference inventory and approximate normalized image anchors:
# - Foreground curb runs from (0,.59) to approximately (.64,1.0); brown
#   bedding alley lies below it. Concrete bed and damp marks occupy the right.
# - Nearest cow occupies approximately (.35,.36)-(.84,.85): a pale broad
#   flank, irregular dark patches, dirty rump at left, black neck and head
#   at right, folded legs and a tail. Several cows overlap to the left.
# - Galvanized open divider loops occupy (0,.16)-(1,.75), overlap the cows,
#   and have prominent upright supports; gaps remain visible between pipes.
# - Concrete rear wall and pale upper panels fill the background. Blue door
#   is approximately (.32,0)-(.44,.19), with blue columns and a partially
#   cropped worker at the right edge. Hidden legs and stall ends are uncertain.
# - Curb slopes strongly down to the right; the upper cross rails and wall
#   seams have a much shallower slope. Cow bodies extend diagonally rightward.
#
# Comparison with second render, estimated from the complete images:
# - Nearest reference cow spans about x=.35-.84 and y=.36-.85; rendered
#   cows form small rounded shapes around x=.05-.77 and y=.48-.72.
# - Reference foreground curb reaches the bottom near x=.64; rendered curb
#   crosses approximately y=.69-.85 and leaves a large empty foreground.
# - Reference door is near x=.32-.44, y=0-.19; rendered door is around
#   x=.40-.50, y=.26-.53. Reference wall/rail region is much higher.
# - Reference shows long cow sides and large dark/light patches; the render
#   looks toward their rear ends, with round spots and little visible head.
# - Reference divider pipes form prominent curved loops above and in front
#   of the cows; render dividers are thin and their visible gaps are shallow.
#
# Ranked corrections and predicted effects:
# 1. CAMERA_POS moves toward the positive-x end of the row and closer to the
#    cows. Their long axes should extend rightward, their silhouettes grow,
#    and the near curb should approach the bottom crop. The wall will shift
#    differently from the foreground, so the door position is independently
#    adjusted. A numerical trial below prints projections for both cameras.
# 2. CAMERA_TARGET aims lower, moving the rear wall and rail landmarks up;
#    the closer position and lower eye height change foreground perspective.
# 3. Cow body length, head position, larger noncircular patches and muddy
#    rump increase the broad high-contrast silhouette. Folded limbs, muzzle
#    and ears are retained as separate parts.
# 4. Longer bent divider loops and heavier posts improve their silhouette
#    and overlap. Surface brightness depends on lighting as well as color.
#
# Expanded primitive estimate: architecture 16, platform 11, rails 102,
# six cows about 138, employee 8, surface marks 32: roughly 307 meshes.
# No boolean operations, fillet boxes, or external assets.

import bpy
import random
from mathutils import Vector
from sceneact import *

random.seed(21)

# Camera and scene dimensions are independently adjustable.
OLD_POS = (6.3, -15.8, 4.15)
OLD_TARGET = (-0.4, 1.10, 1.25)
OLD_LENS = 52
CAMERA_POS = (10.2, -9.6, 3.65)
CAMERA_TARGET = (-0.35, 1.15, 0.90)
CAMERA_LENS = 42
BACK_Y = 5.2
BED_FRONT = -1.35
BED_BACK = 3.7
BED_TOP = .25
STALL_SPACING = 1.62

scene = Scene('Modern dairy free stall barn')
steel = (.56, .60, .60)
blue = (.025, .085, .17)
white = (.68, .66, .58)
black = (.025, .028, .025)
mud = (.24, .22, .16)

def put(parent, name, node):
    parent.include(name, node)
    return node

def ellipsoid(parent, name, center, scale, color):
    obj = ball(1, center=center, color=color)
    obj.resize(scale, pivot=center)
    put(parent, name, obj)
    return obj

def pipe(parent, name, a, b, radius=.04, color=steel):
    put(parent, name, rod(radius, start=a, end=b, color=color))

architecture = Asset('Barn architecture')
put(architecture, 'bedding alley floor',
    box((22, 18, .12), center=(0, 0, -.08), color=(.32,.29,.22)))
put(architecture, 'concrete lower wall',
    box((22,.20,2.50), center=(0,BACK_Y,1.25), color=(.40,.43,.43)))
put(architecture, 'pale upper panels',
    box((22,.18,2.50), center=(0,BACK_Y,3.75), color=(.75,.77,.76)))
for i,x in enumerate((-10,-7.3,-4.7,-1.9,1.35,4.8,8.0,10.5)):
    put(architecture, 'blue structural column %d'%i,
        box((.14,.23,5), center=(x,BACK_Y-.12,2.5), color=blue))
# Position of the door is adjusted separately from the camera.
DOOR_X = -4.2
put(architecture, 'blue door frame',
    box((1.75,.12,2.65), center=(DOOR_X,BACK_Y-.16,1.325), color=blue))
for i,dx in enumerate((-.42,.42)):
    put(architecture, 'door panel %d'%i,
        box((.80,.08,2.40), center=(DOOR_X+dx,BACK_Y-.24,1.25),
            color=(.018,.055,.12)))
put(architecture, 'door crossbar',
    box((1.62,.05,.055), center=(DOOR_X,BACK_Y-.29,1.05),
        color=(.055,.11,.19)))
put(architecture, 'wall horizontal seam',
    box((22,.05,.045), center=(0,BACK_Y-.13,2.5), color=(.31,.34,.34)))
scene.include('architecture', architecture)

platform = Asset('Raised concrete lying beds and walkway')
put(platform, 'bed slab',
    box((20,BED_BACK-BED_FRONT,BED_TOP),
        center=(0,(BED_FRONT+BED_BACK)/2,BED_TOP/2), color=(.49,.50,.48)))
put(platform, 'front curb',
    box((20,.14,.23), center=(0,BED_FRONT-.04,.11), color=(.30,.31,.29)))
put(platform, 'right concrete walkway',
    box((3.4,9,.12), center=(8.4,.1,.02), color=(.46,.47,.45)))
for i,x in enumerate((-8,-6,-4,-2,0,2,4,6,8)):
    put(platform, 'slab joint %d'%i,
        box((.022,1.6,.008), center=(x,-.52,.257), color=(.31,.32,.30)))
scene.include('lying platform', platform)

rails = Asset('Galvanized free stall dividers')
for i in range(11):
    x = -8.15 + i*STALL_SPACING
    pts = [(x,3.72,1.35), (x,2.65,1.35), (x,.35,1.35),
           (x,-.12,1.30), (x,-.38,1.17), (x,-.47,.98),
           (x,-.39,.82), (x,-.15,.76), (x,.62,.73)]
    for j in range(len(pts)-1):
        pipe(rails, 'divider %d loop %d'%(i,j),pts[j],pts[j+1],.046)
    pipe(rails,'divider %d near support'%i,
         (x,-.42,.24),(x,-.42,1.00),.048)
    pipe(rails,'divider %d far support'%i,
         (x,3.70,.24),(x,3.70,1.35),.040)
for i,y in enumerate((2.36,3.65)):
    pipe(rails,'continuous cross rail %d'%i,
         (-9.2,y,1.37),(9.2,y,1.37),.039)
scene.include('stall divider system', rails)

def cow(index, x, y, scale=1, variant=0, dark=False):
    animal = Asset('Holstein cow %d'%index)
    z = BED_TOP

    def E(name,c,s,col):
        p = (x+c[0]*scale,y+c[1]*scale,z+c[2]*scale)
        return ellipsoid(animal,name,p,tuple(v*scale for v in s),col)

    body = black if dark else white
    E('long torso',(0,0,.48),(.65,1.20,.46),body)
    E('rounded hindquarters',(0,-.79,.43),(.61,.55,.40),body)
    E('shoulder',(.01,.78,.51),(.54,.55,.41),body)
    E('neck',(.04,1.17,.57),(.38,.56,.33),black)
    E('head',(.04,1.62,.55),(.30,.38,.26),black)
    E('pale muzzle',(.05,1.94,.46),(.24,.19,.15),(.58,.57,.53))
    E('wet nose',(.05,2.09,.46),(.19,.075,.08),(.12,.12,.11))
    E('left ear',(-.35,1.57,.70),(.22,.14,.07),black)
    E('right ear',(.37,1.57,.70),(.22,.14,.07),black)
    E('left eye',(-.24,1.78,.63),(.03,.035,.03),(.008,.008,.008))
    E('right eye',(.26,1.78,.63),(.03,.035,.03),(.008,.008,.008))
    E('folded left foreleg',(-.43,.35,.17),(.20,.55,.14),body)
    E('folded right foreleg',(.43,.37,.17),(.20,.54,.14),body)
    E('folded hind leg',(.23,-.84,.17),(.36,.30,.14),(.53,.50,.43))
    E('udder',(.08,-.70,.17),(.28,.27,.13),(.48,.34,.31))
    E('muddy hindquarters',(-.06,-1.06,.40),(.46,.20,.28),mud)

    if dark:
        patches = [
            ((-.43,-.48,.65),(.22,.34,.15)),
            ((.38,.26,.71),(.19,.27,.13))]
    else:
        patches = [
            ((-.52,-.42,.56),(.18,.42,.24)),
            ((.51,-.18,.58),(.17,.40,.24)),
            ((-.30,.24,.79),(.30,.34,.14)),
            ((.35,.46,.73),(.23,.30,.15)),
            ((.10,-.73,.77),(.28,.25,.13)),
            ((-.51,.55,.53),(.15,.26,.19))]
    for j,(c,s) in enumerate(patches):
        if variant % 2:
            c = (-c[0],c[1],c[2])
        E('coat marking %d'%j,c,s,white if dark else black)

    pipe(animal,'tail upper',
         (x,y-1.13*scale,z+.35*scale),
         (x+.08*scale,y-1.43*scale,z+.12*scale),.034*scale,mud)
    pipe(animal,'tail end',
         (x+.08*scale,y-1.43*scale,z+.12*scale),
         (x+.20*scale,y-1.67*scale,z+.04*scale),.026*scale,mud)
    scene.include('cow %d'%index,animal)

cow(1,-5.65,.45,.92,1)
cow(2,-4.03,.33,.98,0)
cow(3,-2.41,.40,1.02,1,True)
cow(4,-.79,.30,1.05,0,True)
cow(5,.83,.30,1.08,1)
cow(6,2.45,.53,1.00,0)

surface = Asset('Bedding and damp surface marks')
for i in range(25):
    x = random.uniform(-9,9)
    y = random.uniform(-1.22,3.4)
    r = random.uniform(.04,.15)
    ellipsoid(surface,'bed fleck %d'%i,(x,y,.258),(r,r*.45,.006),
              (.35,.32,.24) if i%3 else (.25,.26,.23))
for i in range(7):
    x = random.uniform(4.5,8)
    y = random.uniform(-2.1,1.3)
    ellipsoid(surface,'damp patch %d'%i,(x,y,.09),
              (random.uniform(.12,.28),random.uniform(.09,.20),.006),
              (.26,.28,.27))
scene.include('bedding and damp patches',surface)

person = Asset('Farm employee')
px,py = 7.3,4.2
ellipsoid(person,'head',(px,py,1.67),(.13,.12,.16),(.37,.25,.20))
ellipsoid(person,'hair',(px,py,1.77),(.14,.12,.09),(.08,.07,.06))
put(person,'blue jacket',
    box((.42,.24,.55),center=(px,py,1.28),color=(.06,.15,.32)))
pipe(person,'left arm',(px-.18,py,1.45),(px-.29,py-.17,1.03),
     .085,(.06,.15,.32))
pipe(person,'right arm',(px+.18,py,1.44),(px+.30,py-.19,1.08),
     .085,(.06,.15,.32))
pipe(person,'left leg',(px-.10,py,1.03),(px-.11,py,.48),
     .09,(.08,.10,.13))
pipe(person,'right leg',(px+.10,py,1.03),(px+.18,py,.48),
     .09,(.08,.10,.13))
scene.include('employee',person)

realize(scene)

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
        if abs(c[0]-.56)<.02 and abs(c[1]-.60)<.02:
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
sc.world.node_tree.links.new(background.outputs['Background'],output.inputs['Surface'])
background.inputs['Color'].default_value = (.65,.70,.76,1)
background.inputs['Strength'].default_value = .46

sc.render.resolution_x = 512
sc.render.resolution_y = 285
sc.render.resolution_percentage = 100
set_view(OLD_POS,OLD_TARGET,lens=OLD_LENS,sensor=36)

# These are point projections, not measured visible contours. The reference
# estimates are separate and some point-to-image correspondences are uncertain.
landmarks = [
    ('door upper left',(DOOR_X-.875,BACK_Y-.24,2.65),(.32,.02)),
    ('door lower right',(DOOR_X+.875,BACK_Y-.24,0),(.44,.20)),
    ('foreground curb',(0,BED_FRONT,.23),(.50,.80)),
    ('rail near bend',(2.39,-.42,1.00),(.83,.60)),
    ('rear rail',(4.81,3.65,1.37),(.90,.25))
]

def projections():
    bpy.context.view_layer.update()
    camera = sc.camera
    dg = bpy.context.evaluated_depsgraph_get()
    matrix = camera.calc_matrix_camera(
        dg,x=sc.render.resolution_x,y=sc.render.resolution_y,
        scale_x=sc.render.pixel_aspect_x,scale_y=sc.render.pixel_aspect_y)
    result = []
    for name,p,ref in landmarks:
        clip = matrix @ camera.matrix_world.inverted() @ Vector((*p,1.0))
        result.append(None if clip.w <= 1e-8 else
                      (.5*(clip.x/clip.w+1),.5*(1-clip.y/clip.w)))
    return result

old = projections()
cam = sc.camera
cam.location = CAMERA_POS
cam.rotation_euler = (Vector(CAMERA_TARGET)-cam.location).to_track_quat('-Z','Y').to_euler()
cam.data.lens = CAMERA_LENS
chosen = projections()

# A small downward-aim trial verifies direction and is restored when it
# moves the chosen foreground landmark farther from its estimated reference.
saved_rotation = cam.rotation_euler.copy()
trial_target = Vector((CAMERA_TARGET[0],CAMERA_TARGET[1],CAMERA_TARGET[2]-.12))
cam.rotation_euler = (trial_target-cam.location).to_track_quat('-Z','Y').to_euler()
trial = projections()
cam.rotation_euler = saved_rotation
bpy.context.view_layer.update()

print('Landmark: reference / previous camera / chosen camera / downward aim trial')
for (name,p,ref),a,b,c in zip(landmarks,old,chosen,trial):
    print(name,ref,a,b,c)

area_emitter((0,-1,7.5),power=1500,size=8,
             target=(0,1,0),color=(.82,.90,1.0))
area_emitter((-5,2,5.5),power=800,size=6,
             target=(0,1,0),color=(.88,.93,1.0))
