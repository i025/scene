from sceneact import *
import bpy
import math
import random

random.seed(23)

# Visual estimates, normalized image coordinates:
# Sill (.08,.16) to (.87,.22); floor enters at (0,.46).
# Large flywheel center (.67,.25); rear flywheel (.35,.29).
# Anvil horn (.49,.36); nearest spindle (.80,.51).
# Foreground bench edge (.49,.65) to (1,.78).
# Camera and arbitrary world scale remain uncertain.
# No rendered observation was supplied. The timeout gives no visual evidence.
# Repair: substantially reduce mesh count, tube samples, floor subdivisions,
# bucket panels and material copies. Preserve the proposed camera and layout.

# CAMERA
CAMERA = (6.5, -8.4, 5.0)
TARGET = (-1.0, .12, 1.48)
LENS = 43

# ARCHITECTURE
WALL_Y = 1.05
BENCH_Z = 1.12

# OBJECT DIMENSIONS / POSES — independent of camera parameters
BENCHES = [
    ("foreground bench", 1.65, 3.15),
    ("anvil bench", -1.34, 2.65),
    ("rear bench", -3.8, 2.12),
    ("distant bench", -6.06, 2.2),
]
LATHES = [
    ("large lathe", 1.83, -.08, 2.38),
    ("rear lathe", -3.82, .03, 1.55),
    ("distant lathe", -6.12, .02, 1.38),
]

# MATERIALS
WOOD = (.25, .20, .125)
TOP = (.39, .33, .23)
LIGHTWOOD = (.47, .39, .27)
IRON = (.105, .12, .115)
STEEL = (.25, .265, .25)
RUST = (.27, .18, .105)
PLASTER = (.49, .53, .46)
TRIM = (.30, .34, .30)

# LIGHTING
WORLD_STRENGTH = .45

scene = Scene("historic workshop")

def put(parent, key, node):
    assert key not in parent.members, key
    return parent.include(key, node)

def block(parent, key, size, center, color):
    assert all(math.isfinite(v) and v > 0 for v in size)
    assert all(math.isfinite(v) for v in center)
    return put(parent, key, box(size=size, center=center, color=color))

def shaft(parent, key, p, q, radius=.025, color=IRON):
    assert math.isfinite(radius) and radius > 0
    assert all(math.isfinite(v) for v in (*p, *q))
    assert sum((a-b)**2 for a, b in zip(p, q)) > 1e-12
    return put(parent, key, rod(radius=radius, start=p, end=q, color=color))

def hoop(parent, key, center, radius, thickness, color=IRON, plane="xz"):
    assert radius > 0 and thickness > 0
    x, y, z = center
    pts = []
    for i in range(21):
        a = 2*math.pi*i/20
        if plane == "xz":
            pts.append((x+radius*math.cos(a), y, z+radius*math.sin(a)))
        elif plane == "yz":
            pts.append((x, y+radius*math.cos(a), z+radius*math.sin(a)))
        else:
            pts.append((x+radius*math.cos(a), y+radius*math.sin(a), z))
    assert all(sum((a-b)**2 for a, b in zip(p, q)) > 1e-12
               for p, q in zip(pts, pts[1:]))
    return put(parent, key, sweep_tube(points=pts, radius=thickness, color=color))

# Architecture: broad floorboards, plaster, piers and four window bays.
room = Asset("room architecture")
for j in range(32):
    c = random.uniform(.88, 1.10)
    block(room, f"floorboard_{j}", (17, .238, .075),
          (-1.5, -5.9+j*.245, -.0375),
          tuple(v*c for v in (.43, .35, .235)))
block(room, "lower plaster", (13, .17, 1.7), (-2, WALL_Y, .85), PLASTER)
block(room, "upper plaster", (13, .17, .45), (-2, WALL_Y, 4.15), PLASTER)
block(room, "left end wall", (.22, 5, 4.5),
      (-8.35, -1.25, 2.2), (.48, .48, .41))
for i, x in enumerate((-8.1, -5.3, -2.5, .3, 3.1)):
    block(room, f"pier_{i}", (.36, .19, 2.1), (x, WALL_Y, 2.75), PLASTER)
for i, x in enumerate((-6.7, -3.9, -1.1, 1.7)):
    block(room, f"daylight_pane_{i}", (2.38, .045, 2.04),
          (x, 1.085, 2.76), (.77, .86, .86))
    block(room, f"sill_{i}", (2.70, .42, .105), (x, .88, 1.73), TRIM)
    for j, dx in enumerate((-1.19, 0, 1.19)):
        block(room, f"mullion_{i}_{j}", (.055, .10, 2.08),
              (x+dx, .95, 2.77), TRIM)
    for j, z in enumerate((1.77, 2.65, 3.77)):
        block(room, f"crossbar_{i}_{j}", (2.38, .10, .055), (x, .95, z), TRIM)
put(scene, "architecture", room)

# Each bench includes its top, apron, legs and stretcher.
# Feet touch z=0; machine feet sit on the slab at z=1.195.
for name, x, length in BENCHES:
    a = Asset(name)
    block(a, "worktop", (length, 1.15, .15), (x, -.02, BENCH_Z), TOP)
    block(a, "front apron", (length, .13, .26), (x, -.59, .91), WOOD)
    for i, dx in enumerate((-length/2+.18, length/2-.18)):
        for j, y in enumerate((-.47, .40)):
            block(a, f"leg_{i}_{j}", (.15, .17, 1.045),
                  (x+dx, y, .5225), WOOD)
    block(a, "low stretcher", (length-.25, .10, .14), (x, .25, .30), WOOD)
    put(scene, name, a)

# Three independent metal lathes, with open space beneath their beds.
for name, x, y, length in LATHES:
    a = Asset(name)
    for i, dx in enumerate((-length*.38, length*.38)):
        block(a, f"foot_{i}", (.36, .48, .09), (x+dx, y, 1.24), IRON)
        block(a, f"cast support_{i}", (.17, .29, .30), (x+dx, y, 1.42), IRON)
    for i, yy in enumerate((-.14, .14)):
        block(a, f"bed rail_{i}", (length, .095, .13), (x, y+yy, 1.62), STEEL)
    block(a, "headstock", (.41, .42, .30), (x+length*.29, y, 1.82), IRON)
    block(a, "tailstock", (.30, .32, .24), (x-length*.35, y, 1.81), IRON)
    shaft(a, "spindle", (x-length*.59, y, 1.92),
          (x+length*.57, y, 1.92), .055, STEEL)
    shaft(a, "belt pulley", (x+length*.10, y, 1.92),
          (x+length*.20, y, 1.92), .135, IRON)
    block(a, "tool slide", (.40, .46, .065), (x-.12, y-.06, 1.73), STEEL)
    shaft(a, "toolpost", (x-.12, y-.12, 1.75), (x-.12, y-.12, 2.02), .033)
    shaft(a, "tool handle", (x-.26, y-.12, 2.02), (x+.02, y-.12, 2.08), .022)
    shaft(a, "feed screw", (x-length*.44, y-.23, 1.58),
          (x+length*.43, y-.23, 1.58), .023, STEEL)
    if name == "large lathe":
        hoop(a, "tailstock handwheel", (x-length*.59, y, 1.92),
             .12, .018, STEEL, "yz")
    put(scene, name, a)

# Flywheels: open rims and five spokes, with their own bench-mounted supports.
for name, x, y, z, r in [
    ("large flywheel", .56, .37, 2.53, .57),
    ("rear flywheel", -3.14, .31, 1.99, .38),
]:
    a = Asset(name)
    block(a, "base", (.48, .43, .09), (x, y, 1.24), IRON)
    for i, side in enumerate((-1, 1)):
        shaft(a, f"upright_{i}", (x+side*.17, y, 1.28),
              (x+side*.065, y, z-.05), .045)
    hoop(a, "wheel rim", (x, y-.04, z), r, .045)
    for k in range(5):
        t = k*2*math.pi/5
        shaft(a, f"spoke_{k}", (x, y-.04, z),
              (x+(r-.035)*math.cos(t), y-.04, z+(r-.035)*math.sin(t)), .031)
    shaft(a, "hub", (x, y-.16, z), (x, y+.15, z), .09, STEEL)
    shaft(a, "crank", (x, y-.17, z), (x+.20, y-.17, z-.18), .025, STEEL)
    shaft(a, "grip", (x+.20, y-.17, z-.18), (x+.20, y-.34, z-.18), .03, WOOD)
    shaft(a, "drive belt", (x+r*.82, y+.08, z-r*.48),
          (x+.13, y+.08, 1.37), .012, (.19, .14, .085))
    put(scene, name, a)

anvil = Asset("large anvil")
block(anvil, "wood support", (.66, .68, .22), (-1.27, -.03, 1.30), WOOD)
block(anvil, "base", (.76, .48, .11), (-1.25, -.02, 1.45), RUST)
block(anvil, "waist", (.39, .31, .30), (-1.27, -.02, 1.65), RUST)
block(anvil, "shoulder", (.58, .39, .18), (-1.27, -.02, 1.80), RUST)
block(anvil, "striking face", (.98, .44, .12), (-1.29, -.02, 1.92), (.32, .30, .24))
for k in range(5):
    xx = -.80+k*.105
    shaft(anvil, f"horn_{k}", (xx, -.02, 1.90),
          (xx+.115, -.02, 1.90), .145*(1-k/5)+.008, RUST)
put(scene, "anvil", anvil)

vise = Asset("foreground bench vise")
block(vise, "mount", (.43, .34, .10), (.06, -.55, 1.24), IRON)
block(vise, "fixed jaw", (.36, .12, .26), (.06, -.65, 1.35), STEEL)
block(vise, "moving jaw", (.36, .13, .22), (.06, -.88, 1.32), IRON)
shaft(vise, "screw", (.06, -.55, 1.24), (.06, -1.04, 1.24), .045, STEEL)
shaft(vise, "handle", (.06, -1.04, .98), (.06, -1.04, 1.48), .018, STEEL)
put(scene, "bench vise", vise)

drawer = Asset("open wooden drawer")
block(drawer, "bottom", (.90, .66, .055), (1.02, -.94, .77), WOOD)
block(drawer, "front", (.97, .07, .27), (1.02, -1.24, .87), (.24, .21, .15))
for i, x in enumerate((.56, 1.48)):
    block(drawer, f"side_{i}", (.055, .65, .22), (x, -.94, .86), WOOD)
shaft(drawer, "pull", (1.02, -1.30, .88), (1.02, -1.35, .88), .045, RUST)
put(scene, "open drawer", drawer)

# Supported hand tools and papers; individual semantic objects remain editable.
for k in range(7):
    a = Asset(f"bench tool {k}")
    x = .22+k*.30
    y = -.42+(k%3)*.14
    shaft(a, "steel shaft", (x, y, 1.214), (x+.36, y+.035, 1.214), .018, STEEL)
    if k%2 == 0:
        shaft(a, "wood handle", (x-.12, y, 1.219), (x, y, 1.219), .026, LIGHTWOOD)
    put(scene, f"bench tool {k}", a)
for k, (x, y) in enumerate(((1.35, -.32), (2.80, -.24), (.85, -.12))):
    a = Asset(f"paper {k}")
    block(a, "sheet", (.43, .32, .008), (x, y, 1.204), (.72, .70, .61))
    a.turn("z", (-12, 8, 20)[k], pivot=(x, y, 1.204))
    put(scene, f"paper {k}", a)
for k in range(4):
    a = Asset(f"rear stock {k}")
    block(a, "wood strip", (.72, .065, .045),
          (-4, -.39+k*.11, 1.218), LIGHTWOOD)
    put(scene, f"rear stock {k}", a)

# Economical hollow buckets: eight wall panels, bottom and open upper rim.
for name, x, y, r, h, color in [
    ("cream bucket", 1.73, -.44, .31, .62, (.55, .54, .41)),
    ("green drum", 3.03, -.40, .40, .79, (.20, .25, .15)),
    ("rear waste bin", -3.0, .07, .24, .56, (.26, .29, .23)),
]:
    a = Asset(name)
    for j in range(8):
        t = 2*math.pi*j/8
        p = (x+r*math.cos(t), y+r*math.sin(t), h/2)
        panel = block(a, f"wall_{j}", (2*r*math.tan(math.pi/8), .028, h), p, color)
        panel.turn("z", math.degrees(t)+90, pivot=p)
    shaft(a, "bottom", (x, y, .015), (x, y, .045), r, (.075, .068, .045))
    put(scene, name, a)

for k in range(3):
    a = Asset(f"leaning tool {k}")
    x = -.36+k*.12
    shaft(a, "shaft", (x, -.76, .03), (x+.04, -.62, 1.30), .018, WOOD)
    shaft(a, "tip", (x+.04, -.62, 1.22), (x+.04, -.62, 1.40), .028)
    put(scene, f"leaning tool {k}", a)

# Sill cans and oil bottles.
for k in range(14):
    a = Asset(f"sill can {k}")
    x = -7.1+k*.68
    h = .14+(k%4)*.04
    color = [STEEL, (.38, .40, .35), (.47, .39, .26)][k%3]
    shaft(a, "body", (x, .79, 1.79), (x, .79, 1.79+h), .05, color)
    shaft(a, "neck", (x, .79, 1.79+h), (x, .79, 1.85+h), .018, color)
    put(scene, f"sill can {k}", a)

for k, x in enumerate((-7.8, -5.4, -2.58, .32, 3.15)):
    a = Asset(f"wall pipe {k}")
    shaft(a, "pipe", (x, .85, 1.05), (x+.10, .85, 3.9), .025, RUST)
    put(scene, f"wall pipe {k}", a)
for k in range(4):
    a = Asset(f"hanging tool {k}")
    x = -5.5+k*.22
    shaft(a, "handle", (x, .80, 2.05), (x+.02, .80, 2.48), .018, WOOD)
    block(a, "head", (.10, .035, .065), (x+.02, .80, 2.48), IRON)
    put(scene, f"hanging tool {k}", a)
a = Asset("right leaning handle")
shaft(a, "shaft", (3.30, .56, .90), (3.75, .68, 3.66), .035, WOOD)
put(scene, "right leaning handle", a)

marker = Asset("floor direction marker")
shaft(marker, "round marker", (-2.60, -2.08, .002),
      (-2.60, -2.08, .006), .26, (.34, .42, .43))
block(marker, "arrow stem", (.10, .20, .006),
      (-2.60, -2.06, .010), (.74, .76, .70))
for k in range(3):
    block(marker, f"arrowhead_{k}", (.24-k*.075, .045, .006),
          (-2.60, -2.17-k*.04, .010), (.74, .76, .70))
put(scene, "floor marker", marker)

# Source audit: no fillets or boolean constructions. All primitive dimensions
# and radii are positive; endpoints and tube samples are distinct.
# Unique include keys are checked. Composite parts stay within semantic Assets.
# No local shader edits or per-mesh material copies are needed.
realize(scene)
set_view(CAMERA, TARGET, lens=LENS, sensor=36)

world = bpy.context.scene.world
if world is None:
    world = bpy.data.worlds.new("workshop daylight")
    bpy.context.scene.world = world
world.use_nodes = True
background = world.node_tree.nodes.get("Background")
if background is None:
    background = world.node_tree.nodes.new("ShaderNodeBackground")
    output = world.node_tree.nodes.get("World Output")
    if output is None:
        output = world.node_tree.nodes.new("ShaderNodeOutputWorld")
    world.node_tree.links.new(background.outputs["Background"], output.inputs["Surface"])
background.inputs["Color"].default_value = (.64, .72, .76, 1)
background.inputs["Strength"].default_value = WORLD_STRENGTH

area_emitter((-1.8, -1.4, 5.7), power=1150, size=6,
             target=(-1, 0, 1), color=(.84, .91, 1))
area_emitter((-4, .55, 3.7), power=850, size=4,
             target=(-2, -2, 0), color=(.85, .93, 1))
area_emitter((3, -4, 4.8), power=430, size=5,
             target=(1, 0, 1), color=(1, .88, .70))

bpy.context.scene.render.resolution_x = 512
bpy.context.scene.render.resolution_y = 384
bpy.context.scene.render.resolution_percentage = 100
bpy.context.scene.view_settings.view_transform = "AgX"
