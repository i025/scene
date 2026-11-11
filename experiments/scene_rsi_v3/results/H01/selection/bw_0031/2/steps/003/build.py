# Discrepancy ledger, normalized coordinates in the supplied portrait images:
# 1. Reference room photograph is x=.03-.94, y=.65-1.00; the current room
#    render fills x=0-1, y=.30-1, with a large blank region above the wall.
#    The architectural boundary is visible with incorrect framing: the camera
#    sees beyond the wall/ceiling. Lower the camera and aim into an enclosed
#    room so the wall and ceiling fill the upper part of the room view.
# 2. Reference main desk occupies x=.03-.67, y=.78-1.00, with a strong
#    diagonal from near left to far right. Current desk occupies x=0-.88,
#    y=.49-.77 and is almost horizontal: visible with wrong perspective and
#    placement. Rotate the viewpoint toward the desk's left end and adjust
#    camera aim and desk depth while keeping its pedestal on the floor.
# 3. Reference doorway and independent console are x=.65-.94, y=.68-.90.
#    Current doorway is x=.62-.67, y=.41-.52 and the small console is largely
#    occluded at x=.72-.89, y=.48-.55. Reposition the two locally on the back
#    wall and frame the right corner to keep their silhouettes distinct.
# The cropped dark fragment at the photograph's lower left is uncertain; a
# small separate foreground cabinet fragment is included at the left edge.
# The photo's back-wall lines slope down slightly to the right, while the
# current lines are nearly level; the foreground console and distant doorway
# both support a more oblique camera. Preserve the wall meter/grille order,
# desk-to-wall separation and pale panels over dark bases.
# The yellow panel is a separate reference view; its precise room location is
# unknown. It is placed on the right return wall, with a dedicated detail camera.
# Inventory: enclosure, instrument wall with square meters and vent, long
# sloping desk, right doorway, small console, cropped foreground fragment,
# GRID panel and ceiling lamps. Hidden room details remain uncertain.
# Approximate expanded SceneAct primitive count: architecture 6, wall
# instruments 125, main console 135, smaller console 30, GRID panel 55,
# fixtures and fragment 8, total about 359. No booleans or fillets.

from sceneact import *
import bpy
import math
from mathutils import Vector

scene = Scene("1970s Dispatch Control Room")
wall = (.72, .70, .65)
ceiling = (.79, .77, .72)
floor = (.29, .265, .23)
cabinet = (.64, .63, .58)
pale = (.82, .80, .74)
metal = (.48, .47, .43)
dark = (.09, .085, .075)
yellow = (.88, .65, .11)
red = (.72, .025, .018)
amber = (1.0, .40, .025)

room = Asset("01 Architecture")
room.include("floor", box((12, 9, .12), center=(0, 0, -.06), color=floor))
room.include("back wall", box((12, .12, 3.3), center=(0, 3.6, 1.65), color=wall))
room.include("right wall", box((.12, 9, 3.3), center=(5.9, -.9, 1.65), color=wall))
room.include("left wall", box((.12, 9, 3.3), center=(-6, -.9, 1.65), color=wall))
room.include("ceiling", box((12, 9, .10), center=(0, -.9, 3.35), color=ceiling))
room.include("back skirting", box((12, .04, .12), center=(0, 3.51, .06), color=metal))
scene.include("01 Architecture", room)

cabs = Asset("02 Main wall cabinets")
cabs.include("cabinet wall", box((7.4, .22, 2.62), center=(-1.55, 3.43, 1.48), color=cabinet))
for i, x in enumerate((-5.22, -4.08, -2.94, -1.80, -.66, .48, 1.62, 2.1)):
    cabs.include("cabinet seam %02d" % i,
                 box((.014, .018, 2.55), center=(x, 3.305, 1.49), color=metal))
# Rows of uniform square meters, including those cropped by the frame.
for c in range(6):
    for r in range(4):
        x, z = -4.98 + c*.39, .70 + r*.38
        cabs.include("meter frame %d %d" % (c,r),
                     box((.285, .025, .285), center=(x,3.29,z), color=dark))
        cabs.include("meter face %d %d" % (c,r),
                     box((.225, .012, .225), center=(x,3.272,z), color=pale))
        cabs.include("meter pointer %d %d" % (c,r),
                     box((.012,.008,.09), center=(x,3.262,z), color=metal))
cabs.include("vent opening", box((1.20,.025,.68), center=(-1.77,3.29,1.56), color=dark))
for i in range(7):
    cabs.include("vent louver %d" % i,
                 box((1.14,.025,.035), center=(-1.77,3.27,1.32+i*.08), color=cabinet))
for c in range(4):
    for r in range(5):
        x, z = -.75+c*.29, .70+r*.30
        cabs.include("right meter rim %d %d" % (c,r),
                     box((.21,.025,.22), center=(x,3.29,z), color=dark))
        cabs.include("right meter face %d %d" % (c,r),
                     box((.16,.012,.17), center=(x,3.272,z), color=pale))
scene.include("02 Main wall cabinets", cabs)

door = Asset("03 Back wall doorway")
door.include("opening", box((.78,.035,2.12), center=(2.50,3.52,1.06), color=dark))
door.include("inner door", box((.59,.018,1.92), center=(2.50,3.495,1.08), color=(.30,.29,.26)))
door.include("upper window", box((.47,.012,.52), center=(2.50,3.48,1.76), color=(.43,.42,.39)))
scene.include("03 Back wall doorway", door)

desk = Asset("04 Main operating console")
desk.include("floor standing pedestal",
             box((6.1,1.26,.73), center=(-1.55,.18,.365), color=(.18,.17,.15)))
desk.include("front writing ledge",
             box((6.32,.46,.10), center=(-1.55,-.64,.83), color=pale))
a = math.radians(18)
pc = Vector((-1.55,.16,1.08))
panel = box((6.32,1.40,.10), center=tuple(pc), color=pale)
panel.turn(axis="+x", degrees=18, pivot=tuple(pc))
desk.include("sloping control surface", panel)

def panel_point(x, y, h=.065):
    return (x, pc.y + y*math.cos(a)-h*math.sin(a),
            pc.z + y*math.sin(a)+h*math.cos(a))

for i in range(8):
    x = -4.58+i*.86
    p = panel_point(x,0,.058)
    seam = box((.016,1.31,.012), center=p, color=metal)
    seam.turn(axis="+x", degrees=18, pivot=p)
    desk.include("panel division %d" % i, seam)
for c in range(19):
    for r in range(4):
        x, y = -4.51+c*.32, -.49+r*.29
        p = panel_point(x,y,.074)
        switch = box((.07,.07,.04), center=p, color=dark if (c+r)%3 else metal)
        switch.turn(axis="+x", degrees=18, pivot=p)
        desk.include("switch %02d %d" % (c,r), switch)
for i in range(10):
    x = -4.40+i*.60
    p = panel_point(x,.49,.07)
    meter = box((.18,.14,.025), center=p, color=dark)
    meter.turn(axis="+x", degrees=18, pivot=p)
    desk.include("console indicator %d" % i, meter)
scene.include("04 Main operating console", desk)

small = Asset("05 Independent right console")
small.include("pedestal", box((1.55,.82,.72), center=(4.35,2.64,.36), color=(.25,.24,.21)))
top_center = (4.35,2.57,.84)
top = box((1.68,.95,.10), center=top_center, color=pale)
top.turn(axis="+x", degrees=13, pivot=top_center)
small.include("sloped top", top)
for c in range(7):
    for r in range(3):
        x, y = 3.73+c*.205, 2.28+r*.22
        z = .91+(y-2.57)*math.sin(math.radians(13))
        small.include("control %d %d" % (c,r),
                      box((.06,.06,.035), center=(x,y,z), color=dark))
scene.include("05 Independent right console", small)

fragment = Asset("06 Foreground edge fragment")
fragment.include("cropped cabinet", box((.30,.52,.70), center=(-5.72,-1.8,.35), color=(.20,.19,.17)))
fragment.include("pale edge", box((.30,.52,.05), center=(-5.72,-1.8,.72), color=pale))
scene.include("06 Foreground edge fragment", fragment)

grid = Asset("07 GRID single line mimic panel")
grid.include("yellow plate", box((.08,1.55,1.90), center=(5.81,1.00,1.85), color=yellow))
def bar(name, y, z, sy, sz, color=dark, x=5.755):
    grid.include(name, box((.018,sy,sz), center=(x,y,z), color=color))
bar("vertical bus", .94,1.85,.035,1.67)
for i,z in enumerate((1.24,1.60,2.10,2.47)):
    bar("horizontal connection %d" % i,.94,z,.70,.035)
for c,y in enumerate((.65,.94,1.23)):
    for r,z in enumerate((1.60,2.10)):
        bar("square indicator rim %d %d" % (c,r),y,z,.17,.19,dark,5.74)
        bar("square amber indicator %d %d" % (c,r),y,z,.105,.13,amber,5.725)
for i,(y,z) in enumerate(((.94,1.10),(.94,2.62),(1.44,2.42),(1.44,1.22))):
    grid.include("red indicator %d" % i,
                 rod(.067,start=(5.74,y,z),end=(5.69,y,z),color=red))
for i in range(4):
    y, z = .43, 1.25+i*.38
    bar("selector dial %d" % i,y,z,.22,.22,pale,5.74)
    grid.include("black selector %d" % i,
                 rod(.044,start=(5.73,y,z),end=(5.68,y,z),color=dark))
scene.include("07 GRID single line mimic panel", grid)

fixtures = Asset("08 Fluorescent ceiling fixtures")
for i,x in enumerate((-3.5,-.8,1.9,4.5)):
    fixtures.include("fluorescent troffer %d" % i,
                     box((1.5,.38,.035), center=(x,2.0,3.28), color=(.93,.92,.85)))
scene.include("08 Fluorescent ceiling fixtures", fixtures)

realize(scene)

sc = bpy.context.scene
if sc.world is None:
    sc.world = bpy.data.worlds.new("SceneWorld")
sc.world.use_nodes = True
background = sc.world.node_tree.nodes.get("Background")
if background is None:
    background = sc.world.node_tree.nodes.new("ShaderNodeBackground")
output = sc.world.node_tree.nodes.get("World Output")
if output is None:
    output = sc.world.node_tree.nodes.new("ShaderNodeOutputWorld")
sc.world.node_tree.links.new(background.outputs["Background"], output.inputs["Surface"])
background.inputs["Color"].default_value = (.65,.63,.58,1)
background.inputs["Strength"].default_value = .35

# Interior camera: a modestly elevated oblique view from the left.
set_view((-5.1,-6.0,2.75), (-.1,2.05,1.32), lens=30)
overview = sc.camera
overview.name = "Camera - room overview"
area_emitter((-2,-1,3.05), power=650, size=5, target=(-1,2,0))
area_emitter((3,1,3.05), power=350, size=3, target=(2,2,0))

bpy.ops.object.camera_add(location=(1.8,-2.7,2.35))
detail = bpy.context.object
detail.name = "Camera - console and GRID detail"
detail.rotation_euler = (Vector((4.1,1.0,1.55))-detail.location).to_track_quat("-Z","Y").to_euler()
detail.data.lens = 36
sc.camera = overview

def grid_text(body, y, z, size):
    curve = bpy.data.curves.new("GRID label " + body, "FONT")
    curve.body = body
    curve.size = size
    curve.extrude = .001
    obj = bpy.data.objects.new("GRID label " + body, curve)
    sc.collection.objects.link(obj)
    obj.location = (5.67,y,z)
    obj.rotation_euler = (math.pi/2,0,math.pi/2)
    mat = bpy.data.materials.get("GRID label ink")
    if mat is None:
        mat = bpy.data.materials.new("GRID label ink")
        mat.diffuse_color = (.025,.025,.02,1)
    curve.materials.append(mat)

grid_text("NETZ", .65, 2.70, .075)
grid_text("FEHLERSTELLE", .64, .96, .052)

# Make the existing indicator surface materials emissive.
for mat in bpy.data.materials:
    if not mat.use_nodes:
        continue
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf is None:
        continue
    rgb = tuple(bsdf.inputs["Base Color"].default_value[:3])
    for indicator in (red, amber):
        if sum(abs(rgb[i]-indicator[i]) for i in range(3)) < .03:
            bsdf.inputs["Emission Color"].default_value = (*indicator,1)
            bsdf.inputs["Emission Strength"].default_value = .8

sc.render.engine = "CYCLES"
sc.cycles.use_denoising = True
try:
    sc.view_settings.view_transform = "Filmic"
except TypeError:
    pass
sc.render.resolution_x = 1920
sc.render.resolution_y = 1080
sc.render.resolution_percentage = 100
sc.render.image_settings.file_format = "PNG"
