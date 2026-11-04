from sceneact import *
import bpy
import math
import random

random.seed(23)

# Visual estimates, normalized image coordinates:
# Window sill: (.08,.16) to (.87,.22); floor starts near (0,.46).
# Large wheel center (.67,.25); small wheel center (.35,.29).
# Anvil horn (.49,.36); foreground spindle (.80,.51).
# Foreground bench edge: (.49,.65) to (1,.78).
# Arbitrary world scale; obscured machine depths and window heights are uncertain.
# Inventory: architecture, four benches, three lathes, two flywheels, anvil,
# vise, open drawer, hand tools, buckets, sill equipment and wall tools.

# CAMERA — independent of object dimensions.
CAMERA = (6.5, -8.4, 5.0)
TARGET = (-1.0, .12, 1.48)
LENS = 43

# ARCHITECTURE
WALL_Y = 1.05
BENCH_Z = 1.12

# OBJECT DIMENSIONS AND POSES
BENCHES = [
    ("foreground_bench", "foreground lathe workbench", 1.65, 3.15),
    ("anvil_bench", "anvil workbench", -1.34, 2.65),
    ("rear_bench", "rear lathe bench", -3.8, 2.12),
    ("distant_bench", "distant tool bench", -6.06, 2.2),
]
LATHES = [
    ("large metal lathe", 1.83, -.08, 2.38),
    ("small rear lathe", -3.82, .03, 1.55),
    ("distant machine", -6.12, .02, 1.38),
]
FLYWHEELS = [
    ("large flywheel", .56, .37, 2.53, .57),
    ("rear flywheel", -3.14, .31, 1.99, .38),
]

# MATERIALS
wood = (.25, .20, .125)
wood_top = (.39, .33, .23)
wood_light = (.47, .39, .27)
iron = (.105, .12, .115)
iron_worn = (.25, .265, .25)
rust = (.27, .18, .105)
wall = (.49, .53, .46)
trim = (.30, .34, .30)
glass = (.77, .86, .86)

# LIGHTING
WORLD_STRENGTH = .45
LIGHTS = [
    ((-1.8, -1.4, 5.7), 1150, 6, (-1, 0, 1), (.84, .91, 1)),
    ((-4, .55, 3.7), 850, 4, (-2, -2, 0), (.85, .93, 1)),
    ((3, -4, 4.8), 430, 5, (1, 0, 1), (1, .88, .70)),
]

scene = Scene("historic metalworking workshop")

# Construction wrappers audit finite positive dimensions, endpoint separation
# and per-parent unique include keys before geometry reaches SceneAct.
def attach(parent, key, node):
    assert key not in parent.members, f"Duplicate child key: {key}"
    return parent.include(key, node)

def cube(parent, key, size, center, color):
    assert all(math.isfinite(v) and v > 0 for v in size)
    assert all(math.isfinite(v) for v in center)
    return attach(parent, key, box(size=size, center=center, color=color))

def bar(parent, key, p, q, radius=.025, color=iron):
    assert math.isfinite(radius) and radius > 0
    assert all(math.isfinite(v) for v in (*p, *q))
    assert sum((a-b)**2 for a, b in zip(p, q)) > 1e-14
    return attach(parent, key, rod(radius=radius, start=p, end=q, color=color))

def tube(parent, key, points, radius, color):
    assert math.isfinite(radius) and radius > 0
    assert len(points) >= 2
    assert all(math.isfinite(v) for p in points for v in p)
    assert all(sum((a-b)**2 for a, b in zip(p, q)) > 1e-14
               for p, q in zip(points, points[1:]))
    return attach(parent, key, sweep_tube(points=points, radius=radius, color=color))

def ring(parent, key, center, radius, thickness, color, plane="xz", n=48):
    assert radius > 0 and thickness > 0
    x, y, z = center
    points = []
    for k in range(n + 1):
        t = 2 * math.pi * k / n
        if plane == "xz":
            points.append((x + radius*math.cos(t), y, z + radius*math.sin(t)))
        elif plane == "yz":
            points.append((x, y + radius*math.cos(t), z + radius*math.sin(t)))
        else:
            points.append((x + radius*math.cos(t), y + radius*math.sin(t), z))
    return tube(parent, key, points, thickness, color)

architecture = Asset("room architecture")
for j in range(35):
    y = -6 + j*.225
    for i in range(5):
        x = -9 + i*3.4 + (j % 2)*1.1
        c = random.uniform(.77, 1.12)
        cube(architecture, f"floor_board_{j}_{i}", (3.385, .216, .075),
             (x, y, -.042), tuple(v*c for v in (.43, .35, .235)))
        for end in (-1, 1):
            if random.random() < .45:
                bar(architecture, f"nail_{j}_{i}_{end}",
                    (x + end*1.61, y-.065, -.001),
                    (x + end*1.61, y-.065, .004), .007, iron)

cube(architecture, "plaster below windows", (13, .17, 1.7),
     (-2, WALL_Y, .85), wall)
cube(architecture, "upper wall", (13, .17, .45),
     (-2, WALL_Y, 4.15), wall)
for i, x in enumerate((-8.1, -5.3, -2.5, .3, 3.1)):
    cube(architecture, f"window_pier_{i}", (.36, .19, 2.1),
         (x, WALL_Y, 2.75), wall)

for i, x in enumerate((-6.7, -3.9, -1.1, 1.7)):
    w = 2.38
    cube(architecture, f"window_glass_{i}", (w, .045, 2.04),
         (x, WALL_Y+.035, 2.76), glass)
    cube(architecture, f"window_sill_{i}", (w+.32, .42, .105),
         (x, .88, 1.73), trim)
    for j, dx in enumerate((-w/2, 0, w/2)):
        cube(architecture, f"window_vertical_{i}_{j}", (.055, .10, 2.08),
             (x+dx, .95, 2.77), trim)
    for j, z in enumerate((1.77, 2.65, 3.77)):
        cube(architecture, f"window_cross_{i}_{j}", (w, .10, .055),
             (x, .95, z), trim)
    for k in range(4):
        cube(architecture, f"outside_{i}_{k}", (.12, .06, .55),
             (x-.83+k*.51, 1.09, 3.18), (.68, .73, .72))

cube(architecture, "left masonry end", (.22, 5, 4.5),
     (-8.35, -1.25, 2.2), (.48, .48, .41))
attach(scene, "architecture", architecture)

# Bench legs reach z=0; slabs support machines at approximately z=1.20.
def bench(name, x, length, width=1.15):
    a = Asset(name)
    for k in range(5):
        c = random.uniform(.85, 1.1)
        cube(a, f"top_plank_{k}", (length, width/5-.008, .15),
             (x, -.02-width/2+(k+.5)*width/5, BENCH_Z),
             tuple(v*c for v in wood_top))
    cube(a, "front_apron", (length, .13, .26), (x, -.59, .91), wood)
    for i, dx in enumerate((-length/2+.18, length/2-.18)):
        for j, y in enumerate((-.47, .40)):
            cube(a, f"leg_{i}_{j}", (.15, .17, 1.01),
                 (x+dx, y, .505), wood)
        cube(a, f"foot_cross_{i}", (.20, 1.12, .12),
             (x+dx, -.03, .12), wood)
    cube(a, "low_stretcher", (length-.25, .10, .14), (x, .25, .30), wood)
    for k in range(21):
        xx = x + random.uniform(-length*.47, length*.47)
        yy = random.uniform(-.53, .49)
        cube(a, f"surface_scuff_{k}", (random.uniform(.03, .25), .009, .003),
             (xx, yy, 1.197), (.18, .16, .11))
    return a

for key, name, x, length in BENCHES:
    attach(scene, key, bench(name, x, length))

def lathe(name, x, y, length):
    a = Asset(name)
    z = 1.23
    for i, dx in enumerate((-length*.38, length*.38)):
        cube(a, f"foot_{i}", (.36, .48, .09), (x+dx, y, z), iron)
        for j, side in enumerate((-1, 1)):
            bar(a, f"support_{i}_{j}", (x+dx, y+side*.20, z+.03),
                (x+dx, y+side*.10, z+.36), .065, iron)
        cube(a, f"bracket_{i}", (.26, .38, .17), (x+dx, y, z+.29), iron)
    for i, yy in enumerate((-.14, .14)):
        cube(a, f"bed_rail_{i}", (length, .095, .13),
             (x, y+yy, z+.39), iron_worn)
    cube(a, "headstock", (.41, .42, .30),
         (x+length*.29, y, z+.59), iron)
    bar(a, "long_spindle", (x-length*.46, y, z+.69),
        (x+length*.57, y, z+.69), .063, iron_worn)
    for k in range(3):
        bar(a, f"pulley_{k}", (x+length*.11+k*.055, y, z+.69),
            (x+length*.14+k*.055, y, z+.69), .14-k*.016, iron)
    cube(a, "tailstock", (.30, .32, .24),
         (x-length*.35, y, z+.58), iron)
    bar(a, "tailstock_screw", (x-length*.59, y, z+.69),
        (x-length*.30, y, z+.69), .035, iron_worn)
    ring(a, "tailstock_handwheel", (x-length*.59, y, z+.69),
         .12, .018, iron_worn, "yz", 24)
    cube(a, "tool_slide", (.40, .46, .065),
         (x-.12, y-.06, z+.50), iron_worn)
    bar(a, "toolpost", (x-.12, y-.12, z+.50),
        (x-.12, y-.12, z+.82), .033, iron)
    bar(a, "tool_handle", (x-.26, y-.12, z+.79),
        (x+.02, y-.12, z+.85), .022, iron)
    bar(a, "feed_screw", (x-length*.44, y-.23, z+.35),
        (x+length*.43, y-.23, z+.35), .025, iron_worn)
    ring(a, "feed_wheel", (x+.14, y-.28, z+.36),
         .10, .018, iron, "xz", 24)
    return a

for name, x, y, length in LATHES:
    attach(scene, name, lathe(name, x, y, length))

def flywheel(name, x, y, z, r):
    a = Asset(name)
    cube(a, "pillar_foot", (.48, .43, .09), (x, y, 1.24), iron)
    for i, sx in enumerate((-1, 1)):
        bar(a, f"upright_{i}", (x+sx*.17, y, 1.27),
            (x+sx*.065, y, z-.05), .045, iron)
    bar(a, "bearing_axle", (x, y-.15, z), (x, y+.17, z), .075, iron_worn)
    ring(a, "outer_rim", (x, y, z), r, .046, iron)
    ring(a, "inner_rim", (x, y-.008, z), r-.075, .019, iron_worn)
    for k in range(6):
        t = k*math.pi/3
        points = []
        for j in range(8):
            f = j/7
            rr = .08+(r-.12)*f
            angle = t+.42*math.sin(f*math.pi)
            points.append((x+rr*math.cos(angle), y, z+rr*math.sin(angle)))
        tube(a, f"curved_spoke_{k}", points, .035, iron)
    bar(a, "hub", (x, y-.10, z), (x, y+.12, z), .115, iron)
    bar(a, "crank", (x, y-.14, z), (x+.20, y-.14, z-.18), .025, iron_worn)
    bar(a, "crank_grip", (x+.20, y-.14, z-.18),
        (x+.20, y-.33, z-.18), .033, wood)
    for i, side in enumerate((-1, 1)):
        bar(a, f"belt_{i}", (x+side*r*.86, y+.07, z-r*.47),
            (x+side*.13, y+.07, 1.36), .012, (.19, .14, .085))
    return a

for name, x, y, z, radius in FLYWHEELS:
    attach(scene, name, flywheel(name, x, y, z, radius))

# The anvil Asset includes its support block and every horn segment.
anvil = Asset("large anvil")
cube(anvil, "oak support block", (.66, .68, .22),
     (-1.27, -.03, 1.29), (.28, .22, .14))
cube(anvil, "wide base", (.76, .48, .11), (-1.25, -.02, 1.45), rust)
cube(anvil, "lower waist", (.39, .31, .22), (-1.27, -.02, 1.59), rust)
cube(anvil, "upper shoulder", (.58, .39, .22), (-1.27, -.02, 1.77), rust)
cube(anvil, "flat striking face", (.88, .44, .12),
     (-1.24, -.02, 1.92), (.32, .30, .24))
for k in range(8):
    xx = -.80+k*.068
    bar(anvil, f"horn_segment_{k}", (xx, -.02, 1.90),
        (xx+.075, -.02, 1.90), .155*(1-k/8)+.008, rust)
cube(anvil, "square heel", (.28, .42, .13), (-1.77, -.02, 1.91), rust)
attach(scene, "anvil", anvil)

vise = Asset("foreground bench vise")
cube(vise, "mount", (.43, .34, .10), (.06, -.55, 1.24), iron)
cube(vise, "fixed jaw", (.36, .12, .26), (.06, -.65, 1.35), iron_worn)
cube(vise, "moving jaw", (.36, .13, .22), (.06, -.88, 1.32), iron)
bar(vise, "screw", (.06, -.55, 1.24), (.06, -1.04, 1.24), .045, iron_worn)
bar(vise, "handle", (.06, -1.04, .98), (.06, -1.04, 1.48), .018, iron_worn)
for i, z in enumerate((.98, 1.48)):
    attach(vise, f"handle_ball_{i}", ball(radius=.035,
           center=(.06, -1.04, z), color=iron_worn))
attach(scene, "bench vise", vise)

drawer = Asset("open wooden drawer")
cube(drawer, "bottom", (.90, .66, .055), (1.02, -.94, .77), wood)
cube(drawer, "front", (.97, .07, .27),
     (1.02, -1.24, .87), (.24, .21, .15))
for i, x in enumerate((.56, 1.48)):
    cube(drawer, f"side_{i}", (.055, .65, .22), (x, -.94, .86), wood)
bar(drawer, "round pull", (1.02, -1.30, .88),
    (1.02, -1.35, .88), .045, rust)
attach(scene, "open drawer", drawer)

# Each hand tool and each paper remains its own movable semantic Asset.
for k in range(11):
    a = Asset(f"foreground hand tool {k}")
    x = random.uniform(.2, 2.55)
    y = random.uniform(-.48, .25)
    length = random.uniform(.20, .48)
    bar(a, "steel shaft", (x, y, 1.215),
        (x+length, y+.035, 1.215), .016, iron_worn)
    if k % 3 == 0:
        bar(a, "wood handle", (x-.13, y, 1.22), (x, y, 1.22), .027, wood_light)
    attach(scene, f"foreground_tool_{k}", a)

for k, (x, y) in enumerate(((1.35, -.32), (2.80, -.24), (.85, -.12))):
    a = Asset(f"paper sheet {k}")
    cube(a, "sheet", (.43, .32, .008), (x, y, 1.21), (.72, .70, .61))
    for j in range(3):
        bar(a, f"mark_{j}", (x-.12, y-.08+j*.07, 1.217),
            (x+.07, y-.08+j*.07, 1.217), .003, (.30, .31, .28))
    a.turn('z', (-12, 8, 20)[k], pivot=(x, y, 1.21))
    attach(scene, f"paper_{k}", a)

for k in range(8):
    a = Asset(f"anvil hand tool {k}")
    x = -2.45+random.random()*1.30
    y = -.43+random.random()*.80
    bar(a, "steel shaft", (x, y, 1.214),
        (x+.29, y+.07, 1.214), .021, iron_worn)
    attach(scene, f"anvil_tool_{k}", a)

for k in range(5):
    a = Asset(f"rear wooden stock {k}")
    cube(a, "stock", (.72, .055, .045),
         (-4.0, -.39+k*.09, 1.23+k*.015), wood_light)
    attach(scene, f"rear_wood_stock_{k}", a)

def bucket(name, x, y, r, h, color):
    a = Asset(name)
    for j in range(28):
        t = 2*math.pi*j/28
        p = (x+r*math.cos(t), y+r*math.sin(t), h/2)
        panel = cube(a, f"wall_panel_{j}",
                     (2*r*math.sin(math.pi/28)*1.03, .035, h), p, color)
        panel.turn('z', math.degrees(t)+90, pivot=p)
    cube(a, "dark interior", (.40, .40, .025),
         (x, y, .09), (.075, .068, .045))
    ring(a, "upper rim", (x, y, h), r, .018, iron_worn, "xy")
    ring(a, "lower band", (x, y, .08), r, .015, iron, "xy")
    points = [(x+r*math.cos(math.pi*j/16), y,
               h+.30*math.sin(math.pi*j/16)) for j in range(17)]
    tube(a, "arched_handle", points, .012, iron)
    return a

attach(scene, "cream bucket",
       bucket("cream bucket", 1.73, -.44, .31, .62, (.55, .54, .41)))
attach(scene, "green foreground drum",
       bucket("green foreground drum", 3.03, -.40, .40, .79, (.20, .25, .15)))
attach(scene, "rear waste bin",
       bucket("rear waste bin", -3.0, .07, .24, .56, (.26, .29, .23)))

for k in range(5):
    a = Asset(f"long leaning tool {k}")
    x = -.36+k*.095
    bar(a, "shaft", (x, -.76, .08), (x+.04, -.62, 1.30), .018, wood)
    bar(a, "metal tip", (x+.04, -.62, 1.22),
        (x+.04, -.62, 1.40), .029, iron)
    attach(scene, f"leaning_rod_{k}", a)

for k in range(23):
    a = Asset(f"sill container {k}")
    x = -7.2+k*.43+random.uniform(-.09, .09)
    y = .79
    h = random.uniform(.12, .30)
    c = random.choice([iron_worn, (.38, .40, .35),
                       (.47, .39, .26), (.22, .28, .25)])
    bar(a, "body", (x, y, 1.80), (x, y, 1.80+h),
        random.uniform(.035, .065), c)
    bar(a, "neck", (x, y, 1.80+h), (x, y, 1.86+h), .020, c)
    if k % 4 == 0:
        bar(a, "oil spout", (x, y, 1.80+h),
            (x+.12, y, 1.93+h), .009, iron_worn)
    attach(scene, f"sill_container_{k}", a)

for k, x in enumerate((-7.8, -5.4, -2.58, .32, 3.15)):
    a = Asset(f"wall pipe {k}")
    bar(a, "vertical pipe", (x, .85, 1.05), (x+.10, .85, 3.9), .025, rust)
    for j, z in enumerate((1.48, 2.80)):
        cube(a, f"clip_{j}", (.12, .05, .055), (x+.03, .82, z), iron)
    attach(scene, f"wall_pipe_{k}", a)

for k in range(7):
    a = Asset(f"hanging wall tool {k}")
    x = -5.5+k*.16
    bar(a, "handle", (x, .80, 2.05), (x+.02, .80, 2.43), .015, wood)
    ring(a, "loop", (x, .80, 2.49), .049, .009, iron, "xz", 20)
    attach(scene, f"wall_tool_{k}", a)

a = Asset("right leaning handle")
bar(a, "shaft", (3.30, .56, .90), (3.75, .68, 3.66), .035, wood)
attach(scene, "right leaning handle", a)

marker = Asset("floor direction marker")
for j in range(15):
    yy = -2.08+(j-7)*.035
    width = .43*math.sqrt(max(.02, 1-((j-7)/7.4)**2))
    cube(marker, f"oval_strip_{j}", (width, .039, .004),
         (-2.60, yy, .004), (.34, .42, .43))
cube(marker, "arrow_stem", (.105, .21, .007),
     (-2.60, -2.08, .009), (.74, .76, .70))
for j in range(5):
    cube(marker, f"arrow_head_{j}", (.25-j*.044, .035, .007),
         (-2.60, -2.19-j*.027, .009), (.74, .76, .70))
attach(scene, "floor marker", marker)

# Source audit only: no fillet_box constructions; positive sizes/radii and
# distinct consecutive endpoints are checked above. Include keys are checked.
# Composite parts share Assets. No image-quality or execution claims are made.
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

for position, power, size, target, color in LIGHTS:
    area_emitter(position, power=power, size=size, target=target, color=color)

# Resolve material targets through their named SceneAct parent subtrees.
# Copy each material slot before changing it, preserving material isolation.
def descendant_meshes(parent):
    meshes = []
    stack = [parent]
    while stack:
        obj = stack.pop()
        if obj.type == 'MESH':
            meshes.append(obj)
        stack.extend(obj.children)
    return meshes

for key in scene.members:
    parent = bpy.data.objects.get(key)
    assert parent is not None, f"Missing realized parent: {key}"
    meshes = descendant_meshes(parent)
    assert meshes, f"Empty realized subtree: {key}"
    for obj in meshes:
        for slot in obj.material_slots:
            if slot.material is None:
                continue
            local_material = slot.material.copy()
            slot.material = local_material
            if local_material.use_nodes:
                shader = local_material.node_tree.nodes.get("Principled BSDF")
                if shader is not None:
                    shader.inputs["Roughness"].default_value = .78

scene_bpy = bpy.context.scene
scene_bpy.render.resolution_x = 512
scene_bpy.render.resolution_y = 384
scene_bpy.render.resolution_percentage = 100
scene_bpy.view_settings.view_transform = 'AgX'
