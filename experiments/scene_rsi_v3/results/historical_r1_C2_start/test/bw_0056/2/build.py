# Reference inventory, approximate normalized image bounds:
# Cleanroom ceiling, lights and pale walls: whole background; floor mostly hidden.
# Foreground operator: x=.17-.68, y=0-1; hairnet and profile, white coat,
# raised arm reaching to the HMI; lower body cropped by the image.
# Background operator: x=0-.21, y=.14-1; white coat, hairnet, glasses, hands.
# Packaging line: x=.40-1, y=.32-1; steel framing, dark mechanisms, transparent
# guards and pale conveyor extending toward the viewer.
# HMI: x=.61-.80, y=.06-.45; tilted silver panel and articulated rear mount.
# Small conveyor posts and fixtures: x=.78-1, y=.69-1.
# Equipment behind the guard and room depth are partly occluded and uncertain.
#
# Feedback comparison: the previous full view places both people too far away
# and behind the guard. The foreground figure should dominate the left-center,
# with her hand at the screen; the conveyor should enter from the lower right.
# The previous screen is viewed from behind and appears too high. This revision
# moves the operator forward, faces the display toward the camera and operator,
# and uses a more level camera while retaining the machine and its component
# hierarchy. Exact hidden machinery remains an estimate.
#
# Expanded primitive estimate: approximately 165 meshes: room 30, machine 85,
# HMI 8, people 30, auxiliary fixtures 12. Each box, rod and ball emits one
# primitive. No fillets, Boolean operations, cloning or tube expansions.

import bpy
from mathutils import Vector
from sceneact import Scene, Asset, box, ball, rod, realize, set_view, area_emitter

scene = Scene("Cleanroom packaging line")

WHITE = (.84, .93, .91)
WALL = (.71, .84, .82)
FLOOR = (.68, .80, .78)
STEEL = (.43, .56, .56)
LIGHT_STEEL = (.68, .78, .77)
DARK = (.055, .105, .11)
BELT = (.87, .93, .87)
SKIN = (.76, .52, .39)
NET = (.60, .77, .75)
SCREEN = (.80, .94, .94)

def B(asset, name, size, center, color, opacity=1):
    asset.include(name, box(size=size, center=center, color=color, opacity=opacity))

def R(asset, name, start, end, radius, color):
    asset.include(name, rod(radius=radius, start=start, end=end, color=color))

def S(asset, name, center, radius, scale, color):
    node = ball(radius=radius, center=center, color=color)
    node.resize(scale, pivot=center)
    asset.include(name, node)

# Architecture: an enclosed cleanroom, extending beyond the camera view.
room = Asset("Cleanroom architecture")
B(room, "anti-static floor", (14, 18, .10), (0, 3, -.06), FLOOR)
B(room, "back wall", (14, .10, 3.25), (0, 8, 1.62), WALL)
B(room, "left wall", (.10, 18, 3.25), (-4.0, 3, 1.62), WALL)
B(room, "right wall", (.10, 18, 3.25), (3.7, 3, 1.62), (.76, .87, .85))
B(room, "suspended ceiling", (14, 18, .10), (0, 3, 3.30), (.72, .84, .82))
for i, x in enumerate((-3, -1.5, 0, 1.5, 3)):
    B(room, "ceiling longitudinal grid %d" % i, (.025, 15, .025),
      (x, 2, 3.23), (.56, .70, .68))
for i, y in enumerate((-3, -1, 1, 3, 5, 7)):
    B(room, "ceiling cross grid %d" % i, (8, .025, .025),
      (0, y, 3.23), (.56, .70, .68))
    for j, x in enumerate((-2.25, .75, 2.25)):
        B(room, "recessed light %d %d" % (i, j), (1.00, 1.03, .025),
          (x, y + .60, 3.215), (.96, 1.0, .99))
for i, x in enumerate((-2, 0, 2)):
    B(room, "floor seam %d" % i, (.012, 15, .006),
      (x, 2, .002), (.55, .69, .67))
scene.include("architecture", room)

# Packaging machine. The line runs along the room depth, with its near end
# entering the bottom right of the camera view.
machine = Asset("Stainless packaging machine")
B(machine, "lower cabinet", (1.55, 4.0, .74), (.90, 1.05, .44), STEEL)
B(machine, "front cabinet panel", (1.48, .035, .60),
  (.90, -.97, .45), LIGHT_STEEL)
B(machine, "work deck", (1.72, 4.05, .10), (.90, 1.05, .88), STEEL)
for x in (.18, 1.62):
    for y in (-.70, 2.70):
        B(machine, "foot %.2f %.2f" % (x, y), (.10, .10, .14),
          (x, y, .07), DARK)

B(machine, "conveyor belt", (.76, 5.0, .075), (.87, .45, .99), BELT)
for x in (.43, 1.31):
    B(machine, "belt side channel %.2f" % x, (.065, 4.95, .14),
      (x, .45, 1.02), STEEL)
    B(machine, "upper guide rail %.2f" % x, (.032, 4.0, .035),
      (x, .70, 1.24), LIGHT_STEEL)
    for y in (-1.1, -.2, .7, 1.6, 2.5):
        R(machine, "guide support %.2f %.2f" % (x, y),
          (x, y, 1.02), (x, y, 1.24), .018, STEEL)
for i in range(9):
    y = -1.45 + i * .47
    B(machine, "tray %02d" % i, (.62, .32, .035),
      (.87, y, 1.05), (.92, .96, .90))
    B(machine, "tray lip %02d" % i, (.62, .022, .023),
      (.87, y - .15, 1.075), (.75, .84, .79))

# Guard frame and lightly tinted transparent panels.
for x in (.08, 1.70):
    for y in (-.40, .90, 2.30):
        B(machine, "guard upright %.2f %.2f" % (x, y),
          (.045, .045, 1.13), (x, y, 1.53), LIGHT_STEEL)
    B(machine, "guard top rail %.2f" % x, (.045, 2.75, .045),
      (x, .95, 2.10), LIGHT_STEEL)
    B(machine, "guard middle rail %.2f" % x, (.035, 2.75, .035),
      (x, .95, 1.24), LIGHT_STEEL)
    B(machine, "clear side pane %.2f" % x, (.012, 2.68, 1.05),
      (x, .95, 1.54), (.68, .88, .86), .08)
for y in (-.40, 2.30):
    B(machine, "guard cross rail %.2f" % y, (1.65, .045, .045),
      (.89, y, 2.10), LIGHT_STEEL)
B(machine, "clear front pane", (1.58, .012, 1.05),
  (.89, -.40, 1.54), (.68, .88, .86), .07)

# Open mechanical assembly visible through the guard.
for k, y in enumerate((.45, 1.35, 2.20)):
    B(machine, "dark crossbeam %d" % k, (1.45, .11, .12),
      (.89, y, 1.58), DARK)
    B(machine, "actuator plate %d" % k, (1.20, .30, .065),
      (.89, y, 1.84), STEEL)
    R(machine, "cross shaft %d" % k, (.28, y, 1.35),
      (1.48, y, 1.35), .035, LIGHT_STEEL)
    for j, x in enumerate((.46, 1.29)):
        R(machine, "pneumatic cylinder %d %d" % (k, j),
          (x, y, 1.39), (x, y, 1.79), .064, STEEL)
        R(machine, "piston rod %d %d" % (k, j),
          (x, y, 1.17), (x, y, 1.40), .024, LIGHT_STEEL)
        B(machine, "actuator mount %d %d" % (k, j),
          (.18, .18, .08), (x, y, 1.81), DARK)
for x in (.30, 1.50):
    B(machine, "long profile %.2f" % x, (.08, 2.7, .09),
      (x, 1.0, 1.46), DARK)
    for y in (.2, 1.05, 1.9):
        B(machine, "profile bracket %.2f %.2f" % (x, y),
          (.15, .14, .16), (x, y, 1.47), STEEL)
B(machine, "rear motor housing", (.50, .46, .44),
  (1.05, 2.05, 1.76), DARK)
B(machine, "front nameplate", (.25, .015, .09),
  (.95, -.995, .70), (.87, .93, .90))
B(machine, "side nameplate", (.015, .27, .10),
  (1.72, .60, 1.04), (.87, .93, .90))
scene.include("packaging line", machine)

fixtures = Asset("Conveyor auxiliary fixtures")
for i, y in enumerate((-1.3, -.65, .15)):
    R(fixtures, "vertical post %d" % i,
      (1.83, y, .78), (1.83, y, 1.33), .038, STEEL)
    B(fixtures, "dark post cap %d" % i, (.16, .16, .08),
      (1.83, y, 1.34), DARK)
    B(fixtures, "small bracket %d" % i, (.28, .12, .08),
      (1.73, y, 1.05), LIGHT_STEEL)
scene.include("auxiliary fixtures", fixtures)

# The screen faces toward negative Y. Its tilted rectangular surface remains
# separate from the housing, bezel, pivot and adjustable support.
hmi = Asset("Touchscreen and articulated support")
R(hmi, "vertical support", (1.52, .68, 1.61),
  (1.52, .68, 2.26), .065, STEEL)
R(hmi, "rear arm", (1.52, .68, 2.26),
  (1.24, .20, 2.34), .073, DARK)
R(hmi, "front arm", (1.24, .20, 2.34),
  (1.08, -.10, 2.38), .052, STEEL)
S(hmi, "arm joint", (1.24, .20, 2.34), .10, (1, 1, 1), DARK)
pivot = (1.00, -.30, 2.31)
def panel(name, size, center, color):
    node = box(size=size, center=center, color=color)
    node.turn(axis="+y", degrees=16, pivot=pivot)
    hmi.include(name, node)
panel("panel housing", (.72, .10, .83), pivot, (.37, .49, .50))
panel("silver bezel", (.67, .024, .77), (1.00, -.362, 2.31),
      (.79, .88, .86))
panel("illuminated display", (.56, .012, .65), (1.00, -.380, 2.31),
      SCREEN)
panel("lower display stripe", (.53, .008, .025), (1.00, -.390, 2.03),
      (.56, .69, .72))
scene.include("HMI", hmi)

# Foreground operator: body closer to camera, with raised sleeve and hand
# reaching the panel. Smooth scaled balls keep this figure a simple placeholder.
foreground = Asset("Foreground operator")
S(foreground, "coat torso", (-.70, -1.92, 1.13), .48,
  (.75, .43, 1.10), WHITE)
S(foreground, "coat lower body", (-.72, -1.92, .62), .47,
  (.78, .44, 1.10), (.82, .92, .90))
R(foreground, "coat seam", (-.72, -2.135, .42),
  (-.70, -2.135, 1.28), .009, (.70, .81, .79))
R(foreground, "neck", (-.67, -1.92, 1.50),
  (-.67, -1.92, 1.65), .085, SKIN)
S(foreground, "face", (-.63, -1.92, 1.77), .16,
  (.78, .86, 1.12), SKIN)
S(foreground, "nose", (-.50, -1.95, 1.78), .039,
  (1.0, .7, .8), SKIN)
S(foreground, "hairnet", (-.70, -1.91, 1.85), .18,
  (1.02, .95, .78), NET)
R(foreground, "hairnet edge", (-.82, -2.04, 1.82),
  (-.59, -2.04, 1.82), .012, (.85, .94, .91))
R(foreground, "raised upper sleeve", (-.46, -1.92, 1.39),
  (-.12, -1.53, 1.43), .135, WHITE)
R(foreground, "raised fore sleeve", (-.12, -1.53, 1.43),
  (.43, -.88, 1.83), .105, WHITE)
R(foreground, "hand at display", (.43, -.88, 1.83),
  (.62, -.65, 2.00), .048, SKIN)
R(foreground, "lower sleeve", (-.97, -1.91, 1.36),
  (-1.00, -2.00, .94), .10, WHITE)
for side in (-1, 1):
    B(foreground, "trouser %d" % side, (.19, .22, .42),
      (-.72 + side * .14, -1.92, .23), DARK)
scene.include("foreground operator", foreground)

# Background person, partly cut by the left frame.
background_person = Asset("Background operator")
S(background_person, "coat torso", (-1.75, 1.1, 1.12), .43,
  (.72, .42, 1.05), WHITE)
S(background_person, "coat skirt", (-1.75, 1.1, .58), .43,
  (.76, .43, 1.05), (.82, .92, .90))
R(background_person, "neck", (-1.75, 1.1, 1.46),
  (-1.75, 1.1, 1.60), .08, SKIN)
S(background_person, "face", (-1.75, 1.08, 1.70), .15,
  (.82, .88, 1.13), SKIN)
S(background_person, "hairnet", (-1.77, 1.11, 1.80), .16,
  (1, .94, .76), NET)
for side in (-1, 1):
    R(background_person, "sleeve %d" % side,
      (-1.75 + side * .22, 1.1, 1.34),
      (-1.75 + side * .25, 1.0, 1.02), .095, WHITE)
    R(background_person, "bent sleeve %d" % side,
      (-1.75 + side * .25, 1.0, 1.02),
      (-1.75 + side * .04, .91, 1.04), .07, WHITE)
    S(background_person, "hand %d" % side,
      (-1.75 + side * .04, .91, 1.04), .05, (1, 1, .8), SKIN)
    R(background_person, "glasses %d" % side,
      (-1.75 + side * .015, .944, 1.73),
      (-1.75 + side * .095, .95, 1.73), .009, DARK)
    B(background_person, "trouser %d" % side, (.18, .20, .40),
      (-1.75 + side * .13, 1.1, .22), DARK)
scene.include("background operator", background_person)

realize(scene)

# Restrained steel reflections and a softly luminous HMI.
for mat in bpy.data.materials:
    if not mat.use_nodes:
        mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf is None:
        continue
    c = tuple(bsdf.inputs["Base Color"].default_value[:3])
    bsdf.inputs["Roughness"].default_value = .48
    if max(c) - min(c) < .17 and .30 < sum(c) / 3 < .70:
        bsdf.inputs["Metallic"].default_value = .55
        bsdf.inputs["Roughness"].default_value = .30
    if c[0] > .77 and c[1] > .91 and c[2] > .91:
        if "Emission Color" in bsdf.inputs:
            bsdf.inputs["Emission Color"].default_value = (c[0], c[1], c[2], 1)
            bsdf.inputs["Emission Strength"].default_value = .16

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
background.inputs["Color"].default_value = (.73, .88, .86, 1)
background.inputs["Strength"].default_value = .48

set_view((.05, -5.0, 1.72), (.05, .4, 1.67), lens=35)
area_emitter((-.8, -1.8, 3.1), power=420, size=4,
             target=(0, 0, 1.1), color=(.90, 1, .98))
area_emitter((-2, 2.5, 3.1), power=350, size=3,
             target=(-.5, 1, 1), color=(.90, .98, 1))
area_emitter((2.5, 2.5, 3.1), power=400, size=3,
             target=(.8, 1, 1.2), color=(.92, 1, .98))

sc.render.engine = "CYCLES"
sc.cycles.samples = 32
sc.render.resolution_x = 1536
sc.render.resolution_y = 1023
sc.render.resolution_percentage = 100
sc.view_settings.view_transform = "AgX"
sc.camera.data.dof.use_dof = True
sc.camera.data.dof.focus_distance = (
    sc.camera.location - Vector((-.70, -1.92, 1.55))
).length
sc.camera.data.dof.aperture_fstop = 8.0
