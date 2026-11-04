from sceneact import *
import bpy
import math

# Visual estimates, normalized reference anchors:
# window right jamb (.29,.39), cabinet bottom corner (.52,.53),
# roll center (.72,.25), towel bottom (.35,.82),
# jug bottom (.68,.88), pitcher right edge (.95,.76).
# Observed step 1: cabinet bottom is near its reference height, but window
# occupies too little width; roll and jug are cropped at right, pitcher absent.
# Counter and towel bottom also project too low. Blender remains visible.
# Hypothesis: overly narrow camera framing explains several margins together.
# Bounded revision: widen lens 80 -> 62, preserving camera pose and target.
# Local hypothesis: roll/jug/pitcher are also spaced too far right of cabinet.
# Move those complete Assets left; preserve other geometry and finishes.
# Inventory and dependencies: countertop supports jug, pitcher, blender, can,
# cup and sponge; wall/cabinet supports ring and paper holder; ring supports towel.
# Arbitrary scale; camera orientation and inferred hidden depths remain uncertain.

# CAMERA
CAMERA = (-1.58, -3.45, 2.13)
TARGET = (-.10, .40, 1.73)
LENS = 62

# ARCHITECTURE
COUNTER_Z = .88
CAB_BOTTOM = 1.67

# OBJECT DIMENSIONS / POSES — independent of camera parameters
ROLL_CENTER = (.27, .205, 2.29)
ROLL_RADIUS = .185
ROLL_HEIGHT = .77
JUG_CENTER = (.13, -.17, COUNTER_Z)
PITCHER_CENTER = (.53, .10, COUNTER_Z)

# MATERIALS
ivory = (.78, .73, .60)
cabinet_color = (.82, .77, .65)
paper = (.94, .91, .81)
cloth = (.83, .80, .70)
metal = (.48, .48, .40)
blue = (.055, .095, .16)
scene = Scene('Kitchen corner')


def positive(v):
    assert math.isfinite(v) and v > 0
    return v


def point(p):
    assert len(p) == 3 and all(math.isfinite(v) for v in p)
    return tuple(p)


def attach(parent, key, node):
    assert key not in parent.members, key
    return parent.include(key, node)


def cube(parent, key, size, center, color, radius=None):
    size = tuple(positive(v) for v in size)
    center = point(center)
    if radius is None:
        node = box(size, center=center, color=color)
    else:
        positive(radius)
        assert radius <= min(size) / 2, (key, size, radius)
        node = fillet_box(size, radius, center=center, color=color)
    return attach(parent, key, node)


def tube(parent, key, points, radius, color):
    positive(radius)
    points = [point(p) for p in points]
    assert len(points) >= 2
    assert all(sum((a[k]-b[k])**2 for k in range(3)) > 1e-16
               for a, b in zip(points, points[1:])), key
    return attach(parent, key,
                  sweep_tube(points=points, radius=radius, color=color))


def cylinder(parent, key, radius, height, center, color):
    positive(radius)
    positive(height)
    return attach(parent, key, rod(radius, length=height,
                                  center=point(center), color=color))


def segment(parent, key, radius, start, end, color):
    positive(radius)
    start, end = point(start), point(end)
    assert sum((start[k]-end[k])**2 for k in range(3)) > 1e-16
    return attach(parent, key, rod(radius, start=start, end=end, color=color))


def sphere(parent, key, radius, center, color):
    positive(radius)
    return attach(parent, key, ball(radius, center=point(center), color=color))


architecture = Asset('Architecture')
cube(architecture, 'back_wall', (4,.10,3.8), (0,.85,1.65), ivory)
cube(architecture, 'counter', (3.1,1.34,.075),
     (-.25,.10,COUNTER_Z-.0375), (.30,.28,.22))
cube(architecture, 'backsplash', (3.1,.055,.16),
     (-.25,.745,.94), (.34,.31,.24))
attach(scene, 'architecture', architecture)

window = Asset('Window and venetian blinds')
cube(window, 'glass', (1.03,.035,2.35), (-1.10,.765,1.97), (.62,.76,.78))
for i, x in enumerate((-1.66,-.55)):
    cube(window, f'jamb_{i}', (.065,.12,2.62),
         (x,.68,1.98), (.87,.85,.75))
cube(window, 'sill', (1.22,.22,.065), (-1.105,.65,.91), (.89,.87,.77))
cube(window, 'center_mullion', (.035,.065,2.35),
     (-1.20,.70,2.02), (.87,.87,.79))
for i in range(34):
    slat = cube(window, f'blind_slat_{i:02d}', (1.08,.095,.018),
                (-1.105,.58,1.00+i*.068), (.81,.82,.75))
    slat.turn('x', -12)
for i, x in enumerate((-1.43,-.77)):
    cube(window, f'ladder_{i}', (.013,.011,2.29),
         (x,.515,2.12), (.78,.77,.67))
tube(window, 'pull_cord', [(-.65,.49,2.65),(-.65,.49,1.93)],
     .004, (.73,.69,.55))
cylinder(window, 'cord_weight', .014,.065,(-.65,.49,1.91),(.78,.72,.57))
attach(scene, 'window', window)

cabinet = Asset('Upper cabinet')
cube(cabinet, 'case', (1.02,.48,1.65),
     (.34,.55,CAB_BOTTOM+.825), cabinet_color)
cube(cabinet, 'door_field', (.82,.035,1.50),
     (.40,.284,2.47), (.77,.72,.60))
for key, x in [('left',-.075),('right',.875)]:
    cube(cabinet, key+'_stile', (.075,.07,1.65),
         (x,.25,2.495), cabinet_color)
for key, z in [('lower',1.71),('upper',3.28)]:
    cube(cabinet, key+'_rail', (.94,.07,.075),
         (.40,.25,z), cabinet_color)
for i, x in enumerate((.005,.795)):
    cube(cabinet, f'inner_vertical_{i}', (.023,.024,1.43),
         (x,.235,2.49), (.84,.79,.67))
for i, z in enumerate((1.785,3.19)):
    cube(cabinet, f'inner_horizontal_{i}', (.80,.024,.023),
         (.40,.235,z), (.84,.79,.67))
sphere(cabinet, 'door_knob', .031, (.84,.195,1.96), (.43,.37,.23))
attach(scene, 'cabinet', cabinet)

holder = Asset('Paper towel holder')
x,y,z = ROLL_CENTER
cube(holder, 'wall_bracket', (.12,.045,.10),
     (x,.235,1.88), (.34,.33,.27), .012)
segment(holder, 'bottom_arm', .025, (x,.24,1.89), (x,.095,1.89), metal)
cylinder(holder, 'spindle', .018,1.00,(x,y,2.30),metal)
cylinder(holder, 'paper_roll', ROLL_RADIUS,ROLL_HEIGHT,ROLL_CENTER,paper)
cylinder(holder, 'top_core', .035,.007,
         (x,y,z+ROLL_HEIGHT/2+.004), (.49,.43,.32))
sphere(holder, 'finial', .037, (x,y,2.77), (.43,.40,.29))
cube(holder, 'loose_sheet', (.32,.012,.67),
     (x,y-.179,z-.035), paper,.004)
attach(scene, 'paper_holder', holder)

ring = Asset('Towel ring and mounting')
segment(ring, 'mount_disk', .063,
        (-.189,.43,2.02),(-.245,.43,2.02),metal)
segment(ring, 'mount_neck', .023,
        (-.245,.43,2.02),(-.30,.34,2.02),metal)
ring_points = []
for i in range(65):
    a = 2*math.pi*i/64
    ring_points.append((-.30,.31+.155*math.cos(a),1.855+.20*math.sin(a)))
tube(ring, 'metal_ring', ring_points,.009,metal)
attach(scene, 'towel_ring', ring)

towel = Asset('Hanging cream towel')
for i in range(24):
    u = i/23
    yy = .12+u*.32
    bottom = 1.055+.035*math.sin(u*9)+.025*math.cos(u*15)
    xx = -.335-.020*math.cos(u*math.pi*8)
    tube(towel, f'front_fold_{i:02d}', [
        (xx,yy,1.675),(xx-.022,yy-.012,1.56),
        (xx-.035,yy-.022,1.36),(xx-.055,yy-.018,bottom)
    ], .015,cloth)
for i in range(15):
    yy = .16+i*.015
    tube(towel, f'rear_fold_{i:02d}', [
        (-.29,yy,1.66),(-.265,yy+.02,1.45),(-.24,yy+.035,1.21)
    ], .013,(.77,.74,.64))
attach(scene, 'towel', towel)

sink = Asset('Sink and faucet')
cube(sink, 'metal_rim', (.91,.64,.028),
     (-1.02,-.27,.889),(.38,.40,.36),.012)
cube(sink, 'dark_basin', (.79,.51,.035),
     (-1.02,-.29,.908),(.045,.057,.05),.012)
cube(sink, 'inner_bottom', (.64,.38,.025),
     (-1.02,-.29,.914),(.075,.09,.08),.01)
cylinder(sink, 'faucet_base', .060,.045,(-.89,.025,.914),metal)
tube(sink, 'faucet', [
    (-.89,.025,.93),(-.89,.025,1.10),(-.89,.025,1.30),
    (-.90,-.005,1.34),(-.93,-.075,1.34),(-.96,-.12,1.29)
], .016,metal)
for i, xx in enumerate((-1.04,-.75)):
    cylinder(sink, f'valve_{i}', .035,.035,(xx,.025,.918),metal)
    segment(sink, f'handle_{i}', .012,
            (xx,.025,.94),(xx-.035,-.025,.98),metal)
attach(scene, 'sink', sink)

jug = Asset('Translucent water jug')
jx,jy,jz = JUG_CENTER
cube(jug, 'body', (.32,.255,.30),
     (jx,jy,jz+.16),(.72,.75,.67),.065)
for i in range(7):
    t = i/6
    width = .30*(1-t)+.105*t
    depth = .245*(1-t)+.12*t
    cube(jug, f'shoulder_{i}', (width,depth,.043),
         (jx+.015*t,jy,jz+.305+.018*i),(.72,.75,.67),.019)
cylinder(jug, 'neck', .047,.055,(jx+.015,jy,jz+.447),(.79,.80,.72))
cylinder(jug, 'cap', .045,.027,(jx+.015,jy,jz+.483),(.86,.85,.73))
tube(jug, 'molded_handle', [
    (jx-.09,jy+.015,jz+.37),(jx-.145,jy+.015,jz+.32),
    (jx-.15,jy+.015,jz+.24),(jx-.10,jy+.015,jz+.22)
], .018,(.67,.70,.63))
attach(scene, 'water_jug', jug)

pitcher = Asset('Blue water filter pitcher')
px,py,pz = PITCHER_CENTER
cube(pitcher, 'vessel', (.28,.27,.36),
     (px,py,pz+.205),blue,.065)
cube(pitcher, 'upper_reservoir', (.30,.275,.16),
     (px-.015,py,pz+.345),(.11,.16,.21),.035)
lid = cube(pitcher, 'sloped_lid', (.33,.29,.033),
           (px-.015,py-.005,pz+.444),(.37,.38,.34),.012)
lid.turn('y', -9)
tube(pitcher, 'clear_handle', [
    (px+.13,py,pz+.39),(px+.235,py,pz+.35),(px+.25,py,pz+.23),
    (px+.21,py,pz+.10),(px+.13,py,pz+.09)
], .026,(.39,.43,.42))
cube(pitcher, 'base', (.27,.25,.026),
     (px,py,pz+.023),(.10,.13,.15),.012)
attach(scene, 'filter_pitcher', pitcher)

blender = Asset('Small blender')
bx,by = -.015,.33
cylinder(blender, 'motor', .095,.22,
         (bx,by,COUNTER_Z+.11),(.025,.03,.027))
cylinder(blender, 'collar', .085,.035,
         (bx,by,COUNTER_Z+.235),(.065,.065,.052))
cup = cylinder(blender, 'clear_cup', .060,.30,
               (bx-.025,by,COUNTER_Z+.39),(.42,.46,.41))
cup.turn('y', -10)
cylinder(blender, 'cup_lip', .063,.018,
         (bx-.052,by,COUNTER_Z+.54),(.56,.58,.51))
attach(scene, 'blender', blender)

can = Asset('Can beside towel')
cylinder(can, 'can_body', .048,.235,
         (-.27,.25,COUNTER_Z+.12),(.33,.38,.20))
cylinder(can, 'top_rim', .049,.012,
         (-.27,.25,COUNTER_Z+.242),(.57,.57,.45))
cylinder(can, 'bottom_rim', .049,.012,
         (-.27,.25,COUNTER_Z+.007),(.57,.57,.45))
cube(can, 'label_patch', (.043,.005,.115),
     (-.27,.201,COUNTER_Z+.12),(.70,.66,.43))
attach(scene, 'can', can)

small_cup = Asset('Small counter cup')
cylinder(small_cup, 'body', .052,.033,
         (-.59,-.015,COUNTER_Z+.018),(.055,.054,.04))
cylinder(small_cup, 'interior', .041,.004,
         (-.59,-.015,COUNTER_Z+.037),(.17,.16,.10))
attach(scene, 'small_cup', small_cup)

sponge = Asset('Sponge')
cube(sponge, 'body', (.16,.10,.033),
     (-1.30,-.15,COUNTER_Z+.025),(.67,.61,.36),.009)
attach(scene, 'sponge', sponge)

# Audit: helpers enforce positive sizes, legal fillets, distinct consecutive
# tube points and unique child keys. Composite relocation uses shared poses.
realize(scene)


def meshes_under(label):
    parent = bpy.data.objects.get(label)
    assert parent is not None, label
    result = []
    def walk(obj):
        if obj.type == 'MESH':
            result.append(obj)
        for child in obj.children:
            walk(child)
    walk(parent)
    assert result, label
    return result


def isolated_materials(obj):
    result = []
    for slot in obj.material_slots:
        if slot.material is not None:
            mat = slot.material.copy()
            slot.material = mat
            mat.use_nodes = True
            result.append(mat)
    return result


for obj in meshes_under('architecture'):
    if obj.dimensions.z < .20:
        for mat in isolated_materials(obj):
            nodes, links = mat.node_tree.nodes, mat.node_tree.links
            bs = nodes.get('Principled BSDF')
            assert bs is not None
            tex = nodes.new('ShaderNodeTexNoise')
            tex.inputs['Scale'].default_value = 155
            tex.inputs['Detail'].default_value = 3
            ramp = nodes.new('ShaderNodeValToRGB')
            ramp.color_ramp.elements[0].position = .25
            ramp.color_ramp.elements[0].color = (.065,.060,.044,1)
            ramp.color_ramp.elements[1].position = .75
            ramp.color_ramp.elements[1].color = (.49,.44,.33,1)
            links.new(tex.outputs['Fac'],ramp.inputs['Fac'])
            links.new(ramp.outputs['Color'],bs.inputs['Base Color'])
            bs.inputs['Roughness'].default_value = .68

paper_meshes = meshes_under('paper_roll') + meshes_under('loose_sheet')
for obj in paper_meshes + meshes_under('towel'):
    for mat in isolated_materials(obj):
        nodes, links = mat.node_tree.nodes, mat.node_tree.links
        bs = nodes.get('Principled BSDF')
        assert bs is not None
        bs.inputs['Roughness'].default_value = .86
        noise = nodes.new('ShaderNodeTexNoise')
        noise.inputs['Scale'].default_value = 180
        bump = nodes.new('ShaderNodeBump')
        bump.inputs['Strength'].default_value = .15
        bump.inputs['Distance'].default_value = .006
        links.new(noise.outputs['Fac'],bump.inputs['Height'])
        links.new(bump.outputs['Normal'],bs.inputs['Normal'])

for label in ('sink','towel_ring'):
    for obj in meshes_under(label):
        for mat in isolated_materials(obj):
            bs = mat.node_tree.nodes.get('Principled BSDF')
            assert bs is not None
            bs.inputs['Metallic'].default_value = .75
            bs.inputs['Roughness'].default_value = .27

# LIGHTING — retained from step 1 to isolate the composition revision.
set_view(CAMERA,TARGET,lens=LENS)
world = bpy.context.scene.world
if world is None:
    world = bpy.data.worlds.new('Warm room world')
    bpy.context.scene.world = world
world.use_nodes = True
background = world.node_tree.nodes.get('Background')
if background is None:
    background = world.node_tree.nodes.new('ShaderNodeBackground')
    output = world.node_tree.nodes.get('World Output')
    if output is None:
        output = world.node_tree.nodes.new('ShaderNodeOutputWorld')
    world.node_tree.links.new(background.outputs['Background'],
                              output.inputs['Surface'])
background.inputs['Color'].default_value = (.68,.70,.68,1)
background.inputs['Strength'].default_value = .35

area_emitter((-2.0,-.1,2.7),power=430,size=2.0,
             target=(.1,.4,1.5),color=(.82,.91,1.0))
area_emitter((-.2,-2.5,3.1),power=150,size=2.5,
             target=(.2,.4,1.7),color=(1.0,.82,.59))
bpy.context.scene.render.resolution_x = 384
bpy.context.scene.render.resolution_y = 512
bpy.context.scene.render.resolution_percentage = 100
bpy.context.scene.view_settings.view_transform = 'AgX'
