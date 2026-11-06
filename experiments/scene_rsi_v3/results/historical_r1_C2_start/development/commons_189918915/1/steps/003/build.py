from sceneact import *
import bpy
import math
import random

# Reference inventory, normalized image bounds:
# Roof and dark transverse beams fill the upper and right portions. Narrow roof
# ribs, conduits and a small round ceiling fitting are visible.
# A chain of bright fluorescent strips runs from roughly (.35, 0) toward
# (.88, .65), beside a bright gridded skylight at (.59, .20)-(.84, .38).
# A tall pallet rack occupies the left side and most of the lower image. Its
# dark open steel structure supports wood pallets and pale or brown wrapped
# loads, with visible gaps between them. A small amount of storage appears at
# the far right. The floor, rack bases and distant contents are obscured.
#
# Review of the second render: the rack and roof are present, but the camera
# roll tilts the lights and rack in the opposite direction to the photograph.
# The rack consequently stays at the left edge instead of extending diagonally
# across the lower frame. Reverse the roll and retain the high camera aim.
# Reduce the prominence of the far wall and add pallet openings and restrained
# surface variation to the foreground loads. Exact hidden goods are uncertain.
#
# Expanded primitive estimate: roof and fittings 40; skylight 15; lights 17;
# main rack 74; 44 loads and pallets with details approximately 200;
# opposite rack approximately 32; enclosure 2. Total about 380 meshes.
random.seed(12)
scene = Scene('Warehouse aisle')

steel = (.17, .17, .13)
steel_light = (.28, .27, .21)
beam_col = (.15, .14, .10)
roof_col = (.28, .27, .20)
roof_alt = (.34, .32, .24)
dark = (.085, .085, .06)
wood = (.48, .29, .08)
wood_light = (.63, .40, .13)
cartons = [(.65, .48, .24), (.75, .60, .37),
           (.56, .42, .23), (.79, .70, .52)]
wrap = (.70, .69, .56)
white = (1.0, .96, .78)
sky_white = (.98, .99, .95)

def addbox(parent, name, size, center, color):
    parent.include(name, box(size=size, center=center, color=color))

def addrod(parent, name, a, b, radius, color):
    parent.include(name, rod(radius=radius, start=a, end=b, color=color))

roof = Asset('corrugated roof and structural beams')
addbox(roof, 'roof sheet', (15, 36, .12), (0, 4, 10), roof_col)
for i in range(27):
    x = -7.4 + i * .57
    addbox(roof, 'roof rib %02d' % i, (.045, 36, .085),
           (x, 4, 9.90), roof_alt)
for i, y in enumerate([-9, -4, 1, 6, 11, 16]):
    addbox(roof, 'cross beam %d' % i, (15, .20, .30),
           (0, y, 9.72), beam_col)
for i, x in enumerate([-5.7, -3.0, 3.8, 6.0]):
    addbox(roof, 'lengthwise purlin %d' % i, (.13, 36, .15),
           (x, 4, 9.76), steel)
roof.include('round ceiling fitting', ball(.13, center=(1.1, -5.2, 9.75),
                                         color=(.45, .42, .32)))
scene.include('roof architecture', roof)

sky = Asset('gridded skylight')
addbox(sky, 'luminous glazing', (2.0, 2.8, .04),
       (2.15, -.4, 9.78), sky_white)
for i, x in enumerate([1.13, 1.63, 2.15, 2.67, 3.17]):
    addbox(sky, 'long grid bar %d' % i, (.055, 2.9, .08),
           (x, -.4, 9.71), steel)
for j in range(9):
    addbox(sky, 'cross grid bar %d' % j, (2.08, .045, .08),
           (2.15, -1.82 + j * .355, 9.70), steel)
scene.include('skylight', sky)

fixtures = Asset('fluorescent ceiling lights and conduits')
for i, y in enumerate([-9, -4.9, -.8, 3.3, 7.4, 11.5, 15.6]):
    addbox(fixtures, 'housing %d' % i, (.32, 2.65, .10),
           (.35, y, 9.52), (.34, .32, .23))
    addbox(fixtures, 'diffuser %d' % i, (.22, 2.45, .045),
           (.35, y, 9.45), white)
for i, x in enumerate([-.35, .95, 4.5]):
    addrod(fixtures, 'conduit %d' % i, (x, -12, 9.6),
           (x, 20, 9.6), .025, dark)
scene.include('ceiling lights', fixtures)

rack = Asset('main pallet rack')
front_x, back_x = -1.9, -4.55
bay_edges = [-8, -4, 0, 4, 8, 12, 16]
levels = [1.0, 3.0, 5.05, 7.1]
for i, y in enumerate(bay_edges):
    for side, x in [('front', front_x), ('back', back_x)]:
        addbox(rack, '%s upright %d' % (side, i), (.14, .14, 9.1),
               (x, y, 4.55), steel_light)
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
    for i in range(6):
        addbox(rack, 'cross support %d %d' % (k, i), (2.65, .12, .12),
               (-3.22, (bay_edges[i] + bay_edges[i + 1]) / 2, z), steel)
scene.include('main rack structure', rack)

goods = Asset('palletized goods')
for bay in range(6):
    y0 = bay_edges[bay]
    for lev, z in enumerate(levels):
        for slot in range(2):
            if (bay, lev, slot) in [(1, 3, 1), (3, 1, 0),
                                    (4, 2, 1), (5, 0, 1)]:
                continue
            y = y0 + 1.05 + slot * 1.85
            x = -3.20 + random.uniform(-.12, .12)
            width = random.uniform(1.65, 2.15)
            depth = random.uniform(1.35, 1.70)
            h = random.uniform(1.05, 1.63)
            key = '%d %d %d' % (bay, lev, slot)
            addbox(goods, 'pallet deck ' + key, (2.24, 1.72, .09),
                   (x, y, z + .20), wood_light)
            for j, dy in enumerate([-.62, 0, .62]):
                addbox(goods, 'pallet block %s %d' % (key, j),
                       (2.12, .18, .16), (x, y + dy, z + .095), wood)
            color = wrap if (bay + lev + slot) % 5 == 0 else random.choice(cartons)
            addbox(goods, 'load ' + key, (width, depth, h),
                   (x, y, z + .25 + h / 2), color)
            if bay < 3 and (lev + slot) % 2 == 0:
                addbox(goods, 'vertical band ' + key, (.025, .045, h + .015),
                       (x + width / 2 + .014, y, z + .25 + h / 2),
                       (.43, .39, .28))
                addbox(goods, 'horizontal band ' + key, (.025, depth + .015, .035),
                       (x + width / 2 + .016, y, z + .25 + h * .48),
                       (.52, .48, .36))
scene.include('pallets and loads', goods)

far = Asset('opposite distant storage rack')
for i, y in enumerate([6, 10, 14, 18]):
    for x in [6.2, 7.7]:
        addbox(far, 'upright %d %.1f' % (i, x), (.12, .12, 8.6),
               (x, y, 4.3), steel)
for k, z in enumerate([1.2, 3.4, 5.6, 7.7]):
    for x in [6.2, 7.7]:
        addbox(far, 'shelf %d %.1f' % (k, x), (.14, 14.2, .18),
               (x, 12, z), steel)
    for i, y in enumerate([7, 9, 11, 13, 15, 17]):
        if (i + k) % 4 != 0:
            addbox(far, 'carton %d %d' % (k, i), (1.18, 1.45, 1.15),
                   (6.95, y, z + .7), cartons[(i + k) % 4])
scene.include('opposite rack', far)

architecture = Asset('warehouse enclosure')
addbox(architecture, 'far wall', (16, .18, 10), (0, 24, 5), (.20, .19, .14))
addbox(architecture, 'floor', (16, 36, .12), (0, 5, -.1), (.25, .24, .19))
scene.include('enclosure', architecture)

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
background.inputs['Color'].default_value = (.30, .27, .18, 1)
background.inputs['Strength'].default_value = .4

for mat in bpy.data.materials:
    if not mat.use_nodes:
        continue
    bsdf = mat.node_tree.nodes.get('Principled BSDF')
    if bsdf:
        c = bsdf.inputs['Base Color'].default_value
        if c[0] > .93 and c[1] > .90 and c[2] > .70:
            if 'Emission Color' in bsdf.inputs:
                bsdf.inputs['Emission Color'].default_value = (1, .94, .76, 1)
                bsdf.inputs['Emission Strength'].default_value = 4.0

set_view((.25, -9.3, 1.55), (-.7, 1.0, 10.8), lens=29, sensor=36)
sc.camera.rotation_euler.rotate_axis('Z', math.radians(-24))

area_emitter((.5, -4, 9.2), power=1100, size=5,
             target=(-2.4, -2, 3.8), color=(1, .79, .46))
area_emitter((1, 5, 9.2), power=1300, size=5,
             target=(-2, 5, 3.7), color=(1, .83, .55))
area_emitter((2, 13, 9.1), power=900, size=5,
             target=(-2, 10, 4), color=(1, .84, .60))
