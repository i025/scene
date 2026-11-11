# Reference inventory, normalized image coordinates, estimated from the photograph:
# Roof and dark steel beams: x=0–1, y=0–.32; beams run nearly horizontally
# and converge toward the right. Left wall and narrow windows: x=0–.26,
# y=.30–.68. Raised equipment, decks, and yellow rails: x=.12–.95,
# y=.30–.76. Two prominent machine housings sit behind the rails.
# Green tank: x=.36–.45, y=.54–.80, overlapping the platform front.
# Silver and blue conveyors: x=0–.71, y=.72–1, cropped by the frame.
# Yellow stairs descend from the platforms toward the foreground, including
# a prominent flight on the right. Duct connections and rear equipment are
# partly occluded and their exact routing is uncertain.
#
# Comparison with the previous full render:
# The rendered roof occupies the top edge as an exterior slab, with empty gray
# outside the building; the photo shows the interior ceiling over the entire
# upper third. The machines and platform span approximately x=.29–.71 in
# the render versus roughly x=.12–.95 in the photo. The rendered tank top is
# near (.39,.54), close to the reference estimate (.405,.54), while the front
# conveyors are much smaller and less cropped than in the photograph.
# Roof beams in the render slope strongly down to the right, unlike the
# near-horizontal long beams in the photograph. The right stairs and machine
# are too far inward. Platform gaps and the yellow railing remain important.
#
# Ranked corrections: (1) put the camera inside the hall and lower it, to
# replace the exterior roof view with the ceiling and reduce downward tilt;
# (2) move closer to the machinery and aim more nearly along the hall, so
# the machines, stairs, and foreground conveyor occupy more of the frame;
# (3) widen the platform and machinery layout in the image while preserving
# the tank in front of it. These camera changes intentionally trade the
# previously close tank-top anchor against the much larger roof and platform
# errors. The projection table checks the same four landmarks as before and
# reports a small trial and the final camera. The platform endpoint
# correspondences are uncertain, so they are not treated as calibrated corners.
# The previous scene coordinates and reference estimates are unchanged; there
# is no geometry scale pivot or translation applied to those landmarks.
#
# Approximate primitive count: hall 49; platforms and railings 44; machinery
# 31; stairs 69; ducts and hangers 35; tank 9; conveyors 73; additional
# foreground frames 15: about 325 primitives. Tube counts include all
# segments and joints. Geometry behind the machines remains approximate.

from sceneact import *
import bpy
from mathutils import Vector

scene = Scene("Workshop")
steel = (0.29, 0.32, 0.31)
dark = (0.105, 0.12, 0.12)
roof = (0.21, 0.23, 0.22)
silver = (0.63, 0.67, 0.66)
bright = (0.76, 0.79, 0.77)
shadow = (0.19, 0.22, 0.21)
yellow = (0.94, 0.61, 0.025)
green = (0.025, 0.31, 0.22)
floor_green = (0.12, 0.35, 0.27)
blue = (0.035, 0.24, 0.55)
window = (0.72, 0.84, 0.91)

def B(parent, name, size, center, color):
    parent.include(name, box(size=size, center=center, color=color))

def R(parent, name, a, b, radius, color):
    parent.include(name, rod(radius=radius, start=a, end=b, color=color))

# The enclosing hall extends beyond the camera, so the ceiling is seen from
# underneath rather than as a freestanding exterior roof slab.
hall = Asset("Steel_frame_hall")
B(hall, "green_epoxy_floor", (20, 34, .12), (0, 1, -.08), floor_green)
B(hall, "left_wall", (.16, 34, 6.7), (-8.4, 1, 3.35), dark)
B(hall, "rear_wall", (16.8, .16, 6.7), (0, 17.8, 3.35), dark)
B(hall, "roof_deck", (17, 34, .18), (0, 1, 6.85), roof)
for i, y in enumerate((-14, -10, -6, -2, 2, 6, 10, 14, 17)):
    B(hall, "left_column_%d" % i, (.26, .30, 6.8), (-8.15, y, 3.4), dark)
    B(hall, "right_column_%d" % i, (.26, .30, 6.8), (8.15, y, 3.4), dark)
    B(hall, "roof_crossbeam_%d" % i, (16.5, .23, .27), (0, y, 6.6), dark)
    if i < 8:
        B(hall, "strip_window_%d" % i, (.035, 1.05, 3.05),
          (-8.29, y + 1.65, 3.25), window)
        B(hall, "window_mullion_%d" % i, (.06, .04, 3.05),
          (-8.24, y + 1.65, 3.25), steel)
        B(hall, "window_crossbar_%d" % i, (.06, 1.05, .045),
          (-8.23, y + 1.65, 3.25), steel)
for i, x in enumerate((-5.5, -2.7, 0, 2.7, 5.5)):
    B(hall, "roof_purlin_%d" % i, (.10, 33, .10), (x, 1, 6.69), steel)
for i, y in enumerate((-8, -2, 4, 10)):
    B(hall, "ceiling_light_%d" % i, (2.1, .12, .04),
      (0, y, 6.51), (0.84, .87, .83))
scene.include("building", hall)

platform = Asset("Raised_processing_platforms")
for name, x, y, sx, sy in [
    ("left", -3.6, 3.2, 5.7, 3.4),
    ("right", 2.3, 4.2, 5.6, 3.8),
]:
    B(platform, name + "_deck", (sx, sy, .17), (x, y, 1.75), steel)
    for i, dx in enumerate((-sx/2 + .16, sx/2 - .16)):
        for j, dy in enumerate((-sy/2 + .16, sy/2 - .16)):
            B(platform, "%s_support_%d_%d" % (name, i, j),
              (.14, .14, 1.72), (x + dx, y + dy, .87), steel)
    front_y = y - sy/2
    for j in range(5):
        px = x - sx/2 + j * sx/4
        R(platform, "%s_front_post_%d" % (name, j),
          (px, front_y, 1.85), (px, front_y, 2.82), .035, yellow)
    for j, z in enumerate((2.34, 2.82)):
        R(platform, "%s_front_rail_%d" % (name, j),
          (x-sx/2, front_y, z), (x+sx/2, front_y, z), .035, yellow)
    for side in (-1, 1):
        px = x + side*sx/2
        for j in range(3):
            py = y - sy/2 + j*sy/2
            R(platform, "%s_side_post_%d_%d" % (name, side, j),
              (px, py, 1.85), (px, py, 2.82), .03, yellow)
        for j, z in enumerate((2.34, 2.82)):
            R(platform, "%s_side_rail_%d_%d" % (name, side, j),
              (px, y-sy/2, z), (px, y+sy/2, z), .03, yellow)
scene.include("platforms", platform)

machines = Asset("Stainless_processing_machines")
for name, x, y, sx, sy, height in [
    ("left_processor", -3.55, 3.65, 3.1, 2.0, 2.15),
    ("right_processor", 2.1, 4.6, 3.25, 2.25, 2.55),
    ("rear_processor", -0.8, 7.2, 2.3, 1.5, 1.5),
]:
    base = 1.84
    B(machines, name+"_body", (sx, sy, height*.68),
      (x, y, base+height*.34), silver)
    B(machines, name+"_upper_housing", (sx*.91, sy*.9, height*.32),
      (x, y, base+height*.84), bright)
    B(machines, name+"_front_panel", (sx*.78, .045, height*.43),
      (x, y-sy/2-.03, base+height*.54), shadow)
    for j in range(4):
        B(machines, "%s_panel_strip_%d" % (name, j),
          (sx*.73, .025, .035),
          (x, y-sy/2-.06, base+height*(.39+j*.10)), silver)
    B(machines, name+"_lower_base", (sx*1.03, sy*1.03, .14),
      (x, y, base+.07), steel)
scene.include("processing_equipment", machines)

stairs = Asset("Access_stairs")
def staircase(name, x, y0, y1, width):
    z0, z1 = .12, 1.84
    for side in (-1, 1):
        xx = x + side*width/2
        R(stairs, "%s_stringer_%d" % (name, side),
          (xx, y0, z0), (xx, y1, z1), .075, steel)
        R(stairs, "%s_handrail_%d" % (name, side),
          (xx, y0, z0+.95), (xx, y1, z1+.95), .035, yellow)
        R(stairs, "%s_midrail_%d" % (name, side),
          (xx, y0, z0+.50), (xx, y1, z1+.50), .025, yellow)
        for j in range(4):
            t = j/3
            yy = y0 + (y1-y0)*t
            zz = z0 + (z1-z0)*t
            R(stairs, "%s_post_%d_%d" % (name, side, j),
              (xx, yy, zz), (xx, yy, zz+.96), .03, yellow)
    for j in range(9):
        t = (j+.5)/9
        B(stairs, "%s_tread_%d" % (name, j), (width, .28, .055),
          (x, y0+(y1-y0)*t, z0+(z1-z0)*t), bright)
staircase("left_stair", -4.5, -1.0, 1.5, 1.05)
staircase("center_stair", -.4, -.15, 1.5, .95)
staircase("right_stair", 5.2, .25, 2.3, 1.05)
scene.include("stairs", stairs)

ducts = Asset("Insulated_ducts")
def tube(name, pts, r):
    ducts.include(name, sweep_tube(points=pts, radius=r, color=bright))
tube("left_high_duct", [(-5.2, 3.6, 3.7), (-5.2, 3.6, 4.55),
                       (-5.0, 3.6, 4.8), (-3.2, 3.6, 4.65),
                       (-2.8, 3.6, 4.35)], .18)
tube("right_riser", [(2.4, 4.6, 4.1), (2.4, 4.6, 5.15),
                    (2.55, 4.6, 5.4), (3.55, 4.6, 5.05),
                    (3.7, 4.6, 4.5)], .22)
tube("cross_process_pipe", [(-3.0, 5.5, 3.65), (-1.0, 5.5, 3.65),
                           (-.7, 5.5, 3.4), (1.3, 5.5, 3.4)], .13)
tube("right_side_pipe", [(4.1, 4.9, 3.65), (5.1, 4.9, 3.65),
                        (5.35, 4.9, 3.45), (5.35, 4.9, 2.1)], .13)
for i, x in enumerate((-4.5, 2.6, 4.7)):
    R(ducts, "hanger_%d" % i, (x, 4.6, 5.0), (x, 4.6, 6.55), .025, steel)
scene.include("ducts_and_hangers", ducts)

tank = Asset("Green_vertical_tank")
tx, ty = -2.0, -.25
R(tank, "cylindrical_shell", (tx, ty, .38), (tx, ty, 1.92), .53, green)
tank.include("top_dome", ball(radius=.53, center=(tx, ty, 1.92), color=green))
tank.include("bottom_dome", ball(radius=.53, center=(tx, ty, .38), color=green))
for i, (dx, dy) in enumerate(((-.34,-.25),(.34,-.25),(-.34,.25),(.34,.25))):
    R(tank, "leg_%d" % i, (tx+dx,ty+dy,.03), (tx+dx,ty+dy,.55), .055, steel)
R(tank, "top_nozzle", (tx,ty,2.38), (tx,ty,2.65), .075, silver)
scene.include("green_tank", tank)

conveyors = Asset("Foreground_conveyor_lines")
def conveyor(name, x, y, length, width):
    B(conveyors, name+"_blue_bed", (length,width,.12), (x,y,.77), blue)
    for side in (-1, 1):
        B(conveyors, "%s_side_rail_%d" % (name, side),
          (length,.075,.16), (x,y+side*width/2,.84), bright)
    for j in range(12):
        xx = x-length/2 + (j+.5)*length/12
        R(conveyors, "%s_roller_%d" % (name, j),
          (xx,y-width/2,.85), (xx,y+width/2,.85), .035, silver)
    for i, dx in enumerate((-length*.38, length*.38)):
        for j, dy in enumerate((-width*.4, width*.4)):
            B(conveyors, "%s_leg_%d_%d" % (name,i,j),
              (.09,.09,.72), (x+dx,y+dy,.37), steel)
    B(conveyors, name+"_drive_motor", (.4,.3,.3),
      (x+length*.36,y+width*.65,.55), steel)
conveyor("front_belt", -3.1, -5.15, 8.3, 1.25)
conveyor("middle_belt", -2.0, -3.55, 7.5, 1.05)
conveyor("right_transfer", 2.5, -1.95, 4.2, .9)

# White transfer equipment bridges the blue belts and the processing platform.
B(conveyors, "transfer_frame_left", (4.2,.12,.13), (-1.0,-1.9,1.05), bright)
B(conveyors, "transfer_frame_right", (4.2,.12,.13), (-1.0,-.95,1.05), bright)
for i in range(9):
    x = -3.0 + i*.5
    R(conveyors, "transfer_roller_%d" % i,
      (x,-1.88,1.08), (x,-.97,1.08), .045, silver)
for i, x in enumerate((-2.7,.6)):
    for j, y in enumerate((-1.8,-1.05)):
        B(conveyors, "transfer_leg_%d_%d" % (i,j),
          (.08,.08,1.0), (x,y,.5), bright)
scene.include("conveyor_system", conveyors)

realize(scene)

# Camera candidates are separate from the geometry parameters. The previous
# state is reproduced exactly, including its selected 34 mm lens. The trial
# moves part way inside the hall; the final candidate continues toward a lower,
# less oblique interior viewpoint. Both candidates are evaluated before the
# final choice, and a weighted fit rejects the final if it worsens the trial.
PREVIOUS_POS = (10.8, -19.5, 8.1)
PREVIOUS_TARGET = (-.35, 2.8, 2.5)
PREVIOUS_LENS = 34
TRIAL_POS = (6.0, -15.5, 5.2)
TRIAL_TARGET = (-.35, 2.8, 2.75)
TRIAL_LENS = 34
FINAL_POS = (3.2, -13.5, 4.6)
FINAL_TARGET = (-.35, 2.8, 2.8)
FINAL_LENS = 34

set_view(PREVIOUS_POS, PREVIOUS_TARGET, lens=PREVIOUS_LENS)
sc = bpy.context.scene
sc.render.resolution_x = 512
sc.render.resolution_y = 267
sc.render.resolution_percentage = 100

anchors = [
    ("tank_top", (tx, ty, 2.45), (.405, .54), 1.0),
    ("right_machine_top", (2.1, 4.6, 4.39), (.69, .30), 1.0),
    ("left_platform_front", (-6.45, 1.5, 2.82), (.15, .47), .7),
    ("right_platform_front", (5.1, 2.3, 2.82), (.88, .43), .7),
]

def set_camera(pos, target, lens):
    cam = sc.camera
    cam.location = pos
    cam.rotation_euler = (Vector(target)-Vector(pos)).to_track_quat('-Z','Y').to_euler()
    cam.data.lens = lens
    bpy.context.view_layer.update()

def project(p):
    cam = sc.camera
    dg = bpy.context.evaluated_depsgraph_get()
    proj = cam.calc_matrix_camera(dg, x=512, y=267, scale_x=1, scale_y=1)
    clip = proj @ cam.matrix_world.inverted() @ Vector((*p, 1))
    if clip.w <= 1e-8:
        return None
    return (.5*(clip.x/clip.w+1), .5*(1-clip.y/clip.w))

def measure(pos, target, lens):
    set_camera(pos, target, lens)
    return [project(p) for _, p, _, _ in anchors]

def score(values):
    total = 0
    for uv, (_, _, ref, weight) in zip(values, anchors):
        if uv is None:
            total += 1e8
        else:
            total += weight*((512*(uv[0]-ref[0]))**2 +
                             (267*(uv[1]-ref[1]))**2)
    return total

previous = measure(PREVIOUS_POS, PREVIOUS_TARGET, PREVIOUS_LENS)
trial = measure(TRIAL_POS, TRIAL_TARGET, TRIAL_LENS)
candidate = measure(FINAL_POS, FINAL_TARGET, FINAL_LENS)
# The indoor trial is the fallback, rather than the exterior prior view:
# the roof crop is a large visible discrepancy that point projections omit.
if score(candidate) <= score(trial):
    chosen = candidate
    chosen_camera = (FINAL_POS, FINAL_TARGET, FINAL_LENS)
else:
    chosen = trial
    chosen_camera = (TRIAL_POS, TRIAL_TARGET, TRIAL_LENS)
set_camera(*chosen_camera)

def residual(uv, ref):
    if uv is None:
        return None
    return (round((uv[0]-ref[0])*512, 1),
            round((uv[1]-ref[1])*267, 1))

for (name, p, ref, weight), old, mid, proposed, final in zip(
        anchors, previous, trial, candidate, chosen):
    print(name, "reference", ref,
          "previous", old, "residual_px", residual(old, ref),
          "trial", mid, "residual_px", residual(mid, ref),
          "candidate", proposed, "residual_px", residual(proposed, ref),
          "chosen", final, "residual_px", residual(final, ref))

if sc.world is None:
    sc.world = bpy.data.worlds.new("SceneWorld")
sc.world.use_nodes = True
nodes = sc.world.node_tree.nodes
background = nodes.get("Background") or nodes.new("ShaderNodeBackground")
output = nodes.get("World Output") or nodes.new("ShaderNodeOutputWorld")
sc.world.node_tree.links.new(background.outputs["Background"], output.inputs["Surface"])
background.inputs["Color"].default_value = (.68, .75, .80, 1)
background.inputs["Strength"].default_value = .55
area_emitter((-6, -2, 5.5), power=1800, size=7, target=(0, 2, 1.7))
area_emitter((4, 3, 6.3), power=1200, size=6, target=(0, 2, 1))
area_emitter((0, -8, 5), power=850, size=6, target=(0, 2, 2))

for mat in bpy.data.materials:
    if not mat.use_nodes:
        continue
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf is None:
        continue
    c = bsdf.inputs["Base Color"].default_value
    r, g, b = c[0], c[1], c[2]
    if g > r*1.4 and g > b*1.05:
        bsdf.inputs["Roughness"].default_value = .25
        bsdf.inputs["Metallic"].default_value = .22
    elif abs(r-g) < .10 and abs(g-b) < .10 and r > .35:
        bsdf.inputs["Metallic"].default_value = .68
        bsdf.inputs["Roughness"].default_value = .3
    else:
        bsdf.inputs["Roughness"].default_value = .48

try:
    sc.view_settings.view_transform = "AgX"
except Exception:
    pass
