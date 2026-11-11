# Reference inventory, approximate normalized image bounds:
# - Cleanroom ceiling, recessed lights and pale walls: whole background; the floor
#   is mostly hidden by people and equipment. Exact room depth is uncertain.
# - Foreground operator: x=.17-.68, y=0-1. Hairnet and profile at top, white coat,
#   right arm reaching toward screen; lower body is cropped and partly obscured.
# - Background operator: x=0-.21, y=.14-1. White coat, hairnet, glasses and
#   hands together; lower legs are cropped.
# - Packaging line: x=.40-1, y=.32-1. Stainless machine, dark mechanisms,
#   clear guard, rails and pale conveyor extending into foreground.
# - Touchscreen: x=.61-.80, y=.06-.45. Tall tilted panel, silver rim and
#   articulated mount behind it.
# - Right-side posts and small machine elements: x=.78-1, y=.69-1.
# Occluded internals, exact equipment depth and details behind the operators
# remain uncertain.
#
# Feedback comparison: the previous rendering showed the entire room from too
# far away, leaving both operators and machine much too small. Its open room
# boundaries and floor dominated the frame, and the screen was too small.
# This revision moves the camera into the scene, enlarges the foreground person
# and screen in the frame, and keeps the conveyor and guard in the foreground.
#
# Estimated expanded primitive count: approximately 180 meshes: architecture
# 25, machine and conveyor 90, screen and mount 8, people 45, accessories 12.
# Every box, ball and rod counts as one; no fillets, booleans or cloned layouts.

import math
import bpy
from mathutils import Vector
from sceneact import Scene, Asset, box, ball, rod, realize, set_view, area_emitter

scene = Scene("Cleanroom packaging line")

WHITE = (.84, .94, .92)
WALL = (.69, .84, .81)
FLOOR = (.67, .80, .77)
STEEL = (.45, .58, .58)
PALE_STEEL = (.66, .76, .75)
DARK = (.055, .10, .105)
BELT = (.86, .92, .86)
SKIN = (.73, .49, .36)
NET = (.61, .78, .76)
SCREEN = (.76, .91, .91)

def B(a, name, size, center, color, opacity=1):
    a.include(name, box(size=size, center=center, color=color, opacity=opacity))

def R(a, name, p, q, radius, color):
    a.include(name, rod(radius=radius, start=p, end=q, color=color))

def S(a, name, center, radius, scale, color):
    n = ball(radius=radius, center=center, color=color)
    n.resize(scale, pivot=center)
    a.include(name, n)

# Continuous enclosing room. Grid and panels are visible overhead rather than
# the exterior edge of the room.
room = Asset("Cleanroom architecture")
B(room, "floor", (14, 18, .10), (0, 3, -.06), FLOOR)
B(room, "back wall", (14, .10, 3.45), (0, 8, 1.72), WALL)
B(room, "right wall", (.10, 18, 3.45), (3.8, 3, 1.72), (.75,.87,.85))
B(room, "ceiling", (14, 18, .10), (0, 3, 3.48), (.71,.84,.82))
for i, x in enumerate((-3,-1.5,0,1.5,3)):
    B(room, "ceiling lengthwise frame %d" % i, (.025,15,.025),
      (x,2,3.41), (.52,.68,.66))
for i, y in enumerate((-3,-1,1,3,5,7)):
    B(room, "ceiling transverse frame %d" % i, (12,.025,.025),
      (0,y,3.41), (.53,.69,.67))
    for j, x in enumerate((-2.25,.75,2.25)):
        B(room, "recessed panel %d %d" % (i,j), (1.02,1.05,.025),
          (x,y+.62,3.405), (.96,1, .99))
for i, x in enumerate((-2,0,2)):
    B(room, "floor seam %d" % i, (.012,15,.006), (x,2,.002), (.55,.69,.67))
scene.include("architecture", room)

# Machine and belt run in the Y direction. The nearer belt end is intentionally
# close enough to be cut by the lower edge of the image.
machine = Asset("Stainless packaging machine")
B(machine, "lower stainless cabinet", (1.65,3.9,.78), (.85,1.05,.45), STEEL)
B(machine, "front cabinet panel", (1.56,.035,.63), (.85,-.92,.46), PALE_STEEL)
B(machine, "work deck", (1.78,3.95,.10), (.85,1.05,.89), STEEL)
for x in (.10,1.60):
    for y in (-.7,2.7):
        B(machine, "foot %.2f %.2f" % (x,y), (.10,.10,.14), (x,y,.07), DARK)

B(machine, "belt surface", (.82,4.9,.07), (.76,.55,.99), BELT)
for x in (.29,1.23):
    B(machine, "belt side channel %.2f" % x, (.065,4.85,.14), (x,.55,1.02), STEEL)
    B(machine, "guide rail %.2f" % x, (.035,4.0,.035), (x,.75,1.24), PALE_STEEL)
    for y in (-.8,.15,1.1,2.05,2.8):
        R(machine, "guide support %.2f %.2f" % (x,y),
          (x,y,1.02), (x,y,1.24), .019, STEEL)
for i in range(9):
    y = -1.35 + i*.47
    B(machine, "tray %02d" % i, (.65,.32,.035), (.76,y,1.045), (.92,.96,.90))
    B(machine, "tray leading lip %02d" % i, (.65,.025,.025),
      (.76,y-.15,1.07), (.74,.84,.79))

# Transparent guarding. Thin panes preserve a view of the distinct mechanisms.
for x in (-.02,1.68):
    for y in (-.48,.85,2.35):
        B(machine, "guard upright %.2f %.2f" % (x,y),
          (.042,.042,1.15), (x,y,1.53), PALE_STEEL)
    B(machine, "guard top rail %.2f" % x, (.045,2.90,.045),
      (x,.94,2.11), PALE_STEEL)
    B(machine, "guard mid rail %.2f" % x, (.035,2.90,.035),
      (x,.94,1.23), PALE_STEEL)
    B(machine, "transparent side %.2f" % x, (.012,2.80,1.07),
      (x,.94,1.54), (.68,.88,.86), .10)
for y in (-.48,2.35):
    B(machine, "guard cross rail %.2f" % y, (1.74,.04,.04),
      (.83,y,2.11), PALE_STEEL)
B(machine, "front transparent panel", (1.65,.012,1.05),
  (.83,-.48,1.55), (.68,.88,.86), .08)

# Cross members, actuators and shafts form a repeated but open mechanical array.
for k, y in enumerate((.45,1.35,2.25)):
    B(machine, "dark crossbeam %d" % k, (1.50,.11,.12), (.83,y,1.58), DARK)
    B(machine, "actuator plate %d" % k, (1.26,.30,.065), (.83,y,1.85), STEEL)
    R(machine, "cross shaft %d" % k, (.20,y,1.35), (1.45,y,1.35), .035, PALE_STEEL)
    for j, x in enumerate((.38,1.25)):
        R(machine, "pneumatic cylinder %d %d" % (k,j),
          (x,y,1.39), (x,y,1.80), .065, STEEL)
        R(machine, "piston %d %d" % (k,j),
          (x,y,1.17), (x,y,1.40), .024, PALE_STEEL)
        B(machine, "cylinder mount %d %d" % (k,j),
          (.18,.18,.08), (x,y,1.82), DARK)
for x in (.22,1.45):
    B(machine, "long profile %.2f" % x, (.08,2.7,.09), (x,1.0,1.46), DARK)
    for y in (.2,1.05,1.9):
        B(machine, "profile bracket %.2f %.2f" % (x,y),
          (.15,.14,.16), (x,y,1.47), STEEL)
B(machine, "rear motor housing", (.50,.46,.44), (.99,2.05,1.76), DARK)
B(machine, "front nameplate", (.25,.015,.09), (.90,-.945,.70), (.87,.93,.90))
B(machine, "side nameplate", (.015,.27,.10), (1.69,.6,1.04), (.87,.93,.90))
scene.include("packaging line", machine)

# Adjacent posts and small fixtures at the right edge of the photograph.
fixtures = Asset("Conveyor auxiliary fixtures")
for i, y in enumerate((-1.10,-.45,.25)):
    x = 1.66
    R(fixtures, "vertical post %d" % i, (x,y,.78), (x,y,1.33), .038, STEEL)
    B(fixtures, "post cap %d" % i, (.16,.16,.08), (x,y,1.34), DARK)
    B(fixtures, "small bracket %d" % i, (.28,.12,.08), (x-.10,y,1.05), PALE_STEEL)
scene.include("auxiliary fixtures", fixtures)

# HMI panel faces toward the camera and operator. Components share a tilted pivot.
hmi = Asset("Touchscreen and articulated arm")
R(hmi, "vertical support", (1.52,.76,1.63), (1.52,.76,2.30), .065, STEEL)
R(hmi, "rear articulated arm", (1.52,.76,2.30), (1.20,.35,2.38), .075, DARK)
R(hmi, "front articulated arm", (1.20,.35,2.38), (1.00,.08,2.43), .055, STEEL)
S(hmi, "arm joint", (1.20,.35,2.38), .105, (1,1,1), DARK)
pivot = (.83,-.02,2.42)
def panel(name, size, center, color):
    n = box(size=size, center=center, color=color)
    n.turn(axis="+y", degrees=12, pivot=pivot)
    hmi.include(name, n)
panel("panel housing", (.83,.10,.79), pivot, (.39,.49,.51))
panel("silver frame", (.78,.024,.74), (.83,-.082,2.42), (.80,.89,.87))
panel("display surface", (.66,.012,.62), (.83,-.100,2.42), SCREEN)
panel("display bottom stripe", (.62,.008,.028), (.83,-.109,2.17), (.56,.68,.72))
scene.include("HMI", hmi)

def person(name, x, y, scale, foreground):
    p = Asset(name)
    def P(v):
        return (x+v[0]*scale, y+v[1]*scale, v[2]*scale)
    def PB(n,size,pos,col):
        B(p,n,tuple(v*scale for v in size),P(pos),col)
    def PR(n,a,b,r,col):
        R(p,n,P(a),P(b),r*scale,col)
    def PS(n,pos,r,shape,col):
        S(p,n,P(pos),r*scale,shape,col)

    PB("coat upper body", (.52,.32,.78), (0,0,1.16), WHITE)
    PB("coat lower body", (.59,.34,.64), (0,0,.58), (.82,.92,.90))
    PB("coat front seam", (.012,.015,.86), (0,-.177,.93), (.68,.80,.78))
    for side in (-1,1):
        PB("trouser %d" % side, (.19,.22,.42), (side*.14,0,.23), DARK)
        PB("shoe %d" % side, (.20,.30,.09), (side*.14,-.04,.05), (.10,.17,.17))
    PR("neck", (0,0,1.48), (0,0,1.62), .09, SKIN)
    PS("face", (.025,-.01,1.73), .155, (.82,.90,1.16), SKIN)
    PS("hairnet", (-.025,.035,1.82), .17, (1,.93,.76), NET)
    PR("hairnet front edge", (-.14,-.075,1.79), (.11,-.075,1.79), .012, (.85,.94,.91))
    if foreground:
        # Raised sleeve and hand continue toward the screen.
        PR("upper raised sleeve", (.22,0,1.39), (.47,-.02,1.43), .13, WHITE)
        PR("fore raised sleeve", (.47,-.02,1.43), (.78,-.02,1.66), .105, WHITE)
        PR("wrist and hand", (.78,-.02,1.66), (.88,-.02,1.72), .050, SKIN)
        PR("lower sleeve", (-.22,0,1.38), (-.26,-.04,.98), .105, WHITE)
        PR("lower hand", (-.26,-.04,.98), (-.23,-.10,.88), .045, SKIN)
        PS("nose", (.14,-.045,1.74), .04, (1,.7,.8), SKIN)
    else:
        for side in (-1,1):
            PR("upper sleeve %d" % side, (side*.22,0,1.36),
               (side*.27,-.05,1.04), .105, WHITE)
            PR("bent sleeve %d" % side, (side*.27,-.05,1.04),
               (side*.05,-.20,1.02), .077, WHITE)
            PS("hand %d" % side, (side*.05,-.20,1.02), .055, (1,1,.7), SKIN)
        for side in (-1,1):
            PR("glasses %d" % side, (side*.015,-.148,1.76),
               (side*.095,-.14,1.76), .009, DARK)
    scene.include(name, p)

person("Foreground operator", -.91,-.18,1.12,True)
person("Background operator", -2.05,2.10,.98,False)

realize(scene)

# Preserve the palette while assigning restrained reflective and screen finishes.
for mat in bpy.data.materials:
    if not mat.use_nodes:
        mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf is None:
        continue
    c = tuple(bsdf.inputs["Base Color"].default_value[:3])
    bsdf.inputs["Roughness"].default_value = .48
    if max(c)-min(c) < .17 and .30 < sum(c)/3 < .70:
        bsdf.inputs["Metallic"].default_value = .55
        bsdf.inputs["Roughness"].default_value = .30

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
background.inputs["Color"].default_value = (.73,.88,.86,1)
background.inputs["Strength"].default_value = .48

set_view((2.4,-4.0,2.05), (-.05,.68,1.65), lens=38)
area_emitter((-.8,-1.2,3.3), power=450, size=4,
             target=(0,.8,1.1), color=(.90,1,.98))
area_emitter((-2,2.5,3.3), power=350, size=3,
             target=(-.5,1,1), color=(.90,.98,1))
area_emitter((2.5,2.5,3.25), power=400, size=3,
             target=(.6,1,1.2), color=(.92,1,.98))

sc.render.engine = "CYCLES"
sc.cycles.samples = 32
sc.render.resolution_x = 1536
sc.render.resolution_y = 1023
sc.render.resolution_percentage = 100
sc.view_settings.view_transform = "AgX"
sc.camera.data.dof.use_dof = True
sc.camera.data.dof.focus_distance = (sc.camera.location - Vector((-.91,-.18,1.6))).length
sc.camera.data.dof.aperture_fstop = 8.0
