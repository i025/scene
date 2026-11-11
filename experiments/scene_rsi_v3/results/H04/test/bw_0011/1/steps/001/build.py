# Reference inventory and approximate normalized image bounds:
# - Foreground: light gray floor, x=0..1, y=.79..1; rear edge rises toward
#   the back/right corner at approximately (.70,.79).
# - Back wall: blue modular panels, x=.10..64, y=.22..83. A stainless
#   double-door cabinet occupies x=.16..31, y=.40..84.
# - Feature wall: pale dandelion image, x=.37..64, y=.24..80, behind
#   the cabinet's right side. Fine floral details are interpreted geometry.
# - Right wall: blue panels, x=.64..91, y=.14..93; dark time display
#   approximately x=.79..88, y=.33..51.
# - Ceiling: dark exposed ceiling and linear grid, x=0..1, y=0..23;
#   bright rectangular LED panels near the rear. Some structure is cropped.
# - Rounded pale skirting follows the wall/floor junction.
# Image anchors: back-wall lower left (.10,.84), feature-wall upper left
# (.37,.24), back/right corner (.64,.25), right-wall foreground lower
# corner (.91,.93), screen center (.84,.42).
# Dominant edges: back-wall panel joints nearly vertical, ceiling grid
# recedes toward the back, right-wall base slopes down toward the right.
# The wall graphic and ceiling service arrangement are partly uncertain.
#
# Expanded geometry estimate: architecture and skirting ~25 meshes,
# cabinet ~28, ceiling grid and services ~40, graphic ~110 rods and boxes,
# screen ~5; total approximately 210 meshes. Text is added with bpy.

import math
import random
import bpy
from mathutils import Vector
from sceneact import Scene, Asset, box, rod, realize, set_view, area_emitter

random.seed(12)

# Major dimensions and camera parameters are independent and editable.
WALL_LEFT = -3.05
CORNER_X = 2.05
BACK_Y = 2.0
RIGHT_FRONT_Y = -2.7
WALL_H = 3.15
CAMERA_POSITION = (0.25, -8.5, 2.65)
CAMERA_TARGET = (0.15, 1.55, 1.60)
CAMERA_LENS = 27.0

blue = (0.055, 0.48, 0.72)
blue_dark = (0.025, 0.31, 0.48)
floor_col = (0.52, 0.56, 0.55)
trim_col = (0.77, 0.83, 0.81)
metal = (0.55, 0.61, 0.60)
metal_dark = (0.24, 0.29, 0.29)
glass_col = (0.25, 0.34, 0.34)
ceiling_col = (0.105, 0.135, 0.14)
grid_col = (0.28, 0.38, 0.40)
art_bg = (0.80, 0.90, 0.85)
art_dark = (0.20, 0.075, 0.17)
art_light = (0.43, 0.49, 0.43)

scene = Scene("Clean laboratory corner")

architecture = Asset("Modular room architecture")
architecture.include("floor", box((8.5, 9.5, .10), center=(0, -.8, -.06), color=floor_col))
architecture.include("back blue wall", box((CORNER_X-WALL_LEFT, .10, WALL_H),
    center=((CORNER_X+WALL_LEFT)/2, BACK_Y, WALL_H/2), color=blue))
architecture.include("right blue wall", box((.10, BACK_Y-RIGHT_FRONT_Y, WALL_H),
    center=(CORNER_X, (BACK_Y+RIGHT_FRONT_Y)/2, WALL_H/2), color=blue))
# Fine dark joints make the modular cladding legible without deep gaps.
for i, x in enumerate([-2.60, -1.65, -.72, .24, 1.17, 1.73]):
    architecture.include("back panel joint %02d" % i,
        box((.012, .015, WALL_H-.12), center=(x, BACK_Y-.057, WALL_H/2), color=blue_dark))
for i, y in enumerate([1.46, .78, .10, -.58, -1.26, -1.94, -2.62]):
    architecture.include("right panel joint %02d" % i,
        box((.015, .012, WALL_H-.12), center=(CORNER_X-.057, y, WALL_H/2), color=blue_dark))
# Low coving is formed by a shallow plinth and a rounded transition.
architecture.include("back cove", box((CORNER_X-WALL_LEFT, .16, .13),
    center=((CORNER_X+WALL_LEFT)/2, BACK_Y-.09, .065), color=trim_col))
architecture.include("back cove round", rod(.075,
    start=(WALL_LEFT, BACK_Y-.16, .075), end=(CORNER_X, BACK_Y-.16, .075), color=trim_col))
architecture.include("right cove", box((.16, BACK_Y-RIGHT_FRONT_Y, .13),
    center=(CORNER_X-.09, (BACK_Y+RIGHT_FRONT_Y)/2, .065), color=trim_col))
architecture.include("right cove round", rod(.075,
    start=(CORNER_X-.16, RIGHT_FRONT_Y, .075), end=(CORNER_X-.16, BACK_Y, .075), color=trim_col))
scene.include("room", architecture)

# Dandelion mural: pale ground and a sparse set of dark crossing stems and
# fine seed rays. It is deliberately modeled, not an image projection.
art = Asset("Dandelion feature wall")
ART_X0, ART_X1 = -1.02, .91
ART_Z0, ART_Z1 = .14, 3.03
ART_Y = BACK_Y-.075
art.include("pale mural panel", box((ART_X1-ART_X0, .025, ART_Z1-ART_Z0),
    center=((ART_X0+ART_X1)/2, ART_Y, (ART_Z0+ART_Z1)/2), color=art_bg))
# Pale lower stripe evokes the warm lower portion of the photograph.
art.include("warm lower image field", box((ART_X1-ART_X0, .006, .30),
    center=((ART_X0+ART_X1)/2, ART_Y-.017, .29), color=(.76,.70,.51)))
def art_line(name, a, b, radius, col):
    art.include(name, rod(radius, start=(a[0], ART_Y-.025, a[1]),
                         end=(b[0], ART_Y-.025, b[1]), color=col))
stems = [
    ((-.95,.20),(.24,1.43)), ((-.88,.37),(.72,.68)),
    ((-.60,.14),(.61,1.05)), ((-.15,.14),(.27,1.57)),
    ((.75,.18),(.12,1.38)), ((.85,.49),(.41,1.44)),
    ((-.93,.82),(.06,.50)), ((-.42,.27),(-.70,1.12)),
    ((.32,.17),(-.23,.83)), ((-.20,1.13),(-.47,2.72)),
    ((.18,1.45),(.62,1.88)), ((-.02,1.33),(-.70,1.57)),
]
for i, (a,b) in enumerate(stems):
    art_line("stem %02d" % i, a, b, .012 if i < 8 else .008, art_dark)
# Partial seed heads around the top and side of the panel.
heads = [(-.50,2.70,.46), (.53,2.82,.48), (-.93,1.65,.46),
         (.78,1.48,.38), (-.63,.73,.34), (.36,.52,.30)]
for j,(hx,hz,r) in enumerate(heads):
    for k in range(13):
        angle = 2*math.pi*k/13 + .12*j
        x1 = hx + .06*math.cos(angle)
        z1 = hz + .06*math.sin(angle)
        x2 = hx + r*math.cos(angle)
        z2 = hz + r*math.sin(angle)
        if ART_X0+.02 < x2 < ART_X1-.02 and ART_Z0+.02 < z2 < ART_Z1-.02:
            art_line("seed ray %d %02d" % (j,k), (x1,z1), (x2,z2), .003, art_light)
scene.include("feature wall", art)

# Stainless cabinet with two glazed doors, shelves visible through glass,
# narrow central handles, and a slightly projecting frame.
cab = Asset("Stainless glass storage cabinet")
CX, CY = -2.03, BACK_Y-.19
CW, CH, CZ = 1.04, 1.90, 1.03
cab.include("cabinet body", box((CW,.28,CH), center=(CX,CY+.07,CZ), color=metal))
cab.include("dark interior", box((CW-.15,.025,CH-.16),
    center=(CX,CY-.081,CZ), color=metal_dark))
for x in [CX-CW/2+.045, CX, CX+CW/2-.045]:
    cab.include("vertical door frame %.2f" % x,
        box((.07,.055,CH-.07), center=(x,CY-.12,CZ), color=metal))
for z in [CZ-CH/2+.04, CZ+CH/2-.04]:
    cab.include("horizontal door frame %.2f" % z,
        box((CW,.055,.075), center=(CX,CY-.12,z), color=metal))
# Interior shelves are placed in front of the dark recess, behind the glazing.
for i,z in enumerate([.40,.68,.96,1.24,1.52,1.80]):
    cab.include("shelf %02d" % i, box((CW-.14,.12,.025),
        center=(CX,CY-.10,z), color=(.67,.72,.70)))
for i,x in enumerate([CX-.25,CX+.25]):
    cab.include("glass door %d" % i, box((.39,.014,CH-.20),
        center=(x,CY-.156,CZ), color=glass_col, opacity=.34))
for i,x in enumerate([CX-.052,CX+.052]):
    cab.include("door handle %d" % i, rod(.012,
        start=(x,CY-.20,.91), end=(x,CY-.20,1.11), color=(.8,.84,.82)))
scene.include("storage cabinet", cab)

# Wall monitor is mounted parallel to the right wall.
monitor = Asset("Digital wall display")
MY, MZ = .72, 2.13
monitor.include("display bezel", box((.055,.75,.65), center=(CORNER_X-.085,MY,MZ),
                                      color=(.055,.10,.17)))
monitor.include("display face", box((.012,.66,.55), center=(CORNER_X-.119,MY,MZ),
                                     color=(.025,.11,.22)))
scene.include("digital display", monitor)

# Suspended T-grid with exposed dark service void and several LED panels.
ceiling = Asset("Exposed grid ceiling")
ceiling.include("dark overhead structure", box((7.0,7.0,.12),
    center=(0,-.1,3.65), color=ceiling_col))
for i,x in enumerate([-3.0,-2.3,-1.6,-.9,-.2,.5,1.2,1.9,2.6,3.3]):
    ceiling.include("long T rail %02d" % i, box((.035,7.0,.045),
        center=(x,-.2,3.28), color=grid_col))
for i,y in enumerate([-3.0,-2.3,-1.6,-.9,-.2,.5,1.2,1.9]):
    ceiling.include("cross T rail %02d" % i, box((6.8,.035,.045),
        center=(0,y,3.28), color=grid_col))
for i,x in enumerate([-2.3,-.9,.5,1.9]):
    ceiling.include("structural beam %d" % i, box((.10,6.8,.18),
        center=(x,-.15,3.54), color=(.17,.21,.21)))
for i,x in enumerate([-2.3,-.9,.5,1.9]):
    for j,y in enumerate([-.9,1.2]):
        ceiling.include("hanger %d %d" % (i,j), rod(.012,
            start=(x,y,3.31), end=(x,y,3.60), color=metal_dark))
for i,x in enumerate([-.55,1.55]):
    ceiling.include("LED panel %d" % i, box((.64,.64,.035),
        center=(x,1.52,3.255), color=(.88,.96,.96)))
scene.include("ceiling", ceiling)

realize(scene)

# The screen text and material properties are applied after realization.
def make_material(name, color, metallic=0, roughness=.45, emission=0):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    p = m.node_tree.nodes.get("Principled BSDF")
    p.inputs["Base Color"].default_value = (*color, 1)
    p.inputs["Metallic"].default_value = metallic
    p.inputs["Roughness"].default_value = roughness
    if emission:
        if "Emission Color" in p.inputs:
            p.inputs["Emission Color"].default_value = (*color, 1)
            p.inputs["Emission Strength"].default_value = emission
        elif "Emission" in p.inputs:
            p.inputs["Emission"].default_value = (*color, 1)
    return m

text_mat = make_material("Pale display lettering", (.52,.73,.82), emission=.25)
def screen_text(name, body, y, z, size):
    curve = bpy.data.curves.new(name, "FONT")
    curve.body = body
    curve.size = size
    curve.align_x = "CENTER"
    curve.align_y = "CENTER"
    obj = bpy.data.objects.new(name, curve)
    bpy.context.collection.objects.link(obj)
    # Local text X follows the wall toward the back; text normal points inward.
    obj.location = (CORNER_X-.130, y, z)
    obj.rotation_euler = (math.pi/2, 0, -math.pi/2)
    obj.data.materials.append(text_mat)

screen_text("Clock", "09:23:07", MY, MZ+.06, .105)
screen_text("Date", "2026 / 11 / 11", MY, MZ-.10, .045)

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
background.inputs["Color"].default_value = (.68,.74,.77,1)
background.inputs["Strength"].default_value = .45

# The fixed runner renders and saves the result; keep its image aspect here.
sc.render.resolution_x = 512
sc.render.resolution_y = 293
sc.render.resolution_percentage = 100
set_view(CAMERA_POSITION, CAMERA_TARGET, lens=CAMERA_LENS)
area_emitter((-.55,1.40,3.20), power=300, size=1.2, target=(-.55,.5,0))
area_emitter((1.45,1.35,3.20), power=300, size=1.2, target=(.5,.3,0))
area_emitter((-1.8,-2.0,3.15), power=300, size=2.5, target=(-.5,1,1))

# Reference positions and computed projections are separately recorded.
landmarks = [
    ("back lower left", (WALL_LEFT,BACK_Y,0), (.10,.84)),
    ("mural upper left", (ART_X0,ART_Y,ART_Z1), (.37,.24)),
    ("back corner upper", (CORNER_X,BACK_Y,WALL_H), (.64,.25)),
    ("right front lower", (CORNER_X,RIGHT_FRONT_Y,0), (.91,.93)),
    ("display center", (CORNER_X-.13,MY,MZ), (.84,.42)),
]
bpy.context.view_layer.update()
cam = sc.camera
dg = bpy.context.evaluated_depsgraph_get()
projection = cam.calc_matrix_camera(dg, x=sc.render.resolution_x,
    y=sc.render.resolution_y, scale_x=sc.render.pixel_aspect_x,
    scale_y=sc.render.pixel_aspect_y)
print("Landmark                 reference       projected")
for name, point, ref in landmarks:
    clip = projection @ cam.matrix_world.inverted() @ Vector((*point,1.0))
    uv = None if clip.w <= 1e-8 else (
        .5*(clip.x/clip.w+1), .5*(1-clip.y/clip.w))
    print(name, ref, None if uv is None else tuple(round(v,3) for v in uv))
