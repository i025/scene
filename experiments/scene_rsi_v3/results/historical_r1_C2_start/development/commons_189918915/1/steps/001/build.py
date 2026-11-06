from sceneact import *
import bpy
import math
import random

# Reference inventory, normalized image coordinates, estimated:
# - Tall warehouse pallet rack fills the left and lower image (x 0-.88, y .12-1).
#   It has dark upright frames, horizontal shelves, diagonal braces, wooden pallets,
#   and many tan or pale wrapped cartons. Far bays shrink toward the lower right.
# - High corrugated metal roof occupies the upper and right image (x .10-1, y 0-.82),
#   crossed by dark structural beams and slender pipes.
# - Bright fluorescent strips recede along the roof near image center; a rectangular
#   gridded skylight is visible in the upper middle-right.
# - The lower aisle and rack bases are mostly outside the frame or hidden by goods.
#   Exact carton contents, distant rack layout and roof fittings remain uncertain.
#
# Primitive estimate: roof and beams ~45; lights and skylight ~34;
# rack frames and shelves ~100; pallets and cartons ~120; distant rack ~35.
# Approximately 334 separate primitives, with no Boolean operations.

random.seed(12)
scene = Scene('Warehouse aisle')

steel = (0.20, 0.20, 0.16)
steel_light = (0.33, 0.31, 0.24)
beam_col = (0.17, 0.16, 0.12)
roof_col = (0.30, 0.29, 0.23)
roof_alt = (0.34, 0.32, 0.25)
dark = (0.105, 0.105, 0.075)
wood = (0.48, 0.30, 0.105)
wood_light = (0.60, 0.39, 0.14)
cartons = [(0.65, 0.49, 0.26), (0.74, 0.60, 0.38),
           (0.57, 0.43, 0.24), (0.79, 0.70, 0.51)]
wrap = (0.70, 0.69, 0.55)
white = (1.0, 0.96, 0.78)

def addbox(parent, name, size, center, color):
    parent.include(name, box(size=size, center=center, color=color))

def addrod(parent, name, a, b, radius, color):
    parent.include(name, rod(radius=radius, start=a, end=b, color=color))

# Roof plane and visible corrugation. Its long axis follows the aisle.
roof = Asset('corrugated roof')
addbox(roof, 'roof sheet', (13, 30, .12), (0, 4, 10.0), roof_col)
for i in range(23):
    x = -6.4 + i * .58
    addbox(roof, 'roof rib %02d' % i, (.045, 30, .085),
           (x, 4, 9.90), roof_alt)
for i, y in enumerate([-9, -4, 1, 6, 11, 16]):
    addbox(roof, 'transverse structural beam %d' % i,
           (13, .20, .30), (0, y, 9.72), beam_col)
for i, x in enumerate([-5.7, -3.0, 3.8, 6.0]):
    addbox(roof, 'longitudinal purlin %d' % i,
           (.13, 30, .15), (x, 4, 9.76), steel)
scene.include('roof architecture', roof)

# Skylight is represented as a luminous inset panel just beneath the roof,
# with its dark rectangular perimeter and grid.
sky = Asset('gridded roof skylight')
addbox(sky, 'glass', (1.65, 2.4, .035), (2.15, 2.5, 9.79), (0.82, 0.87, 0.78))
for x in [1.30, 2.15, 3.0]:
    addbox(sky, 'long frame %.2f' % x, (.055, 2.5, .08), (x, 2.5, 9.72), steel)
for j in range(7):
    y = 1.28 + j * .405
    addbox(sky, 'cross frame %d' % j, (1.75, .045, .08), (2.15, y, 9.71), steel)
scene.include('skylight', sky)

# Strip lights run in a line down the aisle, with dark suspension rails.
fixtures = Asset('ceiling strip lights')
for i, y in enumerate([-7.5, -3.4, .7, 4.8, 8.9, 13.0]):
    addbox(fixtures, 'fixture housing %d' % i, (.32, 2.45, .10),
           (.65, y, 9.52), (0.34, 0.32, 0.23))
    addbox(fixtures, 'bright diffuser %d' % i, (.20, 2.20, .045),
           (.65, y, 9.45), white)
for i, x in enumerate([-.2, 1.12, 4.5]):
    addrod(fixtures, 'ceiling conduit %d' % i, (x, -10, 9.60),
           (x, 17, 9.60), .025, dark)
scene.include('fluorescent fixtures and conduits', fixtures)

# Main rack: four bays, tall open steel frames and shelf beams.
rack = Asset('left pallet rack structure')
front_x, back_x = -1.9, -4.55
bay_edges = [-8, -4, 0, 4, 8, 12, 16]
levels = [1.0, 3.0, 5.05, 7.1]
for i, y in enumerate(bay_edges):
    for side, x in [('front', front_x), ('back', back_x)]:
        addbox(rack, '%s upright %d' % (side, i), (.14, .14, 9.1),
               (x, y, 4.55), steel_light)
    # Cross-braces retain the open silhouette of the upright frames.
    for k in range(4):
        z = .2 + k * 2.15
        if k % 2 == 0:
            a, b = (back_x, y, z), (front_x, y, z + 2.05)
        else:
            a, b = (front_x, y, z), (back_x, y, z + 2.05)
        addrod(rack, 'frame diagonal %d %d' % (i, k), a, b, .035, steel)
for k, z in enumerate(levels):
    for side, x in [('front', front_x), ('back', back_x)]:
        addbox(rack, '%s shelf beam %d' % (side, k), (.15, 24.2, .18),
               (x, 4, z), steel)
    for i in range(len(bay_edges)-1):
        addbox(rack, 'shelf cross support %d %d' % (k, i),
               (2.65, .12, .12), (-3.22, (bay_edges[i]+bay_edges[i+1])/2, z), steel)
scene.include('left rack', rack)

# Individual pallets and large goods. Each row is deliberately sparse enough to
# preserve the visible dark spaces between loads.
goods = Asset('palletized cartons on left rack')
for bay in range(6):
    y0 = bay_edges[bay]
    for lev, z in enumerate(levels):
        for slot in range(2):
            y = y0 + 1.05 + slot * 1.85
            if (bay, lev, slot) in [(1, 3, 1), (3, 1, 0), (4, 2, 1), (5, 0, 1)]:
                continue
            x = -3.20 + random.uniform(-.12, .12)
            width = random.uniform(1.65, 2.15)
            depth = random.uniform(1.35, 1.70)
            h = random.uniform(1.05, 1.63)
            addbox(goods, 'pallet %d %d %d' % (bay, lev, slot),
                   (2.24, 1.72, .14), (x, y, z+.16), wood)
            addbox(goods, 'pallet front edge %d %d %d' % (bay, lev, slot),
                   (.10, 1.72, .12), (x+1.08, y, z+.23), wood_light)
            color = random.choice(cartons)
            if (bay + lev + slot) % 5 == 0:
                color = wrap
            addbox(goods, 'load %d %d %d' % (bay, lev, slot),
                   (width, depth, h), (x, y, z+.27+h/2), color)
            # Broad packing bands are visible on the larger foreground loads.
            if bay < 3 and (lev + slot) % 2 == 0:
                addbox(goods, 'vertical packing strap %d %d %d' % (bay, lev, slot),
                       (.025, .055, h+.015),
                       (x+width/2+.014, y, z+.27+h/2), (0.40, 0.36, 0.23))
                addbox(goods, 'horizontal packing strap %d %d %d' % (bay, lev, slot),
                       (.025, depth+.015, .045),
                       (x+width/2+.016, y, z+.27+h*.48), (0.49, 0.44, 0.31))
scene.include('pallets and stored cartons', goods)

# A narrower distant rack at the opposite edge of the aisle.
far = Asset('opposite distant storage rack')
for i, y in enumerate([2, 6, 10, 14, 18]):
    for x in [4.9, 6.4]:
        addbox(far, 'upright %d %.1f' % (i, x), (.12, .12, 8.6),
               (x, y, 4.3), steel)
for k, z in enumerate([1.2, 3.4, 5.6, 7.7]):
    for x in [4.9, 6.4]:
        addbox(far, 'long shelf %d %.1f' % (k, x), (.14, 16.2, .18),
               (x, 10, z), steel)
    for i, y in enumerate([3, 5, 7, 9, 11, 13, 15, 17]):
        if (i+k) % 4 != 0:
            addbox(far, 'distant carton %d %d' % (k, i),
                   (1.18, 1.45, 1.15), (5.65, y, z+.7), cartons[(i+k)%4])
scene.include('opposite rack', far)

# Far wall provides a dark architectural closure where the aisle is visible.
architecture = Asset('warehouse enclosure')
addbox(architecture, 'far wall', (13, .18, 10), (0, 19, 5), (0.25, .24, .18))
addbox(architecture, 'floor', (13, 30, .12), (0, 4, -.1), (0.25, .24, .19))
scene.include('warehouse enclosure', architecture)

realize(scene)

# Configure the scene after realization, which clears Blender's previous world.
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
background.inputs['Color'].default_value = (0.30, 0.27, 0.18, 1)
background.inputs['Strength'].default_value = .45

# Make the plastic light diffusers and skylight visibly luminous.
for mat in bpy.data.materials:
    if not mat.use_nodes:
        continue
    bsdf = mat.node_tree.nodes.get('Principled BSDF')
    if bsdf:
        c = bsdf.inputs['Base Color'].default_value
        if c[0] > .93 and c[1] > .90 and c[2] > .70:
            if 'Emission Color' in bsdf.inputs:
                bsdf.inputs['Emission Color'].default_value = (1.0, .91, .67, 1)
                bsdf.inputs['Emission Strength'].default_value = 3.5

set_view((.25, -9.3, 1.55), (-.05, 3.2, 9.0), lens=29, sensor=36)
area_emitter((.5, -4, 9.2), power=1100, size=5,
             target=(-2.4, -2, 3.8), color=(1.0, .79, .46))
area_emitter((1, 5, 9.2), power=1300, size=5,
             target=(-2, 5, 3.7), color=(1.0, .83, .55))
area_emitter((2, 13, 9.1), power=900, size=5,
             target=(-2, 10, 4), color=(1.0, .84, .60))
