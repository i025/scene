# Reference inventory, estimated from the lower photograph:
# - Room enclosure and floor: the full lower image, with a pale instrument wall
#   across the back and a perpendicular right wall; upper room extent is cropped.
# - Main wall instrument array: approximately x=.03-.56, y=.68-.87 of the full
#   reference image; uniform square meters surround a wide horizontal vent.
# - Long operating desk: approximately x=.03-.68, y=.77-.98; a sloping upper
#   control surface and a lower horizontal writing ledge overlap a dark base.
# - Small independent console: approximately x=.77-.94, y=.76-.89, against
#   the right wall. A tall dark doorway or cabinet is immediately to its left.
# - Yellow GRID mimic panel: approximately x=.03-.52, y=.19-.64 in the upper
#   inset. Its exact location in the photographed room is uncertain; it is
#   represented as a separate wall-mounted panel on the right side of the room.
# - Ceiling and the room beyond the photographed crop are uncertain.
#
# Estimated primitive meshes: room and architectural parts ~20; wall meters
# ~75; long desk and controls ~170; small console ~35; GRID panel ~60;
# lighting fixtures ~8. Total approximately 370 meshes. Text objects are
# created separately. Dimensions are approximate and intentionally editable.

from sceneact import Scene, Asset, box, ball, rod, realize, set_view, area_emitter
import bpy
import math
from mathutils import Vector

scene = Scene("1970s_grid_control_room")

# Shared color palette.
WALL = (0.72, 0.71, 0.66)
CEILING = (0.83, 0.82, 0.77)
FLOOR = (0.34, 0.32, 0.29)
PANEL = (0.68, 0.67, 0.62)
PANEL_LIGHT = (0.78, 0.77, 0.71)
FRAME = (0.19, 0.19, 0.18)
INK = (0.09, 0.09, 0.085)
FACE = (0.84, 0.83, 0.77)
BASE = (0.25, 0.24, 0.22)
YELLOW = (0.90, 0.67, 0.16)
RED = (0.78, 0.025, 0.018)
AMBER = (1.0, 0.45, 0.025)

def add_box(parent, name, size, center, color):
    parent.include(name, box(size=size, center=center, color=color))

# The camera looks toward the back wall at y=3.3. The room is open at the
# camera side so the visible furniture is not obscured.
architecture = Asset("Architecture")
add_box(architecture, "floor", (9.0, 7.0, 0.12), (0, 0, -0.06), FLOOR)
add_box(architecture, "back_wall", (9.0, 0.12, 3.4), (0, 3.35, 1.7), WALL)
add_box(architecture, "right_wall", (0.12, 7.0, 3.4), (4.5, 0, 1.7), WALL)
add_box(architecture, "ceiling", (9.0, 7.0, 0.08), (0, 0, 3.44), CEILING)
add_box(architecture, "back_skirt", (9.0, 0.08, 0.12), (0, 3.25, 0.06), BASE)
add_box(architecture, "right_skirt", (0.08, 7.0, 0.12), (4.42, 0, 0.06), BASE)
scene.include("architecture", architecture)

# Instrument wall: panel seams, square bezels and lighter meter faces.
wall = Asset("Main_wall_instruments")
add_box(wall, "instrument_wall_backing", (5.55, 0.11, 1.86),
        (-1.51, 3.24, 1.55), PANEL)
for i in range(7):
    x = -4.23 + i * 0.91
    add_box(wall, "panel_seam_%02d" % i, (0.018, 0.015, 1.84),
            (x, 3.174, 1.55), FRAME)

# The center opening is a distinct ventilation grille.
for x in [-3.99, -3.56, -3.13, -2.70, -0.32, 0.11, 0.54]:
    for z in [0.98, 1.38, 1.78, 2.18]:
        key = "%s_%s" % (str(x), str(z))
        add_box(wall, "meter_frame_" + key, (0.32, 0.045, 0.31),
                (x, 3.15, z), FRAME)
        add_box(wall, "meter_face_" + key, (0.255, 0.018, 0.245),
                (x, 3.12, z), FACE)
        # Short dark needle preserves the readable instrument silhouette.
        wall.include("meter_needle_" + key,
                     rod(radius=0.009, start=(x-0.055, 3.105, z-0.035),
                         end=(x+0.04, 3.105, z+0.045), color=INK))
add_box(wall, "vent_border", (1.55, 0.06, 0.72), (-1.50, 3.14, 1.62), FRAME)
add_box(wall, "vent_recess", (1.45, 0.025, 0.62), (-1.50, 3.10, 1.62), PANEL_LIGHT)
for i in range(7):
    add_box(wall, "vent_slat_%02d" % i, (1.34, 0.025, 0.025),
            (-1.50, 3.075, 1.37 + i * 0.078), FRAME)
scene.include("main_wall_instruments", wall)

# Long control desk. The sloping plane is assembled in local coordinates:
# increasing y moves toward the back and increases height.
desk = Asset("Long_sloping_operating_desk")
add_box(desk, "pedestal", (5.35, 1.28, 0.72), (-1.35, 0.55, 0.36), BASE)
add_box(desk, "pedestal_front", (5.4, 0.055, 0.59), (-1.35, -0.11, 0.35), (0.31, 0.30, 0.27))
add_box(desk, "writing_ledge", (5.65, 0.48, 0.09), (-1.35, -0.04, 0.79), PANEL_LIGHT)
slope_angle = math.radians(18)
surface = box(size=(5.65, 1.35, 0.12), center=(-1.35, 0.88, 1.05), color=PANEL_LIGHT)
surface.turn(axis="+x", degrees=18)
desk.include("sloping_control_surface", surface)

def slope_point(x, ylocal, lift=0.075):
    return (x, 0.88 + ylocal * math.cos(slope_angle) - lift * math.sin(slope_angle),
            1.05 + ylocal * math.sin(slope_angle) + lift * math.cos(slope_angle))

# Fine controls remain geometrically separate and are laid out in grouped
# columns, leaving visible gaps between desk sections.
for section in range(6):
    cx = -3.60 + section * 0.90
    for row in range(3):
        yy = -0.36 + row * 0.31
        for col in range(3):
            xx = cx + (col-1)*0.20
            p = slope_point(xx, yy, 0.08)
            desk.include("control_%d_%d_%d" % (section, row, col),
                         ball(radius=0.035 if row != 2 else 0.045,
                              center=p, color=FRAME))
    # Pale rectangular meter plate near the upper edge of each desk section.
    p = slope_point(cx, 0.49, 0.07)
    plate = box(size=(0.36, 0.16, 0.015), center=p, color=FACE)
    plate.turn(axis="+x", degrees=18)
    desk.include("desk_meter_plate_%d" % section, plate)
scene.include("long_operating_desk", desk)

# Tall doorway or cabinet and the smaller independent right-side console.
side = Asset("Right_side_console_and_cabinet")
add_box(side, "cabinet_frame", (0.76, 0.12, 2.30), (2.12, 3.21, 1.30), PANEL_LIGHT)
add_box(side, "cabinet_dark_inset", (0.54, 0.035, 1.91), (2.12, 3.13, 1.32), FRAME)
add_box(side, "cabinet_top_glass", (0.43, 0.02, 0.40), (2.12, 3.105, 1.94), (0.37, 0.38, 0.35))
add_box(side, "small_console_base", (1.35, 0.82, 0.78), (3.21, 2.26, 0.39), BASE)
small = box(size=(1.43, 0.88, 0.10), center=(3.21, 2.23, 0.88), color=PANEL_LIGHT)
small.turn(axis="+x", degrees=16)
side.include("small_console_control_surface", small)
for i in range(5):
    for j in range(3):
        x = 2.72 + i * 0.24
        ylocal = -0.25 + j * 0.23
        y = 2.23 + ylocal * math.cos(math.radians(16))
        z = 0.88 + ylocal * math.sin(math.radians(16)) + 0.07
        side.include("small_button_%d_%d" % (i, j),
                     ball(radius=0.034, center=(x, y, z), color=FRAME))
scene.include("right_console_and_cabinet", side)

# The GRID panel is on the right wall. Its diagram faces toward negative X.
# Coordinates u and v map across the panel and upwards.
grid = Asset("GRID_yellow_mimic_panel")
gx, gy, gz = 4.39, 0.55, 1.87
add_box(grid, "yellow_face", (0.10, 1.85, 1.85), (gx, gy, gz), YELLOW)
def grid_line(name, u1, v1, u2, v2, radius=0.015):
    grid.include(name, rod(radius=radius,
        start=(gx-0.061, gy+u1, gz+v1),
        end=(gx-0.061, gy+u2, gz+v2), color=INK))
# Vertical bus and branches, with visible open spaces around the symbols.
grid_line("main_bus", 0.24, -0.82, 0.24, 0.82, 0.022)
for i, v in enumerate([-.54, -.15, .23, .59]):
    grid_line("branch_%d" % i, -.45, v, .60, v)
    grid_line("branch_drop_%d" % i, -.45, v, -.45, v-.16)
for i, u in enumerate([-.18, .05, .45]):
    grid_line("vertical_link_%d" % i, u, -.46, u, .37)
for i, (u, v) in enumerate([(-.45,.59),(-.45,.23),(-.45,-.15),
                             (-.45,-.54),(.61,.59),(.61,-.54)]):
    grid.include("red_lamp_%d" % i,
                 ball(radius=0.057, center=(gx-0.09, gy+u, gz+v), color=RED))
for i, (u, v) in enumerate([(-.18,.23),(.05,.23),(.45,.23),
                             (-.18,-.15),(.05,-.15),(.45,-.15),
                             (.24,.70),(.24,-.68)]):
    add_box(grid, "amber_frame_%d" % i, (0.035, 0.14, 0.14),
            (gx-0.08, gy+u, gz+v), FRAME)
    add_box(grid, "amber_lamp_%d" % i, (0.025, 0.085, 0.085),
            (gx-0.105, gy+u, gz+v), AMBER)
for i, v in enumerate([-.65, -.32, .02, .36, .70]):
    grid.include("selector_%d" % i,
                 ball(radius=0.055, center=(gx-0.085, gy-.72, gz+v), color=FRAME))
scene.include("GRID_mimic_panel", grid)

# Ceiling fluorescent panels, also serving as visible light sources.
fixtures = Asset("Ceiling_fluorescent_fixtures")
for i, x in enumerate([-2.8, 0.0, 2.8]):
    add_box(fixtures, "troffer_frame_%d" % i, (1.7, 0.48, 0.045),
            (x, 0.65, 3.37), FRAME)
    add_box(fixtures, "troffer_diffuser_%d" % i, (1.58, 0.36, 0.025),
            (x, 0.65, 3.335), FACE)
scene.include("ceiling_fixtures", fixtures)

realize(scene)

# Configure world after realization.
sc = bpy.context.scene
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
background.inputs["Color"].default_value = (0.75, 0.73, 0.68, 1)
background.inputs["Strength"].default_value = 0.45

# Two named cameras: the panorama is active for the runner; the second is
# available in the scene for an operator-console and mimic-panel close-up.
set_view((8.0, -10.8, 5.8), (-0.2, 1.1, 1.20), lens=34)
panorama = sc.camera
panorama.name = "Camera_Panorama"

def make_camera(name, location, target, lens):
    data = bpy.data.cameras.new(name)
    obj = bpy.data.objects.new(name, data)
    sc.collection.objects.link(obj)
    obj.location = location
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()
    data.lens = lens
    return obj

make_camera("Camera_Console_GRID_Closeup", (5.8, -4.6, 3.5),
            (2.1, 1.1, 1.35), 42)
sc.camera = panorama

area_emitter((0, -1.5, 3.2), power=750, size=5.0, target=(0, 1, 0))
area_emitter((-3, 1.2, 3.2), power=450, size=3.0, target=(-2, 1, 0))
area_emitter((3, 1.2, 3.2), power=400, size=3.0, target=(2, 1, 0))

# Small German labels on the panel, placed directly on its face.
def grid_label(body, u, v, size=0.065):
    curve = bpy.data.curves.new("Label_" + body, "FONT")
    curve.body = body
    curve.size = size
    curve.extrude = 0
    obj = bpy.data.objects.new("GRID_label_" + body, curve)
    sc.collection.objects.link(obj)
    obj.location = (gx-0.125, gy+u, gz+v)
    # Text local X points along world Y; its normal points toward negative X.
    obj.rotation_euler = (math.radians(90), 0, math.radians(90))
    mat = bpy.data.materials.get("GRID_label_dark")
    if mat is None:
        mat = bpy.data.materials.new("GRID_label_dark")
        mat.diffuse_color = (0.04, 0.04, 0.035, 1)
    curve.materials.append(mat)

grid_label("NETZ", -0.78, 0.79, 0.075)
grid_label("FEHLERSTELLE", -0.72, -0.78, 0.055)

# The fixed runner manages rendering and saving. The following settings express
# the requested output without performing either operation in this program.
sc.render.engine = "CYCLES"
sc.cycles.use_denoising = True
sc.render.resolution_x = 1920
sc.render.resolution_y = 1080
sc.render.resolution_percentage = 100
sc.render.image_settings.file_format = "PNG"
try:
    sc.view_settings.view_transform = "Filmic"
except TypeError:
    pass
