# Reference inventory and anchors (normalized image coordinates, visual estimates):
# - Dark steel roof and beams: entire upper region, y=0.00–0.38.
# - Window wall: left background, x=0.00–0.24, y=0.29–0.67.
# - Raised processing line and yellow railings: x=0.10–0.96, y=0.35–0.86.
# - Main stainless machine: x=0.59–0.79, y=0.30–0.66; silver duct rises above it.
# - Smaller machine and ducts: x=0.23–0.48, y=0.30–0.58.
# - Green vertical tank: x=0.36–0.45, y=0.53–0.80, in front of platform.
# - Blue and silver conveyor: x=0.00–0.61, y=0.74–1.00, partly cropped.
# - Yellow stairs: left x=0.06–0.28, center x=0.43–0.58, right x=0.74–0.88.
# - Green floor is visible between and to the right of equipment.
# Roof beams run mainly left-to-right with a shallow diagonal. Conveyor rails and
# platform edges recede toward the right. Railings overlap the machine bodies;
# the tank overlaps the platform. Far equipment and connections are partly occluded.
#
# Approximate expanded primitive count: architecture 65, platforms/rails/stairs 130,
# machines and ducts 75, tank 8, conveyor 80, miscellaneous 20: about 378.
# All dimensions are meters. Hidden equipment details are intentionally uncertain.

from sceneact import *
import bpy
import math
from mathutils import Vector

scene = Scene("Workshop")

# Palette
steel = (0.48, 0.52, 0.53)
silver = (0.68, 0.71, 0.70)
bright = (0.80, 0.83, 0.82)
dark = (0.12, 0.15, 0.16)
beam = (0.085, 0.105, 0.105)
wall = (0.20, 0.23, 0.23)
roof = (0.25, 0.28, 0.27)
yellow = (0.95, 0.67, 0.025)
green = (0.015, 0.37, 0.24)
floor_green = (0.13, 0.34, 0.26)
blue = (0.08, 0.30, 0.68)
white = (0.78, 0.81, 0.79)
window = (0.68, 0.80, 0.82)

def add(asset, name, node):
    asset.include(name, node)

def B(asset, name, size, center, color):
    add(asset, name, box(size=size, center=center, color=color))

def R(asset, name, a, b, radius, color):
    add(asset, name, rod(radius=radius, start=a, end=b, color=color))

# Architecture: broad roof and floor, steel posts, wall and vertical strip windows.
arch = Asset("Steel framed hall")
B(arch, "epoxy floor", (23, 16, .14), (0, 1, -.08), floor_green)
B(arch, "roof deck", (23, 16, .16), (0, 1, 7.35), roof)
B(arch, "back wall", (23, .18, 7.3), (0, 8.9, 3.65), wall)
B(arch, "left wall", (.18, 16, 7.3), (-11.4, 1, 3.65), wall)
# Tall glazing is set just forward of the dark wall, with dark mullions.
for i, x in enumerate([-10.3, -8.9, -7.5, -6.1, -4.7, -3.3]):
    B(arch, "window %d" % i, (.56, .035, 3.1), (x, 8.77, 2.8), window)
    B(arch, "window center mullion %d" % i, (.035, .04, 3.1), (x, 8.73, 2.8), beam)
    for j, z in enumerate([1.75, 2.55, 3.35]):
        B(arch, "window crossbar %d %d" % (i, j), (.56, .045, .035), (x, 8.72, z), beam)
# Structural columns and visible connections to transverse and longitudinal beams.
for i, x in enumerate([-10.9, -6.5, -2.1, 2.3, 6.7, 11.1]):
    for j, y in enumerate([-6.5, 1.0, 8.6]):
        B(arch, "column %d %d" % (i, j), (.24, .25, 7.3), (x, y, 3.65), beam)
    B(arch, "roof transverse girder %d" % i, (.25, 15.5, .30), (x, 1, 7.07), beam)
for i, y in enumerate([-6.5, -2.7, 1.1, 4.9, 8.6]):
    B(arch, "roof longitudinal girder %d" % i, (22, .22, .30), (0, y, 7.04), beam)
for i, x in enumerate([-8, -2, 4, 9]):
    B(arch, "ceiling light %d" % i, (2.1, .12, .04), (x, 3.3, 7.23), white)
scene.include("architecture", arch)

# Long steel platform: distinct deck, legs, rails, and staircases.
platform = Asset("Raised machinery platform")
B(platform, "deck slab", (16.8, 3.2, .20), (.1, 3.4, 2.40), steel)
B(platform, "front fascia", (16.8, .15, .45), (.1, 1.82, 2.25), dark)
B(platform, "back fascia", (16.8, .15, .40), (.1, 4.98, 2.25), steel)
for i, x in enumerate([-7.8, -5.2, -2.6, 0, 2.6, 5.2, 7.9]):
    for j, y in enumerate([2.0, 4.8]):
        B(platform, "leg %d %d" % (i, j), (.14, .14, 2.35), (x, y, 1.17), steel)
# Railings at front; leave gaps aligned with the stair landings.
for seg, (x1, x2) in enumerate([(-8.2, -6.6), (-5.0, -1.8), (-.3, 3.6), (5.0, 8.4)]):
    for h in [2.95, 3.52]:
        R(platform, "front rail %d %.2f" % (seg, h), (x1, 1.75, h), (x2, 1.75, h), .035, yellow)
    n = max(1, int((x2 - x1) / .7))
    for k in range(n + 1):
        x = x1 + (x2 - x1) * k / n
        R(platform, "front upright %d %d" % (seg, k), (x, 1.75, 2.47), (x, 1.75, 3.53), .028, yellow)
for h in [2.95, 3.52]:
    R(platform, "back rail %.2f" % h, (-8.2, 5.02, h), (8.4, 5.02, h), .03, yellow)
for i in range(17):
    x = -8.2 + i * 1.04
    R(platform, "back upright %d" % i, (x, 5.02, 2.47), (x, 5.02, 3.52), .026, yellow)

def stairs(asset, label, x, y_front, y_back, width):
    # Bottom at y_front, landing at y_back.
    z0, z1 = .12, 2.47
    for side in [-1, 1]:
        xx = x + side * width / 2
        R(asset, label + " stringer " + str(side),
          (xx, y_front, z0), (xx, y_back, z1), .055, yellow)
        R(asset, label + " handrail " + str(side),
          (xx, y_front, z0 + .95), (xx, y_back, z1 + .95), .035, yellow)
        for j in range(4):
            t = j / 3
            yy = y_front + (y_back-y_front)*t
            zz = z0 + (z1-z0)*t
            R(asset, label + " post %d %d" % (side, j),
              (xx, yy, zz), (xx, yy, zz+.95), .026, yellow)
    for j in range(9):
        t = (j + .5) / 9
        yy = y_front + (y_back-y_front)*t
        zz = z0 + (z1-z0)*t
        B(asset, label + " tread %d" % j, (width, .23, .055), (x, yy, zz), steel)

stairs(platform, "left stair", -5.8, -1.0, 1.75, 1.15)
stairs(platform, "middle stair", -1.0, -1.0, 1.75, 1.05)
stairs(platform, "right stair", 4.25, -1.2, 1.75, 1.12)
scene.include("platform and access stairs", platform)

# Processing machines: large box housings with dark working openings and supports.
machines = Asset("Stainless processing machines")
def machine(label, x, y, width, depth, height):
    base = 2.52
    B(machines, label + " main body", (width, depth, height),
      (x, y, base + height/2), silver)
    B(machines, label + " lower plinth", (width+.16, depth+.10, .22),
      (x, y, base+.12), dark)
    B(machines, label + " top hood", (width*.88, depth*.92, .26),
      (x, y, base+height+.12), bright)
    # Front face looks toward the camera.
    fy = y-depth/2-.012
    B(machines, label + " front opening", (width*.75, .035, height*.39),
      (x, fy, base+height*.47), dark)
    B(machines, label + " front roller", (width*.69, .06, .15),
      (x, fy-.04, base+height*.36), steel)
    for j in range(5):
        B(machines, label + " opening slat %d" % j, (width*.68, .04, .025),
          (x, fy-.045, base+height*.39+j*.10), bright)
    for dx in [-.43, .43]:
        B(machines, label + " corner trim " + str(dx), (.07, .05, height*.72),
          (x+width*dx, fy-.025, base+height*.52), bright)
    B(machines, label + " control cabinet", (.50, .28, .70),
      (x+width*.39, fy-.18, base+height*.50), white)
machine("main machine", 3.1, 3.65, 3.0, 2.1, 1.75)
machine("left machine", -5.1, 3.7, 2.6, 1.9, 1.35)
machine("middle machine", -.9, 3.8, 2.1, 1.7, 1.05)
machine("far machine", 7.1, 4.0, 1.45, 1.5, 1.15)
scene.include("processing line", machines)

# Insulated overhead ducts and visible elbows, represented by short connected rods.
ducts = Asset("Insulated ducts and process pipes")
def tube(label, points, radius):
    for i in range(len(points)-1):
        R(ducts, label + " section %d" % i, points[i], points[i+1], radius, bright)
    for i, p in enumerate(points[1:-1]):
        add(ducts, label + " elbow %d" % i, ball(radius, center=p, color=silver))
tube("main rising duct", [(3.1,3.8,4.3),(3.1,3.8,5.35),(3.35,3.8,5.65),
                           (4.1,3.8,5.35),(4.35,3.8,5.05)], .22)
tube("left duct", [(-5.2,3.9,4.0),(-5.2,3.9,4.85),(-4.9,3.9,5.05),
                    (-3.3,3.9,4.8),(-2.8,3.9,4.15)], .17)
tube("connecting duct", [(-2.9,4.1,4.0),(-1.8,4.1,4.45),
                          (1.2,4.1,4.45),(1.8,4.1,4.2)], .12)
tube("side process pipe", [(-7.8,5.2,3.8),(7.8,5.2,3.8)], .09)
for i, x in enumerate([-5, -1, 3, 7]):
    R(ducts, "hanger %d" % i, (x, 4.1, 4.5), (x, 4.1, 6.9), .025, steel)
scene.include("ductwork", ducts)

# Vertical painted receiver tank: cylinder, rounded caps, feet and a small nozzle.
tank = Asset("Green vertical receiver tank")
tx, ty = -3.35, .15
R(tank, "cylindrical shell", (tx,ty,.35), (tx,ty,2.25), .58, green)
add(tank, "rounded top", ball(.58, center=(tx,ty,2.25), color=green))
add(tank, "rounded bottom", ball(.58, center=(tx,ty,.35), color=green))
for i, dx in enumerate([-.38, .38]):
    B(tank, "foot %d" % i, (.14,.18,.38), (tx+dx,ty,.19), dark)
R(tank, "top nozzle", (tx,ty,2.72), (tx,ty,2.98), .09, steel)
R(tank, "side pipe", (tx+.5,ty,1.65), (tx+.9,ty,1.65), .07, steel)
scene.include("green tank", tank)

# Conveyor occupies the foreground: blue belt sections, silver side rails, cross
# rollers, support legs and side drive. Parallel lanes overlap in the photograph.
conv = Asset("Foreground conveyor line")
for lane, cy in enumerate([-5.25, -3.85]):
    B(conv, "blue conveyor bed %d" % lane, (12.2, 1.10, .12), (-3.25, cy, .87), blue)
    for side in [-1, 1]:
        yy = cy + side*.61
        B(conv, "longitudinal guide %d %d" % (lane,side),
          (12.4,.08,.20), (-3.25,yy,1.01), bright)
        for j, x in enumerate([-8.7,-5.4,-2.1,1.2]):
            B(conv, "support %d %d %d" % (lane,side,j),
              (.09,.10,.87), (x,yy,.43), steel)
    for j in range(18):
        x = -9.0 + j*.66
        R(conv, "roller %d %d" % (lane,j), (x,cy-.52,.96), (x,cy+.52,.96), .038, silver)
    B(conv, "end cross member %d" % lane, (.12,1.3,.15), (2.8,cy,.83), steel)
B(conv, "drive motor", (.65,.44,.38), (1.9,-3.1,.55), dark)
scene.include("blue roller conveyor", conv)

# Additional transfer tables and vertical side cabinets visible under the platforms.
support = Asset("Transfer tables and utilities")
for i, (x,y) in enumerate([(-7.4,-1.8),(-3.0,-2.0),(.6,-1.5),(7.1,1.4)]):
    B(support, "transfer frame %d" % i, (2.3,1.1,.15), (x,y,1.05), bright)
    for dx in [-.9,.9]:
        for dy in [-.43,.43]:
            B(support, "transfer leg %d %.1f %.1f" % (i,dx,dy),
              (.07,.07,1.0), (x+dx,y+dy,.5), steel)
B(support, "right electrical enclosure", (.75,.50,2.2), (8.0,3.4,3.55), white)
scene.include("transfer equipment", support)

realize(scene)

# Camera parameters remain independent of asset dimensions.
CAMERA_POSITION = (12.8, -23.5, 8.2)
CAMERA_TARGET = (-.2, 2.0, 3.0)
CAMERA_LENS = 35
set_view(CAMERA_POSITION, CAMERA_TARGET, lens=CAMERA_LENS, sensor=36)

sc = bpy.context.scene
sc.render.resolution_x = 512
sc.render.resolution_y = 267
sc.render.resolution_percentage = 100
sc.render.pixel_aspect_x = 1
sc.render.pixel_aspect_y = 1

# Reference estimates and computed positions are recorded separately.
landmarks = [
    ("left window top", (-8.9, 8.73, 4.35), (.10, .34)),
    ("main machine top", (3.1, 3.65, 4.40), (.68, .31)),
    ("tank top", (tx, ty, 2.83), (.40, .53)),
    ("near conveyor end", (-9.35, -5.86, 1.01), (.02, .94)),
]
bpy.context.view_layer.update()
cam = sc.camera
dg = bpy.context.evaluated_depsgraph_get()
projection = cam.calc_matrix_camera(
    dg, x=sc.render.resolution_x, y=sc.render.resolution_y,
    scale_x=sc.render.pixel_aspect_x, scale_y=sc.render.pixel_aspect_y)
print("Landmark | reference | projected")
for name, point, ref in landmarks:
    clip = projection @ cam.matrix_world.inverted() @ Vector((*point, 1.0))
    uv = None if clip.w <= 1e-8 else (
        .5*(clip.x/clip.w+1), .5*(1-clip.y/clip.w))
    print(name, ref, None if uv is None else tuple(round(v,3) for v in uv))

# World initialization is explicit because realization clears the Blender scene.
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
background.inputs["Color"].default_value = (.67, .74, .76, 1)
background.inputs["Strength"].default_value = .55

area_emitter((-7, 5, 6.4), power=1800, size=7, target=(0,0,1))
area_emitter((2, -3, 7), power=1300, size=8, target=(0,2,1.5))
area_emitter((8, 5, 6.7), power=1000, size=6, target=(2,2,1))

# Adjust existing realized materials by their displayed colors.
for mat in bpy.data.materials:
    if not mat.use_nodes:
        continue
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf is None:
        continue
    c = tuple(mat.diffuse_color[:3])
    if max(abs(c[i]-floor_green[i]) for i in range(3)) < .03:
        bsdf.inputs["Roughness"].default_value = .22
        bsdf.inputs["Metallic"].default_value = .1
    elif any(max(abs(c[i]-v[i]) for i in range(3)) < .03
             for v in [steel, silver, bright]):
        bsdf.inputs["Metallic"].default_value = .72
        bsdf.inputs["Roughness"].default_value = .28
    elif max(abs(c[i]-yellow[i]) for i in range(3)) < .03:
        bsdf.inputs["Metallic"].default_value = .25
        bsdf.inputs["Roughness"].default_value = .38

sc.render.engine = "CYCLES"
sc.cycles.samples = 32
sc.cycles.use_denoising = True
try:
    sc.view_settings.view_transform = "AgX"
except Exception:
    pass
