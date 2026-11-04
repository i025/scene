from sceneact import *
import bpy
import math
import random

random.seed(19)

# Visual estimates, normalized image coordinates:
# back upper shelf: (.18,.34) to (.78,.34)
# right upper shelf cropped at (1,.25)
# middle shelf left end: (.18,.56)
# workbench rear edge: (.20,.73)
# foreground nail bowl: (.66,.90)
# left window edge: (.075,.39)
# Arbitrary world scale; room depth and camera height remain uncertain.
# Inventory: plaster walls, window, shelves, planes, wall squares, dividers,
# saws, mallets, chisel racks, bench, vise, kettle, bottle, nail bowl, brace.
# Each semantic object owns its complete geometry. Shelf and bench objects
# use explicit support heights. No rendering or edit results are available.

# CAMERA PARAMETERS — independent of object dimensions.
CAMERA = (0.05, -5.6, 2.85)
LOOK_AT = (0.0, 1.1, 2.12)
LENS = 30

# ARCHITECTURE PARAMETERS
BACK = 2.45
LEFT, RIGHT = -2.8, 2.65
LEVELS = [1.05, 1.65, 2.23, 2.86]
BENCH_Z = .91

# OBJECT DIMENSIONS AND POSES
BENCH_SIZE = (4.5, 2.0, .15)
BENCH_CENTER = (-.18, -1.55, BENCH_Z - .075)

# MATERIAL PARAMETERS
plaster = (.71, .73, .68)
wood = (.37, .19, .073)
honey = (.56, .31, .11)
edgewood = (.65, .39, .16)
darkwood = (.20, .105, .047)
iron = (.105, .12, .115)
steel = (.35, .38, .36)
black = (.055, .065, .061)

# LIGHTING PARAMETERS
WORLD_STRENGTH = .65

scene = Scene('Antique woodworking workshop')

# Source guards: unique child keys, finite positive dimensions, and
# distinct rod/tube endpoints. No fillet_box constructions are used.
def finite_point(p):
    assert len(p) == 3 and all(math.isfinite(float(v)) for v in p)

def positive(v):
    assert math.isfinite(float(v)) and v > 0

def add(parent, key, node):
    assert key not in parent.members, "Duplicate include key: " + key
    return parent.include(key, node)

def B(parent, key, size, center, color):
    for v in size:
        positive(v)
    finite_point(center)
    return add(parent, key, box(size=size, center=center, color=color))

def R(parent, key, a, b, r, color):
    positive(r)
    finite_point(a)
    finite_point(b)
    assert sum((a[i] - b[i]) ** 2 for i in range(3)) > 1e-14
    return add(parent, key, rod(radius=r, start=a, end=b, color=color))

def S(parent, key, radius, center, color):
    positive(radius)
    finite_point(center)
    return add(parent, key, ball(radius=radius, center=center, color=color))

def line(parent, key, pts, r, color):
    positive(r)
    assert len(pts) >= 2
    for p in pts:
        finite_point(p)
    for a, b in zip(pts, pts[1:]):
        assert sum((a[i] - b[i]) ** 2 for i in range(3)) > 1e-14
    return add(parent, key, sweep_tube(points=pts, radius=r, color=color))

def woodcolor():
    f = random.uniform(.72, 1.25)
    return tuple(min(1, c * f) for c in wood)

room = Asset('Plastered room')
B(room, 'back wall', (5.7,.13,4.7), (0,BACK+.15,2.23), plaster)
B(room, 'right wall', (.13,6.5,4.7), (RIGHT+.17,-.55,2.23), (.68,.70,.65))
B(room, 'left wall', (.13,6.5,4.7), (LEFT-.15,-.55,2.23), (.73,.75,.70))
B(room, 'floor', (6,8,.12), (0,-.7,-.08), (.31,.28,.21))
add(scene, 'room', room)

window = Asset('Tall left window')
B(window, 'blue glass', (.035,1.55,2.9), (LEFT+.015,.12,2.55), (.30,.52,.61))
for i, y in enumerate([-.69,.12,.93]):
    B(window, 'jamb_%d' % i, (.11,.065,3.05), (LEFT+.09,y,2.55), (.20,.24,.22))
for i, z in enumerate([1.03,2.05,3.05,4.07]):
    B(window, 'cross_%d' % i, (.12,1.7,.055), (LEFT+.10,.12,z), (.72,.74,.66))
add(scene, 'window', window)

# Each shelf owns its boards, front trim, and supporting brackets.
for i, z in enumerate(LEVELS):
    shelf = Asset('Continuous shelf %d' % i)
    B(shelf, 'back board', (5.38,.48,.075), (-.05,BACK-.26,z), edgewood)
    B(shelf, 'front worn lip', (5.4,.035,.045), (-.05,BACK-.51,z+.008), honey)
    B(shelf, 'right return', (.48,3.1,.075), (RIGHT-.23,.66,z), edgewood)
    B(shelf, 'left return', (.38,2.6,.065), (LEFT+.17,.97,z), honey)
    for j, x in enumerate([-2.5,-1.3,.1,1.5,2.4]):
        R(shelf, 'back bracket %d' % j,
          (x,BACK-.015,z-.37), (x,BACK-.43,z-.055), .017, iron)
    for j, y in enumerate([-.65,.45,1.6]):
        R(shelf, 'side bracket %d' % j,
          (RIGHT-.015,y,z-.34), (RIGHT-.43,y,z-.055), .018, iron)
    add(scene, 'shelf %d' % i, shelf)

def plane(name, position, length=.42, width=.13, height=.13,
          angle=0, metal=False):
    for v in (length, width, height):
        positive(v)
    p = Asset(name)
    c = black if metal else woodcolor()
    B(p, 'sole', (length,width,.025), (0,0,.014),
      steel if metal else darkwood)
    B(p, 'body', (length,width,height), (0,0,height/2+.025), c)
    blade = B(p, 'sloping iron', (.085,width*.79,.13),
              (length*.02,0,height+.045), steel)
    blade.turn('y', -27)
    wedge = B(p, 'wooden wedge', (.08,width*.65,.10),
              (-length*.07,0,height+.045), darkwood)
    wedge.turn('y', -25)
    if length > .34:
        line(p, 'rear tote',
             [(-length*.32,0,height),
              (-length*.38,0,height+.12),
              (-length*.30,0,height+.20),
              (-length*.20,0,height+.19),
              (-length*.17,0,height+.07)], .025, darkwood)
        R(p, 'front knob stem', (length*.30,0,height),
          (length*.30,0,height+.065), .022, darkwood)
        S(p, 'front knob', .034, (length*.30,0,height+.07), darkwood)
    for k in range(2):
        B(p, 'body grain %d' % k, (length*.86,.004,.006),
          (0,-width/2-.001,.055+k*.035), tuple(v*.70 for v in c))
    # Complete the composite before rotating and positioning it.
    p.turn('z', angle, pivot=(0,0,0))
    p.move(position)
    add(scene, name, p)

for i in range(39):
    x = -2.58 + i*.132
    h = random.uniform(.17,.32)
    p = Asset('Upright moulding plane %02d' % i)
    c = woodcolor()
    B(p, 'wood stock', (.095,.27,h), (x,BACK-.28,LEVELS[3]+.04+h/2), c)
    B(p, 'raised toe', (.07,.07,.10), (x,BACK-.39,LEVELS[3]+h+.05), c)
    blade = B(p, 'blade', (.045,.025,h*.65),
              (x,BACK-.20,LEVELS[3]+h+.035), steel)
    blade.turn('x', -12)
    B(p, 'side stripe', (.009,.275,h*.8),
      (x-.027,BACK-.28,LEVELS[3]+h*.5+.045), darkwood)
    add(scene, 'moulding plane %02d' % i, p)

for level, count in [(0,12),(1,13),(2,13)]:
    for i in range(count):
        x = -2.45 + i*(4.92/(count-1))
        plane('Back shelf %d plane %02d' % (level,i),
              (x,BACK-.29,LEVELS[level]+.04),
              random.uniform(.30,.48), random.uniform(.11,.18),
              random.uniform(.085,.16), random.uniform(-7,7),
              metal=(level == 1 and i % 3 == 0) or
                    (level == 2 and i % 4 == 0))

for level in range(4):
    for i in range(7):
        y = -.70 + i*.43
        plane('Right shelf %d plane %d' % (level,i),
              (RIGHT-.25,y,LEVELS[level]+.04),
              random.uniform(.34,.52), random.uniform(.13,.21),
              random.uniform(.13,.25), 90+random.uniform(-5,5),
              metal=(level < 2 and i % 3 == 0))

for level in [1,2,3]:
    for i in range(6):
        plane('Left shelf %d plane %d' % (level,i),
              (LEFT+.21,-.18+i*.43,LEVELS[level]+.04),
              .32,.12,.14,90,False)

def square(name, cx, cz, span, ang, color):
    a = Asset(name)
    B(a, 'long arm', (.075,.042,span), (0,0,span/2), color)
    B(a, 'short arm', (span*.74,.042,.075), (span*.37,0,.035), color)
    B(a, 'long polished edge', (.012,.047,span*.94),
      (.022,-.005,span/2), steel)
    a.turn('y', ang, pivot=(0,0,0))
    a.move((cx,BACK-.025,cz))
    add(scene, name, a)

square('Largest diagonal framing square', -1.17,3.31,1.52,-43,black)
square('Nested framing square', -1.00,3.39,1.12,-43,iron)
square('Small diagonal framing square', -.78,3.47,.76,-43,black)
square('Upright framing square', .15,3.31,1.06,0,black)
square('Narrow try square', .57,3.34,.76,15,iron)

for j, (x,h) in enumerate([(1.04,.92),(1.30,.61),(1.52,.36)]):
    a = Asset('Wall dividers %d' % j)
    z = 3.45
    R(a, 'left leg', (x-.18,BACK-.06,z), (x,BACK-.06,z+h), .016, darkwood)
    R(a, 'right leg', (x+.18,BACK-.06,z), (x,BACK-.06,z+h), .016, darkwood)
    S(a, 'pivot', .032, (x,BACK-.06,z+h), steel)
    add(scene, 'wall dividers %d' % j, a)

for j, x in enumerate([1.92,2.30]):
    a = Asset('Wall mallet %d' % j)
    B(a, 'handle', (.055,.055,.75), (x,BACK-.10,3.69), wood)
    B(a, 'head', (.34,.13,.13),
      (x,BACK-.10,3.93 if j == 0 else 3.47),
      darkwood if j == 0 else black)
    add(scene, 'wall mallet %d' % j, a)

saw = Asset('High wall handsaw')
blade = B(saw, 'wide steel blade', (.9,.035,.16),
          (-2.22,BACK-.06,4.34), iron)
blade.turn('y', 25)
line(saw, 'wood grip',
     [(-2.75,BACK-.08,4.56),(-2.9,BACK-.08,4.68),
      (-2.98,BACK-.08,4.53),(-2.79,BACK-.08,4.42)], .045, darkwood)
add(scene, 'wall saw', saw)

for row, z in enumerate([1.72,2.53,3.43]):
    rack = Asset('Window tool rack %d' % row)
    B(rack, 'rack rail', (.13,2.5,.065), (LEFT+.19,.51,z), honey)
    for i in range(10):
        y = -.58 + i*.245
        hh = random.uniform(.21,.39)
        R(rack, 'chisel blade %d' % i,
          (LEFT+.23,y,z-.05), (LEFT+.23,y,z+hh*.40), .014, steel)
        R(rack, 'wood handle %d' % i,
          (LEFT+.23,y,z+hh*.40), (LEFT+.23,y,z+hh), .034, woodcolor())
    add(scene, 'window rack %d' % row, rack)

for i in range(13):
    label = Asset('Shelf label %d' % i)
    x = -2.45 + i*.40
    B(label, 'cream card', (.13,.008,.035),
      (x,BACK-.535,1.06), (.83,.79,.61))
    B(label, 'faded ink', (.072,.009,.006),
      (x,BACK-.542,1.06), (.28,.27,.20))
    add(scene, 'shelf label %d' % i, label)

book = Asset('Yellow booklet')
B(book, 'cover', (.24,.035,.31), (0,0,0), (.84,.58,.13))
for k in range(4):
    B(book, 'printed line %d' % k, (.13,.008,.009),
      (0,-.027,.04+k*.026), darkwood)
book.turn('y', 12, pivot=(0,0,0))
book.move((-1.57,BACK-.25,3.11))
add(scene, 'booklet', book)

bench = Asset('Crowded foreground workbench')
B(bench, 'thick top', BENCH_SIZE, BENCH_CENTER, (.36,.245,.125))
for i in range(8):
    B(bench, 'top plank seam %d' % i, (4.46,.012,.006),
      (-.18,-2.43+i*.25,BENCH_Z+.003), darkwood)
for i, x in enumerate([-2.12,1.69]):
    for j, y in enumerate([-2.25,-.89]):
        B(bench, 'leg %d %d' % (i,j), (.16,.18,.83), (x,y,.415), wood)
B(bench, 'front apron', (4.45,.12,.26), (-.18,-2.48,.69), darkwood)
add(scene, 'bench', bench)

vise = Asset('Large wooden bench vise')
B(vise, 'rear jaw', (.81,.15,.38), (.37,-.70,1.08), wood)
B(vise, 'front jaw', (.86,.17,.34), (.37,-1.01,1.06), honey)
for i, x in enumerate([.12,.64]):
    R(vise, 'wood screw %d' % i,
      (x,-.70,1.04), (x,-1.20,1.04), .052, darkwood)
R(vise, 'cross handle', (.64,-1.23,.88), (.64,-1.23,1.28), .025, wood)
add(scene, 'vise', vise)

for i in range(10):
    plane('Bench plane %d' % i,
          (random.uniform(-1.9,1.7),random.uniform(-2.18,-.93),BENCH_Z+.012),
          random.uniform(.30,.69), random.uniform(.12,.21),
          random.uniform(.08,.17), random.uniform(-35,35), i % 3 == 0)

# Saw blade, teeth, and handle use the same local frame and move together.
for i in range(5):
    a = Asset('Foreground handsaw %d' % i)
    x = -1.95 + i*.27
    z = BENCH_Z+.08+i*.013
    B(a, 'steel blade', (.15,.83,.018), (0,0,0), (.40,.42,.38))
    line(a, 'wooden grip',
         [(-.045,.44,.03),(-.09,.63,.05),
          (.06,.71,.05),(.10,.48,.03)], .032, honey)
    for j in range(9):
        B(a, 'saw tooth %d' % j, (.025,.025,.018),
          (.085,-.36+j*.07,0), steel)
    a.turn('z', -13+i*6, pivot=(0,0,0))
    a.move((x,-1.94,z))
    add(scene, 'foreground saw %d' % i, a)

def chisel(name, x, y, length, angle):
    a = Asset(name)
    R(a, 'steel shaft', (0,-length*.5,.024),
      (0,length*.18,.024), .013, steel)
    B(a, 'flat cutting end', (.055,.13,.014),
      (0,-length*.50,.022), steel)
    R(a, 'wood handle', (0,length*.17,.027),
      (0,length*.48,.027), .033, honey)
    a.turn('z', angle, pivot=(0,0,0))
    a.move((x,y,BENCH_Z+.04))
    add(scene, name, a)

for i in range(13):
    chisel('Loose bench chisel %d' % i,
           random.uniform(-1.9,1.7), random.uniform(-2.43,-1.1),
           random.uniform(.36,.67), random.uniform(-90,90))

mallet = Asset('Foreground wooden mallet')
R(mallet, 'long handle', (.75,-2.40,1.02), (1.55,-1.65,1.02), .035, honey)
head = B(mallet, 'block head', (.37,.16,.18), (1.48,-1.70,1.05), edgewood)
head.turn('z', -37)
add(scene, 'foreground mallet', mallet)

kettle = Asset('Black metal kettle')
body = S(kettle, 'rounded body', .19, (-.92,-1.02,1.12), black)
body.resize((1,1,.87))
R(kettle, 'lid', (-.92,-1.02,1.27), (-.92,-1.02,1.29), .15, iron)
S(kettle, 'lid knob', .032, (-.92,-1.02,1.32), darkwood)
line(kettle, 'arched handle',
     [(-1.08,-1.02,1.20),(-1.09,-1.02,1.47),
      (-.94,-1.02,1.55),(-.77,-1.02,1.43),(-.76,-1.02,1.20)], .017, steel)
line(kettle, 'spout',
     [(-.77,-1.02,1.13),(-.64,-1.02,1.23),(-.63,-1.02,1.31)], .039, iron)
add(scene, 'kettle', kettle)

bottle = Asset('Cloudy bottle')
R(bottle, 'body', (-.31,-1.24,.94), (-.31,-1.24,1.30), .085, (.48,.50,.40))
S(bottle, 'shoulder', .082, (-.31,-1.24,1.29), (.48,.50,.40))
R(bottle, 'neck', (-.31,-1.24,1.30), (-.31,-1.24,1.43), .035, (.53,.55,.44))
R(bottle, 'cork', (-.31,-1.24,1.43), (-.31,-1.24,1.47), .038, honey)
B(bottle, 'paper label', (.13,.009,.14), (-.31,-1.325,1.12), (.71,.68,.53))
add(scene, 'bottle', bottle)

bowl = Asset('Bowl filled with nails')
cx, cy = .67, -2.01
R(bowl, 'base', (cx,cy,.935), (cx,cy,.963), .18, iron)
for i in range(24):
    t = 2*math.pi*i/24
    u = 2*math.pi*(i+1)/24
    a = (cx+.18*math.cos(t),cy+.18*math.sin(t),.955)
    b = (cx+.29*math.cos(t),cy+.29*math.sin(t),1.13)
    c = (cx+.29*math.cos(u),cy+.29*math.sin(u),1.13)
    R(bowl, 'sloping side %d' % i, a, b, .034, iron)
    R(bowl, 'rim %d' % i, b, c, .018, steel)
for i in range(65):
    x = cx+random.uniform(-.19,.19)
    y = cy+random.uniform(-.18,.18)
    z = random.uniform(1.00,1.12)
    angle = random.uniform(0,math.pi*2)
    end = (x+.11*math.cos(angle),y+.11*math.sin(angle),
           z+random.uniform(-.015,.025))
    R(bowl, 'nail %d' % i, (x,y,z), end, .0045, steel)
    S(bowl, 'nail head %d' % i, .011, (x,y,z), steel)
add(scene, 'nail bowl', bowl)

drill = Asset('Iron brace drill')
line(drill, 'crank',
     [(2.29,.08,1.17),(2.29,.08,1.43),(2.02,.08,1.43),
      (2.02,.08,1.64),(2.29,.08,1.64),(2.29,.08,1.84)], .024, iron)
R(drill, 'wood grip', (2.01,.08,1.45), (2.01,.08,1.61), .053, darkwood)
knob = S(drill, 'top palm knob', .095, (2.29,.08,1.84), darkwood)
knob.resize((1,1,.5))
add(scene, 'brace drill', drill)

# Realize clears Blender; all Blender scene settings follow this call.
realize(scene)
set_view(CAMERA, LOOK_AT, lens=LENS)

world = bpy.context.scene.world
if world is None:
    world = bpy.data.worlds.new('Workshop daylight')
    bpy.context.scene.world = world
world.use_nodes = True
background = world.node_tree.nodes.get('Background')
if background is None:
    background = world.node_tree.nodes.new('ShaderNodeBackground')
    output = world.node_tree.nodes.get('World Output')
    if output is None:
        output = world.node_tree.nodes.new('ShaderNodeOutputWorld')
    world.node_tree.links.new(background.outputs['Background'], output.inputs['Surface'])
background.inputs['Color'].default_value = (.75,.82,.85,1)
background.inputs['Strength'].default_value = WORLD_STRENGTH

area_emitter((-3,-.7,3.5), power=750, size=3.0,
             target=(0,.8,1.5), color=(.77,.88,1.0))
area_emitter((0,-2,4.5), power=550, size=4,
             target=(0,1.5,1.8), color=(1,.91,.77))
area_emitter((1.7,1,4.4), power=180, size=2,
             target=(0,1,2), color=(1,.96,.87))

# Resolve every material target through its exact named Asset parent.
# Copy each material before modifying it to preserve local isolation.
def descendant_meshes(root):
    found = []
    stack = [root]
    while stack:
        obj = stack.pop()
        if obj.type == 'MESH':
            found.append(obj)
        stack.extend(obj.children)
    return found

for asset_key in scene.members:
    parent = bpy.data.objects.get(asset_key)
    assert parent is not None, "Missing realized Asset parent: " + asset_key
    meshes = descendant_meshes(parent)
    assert meshes, "Empty realized Asset subtree: " + asset_key
    for obj in meshes:
        for slot in obj.material_slots:
            if slot.material is None:
                continue
            local_material = slot.material.copy()
            slot.material = local_material
            if local_material.use_nodes:
                bsdf = local_material.node_tree.nodes.get('Principled BSDF')
                if bsdf is not None:
                    bsdf.inputs['Roughness'].default_value = .76

bpy.context.scene.render.resolution_x = 512
bpy.context.scene.render.resolution_y = 384
bpy.context.scene.render.resolution_percentage = 100
bpy.context.scene.view_settings.view_transform = 'AgX'
