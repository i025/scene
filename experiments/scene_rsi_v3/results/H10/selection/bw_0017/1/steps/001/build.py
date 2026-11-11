# Reference inventory and image anchors, normalized x-right/y-down:
# - Steel roof and dark transverse beams: y=0.00–0.32, receding toward right.
# - Left wall strip windows: x=0.00–0.25, y=0.33–0.66.
# - Main stainless machines and raised platform: x=0.20–0.91, y=0.29–0.77;
#   yellow rails overlap their fronts, stairs descend toward the foreground.
# - Green vertical tank: x=0.36–0.45, y=0.54–0.82, in front of platform.
# - Blue and silver roller conveyors: x=0.00–0.72, y=0.72–1.00, cropped.
# - Green floor visible through equipment, particularly at lower right.
# - Silver ducts rise above and run alongside machines; rear connections uncertain.
# Dominant edges: roof beams slope gently down to the right; railings run across
# the frame; stair stringers rise toward the right. The conveyor obscures legs.
# Approximate primitive budget: architecture 35, machinery 35, platforms and
# railings 105, stairs 45, ducts 35, tank 8, conveyors 75: roughly 338 meshes.
# Unseen wall, pipe connections and exact machine interiors remain uncertain.

from sceneact import *
import bpy
import math
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

def add_box(parent, name, size, center, color):
    parent.include(name, box(size=size, center=center, color=color))

def add_rod(parent, name, a, b, radius, color):
    parent.include(name, rod(radius=radius, start=a, end=b, color=color))

# Architecture: long hall, left window wall and exposed roof members.
hall = Asset("Steel_frame_hall")
add_box(hall, "green_epoxy_floor", (18, 23, .12), (0, 2, -.08), floor_green)
add_box(hall, "left_wall", (.16, 23, 6.7), (-8.4, 2, 3.35), dark)
add_box(hall, "rear_wall", (16.8, .16, 6.7), (0, 13.4, 3.35), dark)
add_box(hall, "roof_deck", (17, 23, .18), (0, 2, 6.85), roof)
for i, y in enumerate((-8, -4, 0, 4, 8, 12)):
    add_box(hall, f"left_column_{i}", (.26, .3, 6.8), (-8.15, y, 3.4), dark)
    add_box(hall, f"right_column_{i}", (.26, .3, 6.8), (8.15, y, 3.4), dark)
    add_box(hall, f"roof_crossbeam_{i}", (16.5, .23, .27), (0, y, 6.6), dark)
    if i < 5:
        add_box(hall, f"strip_window_{i}", (.035, 1.05, 3.05),
                (-8.29, y + 1.65, 3.25), window)
        add_box(hall, f"window_mullion_{i}", (.06, .04, 3.05),
                (-8.24, y + 1.65, 3.25), steel)
        add_box(hall, f"window_crossbar_{i}", (.06, 1.05, .045),
                (-8.23, y + 1.65, 3.25), steel)
for x in (-5.5, -2.7, 0, 2.7, 5.5):
    add_box(hall, f"roof_purlin_{x}", (.10, 22, .10), (x, 2, 6.69), steel)
for y in (-4, 2, 8):
    add_box(hall, f"ceiling_light_{y}", (2.1, .12, .04), (0, y, 6.51), (0.84, .87, .83))
scene.include("building", hall)

# Raised working decks and structural legs.
platform = Asset("Raised_processing_platforms")
for name, x, y, sx, sy in [
    ("left", -3.6, 3.2, 5.7, 3.4),
    ("right", 2.3, 4.2, 5.6, 3.8)
]:
    add_box(platform, name + "_deck", (sx, sy, .17), (x, y, 1.75), steel)
    for dx in (-sx/2 + .16, sx/2 - .16):
        for dy in (-sy/2 + .16, sy/2 - .16):
            add_box(platform, f"{name}_support_{dx}_{dy}", (.14, .14, 1.72),
                    (x + dx, y + dy, .87), steel)
    # Front safety railing, with a gap between the two decks.
    front_y = y - sy/2
    for j in range(5):
        px = x - sx/2 + j * sx/4
        add_rod(platform, f"{name}_front_post_{j}", (px, front_y, 1.85),
                (px, front_y, 2.82), .035, yellow)
    for z in (2.34, 2.82):
        add_rod(platform, f"{name}_front_rail_{z}",
                (x-sx/2, front_y, z), (x+sx/2, front_y, z), .035, yellow)
    for side in (-1, 1):
        px = x + side*sx/2
        for j in range(3):
            py = y - sy/2 + j*sy/2
            add_rod(platform, f"{name}_side_post_{side}_{j}", (px, py, 1.85),
                    (px, py, 2.82), .03, yellow)
        for z in (2.34, 2.82):
            add_rod(platform, f"{name}_side_rail_{side}_{z}",
                    (px, y-sy/2, z), (px, y+sy/2, z), .03, yellow)
scene.include("platforms", platform)

# Stainless processing housings sit above and behind the platform fronts.
machines = Asset("Stainless_processing_machines")
for name, x, y, sx, sy, height in [
    ("left_processor", -3.55, 3.65, 3.1, 2.0, 2.15),
    ("right_processor", 2.1, 4.6, 3.25, 2.25, 2.55),
    ("rear_processor", -0.8, 7.2, 2.3, 1.5, 1.5),
]:
    base = 1.84
    add_box(machines, name+"_body", (sx, sy, height*.68),
            (x, y, base+height*.34), silver)
    add_box(machines, name+"_upper_housing", (sx*.91, sy*.9, height*.32),
            (x, y, base+height*.84), bright)
    add_box(machines, name+"_front_panel", (sx*.78, .045, height*.43),
            (x, y-sy/2-.03, base+height*.54), shadow)
    for j in range(4):
        add_box(machines, f"{name}_panel_strip_{j}", (sx*.73, .025, .035),
                (x, y-sy/2-.06, base+height*(.39+j*.10)), silver)
    add_box(machines, name+"_lower_base", (sx*1.03, sy*1.03, .14),
            (x, y, base+.07), steel)
scene.include("processing_equipment", machines)

# Straight steel stairs rising from foreground to platform, yellow side rails.
stairs = Asset("Access_stairs")
def staircase(name, x, y0, y1, width):
    z0, z1 = .12, 1.84
    for side in (-1, 1):
        xx = x + side*width/2
        add_rod(stairs, f"{name}_stringer_{side}", (xx, y0, z0),
                (xx, y1, z1), .075, steel)
        add_rod(stairs, f"{name}_handrail_{side}", (xx, y0, z0+.95),
                (xx, y1, z1+.95), .035, yellow)
        add_rod(stairs, f"{name}_midrail_{side}", (xx, y0, z0+.50),
                (xx, y1, z1+.50), .025, yellow)
        for j in range(4):
            t = j/3
            yy = y0 + (y1-y0)*t
            zz = z0 + (z1-z0)*t
            add_rod(stairs, f"{name}_post_{side}_{j}", (xx, yy, zz),
                    (xx, yy, zz+.96), .03, yellow)
    for j in range(9):
        t = (j+.5)/9
        add_box(stairs, f"{name}_tread_{j}", (width, .28, .055),
                (x, y0+(y1-y0)*t, z0+(z1-z0)*t), bright)
staircase("left_stair", -4.5, -1.0, 1.5, 1.05)
staircase("center_stair", -.4, -.15, 1.5, .95)
staircase("right_stair", 5.2, .25, 2.3, 1.05)
scene.include("stairs", stairs)

# Insulated pipework and elbows, expressed as short jointed tube runs.
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
    add_rod(ducts, f"hanger_{i}", (x, 4.6, 5.0), (x, 4.6, 6.55), .025, steel)
scene.include("ducts_and_hangers", ducts)

# Vertical tank, domed ends, feet and nozzle.
tank = Asset("Green_vertical_tank")
tx, ty = -2.0, -.25
add_rod(tank, "cylindrical_shell", (tx, ty, .38), (tx, ty, 1.92), .53, green)
tank.include("top_dome", ball(radius=.53, center=(tx, ty, 1.92), color=green))
tank.include("bottom_dome", ball(radius=.53, center=(tx, ty, .38), color=green))
# Flatten the visual impression of the heads by allowing shell to overlap them.
for i, (dx, dy) in enumerate(((-.34,-.25),(.34,-.25),(-.34,.25),(.34,.25))):
    add_rod(tank, f"leg_{i}", (tx+dx,ty+dy,.03), (tx+dx,ty+dy,.55), .055, steel)
add_rod(tank, "top_nozzle", (tx,ty,2.38), (tx,ty,2.65), .075, silver)
scene.include("green_tank", tank)

# Foreground conveyors: silver frame, blue belts/rollers and supporting legs.
conveyors = Asset("Foreground_conveyor_lines")
def conveyor(name, x, y, length, width):
    add_box(conveyors, name+"_blue_bed", (length,width,.12), (x,y,.77), blue)
    for side in (-1, 1):
        add_box(conveyors, f"{name}_side_rail_{side}", (length,.075,.16),
                (x,y+side*width/2,.84), bright)
    for j in range(10):
        xx = x-length/2 + (j+.5)*length/10
        add_rod(conveyors, f"{name}_roller_{j}", (xx,y-width/2,.85),
                (xx,y+width/2,.85), .035, silver)
    for dx in (-length*.38, length*.38):
        for dy in (-width*.4, width*.4):
            add_box(conveyors, f"{name}_leg_{dx}_{dy}", (.09,.09,.72),
                    (x+dx,y+dy,.37), steel)
    add_box(conveyors, name+"_drive_motor", (.4,.3,.3),
            (x+length*.36,y+width*.65,.55), steel)
conveyor("front_belt", -3.1, -5.15, 8.3, 1.25)
conveyor("middle_belt", -2.0, -3.55, 7.5, 1.05)
conveyor("right_transfer", 2.5, -1.95, 4.2, .9)
scene.include("conveyor_system", conveyors)

realize(scene)

# Camera parameters are independent of equipment dimensions.
CAM_POSITION = (10.8, -19.5, 8.1)
CAM_TARGET = (-.35, 2.8, 2.5)
CAM_LENS = 32
set_view(CAM_POSITION, CAM_TARGET, lens=CAM_LENS)
sc = bpy.context.scene
sc.render.resolution_x = 512
sc.render.resolution_y = 267
sc.render.resolution_percentage = 100
bpy.context.view_layer.update()

# Stable, approximate visual correspondences; the conveyor point is uncertain
# because the near end is cropped. Evaluate a small lens trial before committing.
anchors = [
    ("tank_top", (tx, ty, 2.45), (.405, .54)),
    ("right_machine_top", (2.1, 4.6, 4.39), (.69, .30)),
    ("left_platform_front", (-6.45, 1.5, 2.82), (.15, .47)),
    ("right_platform_front", (5.1, 2.3, 2.82), (.88, .43)),
]
def project(p):
    bpy.context.view_layer.update()
    cam = sc.camera
    dg = bpy.context.evaluated_depsgraph_get()
    proj = cam.calc_matrix_camera(dg, x=512, y=267, scale_x=1, scale_y=1)
    clip = proj @ cam.matrix_world.inverted() @ Vector((*p, 1))
    if clip.w <= 1e-8:
        return None
    return (.5*(clip.x/clip.w+1), .5*(1-clip.y/clip.w))

previous = [project(p) for _, p, _ in anchors]
sc.camera.data.lens = 34
candidate = [project(p) for _, p, _ in anchors]
def error(points):
    return sum(((v[0]-r[0])*512)**2 + ((v[1]-r[1])*267)**2
               for v, (_, _, r) in zip(points, anchors) if v is not None)
# Keep the trial only if it improves the aggregate landmark discrepancy.
if error(candidate) < error(previous):
    CAM_LENS = 34
else:
    sc.camera.data.lens = CAM_LENS
final = [project(p) for _, p, _ in anchors]
for (name, p, ref), old, trial, chosen in zip(anchors, previous, candidate, final):
    def residual(uv):
        return None if uv is None else (round((uv[0]-ref[0])*512,1),
                                        round((uv[1]-ref[1])*267,1))
    print(name, "reference", ref, "previous", old, residual(old),
          "trial", trial, residual(trial), "final", chosen, residual(chosen))

# Daylight and broad highlights.
if sc.world is None:
    sc.world = bpy.data.worlds.new("SceneWorld")
sc.world.use_nodes = True
nodes = sc.world.node_tree.nodes
background = nodes.get("Background") or nodes.new("ShaderNodeBackground")
output = nodes.get("World Output") or nodes.new("ShaderNodeOutputWorld")
sc.world.node_tree.links.new(background.outputs["Background"], output.inputs["Surface"])
background.inputs["Color"].default_value = (.68, .75, .80, 1)
background.inputs["Strength"].default_value = .45
area_emitter((-6, -2, 6), power=1800, size=7, target=(0, 2, 1.7))
area_emitter((4, 3, 6.3), power=1200, size=6, target=(0, 2, 1))
area_emitter((0, -8, 5), power=850, size=6, target=(0, 2, 2))

# Apply material response to the SceneAct-generated colors without external textures.
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
