from sceneact import *
import bpy
import math
import random

random.seed(24)

# Visual estimates, normalized image coordinates:
# monitor: (.03,.12), (.34,.04), (.34,.40), (.07,.48)
# oscilloscope: (.22,.43)-(.45,.59)
# keyboard: (.10,.69)-(.53,.88)
# upright meter: (.59,.40)-(.68,.62)
# lamp shade: (.49,.17)-(.83,.30)
# drawer cabinets: (.44,0)-(1,.27); worktop foreground cropped at v=1.
# Arbitrary world scale; camera elevation and desk depth remain uncertain.
# Inventory: architecture, workbench, cabinets, wall papers and pliers,
# monitor, scope, power supply, controller, keyboard, calculator, meters,
# lamp, soldering equipment, cans, bottle, PCB, leads, probes and organizer.
# Desktop objects contact z=.80; cabinets and hanging tools sit at the wall.
# Source audit only: no render or image-quality measurement has occurred.
# No fillet boxes or local bpy material overrides are used. Every loop has
# unique per-parent keys; all rod endpoints and consecutive tube points differ.

# ---------------- Camera parameters ----------------
CAMERA = (.10, -3.25, 2.90)
TARGET = (0, .20, 1.28)
LENS = 43

# ---------------- Architecture parameters ----------------
DESK_Z = .80
DESK_W = 2.65
DESK_D = 1.66

# ---------------- Object dimensions and poses ----------------
MONITOR_CENTER = (-.96, .48, 1.47)
MONITOR_SIZE = (.86, .075, .65)
SCOPE_CENTER = (-.39, .43, .995)
SCOPE_SIZE = (.64, .33, .35)
METER_CENTER = (.44, .10, 1.04)
METER_SIZE = (.235, .061, .415)
KEYBOARD_CENTER = (-.51, -.37, .83)
KEYBOARD_SIZE = (.99, .36, .042)

# ---------------- Materials ----------------
wood = (.34, .19, .12)
wall = (.53, .52, .43)
black = (.018, .022, .023)
charcoal = (.055, .063, .064)
grey = (.48, .49, .43)
ivory = (.67, .68, .58)
paper = (.82, .82, .73)
metal = (.38, .40, .38)
red = (.56, .025, .017)
yellow = (.94, .60, .012)
blue = (.015, .18, .40)

# ---------------- Lighting parameters ----------------
AMBIENT_STRENGTH = .45
KEY_POSITION = (-.7, -1.1, 3.2)
KEY_POWER = 190
LAMP_POWER = 24

scene = Scene("Electronics workbench")
asset_names = {}
scene_keys = set()
child_keys = {}


def asset(name):
    a = Asset(name)
    asset_names[id(a)] = name
    child_keys[id(a)] = set()
    return a


def include(a, name, node):
    keys = child_keys[id(a)]
    assert name not in keys, f"Duplicate child key: {name}"
    keys.add(name)
    return a.include(name, node)


def finite_point(p):
    assert len(p) == 3 and all(math.isfinite(v) for v in p)


def block(a, name, size, loc, col):
    assert all(math.isfinite(v) and v > 0 for v in size)
    finite_point(loc)
    return include(a, name, box(size=size, center=loc, color=col))


def tube(a, name, points, radius, col):
    assert math.isfinite(radius) and radius > 0
    assert len(points) >= 2
    for p in points:
        finite_point(p)
    for p, q in zip(points, points[1:]):
        assert sum((p[k] - q[k]) ** 2 for k in range(3)) > 1e-14
    return include(a, name, sweep_tube(points=points, radius=radius, color=col))


def bar(a, name, p, q, radius, col):
    finite_point(p)
    finite_point(q)
    assert math.isfinite(radius) and radius > 0
    assert sum((p[k] - q[k]) ** 2 for k in range(3)) > 1e-14
    return include(a, name, rod(radius=radius, start=p, end=q, color=col))


def sphere(a, name, loc, radius, col):
    finite_point(loc)
    assert math.isfinite(radius) and radius > 0
    return include(a, name, ball(radius=radius, center=loc, color=col))


def add(a, name=None):
    key = name if name is not None else asset_names[id(a)]
    assert key not in scene_keys, f"Duplicate scene key: {key}"
    scene_keys.add(key)
    scene.include(key, a)
    return a


# ---------------- Architecture and workbench ----------------
desk = asset("wooden workbench")
block(desk, "thick brown worktop", (DESK_W, DESK_D, .075),
      (0, 0, DESK_Z - .0375), wood)
block(desk, "front edge", (DESK_W, .045, .075),
      (0, -.82, .762), (.23, .12, .075))
for ix, x in enumerate((-1.13, 1.13)):
    for iy, y in enumerate((-.65, .65)):
        block(desk, f"leg_{ix}_{iy}", (.075, .075, .75),
              (x, y, .375), (.21, .20, .16))
add(desk)

room = asset("room architecture")
block(room, "rear wall", (4, .09, 3), (0, .90, 1.5), wall)
block(room, "left wall", (.08, 2.2, 3),
      (-1.49, 0, 1.5), (.36, .37, .31))
add(room)

# ---------------- Rear small-parts cabinets ----------------
for cabinet_i, (cx, width, cols, rows) in enumerate(
        ((.13, .78, 4, 4), (.97, .91, 5, 6))):
    a = asset(f"small parts cabinet {cabinet_i}")
    z0 = 1.70
    height = .67 if cabinet_i == 0 else .91
    block(a, "outer dark frame", (width, .24, height),
          (cx, .77, z0 + height / 2), (.055, .066, .064))
    for r in range(rows):
        for c in range(cols):
            w = (width - .035) / cols
            h = (height - .035) / rows
            x = cx - width / 2 + .018 + (c + .5) * w
            z = z0 + .018 + (r + .5) * h
            color = (.17 + .018 * ((r + c) % 3),
                     .19 + .015 * (r % 2), .17)
            block(a, f"drawer_{r}_{c}", (w - .009, .025, h - .011),
                  (x, .632, z), color)
            block(a, f"label_{r}_{c}", (w * .52, .004, h * .23),
                  (x, .616, z - h * .24), (.61, .64, .56))
            block(a, f"handle_{r}_{c}", (w * .30, .014, .011),
                  (x, .603, z + .007), (.10, .11, .10))
    add(a)

notes = asset("pinned rear documents")
for i, (x, z, w, h) in enumerate(
        ((-.01, 1.57, .42, .25),
         (.43, 1.53, .43, .26),
         (.89, 1.48, .38, .25))):
    block(notes, f"sheet_{i}", (w, .008, h), (x, .835, z), paper)
    for j in range(5):
        block(notes, f"rule_{i}_{j}", (w * .76, .002, .0018),
              (x, .829, z - h * .3 + j * .031), (.55, .57, .52))
add(notes)

# ---------------- Monitor and stand ----------------
monitor = asset("LCD computer monitor")
block(monitor, "pedestal", (.40, .24, .026), (-.96, .38, .821), charcoal)
bar(monitor, "stand", (-.96, .43, .83), (-.96, .48, 1.12), .035, charcoal)
block(monitor, "thick black housing", MONITOR_SIZE, MONITOR_CENTER, black)
block(monitor, "blue display", (.787, .009, .551),
      (-.96, .437, 1.49), (.035, .37, .77))
block(monitor, "pale upper screen", (.767, .004, .46),
      (-.96, .430, 1.52), (.14, .52, .85))
block(monitor, "taskbar", (.78, .004, .025),
      (-.96, .426, 1.225), (.025, .20, .56))
block(monitor, "login white mark", (.055, .003, .008),
      (-.96, .423, 1.48), (.79, .84, .83))
emblem_colors = ((.80, .23, .07), (.16, .60, .22),
                 (.15, .32, .73), (.90, .73, .09))
for i in range(4):
    block(monitor, f"login emblem {i}", (.013, .003, .017),
          (-.98 + (i % 2) * .016, .421, 1.51 + (i // 2) * .019),
          emblem_colors[i])
block(monitor, "bottom logo", (.045, .003, .007),
      (-.96, .435, 1.165), (.48, .49, .45))
monitor.turn("z", -10)
add(monitor)

# ---------------- Oscilloscope ----------------
scope = asset("oscilloscope")
block(scope, "case", SCOPE_SIZE, SCOPE_CENTER, (.59, .60, .53))
block(scope, "front panel", (.64, .018, .35), (-.39, .254, .995), ivory)
block(scope, "screen bezel", (.325, .015, .265),
      (-.515, .239, 1.005), (.28, .30, .27))
block(scope, "dark glass screen", (.278, .005, .219),
      (-.515, .228, 1.005), (.055, .095, .09))
for i in range(5):
    block(scope, f"screen grid v{i}", (.0015, .002, .21),
          (-.625 + i * .055, .224, 1.005), (.10, .15, .13))
    block(scope, f"screen grid h{i}", (.27, .002, .0015),
          (-.515, .223, .92 + i * .043), (.10, .15, .13))
for row in range(4):
    for col in range(4):
        x = -.275 + col * .048
        z = .884 + row * .065
        bar(scope, f"knob_{row}_{col}", (x, .243, z), (x, .213, z),
            .014 if col < 2 else .011, (.66, .67, .59))
for i in range(7):
    block(scope, f"upper button{i}", (.018, .01, .009),
          (-.28 + i * .025, .236, 1.145), (.28, .30, .26))
add(scope)

supply = asset("small bench power supply")
block(supply, "housing", (.31, .29, .27),
      (-1.02, .25, .95), (.46, .48, .40))
block(supply, "front", (.31, .015, .27),
      (-1.02, .095, .95), (.63, .65, .55))
block(supply, "display", (.205, .008, .075),
      (-1.02, .082, 1.025), (.12, .18, .15))
for i in range(3):
    x = -1.10 + i * .08
    bar(supply, f"control{i}", (x, .078, .905), (x, .050, .905),
        .025, (.60, .61, .51))
add(supply)

station = asset("bench soldering power controller")
block(station, "body", (.38, .27, .145),
      (.18, .43, .88), (.025, .033, .035))
block(station, "top panel", (.38, .27, .018),
      (.18, .43, .957), (.19, .24, .25))
for i, col in enumerate((yellow, metal, red)):
    x = .05 + i * .105
    bar(station, f"front socket{i}", (x, .284, .875), (x, .269, .875),
        .018, col)
tube(station, "coiled pale cable",
     [(.02, .47, .98), (.03, .60, 1.02), (.20, .61, 1.03),
      (.29, .52, 1.00), (.16, .50, .99), (.05, .56, 1.02)],
     .012, (.36, .40, .47))
add(station)

# ---------------- Upright multimeter ----------------
meter = asset("upright yellow multimeter")
block(meter, "yellow protective shell", METER_SIZE, METER_CENTER, yellow)
block(meter, "dark inset face", (.195, .009, .365),
      (.44, .065, 1.05), (.15, .17, .15))
block(meter, "LCD surround", (.168, .009, .103),
      (.44, .057, 1.166), (.46, .49, .39))
block(meter, "LCD", (.143, .004, .072),
      (.44, .050, 1.167), (.31, .38, .30))
for i in range(3):
    block(meter, f"LCD segment{i}", (.021, .003, .003),
          (.403 + i * .034, .046, 1.167), (.15, .20, .16))
bar(meter, "selector", (.44, .051, 1.028), (.44, .027, 1.028),
    .045, (.24, .26, .23))
bar(meter, "selector pointer", (.44, .019, 1.028),
    (.459, .018, 1.057), .007, ivory)
for i in range(7):
    angle = math.radians(i * 38)
    block(meter, f"dial mark{i}", (.008, .003, .005),
          (.44 + .066 * math.cos(angle), .049,
           1.028 + .066 * math.sin(angle)), paper)
for i, col in enumerate((black, black, red)):
    x = .38 + i * .061
    bar(meter, f"lead socket{i}", (x, .05, .898), (x, .032, .898),
        .012, col)
meter.turn("x", -10)
add(meter)

# ---------------- Keyboard, calculator and small meter ----------------
keyboard = asset("computer keyboard")
block(keyboard, "keyboard base", KEYBOARD_SIZE,
      KEYBOARD_CENTER, (.035, .043, .043))
for r in range(5):
    for c in range(16):
        block(keyboard, f"key_{r}_{c}", (.048, .046, .015),
              (-.965 + c * .058, -.505 + r * .061, .859),
              (.065, .075, .074))
block(keyboard, "space bar", (.28, .044, .015),
      (-.57, -.506, .862), (.08, .085, .083))
keyboard.turn("z", 13)
add(keyboard)

calc = asset("handheld calculator")
block(calc, "case", (.215, .35, .035),
      (-1.12, -.61, .835), (.08, .10, .10))
block(calc, "silver face", (.195, .325, .006),
      (-1.12, -.61, .857), (.59, .61, .54))
block(calc, "LCD", (.153, .071, .006),
      (-1.12, -.505, .863), (.22, .30, .27))
for r in range(6):
    for c in range(5):
        block(calc, f"button{r}_{c}", (.025, .025, .008),
              (-1.19 + c * .035, -.735 + r * .034, .865),
              (.08, .14, .16) if c < 4 else (.29, .32, .31))
calc.turn("z", 12)
add(calc)

smallmeter = asset("small meter lying on bench")
block(smallmeter, "rubber body", (.18, .29, .035),
      (.24, -.285, .838), black)
block(smallmeter, "yellow front", (.15, .26, .01),
      (.24, -.285, .861), (.68, .54, .04))
block(smallmeter, "screen", (.12, .069, .009),
      (.24, -.20, .87), (.30, .36, .29))
bar(smallmeter, "rotary switch", (.24, -.30, .87),
    (.24, -.30, .886), .039, charcoal)
for i in range(2):
    sphere(smallmeter, f"jack{i}", (.205 + i * .068, -.39, .873),
           .012, red if i else black)
smallmeter.turn("z", -16)
add(smallmeter)

# ---------------- Complete articulated lamp ----------------
lamp = asset("articulated desk lamp")
block(lamp, "clamp", (.13, .13, .10), (1.16, .48, .83), black)
bar(lamp, "lower upright", (1.16, .48, .87),
    (1.12, .48, 1.51), .017, black)
bar(lamp, "upper arm", (1.12, .48, 1.51),
    (1.02, .43, 1.84), .021, black)
bar(lamp, "parallel linkage", (1.19, .48, 1.05),
    (1.15, .48, 1.70), .009, metal)
sphere(lamp, "upper hinge", (1.03, .43, 1.83), .045, black)
block(lamp, "long wide shade", (.91, .23, .095),
      (.58, .34, 1.865), (.018, .023, .022))
block(lamp, "white underside", (.80, .19, .008),
      (.56, .34, 1.815), (.64, .64, .53))
block(lamp, "left highlight", (.09, .20, .006),
      (.19, .34, 1.916), (.47, .48, .44))
tube(lamp, "power cord",
     [(1.04, .40, 1.83), (1.19, .36, 1.76), (1.20, .30, 1.46),
      (1.12, .23, 1.12), (1.18, .13, .82), (.94, -.03, .811)],
     .008, black)
lamp.turn("z", -5)
add(lamp)

# ---------------- Papers and soldering iron ----------------
papers = asset("loose white papers")
for i in range(4):
    p = box((.41, .35, .002), center=(.79, .12, .808 + i * .0025),
            color=paper)
    p.turn("z", -11 + i * 4)
    include(papers, f"paper{i}", p)
for i in range(7):
    block(papers, f"handwritten line{i}", (.18, .0018, .001),
          (.80, .04 + i * .024, .821), (.40, .42, .37))
add(papers)

iron = asset("soldering iron stand")
block(iron, "heavy stand base", (.27, .25, .045),
      (1.06, .18, .835), (.22, .23, .20))
block(iron, "yellow sponge", (.15, .09, .017),
      (1.06, .09, .866), (.46, .36, .12))
bar(iron, "metal support", (1.02, .23, .86),
    (1.12, .30, 1.08), .028, metal)
for i in range(7):
    y = .23 + i * .014
    bar(iron, f"coil edge{i}", (1.055, y, .94 + i * .009),
        (1.14, y, 1.00 + i * .009), .008, (.22, .24, .23))
bar(iron, "turquoise handle", (1.12, .31, 1.09),
    (.99, .12, .96), .033, (.025, .27, .29))
bar(iron, "shaft", (.99, .12, .96), (.88, -.03, .85), .010, metal)
tube(iron, "iron cable",
     [(1.14, .33, 1.10), (1.25, .29, 1.08), (1.28, .10, .91),
      (1.22, -.16, .82), (.92, -.27, .812)], .010, black)
add(iron)

# ---------------- Rear cans and water bottle ----------------
can_specs = ((.91, .49, .36, .052, (.58, .62, .56)),
             (1.06, .57, .28, .049, (.42, .46, .42)))
for i, (x, y, h, r, col) in enumerate(can_specs):
    a = asset(f"aerosol can {i}")
    bar(a, "can", (x, y, .805), (x, y, .805 + h), r, col)
    bar(a, "top rim", (x, y, .805 + h), (x, y, .815 + h),
        r * .95, metal)
    bar(a, "nozzle", (x, y, .815 + h), (x, y, .834 + h), .016, black)
    for j in range(3):
        block(a, f"label marking{j}", (.054, .003, .018),
              (x, y - r - .001, .90 + j * .04),
              red if j == 1 else paper)
    add(a)

bottle = asset("water bottle")
bar(bottle, "bottle body", (1.27, .65, .82),
    (1.27, .65, 1.10), .064, (.29, .36, .32))
bar(bottle, "shoulder", (1.27, .65, 1.10),
    (1.27, .65, 1.17), .043, (.34, .40, .35))
bar(bottle, "neck", (1.27, .65, 1.17),
    (1.27, .65, 1.22), .025, (.38, .43, .37))
bar(bottle, "blue cap", (1.27, .65, 1.22),
    (1.27, .65, 1.245), .029, (.03, .10, .24))
add(bottle)

# ---------------- Wall tools ----------------
for i, (x, z) in enumerate(((-.55, 1.40), (-.39, 1.40), (-.22, 1.37))):
    a = asset(f"hanging pliers {i}")
    bar(a, "steel jaw left", (x - .012, .792, z + .045),
        (x - .023, .792, z + .145), .010, metal)
    bar(a, "steel jaw right", (x + .009, .792, z + .045),
        (x + .019, .792, z + .13), .009, metal)
    sphere(a, "pivot", (x, .789, z + .028), .018, metal)
    tube(a, "left handle",
         [(x - .009, .785, z + .025), (x - .043, .782, z - .045),
          (x - .045, .778, z - .105)], .012, red)
    tube(a, "right handle",
         [(x + .009, .785, z + .025), (x + .043, .782, z - .045),
          (x + .035, .778, z - .105)], .012, red)
    add(a)

# ---------------- PCB and solder spool ----------------
board = asset("exposed circuit board")
block(board, "blue PCB", (.23, .18, .013),
      (-.70, .055, .817), (.015, .16, .26))
for i in range(8):
    x = -.79 + (i % 4) * .05
    y = .005 + (i // 4) * .08
    block(board, f"component{i}", (.026, .032, .018), (x, y, .833), black)
    for j in range(2):
        bar(board, f"pin{i}_{j}", (x - .016, y + j * .015, .829),
            (x - .022, y + j * .015, .829), .002, metal)
for i in range(3):
    x = -.73 + i * .047
    bar(board, f"capacitor{i}", (x, .10, .827), (x, .10, .855),
        .012, (.16, .21, .20))
add(board)

spool = asset("solder spool")
bar(spool, "spool core", (-.30, -.50, .808),
    (-.30, -.50, .848), .042, (.67, .70, .62))
bar(spool, "top label", (-.30, -.50, .848),
    (-.30, -.50, .853), .034, (.15, .43, .39))
bar(spool, "center hole", (-.30, -.50, .853),
    (-.30, -.50, .856), .010, black)
add(spool)

# ---------------- Editable test leads ----------------
wire_specs = [
    (red, [(.40,.045,.88),(.46,-.10,.83),(.39,-.44,.821),
           (.04,-.51,.821),(-.10,-.34,.824),(.10,-.22,.824),
           (.43,-.35,.824),(.65,-.61,.822)]),
    (black, [(.38,.05,.87),(.34,-.10,.823),(.59,-.19,.822),
             (.78,-.42,.823),(.52,-.64,.823),(.18,-.59,.824)]),
    (red, [(-.62,-.16,.82),(-.47,-.30,.826),(-.27,-.28,.827),
           (.04,-.42,.829),(.23,-.66,.824),(.60,-.71,.821),
           (.67,-.58,.824)]),
    (black, [(-.62,-.18,.82),(-.73,-.51,.821),(-.59,-.74,.823),
             (-.18,-.73,.823),(.09,-.55,.824),(.36,-.58,.826)]),
    (red, [(.20,-.39,.87),(.07,-.46,.83),(-.12,-.40,.824),
           (-.21,-.29,.824),(.09,-.27,.826),(.42,-.41,.824),
           (.65,-.23,.824)]),
    (black, [(.26,-.40,.87),(.32,-.49,.83),(.55,-.44,.826),
             (.68,-.29,.827),(.50,-.14,.823),(.21,-.12,.822),
             (.14,.04,.83)]),
    (black, [(-1.04,.11,.90),(-1.19,-.04,.82),(-1.25,-.27,.823),
             (-.91,-.38,.824),(-.88,-.09,.823)]),
    (red, [(.79,-.15,.83),(.85,-.36,.821),(.69,-.48,.827),
           (.40,-.40,.829),(.21,-.48,.831)]),
]
for i, (col, pts) in enumerate(wire_specs):
    a = asset(f"test lead {i}")
    tube(a, "insulated wire", pts, .006 if i < 6 else .0045, col)
    add(a)

# ---------------- Foreground probes and tools ----------------
probe_specs = ((.26, -.665, 83, red),
               (.45, -.72, 91, black),
               (-.12, -.64, 118, black))
for i, (x, y, angle, col) in enumerate(probe_specs):
    a = asset(f"test probe {i}")
    bar(a, "handle", (x - .105, y, .832), (x + .065, y, .832), .013, col)
    bar(a, "metal needle", (x + .065, y, .832),
        (x + .135, y, .832), .004, metal)
    block(a, "finger guard", (.014, .042, .027), (x + .045, y, .834), col)
    a.turn("z", angle - 90)
    add(a)

# Separate semantic objects retain their own complete hierarchies.
driver = asset("yellow screwdriver")
bar(driver, "grip", (.76, -.44, .831), (.83, -.29, .831), .018, yellow)
bar(driver, "shaft", (.83, -.29, .831), (.89, -.15, .831), .005, metal)
add(driver)

driver = asset("blue screwdriver")
bar(driver, "grip", (.71, -.20, .84), (.79, -.15, .84),
    .019, (.02, .17, .38))
bar(driver, "shaft", (.79, -.15, .84), (.88, -.09, .84), .004, metal)
add(driver)

clip = asset("loose red test clip")
bar(clip, "insulated body", (.44, -.49, .835), (.52, -.52, .835), .009, red)
bar(clip, "metal jaw", (.52, -.52, .835), (.57, -.54, .835), .006, metal)
add(clip)

# ---------------- Yellow slips and foreground organizer ----------------
scraps = asset("yellow paper scraps")
for i in range(12):
    x = random.uniform(.72, 1.03)
    y = random.uniform(-.70, -.37)
    p = box((random.uniform(.035, .075), random.uniform(.025, .050), .002),
            center=(x, y, .812 + i * .0004), color=(.91, .70, .06))
    p.turn("z", random.uniform(-40, 40))
    include(scraps, f"scrap{i}", p)
add(scraps)

tray = asset("foreground component organizer")
block(tray, "case", (.31, .49, .045),
      (1.22, -.56, .827), (.14, .19, .20))
block(tray, "blue lid", (.30, .47, .012),
      (1.22, -.56, .858), (.06, .15, .26))
for i in range(5):
    block(tray, f"long divider{i}", (.004, .46, .021),
          (1.10 + i * .057, -.56, .87), (.23, .29, .30))
for j in range(6):
    block(tray, f"cross divider{j}", (.29, .004, .022),
          (1.22, -.76 + j * .078, .87), (.25, .29, .29))
for i in range(8):
    block(tray, f"orange part{i}", (.029, .071, .014),
          (1.12 + (i % 3) * .08, -.72 + (i // 3) * .13, .884),
          (.56, .13, .025))
tray.turn("z", -10)
add(tray)

for i, (x, y) in enumerate(((.97, -.25), (.89, -.54), (-.02, -.43))):
    slip = asset(f"loose white paper slip {i}")
    p = box((.09, .065, .002), center=(x, y, .814), color=paper)
    p.turn("z", i * 18 - 14)
    include(slip, "paper", p)
    add(slip)

coil = asset("right edge cable coil")
for i in range(4):
    pts = []
    for j in range(17):
        t = 2 * math.pi * j / 16
        pts.append((1.17 + .10 * math.cos(t),
                    -.12 + .075 * math.sin(t), .84 + i * .009))
    tube(coil, f"coil loop{i}", pts, .006, black)
add(coil)

# ---------------- Realization, camera and lighting ----------------
# All semantic object parts were attached before their parent transforms.
# Materials are supplied through SceneAct; no shared bpy materials are edited.
realize(scene)
set_view(position=CAMERA, target=TARGET, lens=LENS, sensor=36)

scene_bpy = bpy.context.scene
world = scene_bpy.world
if world is None:
    world = bpy.data.worlds.new("Workshop ambient")
    scene_bpy.world = world
world.use_nodes = True
background = world.node_tree.nodes.get("Background")
if background is None:
    background = world.node_tree.nodes.new("ShaderNodeBackground")
    output = world.node_tree.nodes.get("World Output")
    if output is None:
        output = world.node_tree.nodes.new("ShaderNodeOutputWorld")
    world.node_tree.links.new(background.outputs["Background"],
                              output.inputs["Surface"])
background.inputs["Color"].default_value = (.32, .34, .31, 1)
background.inputs["Strength"].default_value = AMBIENT_STRENGTH

area_emitter(position=KEY_POSITION, power=KEY_POWER, size=2.5,
             target=(0, 0, .8), color=(1, .94, .80))
area_emitter(position=(.45, .30, 1.79), power=LAMP_POWER, size=.65,
             target=(.6, -.05, .8), color=(.88, .94, 1))

scene_bpy.render.resolution_x = 512
scene_bpy.render.resolution_y = 388
scene_bpy.render.resolution_percentage = 100
scene_bpy.view_settings.view_transform = "AgX"
# The fixed runtime owns rendering and saving.
