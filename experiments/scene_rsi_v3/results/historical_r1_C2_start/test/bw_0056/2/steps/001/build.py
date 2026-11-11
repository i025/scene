# Reference inventory, normalized image coordinates (approximate):
# - Cleanroom walls, ceiling, lights and floor: entire image; room depth is uncertain.
# - Foreground operator: x=.17-.68, y=0-1; white coat, hairnet, face, raised arm.
# - Background operator: x=0-.21, y=.14-1; white coat, hairnet, clasped hands.
# - Packaging machine: x=.42-1, y=.32-1; stainless chassis, exposed mechanisms,
#   clear framed guards, guide rails, front conveyor and small labels.
# - HMI and articulated mount: x=.61-.83, y=.06-.47; tilted pale display facing
#   the foreground operator, dark mount and rear support.
# - Light conveyor: x=.49-.83, y=.78-1; individual pale trays and metal rails.
# Hidden machine internals and the room beyond the frame are uncertain.
#
# Estimated expanded primitive count: about 180 meshes. Each box, ball and rod
# is counted once; no fillets, booleans, cloning or long tube paths are used.

import math
import bpy
from mathutils import Vector
from sceneact import Scene, Asset, box, ball, rod, realize, set_view, area_emitter

scene = Scene("Cleanroom packaging line")

WHITE = (0.80, 0.91, 0.89)
WALL = (0.69, 0.82, 0.80)
FLOOR = (0.57, 0.73, 0.71)
STEEL = (0.43, 0.56, 0.56)
DARK = (0.075, 0.13, 0.14)
BELT = (0.80, 0.88, 0.82)
GLASS = (0.65, 0.87, 0.85)
SKIN = (0.73, 0.49, 0.35)
HAIR = (0.53, 0.72, 0.70)
PANEL = (0.76, 0.84, 0.84)
SCREEN = (0.76, 0.91, 0.91)

def add(asset, name, node):
    asset.include(name, node)

def B(asset, name, size, center, color, opacity=1):
    add(asset, name, box(size=size, center=center, color=color, opacity=opacity))

def R(asset, name, start, end, radius, color):
    add(asset, name, rod(radius=radius, start=start, end=end, color=color))

def S(asset, name, center, radius, scale, color):
    n = ball(radius=radius, center=center, color=color)
    n.resize(scale, pivot=center)
    add(asset, name, n)

# Architecture. The room extends behind the machine.
room = Asset("Cleanroom architecture")
B(room, "floor", (8, 11, .10), (0, 1.5, -.06), FLOOR)
B(room, "back wall", (8, .12, 3.45), (0, 6.0, 1.72), WALL)
B(room, "right wall", (.12, 11, 3.45), (3.8, 1.5, 1.72), (0.75, .86, .84))
B(room, "ceiling", (8, 11, .10), (0, 1.5, 3.48), (0.70, .83, .81))
for i, x in enumerate((-3, -1.5, 0, 1.5, 3)):
    B(room, "ceiling longitudinal grid %d" % i, (.025, 10, .025), (x, 1.3, 3.40), STEEL)
for i, y in enumerate((-3, -1, 1, 3, 5)):
    B(room, "ceiling cross grid %d" % i, (7.7, .025, .025), (0, y, 3.40), STEEL)
    for j, x in enumerate((-2.25, .75, 2.25)):
        B(room, "recessed light %d %d" % (i,j), (1.05, 1.02, .035),
          (x, y+.65, 3.415), (0.96, 1.0, .99))
for i, x in enumerate((-2, 0, 2)):
    B(room, "floor seam %d" % i, (.012, 10, .006), (x, 1.2, .002), (.48,.65,.63))
scene.include("architecture", room)

# Machine occupies the right side, conveyor runs from foreground to background.
machine = Asset("Packaging machine")
B(machine, "lower cabinet", (1.65, 3.65, .77), (.85, 1.05, .48), (0.48,.61,.60))
B(machine, "front cabinet panel", (1.55,.035,.60), (.85,-.79,.48), (0.60,.71,.70))
B(machine, "upper work deck", (1.78,3.75,.10), (.85,1.05,.91), STEEL)
for x in (.10, 1.60):
    for y in (-.56, 2.63):
        B(machine, "cabinet foot %.1f %.1f" % (x,y), (.10,.10,.16), (x,y,.08), DARK)

# Light belt and its repeated transverse trays, with parallel guides.
B(machine, "conveyor belt", (.79,4.25,.08), (.76,.68,1.00), BELT)
for x in (.30, 1.22):
    B(machine, "conveyor side rail %.2f" % x, (.055,4.27,.12), (x,.68,1.07), STEEL)
    B(machine, "upper guide %.2f" % x, (.025,3.55,.035), (x,.92,1.28), (0.69,.78,.76))
    for y in (-.55,.55,1.65,2.75):
        R(machine, "guide post %.2f %.2f" % (x,y), (x,y,1.07), (x,y,1.28), .018, STEEL)
for i in range(9):
    y = -.95 + i*.46
    B(machine, "pale product tray %02d" % i, (.65,.32,.035), (.76,y,1.06), (.88,.93,.86))
    B(machine, "tray rim %02d" % i, (.63,.025,.025), (.76,y-.145,1.09), (.72,.83,.77))

# Transparent guard enclosure and its light metal frame.
for x in (-.01,1.70):
    for y in (-.30,1.05,2.42):
        B(machine, "guard upright %.2f %.2f" % (x,y), (.045,.045,1.26), (x,y,1.58), STEEL)
    B(machine, "guard top rail %.2f" % x, (.045,2.75,.045), (x,1.06,2.20), STEEL)
    B(machine, "guard mid rail %.2f" % x, (.035,2.75,.035), (x,1.06,1.25), STEEL)
    B(machine, "clear side guard %.2f" % x, (.012,2.68,1.12), (x,1.06,1.64), GLASS, .13)
for y in (-.30,2.42):
    B(machine, "guard transverse %.2f" % y, (1.74,.045,.045), (.845,y,2.20), STEEL)
B(machine, "clear front guard", (1.68,.012,1.05), (.845,-.30,1.65), GLASS, .10)

# Mechanical structure visible through the guards.
for y in (.55,1.50,2.35):
    B(machine, "mechanism crossbeam %.2f" % y, (1.52,.10,.12), (.84,y,1.63), DARK)
    B(machine, "mechanism top plate %.2f" % y, (1.22,.31,.065), (.84,y,1.91), STEEL)
    for x in (.40,1.25):
        R(machine, "pneumatic cylinder %.2f %.2f" % (x,y), (x,y,1.40), (x,y,1.83), .065, STEEL)
        R(machine, "piston rod %.2f %.2f" % (x,y), (x,y,1.20), (x,y,1.43), .025, (.72,.79,.76))
        B(machine, "actuator mount %.2f %.2f" % (x,y), (.19,.19,.08), (x,y,1.85), DARK)
    R(machine, "horizontal shaft %.2f" % y, (.27,y,1.45), (1.43,y,1.45), .035, STEEL)
for x in (.24,1.47):
    B(machine, "linear profile %.2f" % x, (.08,2.65,.09), (x,1.08,1.47), DARK)
    for y in (.25,1.1,1.95):
        B(machine, "profile bracket %.2f %.2f" % (x,y), (.16,.13,.15), (x,y,1.49), STEEL)
B(machine, "dark rear motor", (.49,.50,.43), (1.02,2.20,1.80), DARK)
B(machine, "front nameplate", (.25,.012,.09), (.92,-.815,.71), (.84,.90,.87))
B(machine, "side nameplate", (.012,.29,.10), (1.684,.63,1.06), (.84,.91,.88))
scene.include("packaging machine", machine)

# Screen is a slim tilted assembly. Panel plane is mostly X/Z, facing the
# operator and the camera. Rotate all panel components around the same pivot.
hmi = Asset("Articulated HMI")
R(hmi, "support column", (1.50,1.20,1.75), (1.50,1.20,2.38), .065, STEEL)
R(hmi, "rear arm", (1.50,1.20,2.38), (1.13,.66,2.48), .075, DARK)
R(hmi, "adjustable arm", (1.13,.66,2.48), (.92,.33,2.55), .055, STEEL)
S(hmi, "arm pivot", (1.13,.66,2.48), .11, (1,1,1), DARK)
pivot = (.78,.20,2.49)
def screen_part(name, size, center, color):
    n = box(size=size, center=center, color=color)
    n.turn(axis="+y", degrees=12, pivot=pivot)
    hmi.include(name,n)
screen_part("outer housing", (.93,.11,.76), pivot, (.43,.54,.55))
screen_part("silver bezel", (.86,.025,.69), (.78,.133,2.49), (.80,.87,.85))
screen_part("illuminated display", (.72,.012,.55), (.78,.111,2.49), SCREEN)
screen_part("display lower bar", (.68,.008,.035), (.78,.101,2.27), (.57,.70,.72))
scene.include("touchscreen and arm", hmi)

# Simplified human silhouettes. Individual coat, head, hairnet and limb parts
# remain separate for later adjustment.
def person(name, x, y, scale, foreground=False):
    p = Asset(name)
    def P(v):
        return (x+v[0]*scale, y+v[1]*scale, v[2]*scale)
    def PB(n, size, pos, col):
        B(p,n,tuple(a*scale for a in size),P(pos),col)
    def PR(n, a, b, r, col):
        R(p,n,P(a),P(b),r*scale,col)
    def PS(n,pos,r,shape,col):
        S(p,n,P(pos),r*scale,shape,col)
    PB("coat torso", (.53,.29,.80), (0,0,1.11), WHITE)
    PB("coat skirt", (.59,.31,.55), (0,0,.58), (.79,.90,.88))
    PB("coat center seam", (.012,.012,.96), (0,-.158,.88), (.64,.78,.75))
    for side in (-1,1):
        PB("trouser leg %s" % side, (.18,.21,.48), (side*.14,0,.25), DARK)
        PB("shoe %s" % side, (.20,.32,.10), (side*.14,-.045,.05), (.12,.19,.19))
    PR("neck", (0,0,1.48), (0,0,1.63), .09, SKIN)
    PS("head", (0,-.005,1.73), .155, (.83,.88,1.14), SKIN)
    PS("hairnet", (-.015,.025,1.82), .16, (1,.95,.74), HAIR)
    PR("hairnet edge", (-.13,-.08,1.79), (.12,-.08,1.79), .012, (.79,.90,.87))
    if foreground:
        PR("raised upper sleeve", (.23,0,1.36), (.48,-.04,1.35), .12, WHITE)
        PR("raised fore sleeve", (.48,-.04,1.35), (.75,-.10,1.54), .095, WHITE)
        PR("operating hand", (.75,-.10,1.54), (.84,-.10,1.58), .048, SKIN)
        PR("lower sleeve", (-.23,0,1.35), (-.28,-.06,.96), .105, WHITE)
        PR("lower hand", (-.28,-.06,.96), (-.25,-.13,.86), .046, SKIN)
    else:
        for side in (-1,1):
            PR("sleeve %s" % side, (side*.23,0,1.35), (side*.27,-.08,1.02), .095, WHITE)
            PR("bent forearm %s" % side, (side*.27,-.08,1.02), (side*.05,-.22,1.02), .075, WHITE)
            PS("hand %s" % side, (side*.05,-.22,1.02), .06, (1,1,.7), SKIN)
    scene.include(name,p)

person("Foreground operator", -1.00, -.05, 1.10, True)
person("Background operator", -2.18, 2.55, .98, False)

realize(scene)

# Set physically plausible material behavior on the generated colored meshes.
for mat in bpy.data.materials:
    if not mat.use_nodes:
        mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if not bsdf:
        continue
    c = tuple(bsdf.inputs["Base Color"].default_value[:3])
    bsdf.inputs["Roughness"].default_value = .43
    if max(c)-min(c) < .16 and .32 < sum(c)/3 < .70:
        bsdf.inputs["Metallic"].default_value = .55
        bsdf.inputs["Roughness"].default_value = .31

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
background.inputs["Color"].default_value = (.70,.87,.85,1)
background.inputs["Strength"].default_value = .65

set_view((4.15,-8.5,2.55), (.05,.92,1.53), lens=37)
area_emitter((0,-2.0,3.3), power=650, size=4.5, target=(0,1,1), color=(.86,1,.98))
area_emitter((-2,2.0,3.3), power=500, size=3.5, target=(0,1,1), color=(.86,.98,1))
area_emitter((2.5,3.5,3.2), power=450, size=3, target=(.5,1,1), color=(.90,1,.98))

sc.render.engine = "CYCLES"
sc.cycles.samples = 32
sc.render.resolution_x = 1536
sc.render.resolution_y = 1023
sc.render.resolution_percentage = 100
sc.view_settings.view_transform = "AgX"
camera = sc.camera
camera.data.dof.use_dof = True
camera.data.dof.focus_distance = (camera.location - Vector((-1.0,-.05,1.45))).length
camera.data.dof.aperture_fstop = 8.0
