# Reference inventory and comparison with the first rendered view:
# - Foreground operator: reference approximately (0.17, 0.00)-(0.68, 1.00);
#   previous render approximately (0.27, 0.31)-(0.46, 0.85). The operator was
#   much too small, and the head and coat failed to reach the top and bottom crops.
# - Background worker: reference approximately (0.00, 0.15)-(0.21, 1.00);
#   previous render: not visibly distinguishable against the left wall.
# - HMI: reference approximately (0.62, 0.06)-(0.79, 0.45); previous render
#   approximately (0.56, 0.26)-(0.68, 0.48). It was too small and too low.
# - Belt front: reference approximately (0.55, 0.80)-(0.84, 1.00); previous
#   render approximately (0.35, 0.68)-(0.60, 0.84). It was too far left and
#   its near end was too high. Its sides should converge toward the center.
# - Background: the reference shows bright ceiling panels and equipment behind
#   the people; the previous view had an extensive blank gray left wall and
#   a large expanse of floor. Its machine appeared as a large pale closed block,
#   whereas the reference has a darker, open mechanical region with clear guards.
# Ranked corrections by visible extent and contrast:
# 1. Bring the foreground person closer and increase their image size; move the
#    background person into the visible left side. This changes their contours
#    independently of the machine and should make the foreground coat crop.
# 2. Lower and straighten the camera's view, narrowing the visible floor and
#    showing more of the ceiling and vertical machine structure.
# 3. Move the belt right in the frame, extend its foreground end, and open up
#    the machine base so the guard, dark machinery, and gaps are visible.
# 4. Raise and enlarge the HMI locally, giving it a tall sloping frame and
#    connecting the operator's hand to its left edge.
# Camera trial projections are printed below, before and after a small aim
# change. These numerical point projections do not measure visible contours.
# Occluded machine internals, products and the far room remain approximate.
#
# Expanded primitive estimate: architecture 37, machine 100, HMI 9,
# foreground operator 18, background operator 18, total roughly 182.
# All are boxes, balls or rods; no booleans, fillets, clones or tube expansions.

from sceneact import *
import bpy
import math
from mathutils import Vector

scene = Scene("Cleanroom packaging line")

# Camera pose is independent of the asset parameters. The more level view
# moves the floor/ceiling boundary down and makes foreground verticals larger.
CAM_POS = (0.0, -7.0, 2.10)
CAM_TARGET = (0.0, 1.0, 2.03)
CAM_LENS = 42.0

ROOM_W = 9.0
ROOM_D = 14.0
ROOM_H = 3.35
LINE_X = 1.20
BELT_W = 1.08
BELT_FRONT = -2.25
BELT_BACK = 5.2
BELT_Z = 0.88

white = (0.82, 0.91, 0.89)
coat = (0.86, 0.94, 0.92)
wall = (0.68, 0.81, 0.79)
floor = (0.64, 0.76, 0.73)
steel = (0.42, 0.55, 0.54)
steel_light = (0.66, 0.76, 0.74)
darksteel = (0.09, 0.16, 0.16)
black = (0.025, 0.045, 0.045)
belt_color = (0.82, 0.90, 0.87)
glass_color = (0.54, 0.77, 0.75)
skin = (0.72, 0.48, 0.37)
hairnet = (0.60, 0.77, 0.75)

def B(parent, name, size, center, color, opacity=1):
    parent.include(name, box(size=size, center=center, color=color, opacity=opacity))

def R(parent, name, start, end, radius, color):
    parent.include(name, rod(radius=radius, start=start, end=end, color=color))

def E(parent, name, center, radius_xyz, color):
    obj = ball(1, center=center, color=color)
    obj.resize(radius_xyz, pivot=center)
    parent.include(name, obj)

# The front and left sides are open for the camera. The far wall is deliberately
# pale rather than a dark plane; the ceiling grid supplies the visible depth cues.
room = Asset("Cleanroom architecture")
B(room, "floor", (ROOM_W, ROOM_D, .08), (0, 2, -.05), floor)
B(room, "back wall", (ROOM_W, .08, ROOM_H), (0, 8.0, ROOM_H/2), wall)
B(room, "right wall", (.08, ROOM_D, ROOM_H), (4.5, 1.0, ROOM_H/2),
  (0.72, 0.84, 0.82))
B(room, "ceiling", (ROOM_W, ROOM_D, .08), (0, 1.0, ROOM_H), (0.77, .87, .85))
for x in (-4, -2.5, -1, .5, 2, 3.5):
    B(room, "ceiling rail x %.1f" % x, (.025, 13.8, .02),
      (x, 1, ROOM_H-.05), (.58, .70, .68))
for y in (-4, -2, 0, 2, 4, 6, 7.9):
    B(room, "ceiling rail y %.1f" % y, (8.95, .025, .02),
      (0, y, ROOM_H-.05), (.58, .70, .68))
for x in (-3.25, -1.75, -.25, 1.25, 2.75):
    for y in (-3, -1, 1, 3, 5, 7):
        B(room, "recessed panel %.2f %.2f" % (x, y), (1.05, 1.13, .025),
          (x, y, ROOM_H-.065), (1.0, 1.0, .97))
for x in (-3, -1, 1, 3):
    B(room, "floor seam x %.1f" % x, (.012, 13.8, .004),
      (x, 1, -.008), (.53, .67, .65))
for y in (-2, 0, 2, 4, 6):
    B(room, "floor seam y %.1f" % y, (8.9, .012, .004),
      (0, y, -.007), (.53, .67, .65))
scene.include("architecture", room)

machine = Asset("Stainless packaging machine")
# White lower body is kept below the belt. The space above is open and dark.
B(machine, "lower enclosure", (1.55, 4.55, .43),
  (LINE_X, 1.15, .42), (.56, .68, .66))
B(machine, "base front fascia", (1.55, .05, .39),
  (LINE_X, -1.13, .43), (.67, .77, .75))
B(machine, "recessed front panel", (.36, .01, .105),
  (LINE_X+.43, -1.163, .48), (.83, .89, .86))
B(machine, "nameplate stripe", (.17, .01, .012),
  (LINE_X+.43, -1.171, .49), darksteel)

# Conveyor and narrow side guides. Its near end continues below the frame.
belt_mid = (BELT_FRONT + BELT_BACK)/2
belt_len = BELT_BACK - BELT_FRONT
B(machine, "conveyor bed", (BELT_W+.12, belt_len, .10),
  (LINE_X, belt_mid, BELT_Z-.06), darksteel)
B(machine, "light belt", (BELT_W, belt_len, .035),
  (LINE_X, belt_mid, BELT_Z), belt_color)
for x in (LINE_X-BELT_W/2-.04, LINE_X+BELT_W/2+.04):
    B(machine, "belt side rail %.2f" % x, (.055, belt_len, .105),
      (x, belt_mid, BELT_Z+.035), steel)
    B(machine, "raised guide %.2f" % x, (.035, 4.6, .035),
      (x, 1.6, 1.12), steel_light)
    for y in (-.25, 1.0, 2.25, 3.5):
        R(machine, "guide riser %.2f %.2f" % (x, y),
          (x, y, .92), (x, y, 1.12), .016, steel)
for i, y in enumerate((.0, .65, 1.30, 1.95, 2.60, 3.25, 3.90)):
    B(machine, "waiting tray %d" % i, (.62, .39, .028),
      (LINE_X, y, BELT_Z+.035), (.76, .85, .74))
    B(machine, "tray contents %d" % i, (.50, .27, .018),
      (LINE_X, y, BELT_Z+.057), (.68, .78, .61))

# Guard posts and rails, including foreground glass panels. Thin transparent
# sheets are schematic; their reflections and the framing mark the enclosure.
for x in (LINE_X-.83, LINE_X+.83):
    for y in (-1.0, .35, 1.75, 3.20):
        B(machine, "guard post %.2f %.2f" % (x, y), (.055, .055, 1.02),
          (x, y, 1.39), steel_light)
    B(machine, "guard top rail %.2f" % x, (.055, 4.26, .055),
      (x, 1.10, 1.91), steel_light)
    B(machine, "guard mid rail %.2f" % x, (.045, 4.26, .045),
      (x, 1.10, 1.02), steel)
    for j, (y0, y1) in enumerate(((-.97, .32), (.38, 1.72), (1.78, 3.17))):
        B(machine, "clear side panel %.2f %d" % (x, j),
          (.012, y1-y0, .85), (x, (y0+y1)/2, 1.45), glass_color, .12)
for y in (-1.0, .35, 1.75, 3.2):
    B(machine, "top crossbar %.2f" % y, (1.69, .055, .055),
      (LINE_X, y, 1.91), steel_light)
B(machine, "front guard pane", (1.61, .012, .85),
  (LINE_X, -1.01, 1.45), glass_color, .10)

# Dark head and open mechanical layers are the prominent central high-contrast
# area in the photograph. The exact hidden arrangement is uncertain.
B(machine, "dark head housing", (1.15, .76, .55),
  (LINE_X, 2.28, 1.68), (.055, .10, .10))
B(machine, "upper head plate", (1.43, 1.05, .075),
  (LINE_X, 2.27, 1.98), steel)
B(machine, "lower head plate", (1.38, 1.05, .075),
  (LINE_X, 2.27, 1.36), steel)
for x in (LINE_X-.47, LINE_X-.16, LINE_X+.16, LINE_X+.47):
    R(machine, "actuator cylinder %.2f" % x,
      (x, 1.77, 1.57), (x, 1.77, 1.91), .047, steel_light)
    R(machine, "actuator piston %.2f" % x,
      (x, 1.77, 1.35), (x, 1.77, 1.57), .019, steel)
for z in (1.40, 1.57, 1.78):
    R(machine, "linkage %.2f" % z, (LINE_X-.61, 1.70, z),
      (LINE_X+.61, 1.70, z), .022, darksteel)
for y in (.10, .8, 2.95, 3.35):
    B(machine, "machine cross rail %.2f" % y, (1.47, .07, .065),
      (LINE_X, y, 1.01), steel)
# Separate upright equipment at the right foreground.
for i, x in enumerate((2.17, 2.62, 3.03, 3.43)):
    B(machine, "right upright %d" % i, (.09, .11, .63),
      (x, -1.15, .72), steel)
    B(machine, "right upright cap %d" % i, (.13, .14, .06),
      (x, -1.15, 1.06), black)
    B(machine, "right foot %d" % i, (.18, .23, .10),
      (x, -1.15, .36), darksteel)
scene.include("packaging machine", machine)

# The HMI face is a tall thin rectangle tilted in its own plane. Its normal
# faces the camera and the operator, with an articulated mount behind.
hmi = Asset("Articulated touchscreen")
R(hmi, "support mast", (1.83, .75, 1.83), (1.83, .75, 2.40), .065, darksteel)
R(hmi, "support elbow", (1.83, .75, 2.40), (1.53, .35, 2.60), .060, steel)
E(hmi, "round hinge", (1.83, .75, 2.40), (.10, .10, .10), darksteel)
panel_center = (1.27, .20, 2.48)
panel = box((.74, .085, 1.19), center=panel_center, color=(.38, .51, .50))
panel.turn(axis="+y", degrees=20, pivot=panel_center)
hmi.include("screen metal rim", panel)
screen_center = (1.27, .148, 2.48)
display = box((.62, .018, 1.04), center=screen_center, color=(.79, .92, .93))
display.turn(axis="+y", degrees=20, pivot=screen_center)
hmi.include("screen face", display)
# A simple pale interface stripe preserves the display's luminous appearance.
stripe_center = (1.27, .135, 2.50)
stripe = box((.46, .008, .79), center=stripe_center, color=(.88, .96, .95))
stripe.turn(axis="+y", degrees=20, pivot=stripe_center)
hmi.include("display interior", stripe)
scene.include("HMI", hmi)

# Foreground operator is closer to the camera than the equipment. The coat is
# constructed from broad overlapping volumes and a hem rather than a single
# oval so that it retains a roughly straight work-coat silhouette.
person = Asset("Foreground operator")
B(person, "coat body", (.71, .35, 1.05), (-1.10, -3.05, 1.03), coat)
E(person, "coat shoulder", (-1.10, -3.05, 1.55), (.38, .22, .22), coat)
B(person, "coat skirt", (.78, .38, .65), (-1.10, -3.05, .48), (.84, .92, .90))
B(person, "coat front seam", (.018, .012, .93), (-.83, -3.25, .98), (.71, .82, .80))
E(person, "neck", (-1.08, -3.05, 1.72), (.11, .10, .13), skin)
E(person, "head", (-1.02, -3.05, 1.91), (.15, .13, .21), skin)
E(person, "face profile", (-.89, -3.06, 1.91), (.07, .10, .12), skin)
E(person, "nose", (-.82, -3.08, 1.94), (.045, .045, .037), skin)
E(person, "hairnet", (-1.10, -3.02, 2.06), (.19, .16, .15), hairnet)
R(person, "hairnet lower edge", (-1.27, -3.12, 2.02),
  (-.98, -3.12, 1.99), .015, (.79, .88, .85))
# The bent arm extends toward the screen, with an elbow and tapered forearm.
R(person, "upper sleeve", (-.79, -3.02, 1.56), (-.38, -2.94, 1.49), .14, coat)
E(person, "elbow", (-.38, -2.94, 1.49), (.14, .14, .14), coat)
R(person, "forearm sleeve", (-.38, -2.94, 1.49), (.08, -2.55, 1.82), .105, coat)
E(person, "cuff", (.08, -2.55, 1.82), (.11, .10, .08), white)
E(person, "touching hand", (.17, -2.48, 1.88), (.12, .07, .06), skin)
R(person, "lower sleeve", (-1.40, -3.05, 1.48), (-1.42, -3.05, .98), .10, coat)
scene.include("foreground operator", person)

# Second worker stands far enough back to be smaller, at image left.
worker = Asset("Background operator")
B(worker, "coat body", (.62, .32, 1.03), (-2.42, .85, 1.02), coat)
E(worker, "shoulders", (-2.42, .85, 1.48), (.34, .19, .20), coat)
B(worker, "coat skirt", (.68, .34, .55), (-2.42, .85, .53), (.84, .92, .90))
for side in (-1, 1):
    E(worker, "trouser leg %d" % side, (-2.42+side*.13, .85, .22),
      (.12, .13, .25), (.12, .18, .17))
E(worker, "head", (-2.42, .84, 1.78), (.14, .12, .19), skin)
E(worker, "hairnet", (-2.42, .85, 1.91), (.16, .14, .12), hairnet)
R(worker, "glasses", (-2.54, .715, 1.80), (-2.30, .715, 1.80), .012, darksteel)
R(worker, "left upper sleeve", (-2.68, .83, 1.40), (-2.69, .76, 1.09), .09, coat)
R(worker, "left forearm", (-2.69, .76, 1.09), (-2.40, .69, 1.00), .075, coat)
R(worker, "right upper sleeve", (-2.16, .83, 1.40), (-2.16, .76, 1.10), .09, coat)
R(worker, "right forearm", (-2.16, .76, 1.10), (-2.35, .69, 1.00), .075, coat)
E(worker, "hands", (-2.37, .68, 1.00), (.10, .06, .06), skin)
scene.include("background worker", worker)

realize(scene)
set_view(CAM_POS, CAM_TARGET, lens=CAM_LENS, sensor=36)
sc = bpy.context.scene
sc.render.resolution_x = 1536
sc.render.resolution_y = 1023
sc.render.resolution_percentage = 100

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
background.inputs["Color"].default_value = (.72, .86, .83, 1)
background.inputs["Strength"].default_value = .55

area_emitter((-1, -3, 3.15), power=500, size=4.0,
             target=(-.5, 0, 1.2), color=(.88, 1.0, .97))
area_emitter((1, 1, 3.15), power=650, size=4.0,
             target=(1, 1, 1), color=(.88, 1.0, .98))
area_emitter((-2, 5, 3.15), power=500, size=3.5,
             target=(0, 2, 1), color=(.86, .98, 1.0))

# Reference estimates and world-space points are kept separate. The screen
# top and belt corner are on geometry; ceiling point is a panel corner.
landmarks = [
    ("HMI upper edge", (1.07, .20, 3.04), (.74, .06)),
    ("belt front left", (LINE_X-BELT_W/2, BELT_FRONT, BELT_Z), (.56, .84)),
    ("machine head top", (LINE_X, 2.27, 2.02), (.55, .38)),
    ("background panel corner", (-2.275, 4.435, ROOM_H-.065), (.25, .16)),
    ("foreground hairnet top", (-1.10, -3.02, 2.21), (.32, .01)),
]

def project_points():
    bpy.context.view_layer.update()
    cam = sc.camera
    dg = bpy.context.evaluated_depsgraph_get()
    projection = cam.calc_matrix_camera(
        dg, x=sc.render.resolution_x, y=sc.render.resolution_y,
        scale_x=sc.render.pixel_aspect_x, scale_y=sc.render.pixel_aspect_y)
    result = []
    for label, point, ref in landmarks:
        clip = projection @ cam.matrix_world.inverted() @ Vector((*point, 1.0))
        uv = None if clip.w <= 1e-8 else (
            .5*(clip.x/clip.w+1), .5*(1-clip.y/clip.w))
        result.append((label, ref, uv))
    return result

def show_table(title, values):
    print(title)
    for label, ref, uv in values:
        print(label, "reference", ref, "projected",
              None if uv is None else tuple(round(v, 3) for v in uv))

base_values = project_points()
show_table("Chosen camera", base_values)

# A small upward aim trial: stationary features should move down in the image.
# Restore the chosen camera afterward; this is a direction check, not a fit.
cam = sc.camera
original_rotation = cam.rotation_euler.copy()
trial_target = Vector((CAM_TARGET[0], CAM_TARGET[1], CAM_TARGET[2] + .10))
cam.rotation_euler = (trial_target - cam.location).to_track_quat("-Z", "Y").to_euler()
trial_values = project_points()
show_table("Trial upward aim", trial_values)
cam.rotation_euler = original_rotation
bpy.context.view_layer.update()

# Broad PBR finish. Glass remains translucent through the SceneAct opacity.
for mat in bpy.data.materials:
    if mat.use_nodes:
        shader = mat.node_tree.nodes.get("Principled BSDF")
        if shader:
            shader.inputs["Roughness"].default_value = .45

sc.camera.data.dof.use_dof = False
sc.render.image_settings.file_format = "PNG"
