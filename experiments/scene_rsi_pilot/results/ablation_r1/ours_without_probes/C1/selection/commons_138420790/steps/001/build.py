from sceneact import *
import bpy
import math

# Visual estimates, normalized image anchors:
# 1. Foreground timber occupies x=.17-.30 and crosses both vertical boundaries.
# 2. Hood corners near (.42,.09), (.56,.045), (.73,.15); bottom near (.56,.43).
# 3. Island top corners near (.33,.59), (.66,.55), (.90,.57), (.62,.63).
# 4. Island floor contacts near (.33,.77), (.62,.85), (.90,.72).
# 5. Illuminated rear recess spans x=.30-.59 and y=.49-.56.
# 6. Oven column spans x=.67-.79 and y=.43-.58.
# Scale is arbitrary; camera distance and recess depth remain visual estimates.
# Inventory: tile floor, exposed ceiling beams, two timber columns, rear cabinets,
# lit backsplash, oven tower, island drawers, sink, faucet, hob, hood, red kettle.
# Supports: cabinetry and timber meet the floor; fittings meet their countertops;
# the extractor hangs from the ceiling. Each semantic composite owns its parts.
# This is a source audit only; no rendered image or edit result has been inspected.

# CAMERA PARAMETERS: independent of object dimensions.
CAMERA = (-5.4, -7.7, 3.25)
TARGET = (0.0, .45, 1.91)
LENS = 35

# ARCHITECTURE PARAMETERS
CEILING_Z = 3.85
BACK_Y = 2.18

# OBJECT DIMENSIONS AND POSES
ISLAND_X = .38
ISLAND_Y = -.25
ISLAND_W = 2.35
ISLAND_D = 1.18
COUNTER_Z = 1.02
HOOD_CENTER = (.16, -.05, 2.75)
HOOD_SIZE = (1.20, .94, 1.58)

# MATERIAL PARAMETERS
STONE = (.66, .67, .64)
COUNTER = (.79, .80, .75)
CHARCOAL = (.045, .052, .050)
BLACK = (.018, .023, .022)
CEILING_COLOR = (.045, .055, .053)
WOOD = (.43, .285, .16)
TILE = (.57, .575, .55)
STEEL = (.36, .38, .37)

# LIGHTING PARAMETERS
AMBIENT_STRENGTH = .29
EXPOSURE = .35

scene = Scene('Kitchen showroom')

# Validated construction helpers. No fillet_box is used in this program.
def finite_vector(values):
    return all(math.isfinite(float(v)) for v in values)

def cube(parent, key, size, center, color):
    assert finite_vector(size) and all(v > 0 for v in size)
    assert finite_vector(center)
    assert key not in parent.members, "Duplicate include key: " + key
    return parent.include(
        key, box(size=size, center=center, color=color)
    )

def add_rod(parent, key, radius, start, end, color):
    assert math.isfinite(radius) and radius > 0
    assert finite_vector(start) and finite_vector(end)
    assert sum((a - b) ** 2 for a, b in zip(start, end)) > 1e-16
    assert key not in parent.members
    return parent.include(
        key, rod(radius=radius, start=start, end=end, color=color)
    )

def add_tube(parent, key, points, radius, color):
    assert math.isfinite(radius) and radius > 0
    assert len(points) >= 2
    assert all(finite_vector(point) for point in points)
    assert all(
        sum((a - b) ** 2 for a, b in zip(p, q)) > 1e-16
        for p, q in zip(points[:-1], points[1:])
    )
    assert key not in parent.members
    return parent.include(
        key, sweep_tube(points=points, radius=radius, color=color)
    )

# Architectural shell.
architecture = Asset('Architecture')
cube(architecture, 'floor foundation', (14, 15, .12),
     (0, 0, -.075), TILE)
cube(architecture, 'rear wall', (9, .15, 3.9),
     (0, BACK_Y + .35, 1.95), (.36, .38, .36))
cube(architecture, 'left wall', (.16, 8, 3.9),
     (-3.6, 1.7, 1.95), (.43, .44, .40))
cube(architecture, 'ceiling', (13, 12, .13),
     (0, 1, CEILING_Z), CEILING_COLOR)

# Thin grout strips sit directly on the foundation surface.
for i in range(-7, 8):
    cube(architecture, 'floor grout x %d' % i, (.008, 14, .002),
         (i * .91, 0, -.014), (.39, .40, .38))
for i in range(-7, 9):
    cube(architecture, 'floor grout y %d' % i, (14, .008, .002),
         (0, i * .91, -.014), (.39, .40, .38))

for i, x in enumerate([-3.15, -.9, 1.55, 3.8]):
    cube(architecture, 'deep ceiling beam %d' % i, (.24, 11, .31),
         (x, .5, 3.65), (.038, .047, .046))
for i in range(13):
    cube(architecture, 'ceiling rib %d' % i, (11, .045, .085),
         (0, -3 + i * .51, 3.76), (.026, .033, .032))
scene.include('architectural shell', architecture)

# Timber supports retain their grain strips and knots as named children.
for label, px, py in [
    ('foreground', -1.68, -1.39),
    ('far right', 2.66, 1.51),
]:
    post = Asset(label + ' timber support')
    cube(post, 'solid timber', (.34, .34, 4.5),
         (px, py, 2.05), WOOD)
    for j in range(13):
        xx = px - .151 + j * .024
        color = (
            .33 + .045 * (j % 3),
            .215 + .027 * (j % 3),
            .12 + .018 * (j % 3),
        )
        cube(post, 'front grain %d' % j, (.005, .002, 4.45),
             (xx, py - .171, 2.05), color)
    for j, z in enumerate([.42, 1.62, 2.98]):
        add_rod(
            post, 'small knot %d' % j, .013,
            (px + .055, py - .1745, z),
            (px + .055, py - .1715, z),
            (.24, .15, .08)
        )
    scene.include(label + ' timber column', post)

# Rear cabinetry and illuminated working recess.
rear = Asset('Rear kitchen cabinetry')
cube(rear, 'left tall cabinet', (.91, .68, 2.48),
     (-2.07, 1.85, 1.24), CHARCOAL)
cube(rear, 'left cabinet upper door', (.875, .027, 1.35),
     (-2.07, 1.495, 1.78), (.065, .071, .067))
cube(rear, 'left cabinet lower door', (.875, .027, 1.04),
     (-2.07, 1.495, .565), (.06, .066, .062))
cube(rear, 'base run', (3.45, .66, .88),
     (-.20, 1.86, .44), BLACK)
cube(rear, 'rear worktop', (3.52, .72, .055),
     (-.20, 1.83, .91), (.13, .14, .13))
for i in range(5):
    cube(rear, 'base front %d' % i, (.675, .025, .77),
         (-1.56 + i * .69, 1.515, .46), CHARCOAL)

cube(rear, 'recess backsplash', (2.45, .035, .59),
     (-.43, 2.115, 1.25), (.24, .21, .19))
cube(rear, 'recess upper shadow', (2.52, .56, .13),
     (-.43, 1.88, 1.63), (.025, .029, .027))
cube(rear, 'upper cabinet bank', (2.48, .53, .61),
     (-.43, 1.91, 1.99), (.041, .049, .046))
for i in range(4):
    cube(rear, 'upper door seam %d' % i, (.008, .012, .60),
         (-1.34 + i * .61, 1.637, 1.99), (.014, .018, .016))
cube(rear, 'recess light strip', (2.36, .025, .014),
     (-.43, 1.65, 1.556), (.95, .83, .65))
scene.include('rear cabinets', rear)

# Tall appliance cabinet: all oven parts belong to this Asset.
oven = Asset('Tall oven cabinet')
cube(oven, 'cabinet carcass', (1.02, .77, 2.54),
     (1.82, 1.88, 1.27), CHARCOAL)
cube(oven, 'left stile', (.10, .06, 2.51),
     (1.34, 1.465, 1.27), (.025, .029, .027))
cube(oven, 'right stile', (.10, .06, 2.51),
     (2.30, 1.465, 1.27), (.025, .029, .027))
cube(oven, 'upper door', (.81, .035, .64),
     (1.82, 1.472, 2.17), BLACK)
cube(oven, 'lower storage', (.81, .035, .78),
     (1.82, 1.472, .43), BLACK)
for i, z in enumerate([1.02, 1.55]):
    cube(oven, 'oven face %d' % i, (.78, .045, .47),
         (1.82, 1.445, z), (.17, .18, .17))
    cube(oven, 'oven glass %d' % i, (.65, .018, .30),
         (1.82, 1.411, z - .025), (.025, .043, .047))
    cube(oven, 'oven control %d' % i, (.73, .017, .07),
         (1.82, 1.410, z + .175), (.22, .23, .22))
    cube(oven, 'oven handle %d' % i, (.60, .045, .025),
         (1.82, 1.366, z + .12), STEEL)
scene.include('oven tower', oven)

surround = Asset('Appliance architectural surround')
cube(surround, 'top fascia', (1.63, .89, .35),
     (1.84, 1.87, 2.72), (.36, .38, .36))
cube(surround, 'right dark pier', (.21, .91, 2.55),
     (2.56, 1.87, 1.275), (.055, .063, .059))
scene.include('appliance surround', surround)

# Island: plinth supports the body, drawers and countertop.
island = Asset('Island cabinetry')
cube(island, 'recessed support plinth', (2.19, 1.03, .12),
     (ISLAND_X, ISLAND_Y, .065), (.14, .15, .14))
cube(island, 'cabinet body', (ISLAND_W, ISLAND_D, .86),
     (ISLAND_X, ISLAND_Y, .55), STONE)
cube(island, 'left end slab', (.055, ISLAND_D, .91),
     (ISLAND_X - ISLAND_W / 2 - .006, ISLAND_Y, .535),
     (.61, .63, .61))
front_y = ISLAND_Y - ISLAND_D / 2 - .018
for i in range(3):
    z = .215 + i * .278
    cube(island, 'drawer dark reveal %d' % i,
         (ISLAND_W - .075, .025, .018),
         (ISLAND_X, front_y, z + .135), (.25, .27, .25))
    cube(island, 'drawer front %d' % i,
         (ISLAND_W - .07, .035, .256),
         (ISLAND_X, front_y - .012, z), (.69, .71, .68))
cube(island, 'countertop', (ISLAND_W + .045, ISLAND_D + .045, .045),
     (ISLAND_X, ISLAND_Y, COUNTER_Z), COUNTER)
scene.include('kitchen island', island)

# Sink and faucet are separate editable fittings supported by the island top.
sink = Asset('Island sink and faucet')
sx, sy = .58, -.01
cube(sink, 'sink shadow', (.52, .40, .003),
     (sx, sy, 1.045), (.26, .29, .28))
cube(sink, 'sink basin bottom', (.43, .31, .004),
     (sx, sy, 1.048), (.49, .53, .51))
for label, size, center in [
    ('left rim', (.014, .42, .009), (sx - .265, sy, 1.052)),
    ('right rim', (.014, .42, .009), (sx + .265, sy, 1.052)),
    ('front rim', (.54, .014, .009), (sx, sy - .205, 1.052)),
    ('back rim', (.54, .014, .009), (sx, sy + .205, 1.052)),
]:
    cube(sink, label, size, center, (.70, .73, .70))
add_tube(
    sink, 'curved faucet',
    [
        (sx, sy + .29, 1.05),
        (sx, sy + .29, 1.26),
        (sx, sy + .26, 1.32),
        (sx, sy + .15, 1.33),
        (sx, sy + .08, 1.29),
        (sx, sy + .08, 1.22),
    ],
    .014, (.59, .64, .62)
)
add_rod(
    sink, 'faucet lever', .009,
    (sx + .05, sy + .29, 1.07),
    (sx + .05, sy + .29, 1.17),
    (.60, .65, .63)
)
scene.include('sink fittings', sink)

hob = Asset('Flush pale cooktop')
cube(hob, 'glass insert', (.69, .49, .002),
     (-.31, -.31, 1.044), (.72, .74, .68))
for j, (hx, hy) in enumerate([
    (-.49, -.40), (-.15, -.40), (-.49, -.19), (-.15, -.19)
]):
    points = [
        (
            hx + .098 * math.cos(k * 2 * math.pi / 32),
            hy + .074 * math.sin(k * 2 * math.pi / 32),
            1.047,
        )
        for k in range(33)
    ]
    add_tube(hob, 'burner outline %d' % j, points,
             .002, (.87, .87, .78))
scene.include('cooktop', hob)

# Suspended stone extractor and its underside belong to one semantic Asset.
hood = Asset('Suspended stone extractor')
cube(hood, 'stone shaft', HOOD_SIZE, HOOD_CENTER, (.73, .73, .66))
cube(hood, 'underside lip', (1.18, .92, .024),
     (.16, -.05, 1.952), (.58, .59, .54))
cube(hood, 'extractor underside', (.56, .35, .012),
     (.16, -.05, 1.936), (.28, .30, .28))
for i in range(8):
    cube(hood, 'filter slot %d' % i, (.43, .009, .004),
         (.16, -.17 + i * .035, 1.928), (.15, .17, .15))
scene.include('overhead extractor', hood)

# Small red kettle rests on the rear worktop.
kettle = Asset('Red countertop kettle')
kettle.include(
    'black body',
    ball(radius=.087, center=(-.51, 1.79, 1.04),
         color=(.018, .023, .022))
)
add_tube(
    kettle, 'red arch',
    [
        (-.60, 1.79, 1.04),
        (-.60, 1.79, 1.115),
        (-.56, 1.79, 1.16),
        (-.49, 1.79, 1.16),
        (-.44, 1.79, 1.11),
        (-.44, 1.79, 1.04),
    ],
    .014, (.70, .008, .025)
)
cube(kettle, 'base', (.15, .12, .025),
     (-.52, 1.79, .944), (.035, .039, .035))
scene.include('red kettle', kettle)

# All geometry is complete before realization.
realize(scene)
set_view(CAMERA, TARGET, lens=LENS, sensor=36)
scene_bpy = bpy.context.scene

# A World may not survive realization.
world = scene_bpy.world
if world is None:
    world = bpy.data.worlds.new('Showroom ambient')
    scene_bpy.world = world
world.use_nodes = True
background = world.node_tree.nodes.get('Background')
if background is None:
    background = world.node_tree.nodes.new('ShaderNodeBackground')
    output = world.node_tree.nodes.get('World Output')
    if output is None:
        output = world.node_tree.nodes.new('ShaderNodeOutputWorld')
    world.node_tree.links.new(background.outputs['Background'],
                              output.inputs['Surface'])
background.inputs['Color'].default_value = (.47, .49, .46, 1)
background.inputs['Strength'].default_value = AMBIENT_STRENGTH

area_emitter(position=(-3.5, -4.5, 3.7), power=650, size=4.0,
             target=(.3, .2, .8), color=(1.0, .94, .82))
area_emitter(position=(3.1, -.9, 3.5), power=430, size=3.0,
             target=(.2, 0, 1), color=(.88, .93, 1.0))
area_emitter(position=(-.4, 1.66, 1.56), power=48, size=1.8,
             target=(-.4, 2.0, 1.15), color=(1.0, .77, .59))
area_emitter(position=(-1.2, .8, 3.4), power=220, size=2.0,
             target=(0, -.4, .8), color=(1.0, .98, .90))

# Uniform baseline material setup precedes isolated local customization.
for material in bpy.data.materials:
    material.use_nodes = True
    bsdf = material.node_tree.nodes.get('Principled BSDF')
    if bsdf is not None:
        bsdf.inputs['Roughness'].default_value = .57

def descendant_meshes(parent):
    meshes = []
    for child in parent.children:
        if child.type == 'MESH':
            meshes.append(child)
        meshes.extend(descendant_meshes(child))
    return meshes

# Resolve the named SceneAct parent, then traverse its emitted mesh subtree.
hood_parent = bpy.data.objects.get('overhead extractor')
assert hood_parent is not None, "Missing extractor Asset parent"
hood_meshes = descendant_meshes(hood_parent)
assert hood_meshes, "Extractor Asset has no mesh descendants"
for obj in hood_meshes:
    for slot in obj.material_slots:
        if slot.material is None:
            continue
        # SceneAct finishes may be shared with other semantic objects.
        material = slot.material.copy()
        slot.material = material
        material.use_nodes = True
        nodes = material.node_tree.nodes
        links = material.node_tree.links
        bsdf = nodes.get('Principled BSDF')
        assert bsdf is not None
        noise = nodes.new('ShaderNodeTexNoise')
        noise.inputs['Scale'].default_value = 105
        noise.inputs['Detail'].default_value = 2
        bump = nodes.new('ShaderNodeBump')
        bump.inputs['Strength'].default_value = .12
        bump.inputs['Distance'].default_value = .009
        links.new(noise.outputs['Fac'], bump.inputs['Height'])
        links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])

# Reference aspect ratio; the external runner controls saving and rendering.
scene_bpy.render.resolution_x = 384
scene_bpy.render.resolution_y = 512
scene_bpy.render.resolution_percentage = 100
scene_bpy.render.engine = 'CYCLES'
scene_bpy.cycles.samples = 48
scene_bpy.view_settings.view_transform = 'AgX'
scene_bpy.view_settings.exposure = EXPOSURE
