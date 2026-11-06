# Reference inventory, estimated normalized image bounds:
# Cream partition occupies x=.13-.81 and extends beyond the top and bottom.
# Red paneled door occupies x=0-.15. A dark framed display at x=.25-.77,
# y=.06-.63 contains a large open wheel, four small pulleys, horizontal bars,
# hooks, two hanging tools, and a dark mechanism at its lower right.
# A black rail and yellow label sit below the case, with two circular iron
# plates at y=.74-.91 and a small stand beneath the right plate.
# At right are a tall bright divided window, wall, bench and pale floor.
# A teal pipe runs across the top. The machinery's precise functions and
# geometry behind the partition are uncertain.
#
# The last full render placed the case too low and made it too wide. The
# revision raises and narrows the case, moves the window closer to the
# partition, and extends the architecture beyond the camera framing.
# Estimated expanded primitive count: about 150, including 32 rim segments,
# 16 radial plate marks, and all repeated fittings. No boolean operations.

import math
import bpy
from sceneact import *

scene = Scene('Museum machinery')

cream = (.55, .52, .41)
backing = (.59, .60, .54)
dark = (.045, .043, .035)
black = (.025, .026, .021)
iron = (.095, .09, .075)
rust = (.16, .14, .11)
red = (.37, .105, .065)
glass = (.77, .84, .83)

architecture = Asset('Architecture')
architecture.include('partition', box((2.06, .16, 4.4),
    center=(-.35, .10, 2.2), color=cream))
architecture.include('door', box((.70, .10, 4.3),
    center=(-1.69, -.01, 2.15), color=red))
architecture.include('door_edge', box((.035, .05, 4.3),
    center=(-1.34, -.075, 2.15), color=(.22, .065, .04)))
for x in (-1.94, -1.47):
    architecture.include('door_panel_side_' + str(x),
        box((.022, .025, 2.8), center=(x, -.075, 1.75),
            color=(.43, .15, .09)))
architecture.include('door_panel_top', box((.49, .025, .025),
    center=(-1.705, -.075, 3.15), color=(.43, .15, .09)))
architecture.include('door_hinge_upper', box((.05, .055, .16),
    center=(-1.33, -.12, 2.75), color=(.25, .095, .06)))
architecture.include('floor', box((7, 6, .08),
    center=(.4, 1.5, -.05), color=(.50, .50, .43)))
architecture.include('right_wall', box((2.2, .14, 4.4),
    center=(1.30, 1.05, 2.2), color=(.59, .60, .55)))
scene.include('architecture', architecture)

window = Asset('Right window')
window.include('recess', box((.90, .06, 2.48),
    center=(.94, .955, 2.30), color=(.08, .09, .08)))
window.include('glass', box((.77, .025, 2.31),
    center=(.94, .916, 2.31), color=glass))
for x in (.545, .94, 1.335):
    window.include('vertical_' + str(x), box((.035, .05, 2.39),
        center=(x, .88, 2.31), color=(.075, .085, .08)))
for z in (1.12, 1.86, 2.60, 3.50):
    window.include('horizontal_' + str(z), box((.82, .05, .035),
        center=(.94, .88, z), color=(.075, .085, .08)))
window.include('sill', box((1.04, .25, .08),
    center=(.94, .84, 1.07), color=(.31, .32, .28)))
scene.include('window', window)

bench = Asset('Background bench')
bench.include('seat', box((1.6, .40, .09),
    center=(1.20, .64, .86), color=(.27, .16, .10)))
bench.include('front_rail', box((1.6, .06, .13),
    center=(1.20, .40, .74), color=(.10, .075, .055)))
bench.include('lower_rail', box((1.6, .06, .07),
    center=(1.20, .47, .48), color=(.11, .08, .06)))
bench.include('leg', box((.08, .08, .65),
    center=(1.50, .60, .34), color=(.11, .09, .07)))
scene.include('bench', bench)

pipe = Asset('Ceiling pipe')
pipe.include('main', rod(.042, start=(-.14, -.12, 3.85),
    end=(1.45, -.12, 3.85), color=(.075, .16, .15)))
pipe.include('elbow', rod(.045, start=(-.30, -.12, 3.90),
    end=(-.14, -.12, 3.85), color=(.075, .16, .15)))
pipe.include('collar', rod(.054, start=(-.12, -.12, 3.85),
    end=(-.04, -.12, 3.85), color=(.06, .13, .12)))
pipe.include('thin_pipe', rod(.012, start=(-1.50, .02, 3.93),
    end=(-.29, .02, 3.90), color=(.23, .20, .16)))
scene.include('pipe', pipe)

# Case coordinates are compressed horizontally and expanded vertically around
# the center of the previous build, preserving the editable child hierarchy.
CX = -.32
def X(x):
    return CX + .85 * (x - CX)

def Z(z):
    return 2.12 + 1.08 * (z - 2.12) + .08

def B(parent, name, size, center, color):
    parent.include(name, box((size[0] * .85, size[1], size[2] * 1.08),
        center=(X(center[0]), center[1], Z(center[2])), color=color))

def R(parent, name, radius, start, end, color):
    parent.include(name, rod(radius,
        start=(X(start[0]), start[1], Z(start[2])),
        end=(X(end[0]), end[1], Z(end[2])), color=color))

def disk(parent, name, x, z, radius, depth=.055, y=-.31, color=iron):
    parent.include(name, rod(radius,
        start=(X(x), y, Z(z)), end=(X(x), y-depth, Z(z)), color=color))

def ring(parent, name, x, z, radius, y=-.35, tube=.018,
         segments=20, color=black):
    part = Asset(name)
    for i in range(segments):
        a = 2 * math.pi * i / segments
        b = 2 * math.pi * (i + 1) / segments
        R(part, 'segment_%02d' % i, tube,
          (x + radius*math.cos(a), y, z + radius*math.sin(a)),
          (x + radius*math.cos(b), y, z + radius*math.sin(b)), color)
    parent.include(name, part)

display = Asset('Framed tool display')
B(display, 'back_panel', (1.37, .07, 1.83), (-.32, -.115, 2.12), backing)
for x in (-1.045, .405):
    B(display, 'upright_' + str(x), (.075, .14, 1.98),
      (x, -.18, 2.12), dark)
    B(display, 'inner_upright_' + str(x), (.018, .03, 1.87),
      (x + (.05 if x < 0 else -.05), -.26, 2.12), (.13, .13, .10))
for z in (1.14, 3.10):
    B(display, 'crossbar_' + str(z), (1.52, .14, .075),
      (-.32, -.18, z), dark)
B(display, 'inner_top_bar', (1.18, .10, .08),
  (-.40, -.25, 2.53), rust)
B(display, 'upper_bar_end', (.49, .08, .055),
  (-.02, -.30, 2.47), black)
R(display, 'upper_bar_drop', .012, (.21, -.34, 2.47),
  (.24, -.34, 2.28), black)

wheel = Asset('Upper spoked wheel')
ring(wheel, 'rim', -.77, 2.84, .175, segments=20, tube=.019)
for i in range(5):
    a = 2 * math.pi * i / 5 + .15
    R(wheel, 'spoke_%d' % i, .025, (-.77, -.355, 2.84),
      (-.77 + .161*math.cos(a), -.355, 2.84 + .161*math.sin(a)), iron)
disk(wheel, 'hub', -.77, 2.84, .05, .05, -.365, black)
display.include('upper_wheel', wheel)

for i, (x, r) in enumerate([(-.42, .073), (-.20, .063),
                             (.00, .057), (.16, .052)]):
    disk(display, 'pulley_%d' % i, x, 2.84, r, .06, -.30, black)
    disk(display, 'pulley_hub_%d' % i, x, 2.84, r*.36, .015,
         -.37, (.22, .22, .18))

R(display, 'middle_rod', .014, (-.68, -.31, 2.03),
  (-.05, -.31, 2.03), iron)
B(display, 'middle_mount', (.065, .065, .13), (-.36, -.33, 2.01), black)
R(display, 'hanging_pin', .017, (-.36, -.36, 2.03),
  (-.36, -.36, 1.88), iron)
for i, x in enumerate((-.84, -.72)):
    B(display, 'bracket_%d' % i, (.075, .055, .11),
      (x, -.32, 1.91), black)
    R(display, 'bracket_pin_%d' % i, .009,
      (x, -.36, 1.85), (x, -.36, 1.79), iron)
ring(display, 'hanging_ring', -.78, 1.50, .052,
     y=-.34, tube=.012, segments=12, color=iron)
R(display, 'ring_hook', .012, (-.78, -.34, 1.55),
  (-.78, -.34, 1.59), iron)
for i, dx in enumerate((-.02, .025)):
    R(display, 'tool_handle_%d' % i, .018,
      (-.35+dx, -.36, 1.59), (-.37+dx, -.36, 1.40), black)
    disk(display, 'tool_eye_%d' % i, -.35+dx, 1.62, .026, .025, -.34, iron)
B(display, 'lower_tab_left', (.11, .07, .025),
  (-.65, -.33, 1.27), black)
B(display, 'lower_tab_right', (.14, .07, .025),
  (.22, -.33, 1.27), black)

machine = Asset('Display mounted machine')
B(machine, 'mount', (.30, .07, .12), (.15, -.32, 1.91), black)
R(machine, 'shaft', .027, (.02, -.39, 1.92), (.34, -.39, 1.92), iron)
R(machine, 'post', .025, (.22, -.40, 1.82), (.22, -.40, 2.04), iron)
disk(machine, 'upper_gear', .22, 1.92, .075, .06, -.40, black)
disk(machine, 'upper_hub', .22, 1.92, .024, .025, -.47, (.22, .22, .18))
B(machine, 'tower', (.12, .10, .23), (.08, -.37, 1.63), iron)
R(machine, 'tower_top', .035, (.08, -.39, 1.73),
  (.08, -.39, 1.84), black)
B(machine, 'body', (.31, .14, .19), (.10, -.40, 1.51), iron)
B(machine, 'body_upper', (.22, .12, .12),
  (.10, -.40, 1.63), (.14, .14, .11))
disk(machine, 'side_hub', .24, 1.59, .085, .09, -.47, black)
disk(machine, 'side_hub_center', .24, 1.59, .030, .02,
     -.57, (.22, .22, .18))
B(machine, 'lower_base', (.35, .16, .06), (.11, -.40, 1.30), black)
B(machine, 'base_left', (.065, .13, .19), (-.005, -.40, 1.39), iron)
B(machine, 'base_right', (.065, .13, .19), (.225, -.40, 1.39), iron)
disk(machine, 'arch_opening', .11, 1.40, .065, .04, -.49, backing)
display.include('machine', machine)
scene.include('display', display)

lower = Asset('Lower mounted equipment')
lower.include('black_rail', box((1.45, .06, .10),
    center=(-.32, -.12, 1.09), color=black))
lower.include('label', box((.25, .018, .15),
    center=(-.31, -.16, 1.20), color=(.61, .43, .10)))
lower.include('label_fold', box((.25, .025, .035),
    center=(-.31, -.17, 1.12), color=(.46, .32, .08)))
lower.include('rail_bolt', rod(.030, start=(-.62, -.16, 1.09),
    end=(-.62, -.18, 1.09), color=iron))
lower.include('handle', rod(.035, start=(.02, -.18, 1.23),
    end=(.15, -.28, 1.14), color=black))
lower.include('lower_rail', box((1.42, .06, .10),
    center=(-.30, -.12, .58), color=black))

for j, (x, z, r) in enumerate([(-.62, .63, .27), (.06, .63, .24)]):
    plate = Asset('Circular plate %d' % j)
    plate.include('disk', rod(r, start=(x, -.19, z),
        end=(x, -.265, z), color=(.115, .105, .085)))
    for i in range(8):
        a = 2*math.pi*i/8 + .12
        plate.include('radial_mark_%d' % i, rod(.009,
            start=(x+r*.30*math.cos(a), -.28, z+r*.30*math.sin(a)),
            end=(x+r*.90*math.cos(a), -.28, z+r*.90*math.sin(a)),
            color=black))
    plate.include('hub', rod(.055, start=(x, -.28, z),
        end=(x, -.305, z), color=(.22, .21, .17)))
    plate.include('center', rod(.018, start=(x, -.31, z),
        end=(x, -.325, z), color=black))
    lower.include('plate_%d' % j, plate)

for i in range(5):
    a = 2*math.pi*i/5
    x = .06 + .15*math.cos(a)
    z = .63 + .15*math.sin(a)
    lower.include('right_jaw_%d' % i, box((.11, .055, .09),
        center=(x, -.31, z), color=(.14, .13, .105)))
lower.include('stand_post', rod(.025, start=(.06, -.14, .44),
    end=(.06, -.14, .20), color=iron))
lower.include('stand_foot', box((.45, .06, .035),
    center=(.06, -.14, .195), color=iron))
scene.include('lower_equipment', lower)

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
background.inputs['Color'].default_value = (.68, .66, .59, 1)
background.inputs['Strength'].default_value = .45

set_view((1.25, -9.5, 2.8), (-.36, 0, 2.30), lens=90)
area_emitter((-.8, -4.5, 5.5), power=500, size=5, target=(-.3, 0, 1.8))
area_emitter((3, -1, 3.8), power=220, size=3, target=(0, 0, 1.8))
