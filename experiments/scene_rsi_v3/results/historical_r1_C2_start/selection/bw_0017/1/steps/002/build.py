from sceneact import *
import bpy

# Reference inventory, approximate normalized image bounds:
# Hall: dark ribbed ceiling and connected beams in upper 0–0.38; tall narrow
# windows at left, green floor visible mainly lower right. Building extends beyond
# the image. Rear and right-hand building details are partly obscured.
# Processing line: stainless machines and elevated steel deck across x=.23–.96,
# y=.30–.76; larger front-facing unit at x=.62–.79, with dark slatted opening.
# Yellow guardrails and stairs cross x=.08–.96, y=.43–.99, in front of machinery.
# Silver ducts rise over two machines and run sideways; their hidden connections
# are approximate. Green cylindrical tank is in front at x=.36–.45, y=.53–.79.
# Blue and silver conveyor frames cover the lower foreground, x=0–.70,
# and are cropped by the frame. Small distant equipment at right is uncertain.
#
# Review of previous view: the camera was outside and above the hall, exposing
# the roof exterior and leaving excessive empty floor. The reference is inside,
# closer to eye level, with the conveyor and machinery filling the frame. This
# revision extends the hall around the camera, lowers the camera and brings it
# nearer the line. The machinery, railings and conveyor remain separate assets.
#
# Estimated expanded primitives: building ~110, machinery and platform ~75,
# guardrails ~45, three stairs ~75, ducts and tank ~35, conveyors ~100:
# approximately 440 meshes, including expanded tube paths.

scene = Scene("Production hall")

darksteel = (.105, .125, .13)
edge = (.19, .21, .21)
roofcolor = (.25, .27, .26)
wallcolor = (.24, .26, .26)
glass = (.72, .84, .90)
floorcolor = (.075, .27, .20)
yellow = (.95, .62, .015)
silver = (.58, .62, .61)
lightmetal = (.76, .79, .77)
dimmetal = (.33, .37, .36)
black = (.11, .13, .13)
blue = (.035, .22, .55)
green = (.015, .29, .19)
white = (.83, .85, .82)

def B(parent, name, size, center, color):
    parent.include(name, box(size=size, center=center, color=color))

def R(parent, name, a, b, radius, color):
    parent.include(name, rod(radius=radius, start=a, end=b, color=color))

# The enclosing structure extends behind the camera to avoid a cutaway view.
hall = Asset("steel_frame_hall")
B(hall, "epoxy_floor", (25, 38, .12), (0, 1, -.08), floorcolor)
B(hall, "left_exterior_wall", (.18, 38, 6.5), (-10, 1, 3.25), wallcolor)
B(hall, "distant_wall", (20, .18, 6.5), (0, 19.9, 3.25), wallcolor)
B(hall, "roof_deck", (20.2, 38, .15), (0, 1, 6.48), roofcolor)

# Windows are bright inset panels, with visible dark mullions and sills.
for i in range(12):
    y = -14 + i * 3.0
    B(hall, "window_%02d" % i, (.035, 1.05, 2.8),
      (-9.88, y, 2.75), glass)
    for j, z in enumerate((1.36, 2.05, 3.10, 4.14)):
        B(hall, "window_crossbar_%02d_%d" % (i, j),
          (.07, 1.09, .045), (-9.82, y, z), darksteel)
    B(hall, "window_mullion_%02d" % i, (.07, .045, 2.8),
      (-9.82, y, 2.75), darksteel)

# Column webs, flanges and roof beam intersections.
for i, y in enumerate((-14, -9, -4, 1, 6, 11, 16, 19.7)):
    for side, x in enumerate((-9.75, 9.75)):
        B(hall, "column_web_%d_%d" % (i, side), (.18, .20, 6.3),
          (x, y, 3.15), darksteel)
        B(hall, "column_flange_%d_%d" % (i, side), (.35, .08, 6.3),
          (x, y, 3.15), edge)
    B(hall, "transverse_roof_beam_%d" % i, (19.6, .23, .30),
      (0, y, 6.18), darksteel)
for i, x in enumerate((-8, -5, -2, 1, 4, 7)):
    B(hall, "roof_purlin_%d" % i, (.11, 38, .14),
      (x, 1, 6.33), edge)
for i, y in enumerate((-10, -3, 4, 11, 18)):
    B(hall, "ceiling_light_strip_%d" % i, (2.4, .12, .025),
      (-1, y, 6.30), white)
scene.include("hall", hall)

# Main deck and visible supporting steel.
plant = Asset("processing_platform_and_machines")
B(plant, "deck", (13.8, 3.15, .17), (.15, 3.75, 2.04), dimmetal)
for i, x in enumerate((-6.3, -3.1, .1, 3.3, 6.4)):
    for j, y in enumerate((2.24, 5.18)):
        B(plant, "deck_leg_%d_%d" % (i, j), (.16, .16, 1.98),
          (x, y, 1.0), dimmetal)
B(plant, "front_deck_beam", (13.8, .17, .24),
  (.15, 2.17, 1.92), silver)
B(plant, "back_deck_beam", (13.8, .17, .24),
  (.15, 5.25, 1.92), silver)

specs = (
    ("left_processor", -4.45, 3.85, 2.8, 2.0, 1.25),
    ("middle_processor", -1.25, 4.10, 2.6, 1.9, 1.20),
    ("large_processor", 3.05, 3.85, 3.35, 2.10, 2.08),
    ("right_equipment", 7.10, 4.95, 1.35, 1.45, 1.65),
)
for name, x, y, w, d, h in specs:
    machine = Asset(name)
    base = 2.13
    B(machine, "stainless_housing", (w, d, h),
      (x, y, base + h/2), silver)
    B(machine, "top_panel", (w*.95, d*.92, .15),
      (x, y, base + h + .055), lightmetal)
    front = y - d/2 - .025
    B(machine, "dark_processing_aperture", (w*.82, .035, h*.34),
      (x, front, base+h*.55), black)
    B(machine, "lower_front_panel", (w*.90, .055, h*.21),
      (x, front-.025, base+h*.18), lightmetal)
    for j in range(4):
        B(machine, "aperture_slat_%d" % j, (w*.78, .035, .035),
          (x, front-.03, base+h*(.43+j*.075)), dimmetal)
    B(machine, "control_box", (.31, .18, .46),
      (x+w*.38, front-.10, base+h*.72), white)
    plant.include(name, machine)
scene.include("platform_and_machines", plant)

# Railings occupy the horizontal band in front of the machines.
rails = Asset("yellow_platform_guardrails")
for i in range(18):
    x = -6.65 + i*.79
    R(rails, "front_post_%02d" % i, (x, 2.10, 2.10),
      (x, 2.10, 3.13), .028, yellow)
for i, z in enumerate((2.60, 3.12)):
    R(rails, "front_rail_%d" % i, (-6.70, 2.10, z),
      (6.80, 2.10, z), .032, yellow)
for i, y in enumerate((2.15, 2.9, 3.65, 4.4, 5.2)):
    R(rails, "end_post_%d" % i, (6.83, y, 2.10),
      (6.83, y, 3.13), .028, yellow)
for i, z in enumerate((2.60, 3.12)):
    R(rails, "end_rail_%d" % i, (6.83, 2.10, z),
      (6.83, 5.23, z), .032, yellow)
for i, x in enumerate((-6.5, -4.3, -2.1, .1, 2.3, 4.5, 6.7)):
    R(rails, "back_post_%d" % i, (x, 5.25, 2.10),
      (x, 5.25, 3.10), .026, yellow)
R(rails, "back_top", (-6.65, 5.25, 3.10),
  (6.83, 5.25, 3.10), .03, yellow)
scene.include("guardrails", rails)

def stair(name, x, front_y, back_y, width, height, count):
    s = Asset(name)
    for side in (-1, 1):
        xx = x + side*width/2
        R(s, "stringer_%s" % side, (xx, front_y, .10),
          (xx, back_y, height), .05, dimmetal)
        R(s, "top_handrail_%s" % side, (xx, front_y, 1.08),
          (xx, back_y, height+1.0), .034, yellow)
        R(s, "middle_handrail_%s" % side, (xx, front_y, .60),
          (xx, back_y, height+.5), .025, yellow)
        for j in range(4):
            t = j/3
            yy = front_y + (back_y-front_y)*t
            zz = .10 + (height-.10)*t
            R(s, "post_%s_%d" % (side, j), (xx, yy, zz),
              (xx, yy, zz+1), .025, yellow)
    for j in range(count):
        t = (j+.5)/count
        B(s, "tread_%02d" % j, (width, .30, .055),
          (x, front_y+(back_y-front_y)*t,
           .10+(height-.10)*t), lightmetal)
    return s

scene.include("left_stair", stair("left_stair", -5.0, -1.1, 2.1, 1.0, 2.08, 9))
scene.include("middle_stair", stair("middle_stair", -.8, -1.15, 2.1, .95, 2.08, 9))
scene.include("right_stair", stair("right_stair", 6.25, -1.4, 2.1, 1.05, 2.08, 9))

ducts = Asset("silver_insulated_ducts")
ducts.include("left_bent_duct", sweep_tube(
    points=[(-4.3, 4.1, 3.4), (-4.3, 4.1, 4.55),
            (-4.0, 4.1, 4.78), (-2.7, 4.1, 4.65),
            (-2.35, 4.1, 4.10)],
    radius=.17, color=lightmetal))
ducts.include("large_bent_duct", sweep_tube(
    points=[(3.0, 4.0, 4.18), (3.0, 4.0, 5.15),
            (3.25, 4.0, 5.38), (4.2, 4.0, 5.05),
            (4.2, 4.0, 4.2)],
    radius=.21, color=lightmetal))
R(ducts, "horizontal_pipe", (-6.3, 5.4, 4.25),
  (7.0, 5.4, 4.25), .105, silver)
R(ducts, "lower_cross_pipe", (-6.2, 2.5, 1.35),
  (6.7, 2.5, 1.35), .075, lightmetal)
for i, x in enumerate((-4, -1, 2, 5)):
    R(ducts, "ceiling_hanger_%d" % i, (x, 5.4, 4.25),
      (x, 5.4, 6.15), .024, dimmetal)
scene.include("ductwork", ducts)

tank = Asset("green_vertical_tank")
tx, ty = -2.45, -.45
R(tank, "cylindrical_shell", (tx, ty, .55), (tx, ty, 1.85), .47, green)
tank.include("upper_head", ball(radius=.47, center=(tx, ty, 1.85), color=green))
tank.include("lower_head", ball(radius=.47, center=(tx, ty, .55), color=green))
R(tank, "top_nozzle", (tx, ty, 2.25), (tx, ty, 2.48), .07, silver)
R(tank, "top_flange", (tx, ty, 2.40), (tx, ty, 2.45), .14, dimmetal)
for i, (dx, dy) in enumerate(((-.25,-.20), (.25,-.20), (-.25,.20), (.25,.20))):
    R(tank, "leg_%d" % i, (tx+dx,ty+dy,.05),
      (tx+dx,ty+dy,.62), .04, dimmetal)
scene.include("tank", tank)

# Multiple open conveyor frames overlap in the lower foreground.
conveyors = Asset("foreground_conveyor_line")
def conveyor(name, cx, cy, length, width, height):
    p = Asset(name)
    B(p, "blue_belt", (length, width, .075), (cx, cy, height), blue)
    for side in (-1, 1):
        B(p, "side_rail_%s" % side, (length, .075, .17),
          (cx, cy+side*width/2, height+.07), lightmetal)
    for i in range(14):
        x = cx-length/2+(i+.5)*length/14
        R(p, "roller_%02d" % i, (x,cy-width*.48,height+.055),
          (x,cy+width*.48,height+.055), .023, lightmetal)
    for i, dx in enumerate((-length*.4, 0, length*.4)):
        for j, dy in enumerate((-width*.4, width*.4)):
            B(p, "support_%d_%d" % (i,j), (.075,.075,height-.04),
              (cx+dx, cy+dy, (height-.04)/2), silver)
    conveyors.include(name, p)

conveyor("front_conveyor", -3.65, -5.5, 9.8, 1.05, .76)
conveyor("middle_conveyor", -3.35, -4.05, 9.0, .88, .82)
conveyor("rear_conveyor", -3.0, -2.75, 8.1, .72, .88)
B(conveyors, "transfer_housing", (2.2, 1.15, .58),
  (.10, -2.85, .96), lightmetal)
B(conveyors, "transfer_top", (1.85, .85, .045),
  (.10, -2.85, 1.27), dimmetal)
B(conveyors, "drive_motor", (.5, .33, .34),
  (1.45, -2.8, .55), dimmetal)
# Side guides and supporting rails across the transfer area.
for i, x in enumerate((-1.1, -.2, .7, 1.6, 2.5)):
    B(conveyors, "transfer_support_%d" % i, (.07, 1.5, .08),
      (x, -2.0, 1.02), silver)
scene.include("conveyors", conveyors)

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
background.inputs["Color"].default_value = (.72, .80, .84, 1)
background.inputs["Strength"].default_value = .48

for mat in bpy.data.materials:
    if not mat.use_nodes:
        continue
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf is None:
        continue
    c = bsdf.inputs["Base Color"].default_value
    r, g, b = c[0], c[1], c[2]
    if abs(r-floorcolor[0]) < .02 and abs(g-floorcolor[1]) < .02:
        bsdf.inputs["Roughness"].default_value = .18
        bsdf.inputs["Metallic"].default_value = .12
    elif abs(r-green[0]) < .02 and abs(g-green[1]) < .02:
        bsdf.inputs["Roughness"].default_value = .32
        bsdf.inputs["Metallic"].default_value = .25
    elif abs(r-g) < .10 and abs(g-b) < .10 and r > .32:
        bsdf.inputs["Metallic"].default_value = .66
        bsdf.inputs["Roughness"].default_value = .32
    elif r > .65 and g > .38 and b < .15:
        bsdf.inputs["Metallic"].default_value = .28
        bsdf.inputs["Roughness"].default_value = .38

# Interior viewpoint: the roof surrounds the camera and is seen from beneath.
set_view((2.2, -13.0, 4.5), (0.0, 2.8, 2.9), lens=28, sensor=36)
area_emitter((-8.8, -1, 4.1), power=2200, size=6,
             target=(0, 2, 1.8), color=(.82,.91,1.0))
area_emitter((0, 2.0, 6.05), power=1800, size=7,
             target=(0, 2, 0), color=(1.0,.97,.92))
area_emitter((5, -7, 5.6), power=1200, size=6,
             target=(0, 2, 2), color=(1.0,1.0,1.0))

# The external runner performs the final render and saves the project.
sc.render.engine = "CYCLES"
sc.cycles.use_denoising = True
sc.render.resolution_x = 3840
sc.render.resolution_y = 2160
sc.render.resolution_percentage = 100
sc.render.image_settings.file_format = "PNG"
try:
    sc.view_settings.view_transform = "AgX"
except TypeError:
    sc.view_settings.view_transform = "Filmic"
