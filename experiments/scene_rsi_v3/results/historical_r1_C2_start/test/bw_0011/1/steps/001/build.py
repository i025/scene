# Reference inventory, estimated normalized image bounds:
# - Light gray floor: x 0.00–1.00, y 0.79–1.00; curved white wall base.
# - Blue back wall: x 0.09–0.70, y 0.19–0.84, vertical panel joints.
# - Blue right wall: x 0.69–0.91, y 0.15–0.92, receding toward corner.
# - Stainless double-door cabinet: x 0.16–0.31, y 0.40–0.83; glazed
#   doors, center handles, and visible shelves.
# - Dandelion feature wall: x 0.37–0.64, y 0.25–0.81, partially
#   overlapped by fine dark stems and seed heads; exact photograph detail
#   is uncertain and is interpreted geometrically.
# - Digital display: x 0.79–0.88, y 0.33–0.51 on the right wall.
# - Open ceiling: x 0.00–1.00, y 0.00–0.24; dark overhead structure,
#   suspended T-grid, visible rods, and a bright rectangular LED panel.
# - Numeric annotation markers in the reference are intentionally omitted.
#
# Primitive estimate: architecture and panel seams ~35; cabinet ~35;
# mural background and dandelion geometry ~140; ceiling grid, structure,
# hangers and lighting ~55; display ~5. Total approximately 270 meshes.
# Fine photographic detail and hidden construction remain uncertain.

from sceneact import *
import bpy
import math
import random
from mathutils import Vector

random.seed(14)
scene = Scene("Clean laboratory corner")

blue = (0.055, 0.48, 0.71)
blue_dark = (0.025, 0.25, 0.36)
floor_col = (0.51, 0.55, 0.54)
white = (0.84, 0.88, 0.87)
steel = (0.56, 0.62, 0.62)
steel_dark = (0.25, 0.31, 0.32)
glass = (0.30, 0.39, 0.39)
ceiling_dark = (0.19, 0.23, 0.23)
grid_col = (0.49, 0.56, 0.57)

def add(asset, name, size, center, color):
    asset.include(name, box(size=size, center=center, color=color))

# Room proportions: the back wall is frontal, while the right wall returns
# toward the camera. Wall panels are kept as independently editable parts.
room = Asset("Architecture")
add(room, "floor", (7.4, 7.2, 0.12), (0, -1.1, -0.08), floor_col)
add(room, "back_wall", (6.6, 0.12, 3.15), (0, 2.0, 1.575), blue)
add(room, "right_wall", (0.12, 5.5, 3.15), (3.3, -0.70, 1.575), blue)
# Narrow seams between modular steel wall panels.
for i, x in enumerate([-2.75, -1.70, -0.65, 0.45, 1.55, 2.65]):
    add(room, "back_panel_joint_%02d" % i, (0.014, 0.012, 3.05),
        (x, 1.932, 1.56), blue_dark)
for i, y in enumerate([1.28, 0.38, -0.52, -1.42, -2.32]):
    add(room, "right_panel_joint_%02d" % i, (0.012, 0.014, 3.05),
        (3.232, y, 1.56), blue_dark)
# Cove bases: a broad lower rounded transition represented by white rails.
add(room, "back_cove", (6.6, 0.18, 0.14), (0, 1.88, 0.085), white)
add(room, "right_cove", (0.18, 5.45, 0.14), (3.18, -0.69, 0.085), white)
room.include("back_cove_round", rod(radius=0.065, start=(-3.3, 1.78, 0.10),
                                      end=(3.25, 1.78, 0.10), color=white))
room.include("right_cove_round", rod(radius=0.065, start=(3.08, 1.78, 0.10),
                                       end=(3.08, -3.4, 0.10), color=white))
scene.include("room", room)

# Full-height printed feature panel. The softly colored strips approximate
# the photograph's pale cyan-to-warm background without an external image.
mural = Asset("Dandelion feature wall")
mx0, mx1 = -0.96, 1.12
mz0, mz1 = 0.12, 3.00
strips = [
    (0.12, 0.42, (0.72, 0.60, 0.39)),
    (0.42, 0.72, (0.83, 0.78, 0.57)),
    (0.72, 1.05, (0.86, 0.88, 0.72)),
    (1.05, 1.45, (0.82, 0.89, 0.80)),
    (1.45, 1.90, (0.77, 0.88, 0.84)),
    (1.90, 2.40, (0.74, 0.87, 0.86)),
    (2.40, 3.00, (0.77, 0.89, 0.88)),
]
for i, (a, b, col) in enumerate(strips):
    add(mural, "background_band_%02d" % i, (mx1-mx0, 0.025, b-a),
        ((mx0+mx1)/2, 1.905, (a+b)/2), col)
# Subtle division of the feature into printed wall modules.
for i, x in enumerate([-0.28, 0.42]):
    add(mural, "print_panel_joint_%d" % i, (0.009, 0.009, 2.87),
        (x, 1.884, 1.56), (0.42, 0.58, 0.55))

ink = (0.23, 0.12, 0.22)
ink_light = (0.35, 0.30, 0.32)
def mural_line(name, a, b, radius=0.009, color=ink, depth=1.87):
    mural.include(name, rod(radius=radius,
                            start=(a[0], depth, a[1]),
                            end=(b[0], depth, b[1]), color=color))

# Large graceful seed stalks, clipped to the mural's visible rectangle.
stems = [
    [(-0.90,0.18),(-0.50,0.64),(-0.18,1.20),(0.02,1.85),(-0.08,2.56)],
    [(-0.72,0.16),(-0.36,0.42),(0.15,0.60),(0.55,0.98),(0.83,1.50)],
    [(0.80,0.12),(0.51,0.48),(0.20,0.80),(-0.24,1.02),(-0.72,1.12)],
    [(1.04,0.18),(0.69,0.35),(0.37,0.63),(0.23,1.06),(0.54,1.51)],
    [(-0.92,0.42),(-0.53,0.48),(-0.13,0.40),(0.21,0.21)],
]
for j, points in enumerate(stems):
    for k in range(len(points)-1):
        mural_line("stem_%d_%d" % (j,k), points[k], points[k+1], 0.012)

# Seedhead spokes and short forked filaments suggest airy dandelion forms.
heads = [(-0.08,2.55,0.57), (0.83,1.50,0.46), (-0.70,1.13,0.39),
         (0.55,1.50,0.38), (0.14,0.61,0.35)]
for h, (cx, cz, rad) in enumerate(heads):
    for k in range(11):
        ang = (2*math.pi*k/11) + 0.12*h
        ex = cx + rad*math.cos(ang)
        ez = cz + rad*math.sin(ang)
        if not (mx0+0.02 < ex < mx1-0.02 and mz0+0.02 < ez < mz1-0.02):
            continue
        sx = cx + 0.15*rad*math.cos(ang)
        sz = cz + 0.15*rad*math.sin(ang)
        mural_line("head_%d_spoke_%d" % (h,k), (sx,sz), (ex,ez),
                   0.0035, ink_light, 1.864)
        # A short, light crossbar preserves the airy seed silhouette.
        dx, dz = -0.055*math.sin(ang), 0.055*math.cos(ang)
        if mx0 < ex-dx < mx1 and mx0 < ex+dx < mx1 and mz0 < ez-dz < mz1 and mz0 < ez+dz < mz1:
            mural_line("head_%d_tip_%d" % (h,k), (ex-dx,ez-dz),
                       (ex+dx,ez+dz), 0.0025, ink_light, 1.861)
scene.include("feature_wall", mural)

# Recessed-looking stainless cabinet with two individually framed glazed
# doors. Shelves remain visible through the dark glass-colored door panels.
cab = Asset("Stainless glass storage cabinet")
cx = -2.05
add(cab, "body", (1.08,0.25,1.95), (cx,1.77,1.03), steel)
add(cab, "interior", (0.94,0.025,1.76), (cx,1.625,1.05), steel_dark)
for side, x in enumerate([cx-0.265,cx+0.265]):
    add(cab, "glass_door_%d" % side, (0.43,0.018,1.69),
        (x,1.598,1.05), glass)
    for z in [0.27,0.59,0.91,1.23,1.55,1.87]:
        add(cab, "shelf_%d_%.2f" % (side,z), (0.40,0.020,0.022),
            (x,1.575,z), (0.68,0.74,0.72))
    for xx in [x-0.235,x+0.235]:
        add(cab, "door_stile_%d_%.2f" % (side,xx), (0.035,0.045,1.84),
            (xx,1.565,1.05), steel)
    for z in [0.14,1.96]:
        add(cab, "door_rail_%d_%.2f" % (side,z), (0.48,0.045,0.04),
            (x,1.565,z), steel)
for x in [cx-0.055,cx+0.055]:
    cab.include("handle_%.3f" % x,
                rod(radius=0.012, start=(x,1.52,0.98),
                    end=(x,1.52,1.17), color=(0.79,0.82,0.81)))
scene.include("storage_cabinet", cab)

# Dark blue digital display on the right wall.
screen = Asset("Wall mounted digital display")
add(screen, "frame", (0.055,0.92,0.70), (3.20,0.15,2.13), steel_dark)
add(screen, "display_face", (0.014,0.86,0.64), (3.166,0.15,2.13),
    (0.025,0.085,0.20))
for z in [1.92,2.02,2.22]:
    add(screen, "display_rule_%.2f" % z, (0.008,0.71,0.006),
        (3.154,0.15,z), (0.18,0.35,0.51))
scene.include("digital_display", screen)

# Exposed ceiling structure with a suspended T-grid and LED panel.
ceiling = Asset("Suspended ceiling and exposed services")
add(ceiling, "upper_slab", (7.0,5.8,0.12), (0,-0.05,3.70), ceiling_dark)
for i, x in enumerate([-3.0,-1.8,-0.6,0.6,1.8,3.0]):
    add(ceiling, "structural_beam_%d" % i, (0.12,5.8,0.16),
        (x,-0.05,3.53), (0.25,0.29,0.29))
for i, y in enumerate([-2.4,-1.2,0.0,1.2]):
    add(ceiling, "cross_beam_%d" % i, (6.8,0.10,0.12),
        (0,y,3.54), (0.30,0.33,0.33))
# T-grid at ceiling level, with darker openings above.
for i, x in enumerate([-3.0,-2.0,-1.0,0.0,1.0,2.0,3.0]):
    add(ceiling, "grid_long_%d" % i, (0.035,5.6,0.055),
        (x,-0.15,3.17), grid_col)
for i, y in enumerate([-2.8,-1.8,-0.8,0.2,1.2,1.9]):
    add(ceiling, "grid_cross_%d" % i, (6.6,0.035,0.055),
        (0,y,3.17), grid_col)
for i, x in enumerate([-2.0,0.0,2.0]):
    for j, y in enumerate([-1.8,0.2,1.2]):
        ceiling.include("hanger_%d_%d" % (i,j),
                        rod(radius=0.012, start=(x,y,3.19),
                            end=(x,y,3.57), color=steel_dark))
# A few visible services above the grid.
for i, x in enumerate([-2.45, -0.35, 1.45]):
    ceiling.include("overhead_service_%d" % i,
                    rod(radius=0.025, start=(x,-2.8,3.42),
                        end=(x,1.85,3.42), color=(0.32,0.37,0.37)))
add(ceiling, "led_panel_frame", (0.95,0.88,0.045),
    (0.67,0.70,3.135), (0.76,0.83,0.82))
add(ceiling, "led_panel_diffuser", (0.87,0.80,0.025),
    (0.67,0.70,3.105), (0.92,0.99,1.0))
scene.include("ceiling", ceiling)

realize(scene)

# Customize Blender materials after realization.
for mat in bpy.data.materials:
    if not mat.use_nodes:
        mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        c = mat.diffuse_color
        if abs(c[0]-steel[0]) < 0.02 and abs(c[1]-steel[1]) < 0.02:
            bsdf.inputs["Metallic"].default_value = 0.75
            bsdf.inputs["Roughness"].default_value = 0.3
        else:
            bsdf.inputs["Roughness"].default_value = 0.65

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
background.inputs["Color"].default_value = (0.72,0.78,0.80,1)
background.inputs["Strength"].default_value = 0.55

set_view((0.0,-8.8,3.15), (0.10,1.25,1.73), lens=34, sensor=36)
area_emitter((0.67,0.55,3.04), power=650, size=1.5,
             target=(0,0,0.1), color=(0.88,0.96,1.0))
area_emitter((-2.2,-1.8,3.1), power=350, size=2.5,
             target=(-1,1,1.0), color=(0.94,0.98,1.0))
area_emitter((2.2,-1.3,3.1), power=300, size=2.2,
             target=(2,1,1.0), color=(0.94,0.98,1.0))

# Screen typography is positioned directly on the right-wall face.
def screen_text(name, text, y, z, size, color):
    curve = bpy.data.curves.new(name, type="FONT")
    curve.body = text
    curve.align_x = "CENTER"
    curve.align_y = "CENTER"
    curve.size = size
    curve.extrude = 0
    obj = bpy.data.objects.new(name, curve)
    sc.collection.objects.link(obj)
    obj.location = (3.145, y, z)
    # Text local horizontal axis points along the right wall toward the rear;
    # text local vertical axis points upward, with face toward the camera.
    obj.rotation_euler = (math.pi/2, 0, math.pi/2)
    material = bpy.data.materials.get("Display lettering")
    if material is None:
        material = bpy.data.materials.new("Display lettering")
        material.diffuse_color = (*color,1)
    obj.data.materials.append(material)

screen_text("Display time", "09:29:07", 0.15, 2.15, 0.13, (0.60,0.78,0.90))
screen_text("Display date", "2024 / 06 / 18", 0.15, 1.98, 0.055, (0.60,0.78,0.90))
