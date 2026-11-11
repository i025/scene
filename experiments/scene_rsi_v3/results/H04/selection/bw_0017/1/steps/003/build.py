# Reference inventory and visual anchors, normalized to the 512 x 267 image:
# Ceiling and dark steel beams occupy y=0.00–0.35; shallow beam diagonals
# converge toward the right. Strip windows lie at x=0.00–0.23, y=0.34–0.65.
# Raised machinery and yellow railings span x=0.08–0.96, y=0.30–0.75.
# The main stainless housing occupies approximately x=0.61–0.79, y=0.30–0.66,
# with an insulated duct reaching y=0.22. A smaller housing is at x=0.23–0.37.
# The green receiver tank is at x=0.36–0.45, y=0.53–0.80, in front of the
# platform. The blue and silver conveyor fills x=0.00–0.62, y=0.73–1.00.
# Three yellow stair flights overlap the platform and descend toward the viewer.
# Machinery behind the railings and connections at the far right are occluded.
#
# Comparison with the second rendered view, estimated from visible contours:
# 1. The foreground conveyor is only a thin cropped strip at y=0.92–1.00,
#    versus a dense assembly beginning near y=0.73 in the reference. Extend
#    transfer equipment toward the camera and raise its visible top surfaces.
# 2. The tank is at roughly x=0.23–0.30, y=0.62–0.86, versus x=0.36–0.45,
#    y=0.53–0.80. Move the tank to the right and increase its height.
# 3. The main housing is roughly x=0.58–0.76, y=0.42–0.63, versus
#    x=0.61–0.79, y=0.30–0.66. Increase its height and move it slightly right;
#    its upper contour and duct will move up while the platform remains in place.
# 4. The background windows occupy only the extreme left, versus the row at
#    x=0.00–0.23. Move the window wall inward. The rendered roof beams occupy
#    roughly y=0.00–0.20, while the reference has more ceiling and dark framing.
#    Lower the camera aim slightly; the numerical trial below checks its direction.
# 5. The reference has diagonal stair flights, overlapping conveyor frames and
#    open machinery gaps. Retain the stairs and railings, and replace broad solid
#    transfer tabletops with open frames and rollers.
# The reference is brighter near the foreground; this may result from daylight
# and reflective surfaces as well as material color. The side-window lights and
# metallic finishes below address both without assuming a unique cause.
#
# Estimated primitive meshes: hall 95, platform and stairs 130, machines 55,
# ducts 25, tank 7, conveyor and transfer frames 120: approximately 432.
# Boxes, rods and balls each produce one mesh. No booleans or fillet expansions.

from sceneact import *
import bpy
from mathutils import Vector

scene = Scene("Production workshop")

steel = (.39, .43, .43)
silver = (.65, .68, .67)
bright = (.81, .83, .81)
dark = (.095, .115, .12)
beam = (.065, .08, .08)
wall = (.19, .21, .21)
roof = (.27, .29, .28)
yellow = (.95, .65, .015)
green = (.012, .32, .22)
floor_green = (.11, .30, .23)
blue = (.045, .24, .60)
white = (.80, .83, .81)
window = (.72, .83, .87)

def B(parent, name, size, center, color):
    parent.include(name, box(size=size, center=center, color=color))

def R(parent, name, a, b, radius, color):
    parent.include(name, rod(radius=radius, start=a, end=b, color=color))

# Hall proportions and equipment dimensions are kept independent of the camera.
arch = Asset("Steel framed workshop")
B(arch, "green epoxy floor", (32, 35, .14), (0, 3, -.08), floor_green)
B(arch, "roof deck", (32, 35, .16), (0, 3, 7.35), roof)
B(arch, "rear wall", (32, .18, 7.3), (0, 20.4, 3.65), wall)
B(arch, "window wall", (.18, 35, 7.3), (-9.2, 3, 3.65), wall)
B(arch, "right wall", (.18, 35, 7.3), (15.9, 3, 3.65), wall)

for i, y in enumerate([-8, -4.8, -1.6, 1.6, 4.8, 8, 11.2, 14.4, 17.6]):
    B(arch, "window pane %d" % i, (.045, .85, 3.3),
      (-9.08, y, 3.0), window)
    B(arch, "window mullion %d" % i, (.06, .035, 3.3),
      (-9.04, y, 3.0), beam)
    for j, z in enumerate([1.8, 2.6, 3.4, 4.2]):
        B(arch, "window crossbar %d %d" % (i, j), (.06, .85, .035),
          (-9.02, y, z), beam)

for i, y in enumerate([-11, -4, 3, 10, 17]):
    for j, x in enumerate([-9, 15.7]):
        B(arch, "column web %d %d" % (i, j), (.16, .24, 7.25),
          (x, y, 3.62), beam)
        for k, dx in enumerate([-.14, .14]):
            B(arch, "column flange %d %d %d" % (i, j, k),
              (.07, .34, 7.25), (x + dx, y, 3.62), beam)
    B(arch, "transverse roof beam %d" % i, (25, .24, .30),
      (3.35, y, 7.05), beam)
for i, x in enumerate([-9, -5, -.5, 5, 10.5, 15.5]):
    B(arch, "longitudinal roof beam %d" % i, (.22, 34, .24),
      (x, 3, 7.05), beam)
for i, y in enumerate([-6, 0, 6, 12, 18]):
    B(arch, "ceiling light strip %d" % i, (2.4, .12, .035),
      (2, y, 7.22), white)
scene.include("workshop structure", arch)

platform = Asset("Raised steel operating platform")
B(platform, "steel deck", (17.2, 3.1, .18), (.1, 3.8, 2.38), steel)
B(platform, "front edge beam", (17.2, .15, .38), (.1, 2.25, 2.20), dark)
B(platform, "rear edge beam", (17.2, .15, .32), (.1, 5.34, 2.23), steel)
for i, x in enumerate([-8.2, -5.5, -2.8, 0, 2.8, 5.5, 8.3]):
    for j, y in enumerate([2.4, 5.2]):
        B(platform, "deck support %d %d" % (i, j), (.15, .15, 2.30),
          (x, y, 1.15), steel)

for seg, (x1, x2) in enumerate([(-8.4, -6.8), (-5.4, -2.1),
                                 (-.8, 3.0), (4.4, 8.6)]):
    for j, z in enumerate([2.92, 3.48]):
        R(platform, "front rail %d %d" % (seg, j),
          (x1, 2.20, z), (x2, 2.20, z), .035, yellow)
    n = max(1, int((x2 - x1) / .70))
    for j in range(n + 1):
        x = x1 + (x2 - x1) * j / n
        R(platform, "front post %d %d" % (seg, j),
          (x, 2.20, 2.46), (x, 2.20, 3.49), .029, yellow)
for z in [2.92, 3.48]:
    R(platform, "rear rail %.2f" % z, (-8.4, 5.36, z),
      (8.6, 5.36, z), .03, yellow)
for i in range(18):
    x = -8.4 + i
    R(platform, "rear post %d" % i, (x, 5.36, 2.46),
      (x, 5.36, 3.48), .025, yellow)

def stairs(label, x, y0, y1, width):
    z0, z1 = .10, 2.45
    for side in [-1, 1]:
        xx = x + side * width / 2
        R(platform, label + " stringer " + str(side),
          (xx, y0, z0), (xx, y1, z1), .055, yellow)
        R(platform, label + " handrail " + str(side),
          (xx, y0, z0 + .95), (xx, y1, z1 + .95), .035, yellow)
        for j in range(4):
            t = j / 3
            y = y0 + (y1 - y0) * t
            z = z0 + (z1 - z0) * t
            R(platform, label + " baluster %d %d" % (side, j),
              (xx, y, z), (xx, y, z + .95), .025, yellow)
    for j in range(9):
        t = (j + .5) / 9
        B(platform, label + " tread %d" % j, (width, .26, .055),
          (x, y0 + (y1 - y0) * t, z0 + (z1 - z0) * t), bright)

stairs("left staircase", -6.1, -.75, 2.20, 1.15)
stairs("center staircase", -1.45, -.75, 2.20, 1.10)
stairs("right staircase", 4.2, -.85, 2.20, 1.18)
scene.include("platform and stairs", platform)

machines = Asset("Stainless processing line")
def machine(label, x, y, width, depth, height):
    base = 2.48
    fy = y - depth / 2 - .02
    B(machines, label + " housing", (width, depth, height),
      (x, y, base + height / 2), silver)
    B(machines, label + " base", (width + .15, depth + .1, .21),
      (x, y, base + .10), dark)
    B(machines, label + " top cap", (width * .92, depth * .94, .20),
      (x, y, base + height + .10), bright)
    B(machines, label + " front opening", (width * .76, .04, height * .39),
      (x, fy, base + height * .48), dark)
    B(machines, label + " lower roller", (width * .70, .08, .14),
      (x, fy - .04, base + height * .33), steel)
    for j in range(5):
        B(machines, label + " face slat %d" % j,
          (width * .70, .045, .027),
          (x, fy - .045, base + height * .37 + j * .105), bright)
    for j, dx in enumerate([-.44, .44]):
        B(machines, label + " vertical trim %d" % j, (.065, .06, height * .75),
          (x + width * dx, fy - .02, base + height * .52), bright)
    B(machines, label + " control box", (.42, .22, .65),
      (x + width * .42, fy - .15, base + height * .52), white)

machine("main machine", 3.45, 4.1, 3.0, 2.1, 2.15)
machine("left machine", -5.4, 4.15, 2.7, 1.9, 1.35)
machine("center machine", -1.1, 4.2, 2.0, 1.7, 1.05)
machine("far right machine", 7.0, 4.25, 1.45, 1.5, 1.15)
scene.include("processing machines", machines)

ducts = Asset("Insulated duct and process piping")
def tube(label, points, radius):
    for i in range(len(points) - 1):
        R(ducts, label + " section %d" % i, points[i], points[i + 1],
          radius, bright)
    for i, p in enumerate(points[1:-1]):
        ducts.include(label + " elbow %d" % i,
                      ball(radius, center=p, color=silver))

tube("main duct", [(3.45, 4.2, 4.65), (3.45, 4.2, 5.5),
                   (3.65, 4.2, 5.72), (4.35, 4.2, 5.45),
                   (4.6, 4.2, 5.15)], .22)
tube("left duct", [(-5.4, 4.3, 3.85), (-5.4, 4.3, 4.75),
                   (-5.1, 4.3, 4.95), (-3.6, 4.3, 4.70),
                   (-3.1, 4.3, 4.10)], .17)
tube("connecting duct", [(-3.1, 4.4, 4.0), (-2.0, 4.4, 4.35),
                         (1.0, 4.4, 4.35), (1.7, 4.4, 4.15)], .12)
tube("rear process pipe", [(-8.0, 5.6, 3.8), (8.0, 5.6, 3.8)], .085)
for i, x in enumerate([-5, -1, 3, 7]):
    R(ducts, "pipe hanger %d" % i, (x, 4.4, 4.4),
      (x, 4.4, 7.0), .025, steel)
scene.include("ducts and hangers", ducts)

tank = Asset("Green vertical receiver")
tx, ty = -1.55, .65
R(tank, "cylindrical shell", (tx, ty, .43), (tx, ty, 2.52), .56, green)
tank.include("rounded upper head", ball(.56, center=(tx, ty, 2.52), color=green))
tank.include("rounded lower head", ball(.56, center=(tx, ty, .43), color=green))
for i, dx in enumerate([-.35, .35]):
    B(tank, "support foot %d" % i, (.14, .17, .38),
      (tx + dx, ty, .19), dark)
R(tank, "top nozzle", (tx, ty, 3.0), (tx, ty, 3.20), .09, steel)
R(tank, "side outlet", (tx + .50, ty, 1.65),
  (tx + .90, ty, 1.65), .07, steel)
scene.include("vertical green tank", tank)

conveyor = Asset("Foreground blue roller conveyor")
for lane, cy in enumerate([-4.9, -3.55, -2.2]):
    B(conveyor, "blue belt %d" % lane, (13.2, 1.08, .12),
      (-3.0, cy, 1.05), blue)
    for side in [-1, 1]:
        yy = cy + side * .60
        B(conveyor, "side guide %d %d" % (lane, side),
          (13.4, .085, .21), (-3.0, yy, 1.17), bright)
        for j, x in enumerate([-8.8, -5.4, -2.0, 1.4, 3.3]):
            B(conveyor, "leg %d %d %d" % (lane, side, j),
              (.09, .10, 1.04), (x, yy, .52), steel)
    for j in range(17):
        x = -9.2 + j * .75
        R(conveyor, "roller %d %d" % (lane, j),
          (x, cy - .51, 1.13), (x, cy + .51, 1.13), .036, bright)
    B(conveyor, "end member %d" % lane, (.12, 1.3, .16),
      (3.55, cy, 1.0), steel)
B(conveyor, "drive motor", (.65, .44, .38), (2.4, -1.48, .7), dark)
scene.include("conveyor line", conveyor)

utilities = Asset("Open transfer tables and electrical utilities")
for i, (x, y) in enumerate([(-7.0, -.6), (-3.5, -.8), (.0, -.7), (7.2, 1.6)]):
    for side in [-1, 1]:
        B(utilities, "table longitudinal frame %d %d" % (i, side),
          (2.8, .10, .14), (x, y + side * .55, 1.25), bright)
    for side in [-1, 1]:
        B(utilities, "table end frame %d %d" % (i, side),
          (.10, 1.2, .14), (x + side * 1.35, y, 1.25), bright)
    for j in range(7):
        xx = x - 1.2 + .4 * j
        R(utilities, "table roller %d %d" % (i, j),
          (xx, y - .5, 1.31), (xx, y + .5, 1.31), .035, silver)
    for j, dx in enumerate([-1.1, 1.1]):
        for k, dy in enumerate([-.45, .45]):
            B(utilities, "table support %d %d %d" % (i, j, k),
              (.075, .075, 1.2), (x + dx, y + dy, .6), steel)
B(utilities, "right electrical cabinet", (.75, .50, 2.1),
  (8.0, 3.8, 3.52), white)
scene.include("transfer equipment", utilities)

realize(scene)

# The last successful view used position (4.2,-13.8,5.4), target
# (-.1,3.5,3.65), lens 35. A downward aim should move fixed points upward.
# The projection table prints that previous aim and the selected aim separately.
CAMERA_POSITION = (4.2, -13.8, 5.4)
PREVIOUS_TARGET = (-.1, 3.5, 3.65)
CAMERA_TARGET = (-.1, 3.5, 3.35)
CAMERA_LENS = 35
set_view(CAMERA_POSITION, PREVIOUS_TARGET, lens=CAMERA_LENS, sensor=36)

sc = bpy.context.scene
sc.render.resolution_x = 512
sc.render.resolution_y = 267
sc.render.resolution_percentage = 100
sc.render.pixel_aspect_x = 1
sc.render.pixel_aspect_y = 1

landmarks = [
    ("window top", (-9.08, 1.6, 4.65), (.10, .34)),
    ("main machine top", (3.45, 3.05, 4.83), (.68, .31)),
    ("tank top", (tx, ty, 3.08), (.40, .53)),
    ("conveyor corner", (3.55, -3.55, 1.17), (.61, .80)),
]

def projections():
    bpy.context.view_layer.update()
    cam = sc.camera
    dg = bpy.context.evaluated_depsgraph_get()
    matrix = cam.calc_matrix_camera(
        dg, x=sc.render.resolution_x, y=sc.render.resolution_y,
        scale_x=sc.render.pixel_aspect_x, scale_y=sc.render.pixel_aspect_y)
    values = []
    for name, point, ref in landmarks:
        clip = matrix @ cam.matrix_world.inverted() @ Vector((*point, 1.0))
        uv = None if clip.w <= 1e-8 else (
            .5 * (clip.x / clip.w + 1), .5 * (1 - clip.y / clip.w))
        values.append(None if uv is None else tuple(round(v, 3) for v in uv))
    return values

previous = projections()
cam = sc.camera
previous_rotation = cam.rotation_euler.copy()
cam.rotation_euler = (Vector(CAMERA_TARGET) - cam.location).to_track_quat(
    '-Z', 'Y').to_euler()
candidate = projections()
# Restore the earlier aim if the trial fails to move the machine and tank up.
if (previous[1] is None or candidate[1] is None or
    previous[2] is None or candidate[2] is None or
    candidate[1][1] >= previous[1][1] or candidate[2][1] >= previous[2][1]):
    cam.rotation_euler = previous_rotation
bpy.context.view_layer.update()
print("Landmark | reference estimate | previous aim | trial aim")
for i, (name, point, ref) in enumerate(landmarks):
    print(name, ref, previous[i], candidate[i])

if sc.world is None:
    sc.world = bpy.data.worlds.new("SceneWorld")
sc.world.use_nodes = True
nodes = sc.world.node_tree.nodes
background = nodes.get("Background")
if background is None:
    background = nodes.new("ShaderNodeBackground")
output = nodes.get("World Output")
if output is None:
    output = nodes.new("ShaderNodeOutputWorld")
sc.world.node_tree.links.new(background.outputs["Background"], output.inputs["Surface"])
background.inputs["Color"].default_value = (.68, .75, .78, 1)
background.inputs["Strength"].default_value = .65

area_emitter((-8.5, -1, 4.5), power=2400, size=7, target=(0, 2, 1.5))
area_emitter((0, -1, 6.8), power=1600, size=8, target=(0, 3, 1.5))
area_emitter((8, 5, 6.8), power=1500, size=7, target=(3, 3, 1.5))

for mat in bpy.data.materials:
    if not mat.use_nodes:
        continue
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf is None:
        continue
    c = tuple(mat.diffuse_color[:3])
    if max(abs(c[i] - floor_green[i]) for i in range(3)) < .03:
        bsdf.inputs["Roughness"].default_value = .20
        bsdf.inputs["Metallic"].default_value = .10
    elif any(max(abs(c[i] - v[i]) for i in range(3)) < .03
             for v in [steel, silver, bright]):
        bsdf.inputs["Metallic"].default_value = .68
        bsdf.inputs["Roughness"].default_value = .30
    elif max(abs(c[i] - yellow[i]) for i in range(3)) < .03:
        bsdf.inputs["Metallic"].default_value = .22
        bsdf.inputs["Roughness"].default_value = .38

sc.render.engine = "CYCLES"
sc.cycles.use_denoising = True
sc.render.image_settings.file_format = "PNG"
try:
    sc.view_settings.view_transform = "AgX"
except Exception:
    pass
