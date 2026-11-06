from sceneact import *
import bpy
import math
import random

# Reference inventory, estimated normalized image bounds:
# Roof and dark structural beams: most of upper and right image, (0.05,0)-(1,0.85).
# Fluorescent strips: diagonal chain from (0.35,0) toward (0.88,0.65).
# Bright rectangular grid skylight: approximately (0.59,0.20)-(0.83,0.38).
# Main rack: left side and lower image, approximately (0,0.05)-(0.91,1),
# with dark steel frames, open shelf gaps, pallets, and pale or brown loads.
# A few goods and rack fragments appear at the far right edge. Rack bases and
# the distant aisle are outside the view or occluded; exact contents are uncertain.
#
# Feedback comparison: the first view places a large blank end wall in the lower
# center and shows too much of a second rack on the right. Its light strips and
# rack converge vertically, while the reference is visibly tilted and the rack
# extends across the lower image. The skylight is too dark and small. This revision
# aims the camera higher and toward the main rack, rolls it, and brightens the
# skylight. The roof, rack, goods, and lights remain separate editable assets.
#
# Primitive estimate: roof 40, skylight 16, fixtures 17, main frame 76,
# pallets and goods about 155, distant edge rack 30, enclosure 2: about 336 meshes.

random.seed(12)
scene = Scene('Warehouse aisle')

steel = (0.17, 0.17, 0.13)
steel_light = (0.30, 0.29, 0.23)
beam_col = (0.16, 0.15, 0.11)
roof_col = (0.28, 0.27, 0.21)
roof_alt = (0.34, 0.32, 0.25)
dark = (0.095, 0.095, 0.07)
wood = (0.48, 0.29, 0.085)
wood_light = (0.64, 0.40, 0.13)
cartons = [(0.65, 0.48, 0.24), (0.75, 0.60, 0.37),
           (0.56, 0.42, 0.23), (0.79, 0.70, 0.52)]
wrap = (0.72, 0.71, 0.59)
white = (1.0, 0.96, 0.78)
sky_white = (0.98, 0.99, 0.95)

def addbox(parent, name, size, center, color):
    parent.include(name, box(size=size, center=center, color=color))

def addrod(parent, name, a, b, radius, color):
    parent.include(name, rod(radius=radius, start=a, end=b, color=color))

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

sky = Asset('gridded roof skylight')
addbox(sky, 'luminous glazing', (2.0, 2.8, .04),
       (2.15, -0.4, 9.78), sky_white)
for i, x in enumerate([1.13, 1.63, 2.15, 2.67, 3.17]):
    addbox(sky, 'long grid bar %d' % i, (.055, 2.9, .08),
           (x, -.4, 9.71), steel)
for j in range(9):
    y = -1.82 + j * .355
    addbox(sky, 'cross grid bar %d' % j, (2.08, .045, .08),
           (2.15, y, 9.70), steel)
scene.include('skylight', sky)

fixtures = Asset('ceiling strip lights')
for i, y in enumerate([-9.0, -4.9, -.8, 3.3, 7.4, 11.5, 15.6]):
    addbox(fixtures, 'fixture housing %d' % i, (.32, 2.65, .10),
           (.35, y, 9.52), (0.34, 0.32, 0.23))
    addbox(fixtures, 'bright diffuser %d' % i, (.22, 2.45, .045),
           (.35, y, 9.45), white)
for i, x in enumerate([-.35, .95, 4.5]):
    addrod(fixtures, 'ceiling conduit %d' % i, (x, -10, 9.60),
           (x, 17, 9.60), .025, dark)
scene.include('fluorescent fixtures and conduits', fixtures)

rack = Asset('left pallet rack structure')
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
    for i in range(len(bay_edges)-1):
        addbox(rack, 'shelf cross support %d %d' % (k, i),
               (2.65, .12, .12),
               (-3.22, (bay_edges[i]+bay_edges[i+1])/2, z), steel)
scene.include('left rack', rack)

goods = Asset('palletized cartons on left rack')
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
            addbox(goods, 'pallet %d %d %d' % (bay, lev, slot),
                   (2.24, 1.72, .14), (x, y, z+.16), wood)
            addbox(goods, 'pallet front edge %d %d %d' % (bay, lev, slot),
                   (.10, 1.72, .12), (x+1.08, y, z+.23), wood_light)
            color = random.choice(cartons)
            if (bay + lev + slot) % 5 == 0:
                color = wrap
            addbox(goods, 'load %d %d %d' % (bay, lev, slot),
                   (width, depth, h), (x, y, z+.27+h/2), color)
            if bay < 3 and (lev + slot) % 2 == 0:
                addbox(goods, 'vertical packing strap %d %d %d' % (bay, lev, slot),
                       (.025, .055, h+.015),
                       (x+width/2+.014, y, z+.27+h/2), (0.40, 0.36, 0.23))
                addbox(goods, 'horizontal packing strap %d %d %d' % (bay, lev, slot),
                       (.025, depth+.015, .045),
                       (x+width/2+.016, y, z+.27+h*.48), (0.49, 0.44, 0.31))
scene.include('pallets and stored cartons', goods)

far = Asset('opposite distant storage rack')
for i, y in enumerate([6, 10, 14, 18]):
    for x in [6.2, 7.7]:
        addbox(far, 'upright %d %.1f' % (i, x), (.12, .12, 8.6),
               (x, y, 4.3), steel)
for k, z in enumerate([1.2, 3.4, 5.6, 7.7]):
    for x in [6.2, 7.7]:
        addbox(far, 'long shelf %d %.1f' % (k, x), (.14, 14.2, .18),
               (x, 12, z), steel)
    for i, y in enumerate([7, 9, 11, 13, 15, 17]):
        if (i+k) % 4 != 0:
            addbox(far, 'distant carton %d %d' % (k, i),
                   (1.18, 1.45, 1.15), (6.95, y, z+.7),
                   cartons[(i+k) % 4])
scene.include('opposite rack', far)

architecture = Asset('warehouse enclosure')
addbox(architecture, 'far wall', (15, .18, 10), (0, 19, 5), (0.25, .24, .18))
addbox(architecture, 'floor', (15, 30, .12), (0, 4, -.1), (0.25, .24, .19))
scene.include('warehouse enclosure', architecture)

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
background.inputs['Color'].default_value = (0.30, 0.27, 0.18, 1)
background.inputs['Strength'].default_value = .4

for mat in bpy.data.materials:
    if not mat.use_nodes:
        continue
    bsdf = mat.node_tree.nodes.get('Principled BSDF')
    if bsdf:
        c = bsdf.inputs['Base Color'].default_value
        if c[0] > .93 and c[1] > .90 and c[2] > .70:
            if 'Emission Color' in bsdf.inputs:
                bsdf.inputs['Emission Color'].default_value = (1.0, .94, .76, 1)
                bsdf.inputs['Emission Strength'].default_value = 4.0

set_view((.25, -9.3, 1.55), (-.7, 1.0, 10.8), lens=29, sensor=36)
sc.camera.rotation_euler.rotate_axis('Z', math.radians(24))

area_emitter((.5, -4, 9.2), power=1100, size=5,
             target=(-2.4, -2, 3.8), color=(1.0, .79, .46))
area_emitter((1, 5, 9.2), power=1300, size=5,
             target=(-2, 5, 3.7), color=(1.0, .83, .55))
area_emitter((2, 13, 9.1), power=900, size=5,
             target=(-2, 10, 4), color=(1.0, .84, .60))
