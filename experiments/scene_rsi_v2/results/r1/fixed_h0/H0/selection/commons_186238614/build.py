from sceneact import *
import bpy, math, random

random.seed(21)
scene = Scene("Daylit office")
green = (.43, .47, .035)
metal = (.43, .46, .45)

def add(name, node):
    scene.include(name, node)
    return node

def bx(name, size, center, color):
    return add(name, box(size=size, center=center, color=color))

def rr(name, radius, start, end, color):
    return add(name, rod(radius=radius, start=start, end=end, color=color))

# Room.
bx("floor", (4.5, 8.8, .12), (2.1, 1.8, -.06), (.40, .43, .42))
bx("back wall", (4.35, .16, 3.4), (2.1, 5.65, 1.7), (.86, .87, .83))
bx("left wall", (.16, 8.5, 3.4), (-.08, 1.5, 1.7), (.85, .86, .82))
bx("warm right wall", (.16, 8.5, 3.4), (4.33, 1.5, 1.7), (.66, .55, .46))
bx("ceiling", (4.5, 8.7, .15), (2.1, 1.5, 3.43), (.86, .86, .81))
bx("ceiling beam", (4.4, .52, .40), (2.1, 1.65, 3.15), (.83, .83, .78))
bx("left skirting", (.055, 7.8, .085), (.035, 1.6, .043), (.40, .43, .41))
bx("rear skirting", (4.25, .045, .08), (2.1, 5.54, .04), (.43, .45, .42))
bx("right skirting", (.05, 7.7, .10), (4.22, 1.6, .05), (.32, .34, .32))

# Glazed doors recessed into the left wall.
bx("window recess", (.035, 2.85, 2.73), (.016, 3.65, 1.64), (.61, .68, .67))
bx("bright glazing", (.028, 2.74, 2.59), (.04, 3.65, 1.64), (.76, .87, .89))
for i, y in enumerate((2.25, 2.94, 3.63, 4.32, 5.05)):
    bx("window upright %d" % i, (.095, .055, 2.7), (.091, y, 1.64), (.92, .94, .91))
for i, z in enumerate((.29, 2.98)):
    bx("window rail %d" % i, (.105, 2.85, .065), (.09, 3.65, z), (.93, .94, .91))
bx("window transom", (.09, 2.85, .045), (.10, 3.65, 2.61), (.91, .93, .91))
bx("window sill", (.20, 2.94, .075), (.1, 3.65, .255), (.87, .88, .82))
bx("blind housing", (.20, 2.97, .14), (.13, 3.65, 3.04), (.73, .72, .65))
rr("blind rail", .021, (.19, 2.17, 2.96), (.19, 5.13, 2.96), (.48, .46, .38))
for i, y in enumerate((2.99, 4.37)):
    rr("door handle %d" % i, .014, (.17, y, 1.20), (.17, y, 1.42), (.49, .53, .52))
bx("light switch", (.025, .095, .13), (.102, 1.96, 1.30), (.93, .93, .89))

# Heater.
bx("heater body", (.91, .20, .65), (.76, 5.36, .43), (.87, .89, .88))
bx("heater top", (.91, .23, .025), (.76, 5.35, .765), (.96, .96, .92))
for i, x in enumerate((.37, .48, .59, .70, .81, .92, 1.03, 1.14)):
    bx("heater vent %d" % i, (.043, .014, .10), (x, 5.248, .185), (.56, .60, .60))
for i, x in enumerate((.42, 1.09)):
    bx("heater foot %d" % i, (.055, .12, .12), (x, 5.34, .10), (.62, .65, .64))

# Oak cabinetry.
cabinet_height = 1.40
bx("cabinet body", (.47, 4.08, cabinet_height), (4.02, 3.55, cabinet_height/2), (.59, .39, .22))
bx("oak top", (.53, 4.11, .045), (3.99, 3.55, cabinet_height+.0225), (.70, .49, .28))
for i in range(6):
    yy = 1.85 + i * .67
    bx("cabinet door %d" % i, (.035, .655, cabinet_height-.065),
       (3.765, yy, cabinet_height/2), (.64+.025*(i % 2), .44+.02*(i % 2), .26))
    rr("cabinet handle %d" % i, .008, (3.735, yy-.10, 1.17),
       (3.735, yy+.10, 1.17), (.44, .39, .29))
for i in range(130):
    bx("wood grain %d" % i, (.002, random.uniform(.06, .38), .0025),
       (3.744, random.uniform(1.53, 5.55), random.uniform(.07, 1.36)),
       random.choice([(.48, .31, .17), (.73, .53, .32), (.57, .37, .20)]))

# White desk.
bx("desk top", (2.26, 1.18, .075), (3.02, 3.50, 1.045), (.92, .93, .88))
bx("desk front", (2.20, .065, .77), (3.03, 2.975, .62), (.86, .88, .83))
bx("desk right side", (.07, 1.08, .98), (4.11, 3.51, .52), (.86, .88, .84))
bx("desk left support", (.065, .93, .97), (1.94, 3.56, .52), (.86, .88, .84))

# Visitor chairs.
def visitor(name, x, y, yaw):
    a = Asset(name)
    def put(n, node):
        a.include(n, node)
    put("seat", fillet_box((.76, .66, .14), radius=.065,
                          center=(x, y, .49), color=green))
    back = fillet_box((.76, .145, .66), radius=.067,
                      center=(x, y-.28, .77), color=green)
    back.turn(axis="x", degrees=-5)
    put("back", back)
    for s in (-1, 1):
        arm = fillet_box((.115, .49, .32), radius=.05,
                         center=(x+s*.38, y+.025, .68), color=(.41, .46, .025))
        arm.turn(axis="x", degrees=-13)
        put("arm %d" % s, arm)
        put("bracket %d" % s,
            rod(radius=.019, start=(x+s*.29, y, .41),
                end=(x+s*.29, y-.28, .67), color=metal))
    put("pedestal", rod(radius=.027, start=(x, y, .10), end=(x, y, .45), color=metal))
    for j in range(4):
        an = math.radians(45+j*90)
        end = (x+.45*math.cos(an), y+.41*math.sin(an), .04)
        put("foot %d" % j, rod(radius=.022, start=(x, y, .10), end=end, color=metal))
        put("pad %d" % j, box((.08, .065, .022),
                             center=(end[0], end[1], .022), color=(.22, .24, .22)))
    a.turn(axis="z", degrees=yaw, pivot=(x, y, .5))
    add(name, a)

visitor("left visitor chair", 2.28, 1.80, -3)
visitor("right visitor chair", 3.46, 1.85, 10)

# Executive chair.
add("executive back", fillet_box((.58, .15, .76), radius=.07,
    center=(2.68, 4.71, 1.18), color=(.30, .29, .25)))
add("executive seat", fillet_box((.59, .52, .13), radius=.06,
    center=(2.68, 4.44, .75), color=(.29, .28, .24)))
rr("executive column", .038, (2.68, 4.47, .15), (2.68, 4.47, .73), (.33, .35, .34))
for j in range(5):
    an = j*math.tau/5
    rr("executive foot %d" % j, .021, (2.68, 4.47, .18),
       (2.68+.35*math.cos(an), 4.47+.35*math.sin(an), .08), metal)

# Monitor and desktop objects.
bx("monitor foot", (.43, .24, .025), (3.35, 3.91, 1.101), (.61, .62, .60))
rr("monitor stalk", .026, (3.35, 3.94, 1.10), (3.35, 4.00, 1.36), (.57, .58, .57))
monitor = box((.64, .055, .49), center=(3.35, 4.015, 1.48), color=(.57, .55, .53))
monitor.turn(axis="x", degrees=-12)
monitor.turn(axis="z", degrees=-8)
add("monitor back", monitor)
add("monitor logo", ball(.015, center=(3.35, 3.975, 1.48), color=(.35, .34, .32)))
bx("keyboard", (.50, .17, .025), (3.20, 3.66, 1.098), (.77, .79, .76))
bx("paper stack", (.30, .23, .018), (2.96, 3.45, 1.096), (.94, .94, .91))
bx("desk organizer", (.16, .14, .16), (3.76, 3.91, 1.165), (.81, .82, .77))
for i in range(4):
    rr("pen %d" % i, .005, (3.72+i*.02, 3.90, 1.21),
       (3.71+i*.02, 3.90, 1.35), (.35, .38, .36))
rr("mug", .065, (3.67, 3.66, 1.09), (3.67, 3.66, 1.23), (.89, .90, .85))
add("mug handle", sweep_tube(
    points=[(3.72, 3.66, 1.21), (3.78, 3.66, 1.21),
            (3.79, 3.66, 1.14), (3.72, 3.66, 1.13)],
    radius=.011, color=(.86, .87, .82)))

# Plants with separate leaves and branches.
def leaf(name, center, length, width, tilt, angle, color):
    n = ball(radius=1, center=(0, 0, 0), color=color)
    n.resize((width*.5, width*.13, length*.5))
    n.turn(axis="y", degrees=tilt, pivot=(0, 0, 0))
    n.turn(axis="z", degrees=angle, pivot=(0, 0, 0))
    n.move(center)
    add(name, n)

def plant(name, x, y, height, radius, pot_height, seed, floor_z=0):
    rng = random.Random(seed)
    base, top = floor_z+pot_height, floor_z+height
    small = height < .6
    rr(name+" pot", radius, (x, y, floor_z+.01), (x, y, base), (.065, .075, .065))
    rr(name+" rim", radius*1.045, (x, y, base-.025), (x, y, base), (.10, .105, .085))
    rr(name+" soil", radius*.91, (x, y, base), (x, y, base+.006), (.075, .052, .025))
    rr(name+" trunk", .006 if small else .019,
       (x, y, base), (x, y, top-height*.09), (.27, .24, .12))
    for j in range(22 if small else 40):
        angle = rng.uniform(0, math.tau)
        z = rng.uniform(base+height*.08, top-height*.04)
        reach = rng.uniform(.15, .47)*(.7+.3*(1-(z-floor_z)/height))
        if small:
            reach *= .21
        ex, ey = x+math.cos(angle)*reach, y+math.sin(angle)*reach
        ez = min(top, z+rng.uniform(.04, .21)*(.22 if small else 1))
        sz = max(base, z-(.025 if small else .13))
        rr(name+" branch %d" % j, .002 if small else .006,
           (x, y, sz), (ex, ey, ez), (.22, .29, .10))
        for k in range(5):
            t = .32+k*.15
            side = -1 if k % 2 else 1
            off = .012 if small else .055
            center = (x+(ex-x)*t+side*off*math.sin(angle),
                      y+(ey-y)*t-side*off*math.cos(angle),
                      sz+(ez-sz)*t)
            length = rng.uniform(.035, .055) if small else rng.uniform(.12, .21)
            leaf(name+" leaf %d %d" % (j, k), center, length, length*.47,
                 rng.uniform(35, 80), math.degrees(angle)+side*45,
                 rng.choice([(.065, .23, .025), (.12, .32, .035),
                             (.18, .38, .055), (.075, .28, .035)]))

plant("rear ficus", 1.88, 4.82, 2.00, .17, .34, 51)
plant("foreground shrub", .15, .45, 1.45, .23, .27, 27)
plant("desktop plant", 2.83, 3.91, .27, .052, .085, 73, floor_z=1.085)

rr("flower vase", .044, (2.63, 3.71, 1.085), (2.63, 3.71, 1.21), (.70, .74, .62))
for i in range(7):
    xx, yy = 2.63+random.uniform(-.075, .075), 3.71+random.uniform(-.055, .055)
    zz = random.uniform(1.25, 1.37)
    rr("flower stem %d" % i, .003, (2.63, 3.71, 1.17), (xx, yy, zz), (.21, .37, .09))
    for k in range(5):
        an = k*math.tau/5
        add("petal %d %d" % (i, k), ball(.019,
            center=(xx+.022*math.cos(an), yy+.022*math.sin(an), zz),
            color=(.88, .84, .68) if i % 3 else (.65, .16, .24)))

# Framed abstract botanical painting.
bx("picture frame", (.64, .045, .86), (2.86, 5.535, 2.22), (.31, .20, .12))
bx("picture border", (.595, .015, .815), (2.86, 5.504, 2.22), (.72, .58, .39))
bx("painting ground", (.555, .012, .775), (2.86, 5.491, 2.22), (.16, .17, .14))
for i in range(28):
    shape = ball(1, center=(0, 0, 0),
        color=random.choice([(.57, .37, .16), (.68, .54, .31),
                             (.32, .37, .28), (.72, .65, .45), (.28, .25, .18)]))
    shape.resize((random.uniform(.025, .065), .009, random.uniform(.04, .11)))
    shape.turn(axis="y", degrees=random.uniform(-65, 65), pivot=(0, 0, 0))
    shape.move((random.uniform(2.62, 3.08), 5.475, random.uniform(1.88, 2.56)))
    add("painted leaf %d" % i, shape)
for i in range(9):
    rr("painted stem %d" % i, .004, (2.85, 5.462, 1.86),
       (random.uniform(2.63, 3.07), 5.462, random.uniform(2.15, 2.58)), (.58, .47, .29))

bx("ceiling panel surround", (.82, .91, .035), (2.14, 4.11, 3.335), (.83, .84, .80))
bx("ceiling luminous panel", (.74, .82, .018), (2.14, 4.11, 3.31), (.98, .99, .98))

realize(scene)

for obj in bpy.context.scene.objects:
    if obj.type == 'MESH':
        for mat in obj.data.materials:
            if mat and mat.use_nodes:
                p = mat.node_tree.nodes.get("Principled BSDF")
                if p:
                    p.inputs["Roughness"].default_value = .76
                    if any(s in obj.name.lower() for s in ("pedestal", "foot", "bracket", "stalk")):
                        p.inputs["Metallic"].default_value = .52
                        p.inputs["Roughness"].default_value = .31
                    if "luminous" in obj.name.lower():
                        p.inputs["Emission Color"].default_value = (1, 1, 1, 1)
                        p.inputs["Emission Strength"].default_value = 2.5
                    if "bright glazing" in obj.name.lower():
                        p.inputs["Emission Color"].default_value = (.77, .88, 1, 1)
                        p.inputs["Emission Strength"].default_value = .65

set_view(position=(1.61, -2.20, 1.65), target=(1.91, 5.60, 1.65), lens=26, sensor=36)
area_emitter(position=(.32, 3.15, 2.24), power=650, size=3.0,
             target=(2.9, 3.4, .7), color=(.85, .94, 1.0))
area_emitter(position=(2.18, 3.95, 3.24), power=220, size=.85,
             target=(2.6, 3.3, 0), color=(1.0, .98, .91))
area_emitter(position=(1.3, -.8, 2.8), power=130, size=4,
             target=(2.5, 3.8, 1.0), color=(1, .97, .89))

sc = bpy.context.scene
world = sc.world
if world is None:
    world = bpy.data.worlds.new("Office world")
    sc.world = world
world.use_nodes = True
background = world.node_tree.nodes.get("Background")
if background is not None:
    background.inputs["Color"].default_value = (.76, .80, .83, 1)
    background.inputs["Strength"].default_value = .35

sc.render.engine = 'CYCLES'
sc.cycles.samples = 48
sc.cycles.use_denoising = True
sc.render.resolution_x = 512
sc.render.resolution_y = 342
sc.render.resolution_percentage = 100
sc.view_settings.view_transform = 'AgX'
sc.view_settings.look = 'AgX - Medium High Contrast'
sc.view_settings.exposure = .35
