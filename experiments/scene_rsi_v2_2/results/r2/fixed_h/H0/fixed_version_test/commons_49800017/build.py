from sceneact import *
import bpy
import math
import random

random.seed(16)
scene = Scene('Timber hall')

plaster = (.73, .74, .70)
timber = (.45, .47, .42)
pale_wood = (.65, .67, .61)
floor_color = (.79, .80, .76)
base_color = (.26, .28, .23)

def add(name, node):
    scene.include(name, node)
    return node

add('floor', box((34, 38, .16), center=(0, 4, -.08), color=floor_color))
add('rear wall', box((29, .22, 10), center=(0, 14, 5), color=plaster))
add('right wall', box((.22, 30, 10), center=(9, 0, 5), color=plaster))
add('left wall', box((.22, 30, 10), center=(-13, 0, 5), color=plaster))
add('rear baseboard', box((29, .06, .13), center=(0, 13.85, .065), color=base_color))
add('right baseboard', box((.06, 30, .13), center=(8.85, 0, .065), color=base_color))

# A recessed wall turns forward on the right side of the opening.
add('right recess return', box((.16, 5.5, 5.45), center=(5.65, 11.25, 2.725), color=plaster))
add('return baseboard', box((.045, 5.5, .13), center=(5.55, 11.25, .065), color=base_color))

add('transverse timber beam', box((29, .75, 1.02), center=(0, 7.4, 6.06), color=timber))
add('beam lower edge', box((29, .79, .13), center=(0, 7.4, 5.50), color=pale_wood))

# Boarded ceiling.
for j in range(65):
    y = -9 + j * .40
    v = random.uniform(-.025, .025)
    add('ceiling board %02d' % j,
        box((29, .392, .12), center=(0, y, 9.82),
            color=(.70 + v, .71 + v, .66 + v)))

for x in (-9, 3.4, 9):
    add('ceiling rib %.1f' % x,
        box((.19, 28, .36), center=(x, 2, 9.58), color=timber))

# Laminated timber support. Each narrow strip follows the two curved arms.
def curved_strip(name, points, width, depth, color):
    asset = Asset(name)
    for k in range(len(points) - 1):
        a, b = points[k], points[k + 1]
        dx, dz = b[0] - a[0], b[2] - a[2]
        length = math.sqrt(dx * dx + dz * dz)
        node = box((width, depth, length + .025),
                   center=((a[0] + b[0]) / 2,
                           (a[1] + b[1]) / 2,
                           (a[2] + b[2]) / 2),
                   color=color)
        node.turn('y', math.degrees(math.atan2(dx, dz)))
        asset.include('segment %02d' % k, node)
    add(name, asset)

base_x = -3.0
for strip in range(9):
    off = (strip - 4) * .079
    v = random.uniform(-.025, .025)
    color = (.43 + v, .46 + v, .40 + v)
    right = []
    left = []
    for k in range(27):
        t = k / 26
        z = .13 + 9.72 * t
        right.append((base_x + off + 7.05 * t ** 3.0, 0, z))
        left.append((base_x + off - 2.85 * t ** 2.5, .015, z))
    curved_strip('right curved lamination %02d' % strip, right, .077, .76, color)
    curved_strip('left curved lamination %02d' % strip, left, .077, .74, color)

add('column dark foot', box((.80, .81, .16), center=(base_x, 0, .08), color=base_color))

# Vertical timber cladding at the sides of the broad opening.
for side, x0, x1 in [('left', -4.7, -2.65), ('right', 6.0, 8.05)]:
    count = 15
    step = (x1 - x0) / count
    for i in range(count):
        v = random.uniform(-.055, .045)
        add('%s wall board %02d' % (side, i),
            box((step - .008, .20, 5.43),
                center=(x0 + (i + .5) * step, 7.34, 2.715),
                color=(.61 + v, .63 + v, .57 + v)))

# Inset rectangular ventilation grilles.
for i, (x, width) in enumerate([(-8.4, 1.65), (-.4, 1.45), (5.3, 1.0)]):
    add('vent frame %d' % i,
        box((width + .09, .035, .36), center=(x, 7.005, 6.04), color=(.73, .74, .69)))
    add('vent inset %d' % i,
        box((width, .04, .275), center=(x, 6.979, 6.04), color=(.28, .30, .27)))
    for n in range(int(width / .12)):
        add('vent divider %d %d' % (i, n),
            box((.012, .013, .26),
                center=(x - width / 2 + .07 + n * .12, 6.95, 6.04),
                color=(.51, .53, .47)))

for i, x in enumerate((-8.2, -4.5)):
    add('rear vent frame %d' % i,
        box((.96, .035, .30), center=(x, 13.855, 4.25), color=(.79, .80, .75)))
    add('rear vent dark %d' % i,
        box((.83, .045, .22), center=(x, 13.83, 4.25), color=(.37, .39, .35)))
    for n in range(9):
        add('rear grille %d %d' % (i, n),
            box((.018, .012, .21), center=(x - .36 + n * .09, 13.80, 4.25),
                color=pale_wood))

# Door and small wall fixtures in the rear right corner.
add('door', box((.88, .045, 2.65), center=(5.03, 13.85, 1.325), color=(.67, .69, .63)))
for x in (4.57, 5.49):
    add('door jamb %.2f' % x,
        box((.035, .055, 2.69), center=(x, 13.805, 1.345), color=(.49, .51, .46)))
add('door head', box((.95, .055, .035), center=(5.03, 13.805, 2.69), color=(.49, .51, .46)))
add('door handle', box((.035, .07, .16), center=(5.33, 13.76, 1.16), color=base_color))
add('exit sign', box((.29, .045, .18), center=(5.03, 13.80, 2.94), color=(.39, .44, .37)))

for x in (-1.3, 3.5):
    add('low socket %.1f' % x,
        box((.08, .035, .065), center=(x, 13.85, .17), color=(.27, .29, .25)))
add('utility panel', box((.38, .035, .26), center=(3.55, 13.85, .60), color=(.67, .69, .64)))
add('small wall switch', box((.075, .035, .09), center=(3.7, 13.85, 1.18), color=(.58, .60, .55)))

pendants = [(.3, 2.9, 7.65, .34), (7.8, 4.2, 7.55, .29)]
for i, (x, y, bottom, radius) in enumerate(pendants):
    add('pendant wire %d' % i,
        rod(.014, start=(x, y, bottom + 1.06), end=(x, y, 9.72), color=(.25, .27, .23)))
    add('pendant ceiling rose %d' % i,
        rod(.065, start=(x, y, 9.70), end=(x, y, 9.77), color=(.38, .40, .35)))
    add('pendant shade %d' % i,
        rod(radius, start=(x, y, bottom), end=(x, y, bottom + 1.06), color=(.39, .41, .35)))
    add('pendant diffuser %d' % i,
        rod(radius * .94, start=(x, y, bottom - .016), end=(x, y, bottom),
            color=(.97, .97, .91)))

realize(scene)

for mat in bpy.data.materials:
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get('Principled BSDF')
    if bsdf:
        bsdf.inputs['Roughness'].default_value = .82

set_view((7.8, -15, 3.65), (0, 5, 3.35), lens=35, sensor=36)

area_emitter((-6, -5, 8.5), power=2200, size=9,
             target=(-1, 5, 0), color=(1, .99, .96))
area_emitter((6, -2, 8.5), power=1800, size=8,
             target=(2, 7, 1), color=(.97, .99, 1))
area_emitter((-8, 8, 7), power=1100, size=6,
             target=(-2, 8, 1))
for x, y, bottom, radius in pendants:
    area_emitter((x, y, bottom - .035), power=90, size=radius * 1.7,
                 target=(x, y, 0), color=(1, 1, .95))

sc = bpy.context.scene
if sc.world is None:
    sc.world = bpy.data.worlds.new('Hall world')
world = sc.world
world.use_nodes = True
background = world.node_tree.nodes.get('Background')
background.inputs['Color'].default_value = (.78, .80, .76, 1)
background.inputs['Strength'].default_value = .65

sc.render.engine = 'CYCLES'
sc.cycles.samples = 32
sc.cycles.use_denoising = True
sc.render.resolution_x = 512
sc.render.resolution_y = 406
sc.render.resolution_percentage = 100
sc.view_settings.view_transform = 'AgX'
sc.view_settings.exposure = .55
sc.view_settings.gamma = 1.0
