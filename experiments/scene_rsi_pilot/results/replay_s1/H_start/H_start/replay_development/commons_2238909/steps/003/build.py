from sceneact import *
import bpy
import math

# Foreground needs two winding handles before the exposed book column.
# Call-number plaques are too high; lower them while preserving cabinet tops.
# Floor and cabinet faces are too pale; deepen their materials and reduce fill.

scene = Scene('Archive corridor')
IVORY = (.39, .415, .365)
EDGE = (.19, .215, .145)
METAL = (.23, .27, .25)
BLACK = (.018, .025, .021)
FLOOR = (.043, .055, .044)
CEILING = (.43, .45, .395)
LUMINOUS = (.94, .98, 1.0)

def add(parent, name, size, center, color):
    parent.include(name, box(size=size, center=center, color=color))

add(scene, 'floor', (9, 43, .14), (1.3, 15, -.09), FLOOR)
add(scene, 'ceiling', (8, 43, .15), (1.3, 15, 3.24), CEILING)
add(scene, 'left_wall', (.16, 43, 3.25), (-1.72, 15, 1.56),
    (.43, .455, .385))
add(scene, 'end_wall', (8, .15, 3.25), (1.3, 35, 1.56),
    (.32, .35, .27))
add(scene, 'baseboard', (.07, 41, .14), (-1.60, 15, .07),
    (.18, .21, .16))

for i, x in enumerate([-1.52, -1.29, -.93]):
    scene.include('pipe_%d' % i,
        rod(radius=.055 if i == 1 else .035,
            start=(x, -5, 3.07), end=(x, 35, 3.07),
            color=(.36, .39, .31)))
add(scene, 'ceiling_rail', (.11, 41, .11), (.77, 15, 3.10),
    (.53, .55, .47))

for i in range(25):
    y = -1.70 + i * 1.28
    bank = Asset('Mobile shelving %02d' % i)
    front = 1.10 if i == 1 else .82
    width = .94 if i == 1 else 1.22
    add(bank, 'steel_end', (.085, width, 3.05),
        (front, y, 1.555), IVORY)
    add(bank, 'body', (3.7, width, 3.02),
        (front + 1.91, y, 1.54), (.30, .335, .26))
    add(bank, 'folded_edge', (.12, .10, 3.07),
        (front - .015, y - width / 2, 1.55), EDGE)
    add(bank, 'plinth', (.14, width, .11),
        (front - .012, y, .075), (.12, .15, .105))
    add(bank, 'seam', (.009, .012, 2.97),
        (front - .048, y + .05, 1.55), (.28, .31, .255))

    for j, yy in enumerate([y - .29, y + .32]):
        add(bank, 'lock_plate_%d' % j, (.021, .055, .12),
            (front - .057, yy, 1.04), (.34, .39, .37))
        bank.include('lock_pin_%d' % j,
            rod(radius=.012, start=(front - .085, yy, 1.025),
                end=(front - .085, yy, 1.095),
                color=(.13, .17, .15)))

    centers = [y - .34, y + .27] if i == 0 else [y - .08]
    for j, cy in enumerate(centers):
        bank.include('wheel_%d' % j,
            rod(radius=.105, length=.065,
                center=(front - .10, cy, .64),
                axis='+x', color=BLACK))
        bank.include('hub_%d' % j,
            rod(radius=.034, length=.083,
                center=(front - .145, cy, .64),
                axis='+x', color=METAL))
        bank.include('arm_%d' % j,
            rod(radius=.016, start=(front - .19, cy, .64),
                end=(front - .19, cy + .10, .95), color=METAL))
        bank.include('grip_%d' % j,
            rod(radius=.024,
                start=(front - .20, cy + .10, .95),
                end=(front - .20, cy + .30, .95), color=BLACK))

    label_centers = [y - .32, y + .30] if i == 0 else [y + .05]
    label_height = 2.23
    for j, ly in enumerate(label_centers):
        label_width = .34 if i == 0 else .43
        add(bank, 'label_frame_%d' % j,
            (.024, label_width, .16),
            (front - .062, ly, label_height), (.14, .16, .14))
        add(bank, 'label_paper_%d' % j,
            (.027, label_width - .025, .137),
            (front - .078, ly, label_height), (.67, .69, .65))
        if i < 9:
            for row in range(2):
                for col in range(6):
                    add(bank, 'print_%d_%d_%d' % (j, row, col),
                        (.005, .018 + .004 * ((col + row) % 3), .008),
                        (front - .094, ly - .125 + col * .045,
                         label_height + .028 - row * .047),
                        (.18, .20, .19))
    scene.include('bank_%02d' % i, bank)

shelf = Asset('Exposed book bay')
bay_y = -.77
add(shelf, 'back', (.16, .34, 3.00), (1.20, bay_y, 1.54),
    (.035, .05, .025))
for j, z in enumerate([.12, .73, 1.38, 2.06, 2.73, 3.04]):
    add(shelf, 'shelf_%d' % j, (.57, .38, .037),
        (.97, bay_y, z), (.13, .16, .10))
book_colors = [
    (.035, .06, .045), (.17, .045, .018), (.23, .095, .03),
    (.04, .075, .085), (.24, .20, .08), (.055, .08, .045)
]
for row, base in enumerate([.15, .76, 1.41, 2.09, 2.76]):
    for j in range(5):
        h = [.47, .53, .43, .56, .49][(j + row) % 5]
        if row == 4:
            h = .22
        yy = bay_y - .14 + j * .064
        add(shelf, 'book_%d_%d' % (row, j), (.32, .051, h),
            (.91, yy, base + h / 2),
            book_colors[(j + row) % len(book_colors)])
        if row < 2:
            add(shelf, 'spine_label_%d_%d' % (row, j),
                (.006, .037, .065), (.746, yy, base + .12),
                (.48, .51, .42))
scene.include('book_bay', shelf)

for i, yy in enumerate([-.3, 2.6, 6.8, 12.0, 18.0]):
    cart = Asset('Utility cart %d' % i)
    add(cart, 'top', (.47, .77, .06), (-1.35, yy, .77),
        (.12, .15, .08))
    add(cart, 'lower', (.43, .71, .05), (-1.35, yy, .18),
        (.15, .18, .12))
    for j, (xx, dy) in enumerate([
        (-1.54, -.30), (-1.16, -.30),
        (-1.54, .30), (-1.16, .30)
    ]):
        add(cart, 'leg_%d' % j, (.035, .035, .62),
            (xx, yy + dy, .45), METAL)
    scene.include('cart_%d' % i, cart)
add(scene, 'bin', (.32, .38, .54), (-1.39, 1.62, .28),
    (.025, .04, .02))
add(scene, 'box', (.39, .48, .43), (-1.30, 9.1, .23),
    (.27, .23, .12))

for i in range(11):
    yy = -1.0 + i * 3.3
    fixture = Asset('Fluorescent fixture %d' % i)
    add(fixture, 'housing', (.42, 1.65, .17),
        (-.05, yy, 3.055), (.60, .63, .58))
    for j, xx in enumerate([-.15, .05]):
        add(fixture, 'tube_%d' % j, (.12, 1.54, .025),
            (xx, yy, 2.958), LUMINOUS)
    scene.include('fixture_%d' % i, fixture)

sign = Asset('Exit marker')
add(sign, 'panel', (.50, .065, .22), (-1.11, 8.8, 2.53),
    (.65, .68, .59))
for i, xx in enumerate([-1.28, -1.17, -1.06, -.95]):
    add(sign, 'letter_vertical_%d' % i, (.018, .008, .13),
        (xx, 8.763, 2.53), (.52, .025, .015))
    add(sign, 'letter_top_%d' % i, (.065, .008, .014),
        (xx + .02, 8.763, 2.59), (.52, .025, .015))
scene.include('exit', sign)

realize(scene)

for mat in bpy.data.materials:
    mat.use_nodes = True
    bs = mat.node_tree.nodes.get('Principled BSDF')
    if bs is None:
        continue
    rgb = tuple(bs.inputs['Base Color'].default_value[:3])
    bs.inputs['Roughness'].default_value = .43
    if max(abs(rgb[k] - FLOOR[k]) for k in range(3)) < .008:
        bs.inputs['Roughness'].default_value = .21
        bs.inputs['Specular IOR Level'].default_value = .48
    if rgb[0] > .90 and rgb[1] > .94 and rgb[2] > .97:
        bs.inputs['Emission Color'].default_value = (*LUMINOUS, 1)
        bs.inputs['Emission Strength'].default_value = 3.0

CAMERA = (-1.13, -3.45, 1.56)
YAW = math.radians(27.0)
TARGET = (
    CAMERA[0] + 15 * math.sin(YAW),
    CAMERA[1] + 15 * math.cos(YAW),
    1.36
)
set_view(CAMERA, TARGET, lens=30, sensor=36)

sc = bpy.context.scene
if sc.world is None:
    sc.world = bpy.data.worlds.new('Ambient')
sc.world.use_nodes = True
sc.world.node_tree.nodes['Background'].inputs[0].default_value = (
    .46, .49, .40, 1)
sc.world.node_tree.nodes['Background'].inputs[1].default_value = .13

for yy in [-1, 2.3, 5.6, 8.9, 12.2, 15.5, 19, 23, 28, 33]:
    area_emitter(position=(-.05, yy, 2.91), power=90, size=1.7,
        target=(-.15, yy + .3, 0), color=(.91, .96, 1.0))
area_emitter(position=(-1.35, -3, 2.4), power=25, size=3,
    target=(1.0, 1.5, 1.3), color=(.93, .96, .85))

sc.render.resolution_x = 512
sc.render.resolution_y = 384
sc.render.resolution_percentage = 100
sc.render.engine = 'CYCLES'
sc.cycles.samples = 32
sc.cycles.use_denoising = True
sc.view_settings.view_transform = 'AgX'
sc.view_settings.exposure = -.35
