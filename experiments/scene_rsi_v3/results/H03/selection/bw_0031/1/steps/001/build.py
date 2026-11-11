# Reference inventory and visual anchors (estimates, normalized x/y):
# The input is a vertical slide containing two separate photographs, not one
# calibrated room view. The lower photo occupies approximately (0.03,0.65)
# to (0.94,1.00): a long foreground control desk overlaps the wall cabinets,
# with a smaller console at the far right. The cabinet tops and desk edges
# recede to the right; the floor is visible in the foreground and right aisle.
# The separate upper photo (0.03,0.19)-(0.52,0.64) shows a yellow GRID
# demonstration panel with black wiring, red round lamps, amber square lamps,
# switches and small labels. Its exact location in the photographed room is
# uncertain; here it is mounted on the right wall as a readable exhibit.
# The lower photo's wall/floor junction and rear room corners are partly hidden.
#
# Anchor estimates below describe a landscape reconstruction of the lower
# photograph, rather than the collage's page coordinates. They provide an
# operational framing diagnostic, not measured camera calibration.
# Estimated expanded primitive count: room and furnishings ~35, cabinet meters
# ~90, main console controls ~90, GRID panel and wiring ~60, lighting ~8:
# approximately 280-320 meshes, depending on control distribution.

from sceneact import *
import bpy
import math
import json
from mathutils import Vector

# Major scene and camera parameters are intentionally separate.
ROOM_W = 9.0
ROOM_D = 6.8
ROOM_H = 3.4
CAMERA_POSITION = (8.7, -12.8, 7.3)
CAMERA_TARGET = (0.0, 0.25, 1.25)
CAMERA_LENS = 39
IMAGE_WIDTH, IMAGE_HEIGHT = 1920, 1080

scene = Scene("1970s grid dispatch control room")
ivory = (0.68, 0.65, 0.59)
wall = (0.76, 0.74, 0.69)
floor_color = (0.35, 0.32, 0.29)
cabinet = (0.68, 0.67, 0.63)
face = (0.82, 0.81, 0.75)
dark = (0.12, 0.12, 0.11)
black = (0.035, 0.035, 0.03)
yellow = (0.95, 0.70, 0.12)
red = (0.72, 0.035, 0.025)
amber = (0.98, 0.47, 0.025)

def add_box(parent, name, size, center, color):
    parent.include(name, box(size=size, center=center, color=color))

def add_rod(parent, name, radius, start, end, color):
    parent.include(name, rod(radius=radius, start=start, end=end, color=color))

# Architecture. Camera faces the back wall; the right return frames the room.
architecture = Asset("Architecture")
add_box(architecture, "floor", (ROOM_W, ROOM_D, .12),
        (0, 0, -.06), floor_color)
add_box(architecture, "back_wall", (ROOM_W, .12, ROOM_H),
        (0, ROOM_D/2, ROOM_H/2), wall)
add_box(architecture, "right_wall", (.12, ROOM_D, ROOM_H),
        (ROOM_W/2, 0, ROOM_H/2), wall)
add_box(architecture, "ceiling", (ROOM_W, ROOM_D, .08),
        (0, 0, ROOM_H + .04), wall)
add_box(architecture, "back_skirt", (ROOM_W, .06, .12),
        (0, ROOM_D/2-.09, .06), (0.42, .40, .37))
scene.include("architecture", architecture)

# Long cabinet bank with a regular array of square framed indicators.
bank = Asset("Main_wall_instrument_bank")
add_box(bank, "cabinet_body", (6.75, .38, 2.45),
        (-1.05, 3.13, 1.35), cabinet)
add_box(bank, "top_fascia", (6.75, .05, .30),
        (-1.05, 2.91, 2.42), face)
# Nine rows/columns are intentionally estimated rather than calibrated.
for col in range(10):
    x = -4.03 + col * .43
    for row in range(4):
        z = .57 + row * .43
        add_box(bank, f"meter_frame_{col}_{row}", (.31, .045, .31),
                (x, 2.905, z), dark)
        add_box(bank, f"meter_face_{col}_{row}", (.255, .025, .255),
                (x, 2.874, z), face)
        # Single pointer gives the small panels an unmistakable instrument face.
        add_rod(bank, f"pointer_{col}_{row}", .008,
                (x-.055, 2.852, z-.045),
                (x+.035, 2.852, z+.055), dark)
# Wide ventilation grille in the middle-right part of the wall bank.
add_box(bank, "vent_recess", (1.22, .05, .80),
        (1.08, 2.90, 1.40), dark)
for i in range(7):
    add_box(bank, f"vent_slat_{i}", (1.12, .035, .035),
            (1.08, 2.86, 1.09 + i*.10), face)
for i in range(5):
    x = 2.05 + i*.30
    for j in range(4):
        z = .74 + j*.37
        add_box(bank, f"right_frame_{i}_{j}", (.22,.04,.25),
                (x,2.90,z), dark)
        add_box(bank, f"right_face_{i}_{j}", (.17,.025,.20),
                (x,2.87,z), face)
scene.include("wall_instruments", bank)

# Main desk: long horizontal writing ledge and a rising instrument surface.
desk = Asset("Long_sloping_operator_console")
DESK_X = -1.05
DESK_Y = -.25
DESK_LEN = 6.35
add_box(desk, "pedestal", (DESK_LEN, 1.15, .68),
        (DESK_X, DESK_Y+.15, .36), (0.36, .34, .31))
add_box(desk, "writing_ledge", (DESK_LEN+.12, .68, .10),
        (DESK_X, DESK_Y-.56, .78), face)

# Sloping surface runs from y=-0.48,z=.83 up to y=.60,z=1.34.
slope_angle = math.degrees(math.atan2(.51, 1.08))
slope = box((DESK_LEN, 1.195, .10),
            center=(DESK_X, DESK_Y+.06, 1.085), color=face)
slope.turn(axis="x", degrees=slope_angle)
desk.include("sloped_control_surface", slope)
add_box(desk, "rear_lip", (DESK_LEN, .07, .10),
        (DESK_X, DESK_Y+.60, 1.36), cabinet)

# Surface coordinate helper and controls protruding along the surface normal.
def desk_surface(x, t):
    return (x, DESK_Y-.48 + 1.08*t, .84 + .51*t)

normal = (0, -math.sin(math.radians(slope_angle)),
          math.cos(math.radians(slope_angle)))
for i in range(15):
    x = DESK_X - 2.91 + i*.415
    # Dark small switch blocks form the dense operational pattern.
    for j, t in enumerate((.20, .43, .67, .86)):
        p = desk_surface(x, t)
        r = .028 if j != 2 else .041
        add_rod(desk, f"control_{i}_{j}", r, p,
                (p[0]+normal[0]*.045, p[1]+normal[1]*.045,
                 p[2]+normal[2]*.045),
                dark if (i+j)%5 else red)
    if i % 3 == 0:
        p = desk_surface(x+.13, .71)
        add_rod(desk, f"large_dial_{i}", .067, p,
                (p[0],p[1]+normal[1]*.025,p[2]+normal[2]*.025), dark)
scene.include("main_console", desk)

# Small free-standing console at the far right, with its own sloped panel.
small = Asset("Right_independent_console")
add_box(small, "base", (1.40,.82,.78), (3.34,2.18,.39), cabinet)
panel = box((1.42,.87,.08), center=(3.34,2.18,.87), color=face)
panel.turn(axis="x", degrees=15)
small.include("control_top", panel)
for i in range(6):
    for j in range(3):
        x = 2.81+i*.21
        y = 1.88+j*.23
        z = .87 + (y-2.18)*math.tan(math.radians(15)) + .045
        add_rod(small, f"switch_{i}_{j}", .025, (x,y,z),
                (x,y-.01,z+.045), dark if (i+j)%4 else red)
scene.include("independent_console", small)

# Yellow GRID mimic panel on the right return. Geometry lies in the YZ plane.
grid = Asset("Yellow_GRID_mimic_panel")
GRID_X = 4.42
GRID_Y = 1.02
GRID_Z = 1.93
GRID_W = 1.65
GRID_H = 1.65
add_box(grid, "yellow_backboard", (.08,GRID_W,GRID_H),
        (GRID_X,GRID_Y,GRID_Z), yellow)

def grid_wire(name, yz_points, radius=.018, color=black):
    for k in range(len(yz_points)-1):
        a, b = yz_points[k], yz_points[k+1]
        add_rod(grid, f"{name}_{k}", radius,
                (GRID_X-.055, GRID_Y+a[0], GRID_Z+a[1]),
                (GRID_X-.055, GRID_Y+b[0], GRID_Z+b[1]), color)

# Vertical bus with rectangular branches mirrors the diagram's recognizable form.
grid_wire("vertical_bus", [(0,-.72),(0,.70)])
grid_wire("upper_loop", [(0,.43),(-.29,.43),(-.29,.12),(.28,.12),
                         (.28,.43),(0,.43)])
grid_wire("middle_loop", [(0,.04),(-.29,.04),(-.29,-.25),(.28,-.25),
                          (.28,.04),(0,.04)])
grid_wire("lower_branch", [(0,-.38),(-.35,-.38),(-.35,-.53)])
grid_wire("right_branch", [(0,-.38),(.36,-.38),(.36,-.53)])
for k,(dy,dz) in enumerate([(-.22,.27),(-.07,.27),(.09,.27),(.23,.27),
                             (-.22,-.11),(-.07,-.11),(.09,-.11),(.23,-.11),
                             (-.35,-.53),(.36,-.53)]):
    add_box(grid, f"amber_frame_{k}", (.035,.125,.125),
            (GRID_X-.075,GRID_Y+dy,GRID_Z+dz), black)
    add_box(grid, f"amber_lamp_{k}", (.025,.085,.085),
            (GRID_X-.10,GRID_Y+dy,GRID_Z+dz), amber)
for k,(dy,dz) in enumerate([(0,.58),(0,-.65),(-.58,.48),(-.58,.23),
                             (-.58,-.02),(-.58,-.27),(.57,.43)]):
    add_rod(grid, f"red_indicator_{k}", .055,
            (GRID_X-.06,GRID_Y+dy,GRID_Z+dz),
            (GRID_X-.115,GRID_Y+dy,GRID_Z+dz), red)
for k,dz in enumerate((.37,.02,-.34,-.57)):
    add_rod(grid, f"selector_{k}", .055,
            (GRID_X-.06,GRID_Y-.67,GRID_Z+dz),
            (GRID_X-.14,GRID_Y-.67,GRID_Z+dz), black)
scene.include("grid_mimic", grid)

# Simple visible ceiling fixtures. Their geometry is retained as editable parts.
fixtures = Asset("Ceiling_fluorescent_troffers")
for i, x in enumerate((-2.6, 0, 2.6)):
    add_box(fixtures, f"housing_{i}", (1.65,.48,.055),
            (x,0,ROOM_H-.04), cabinet)
    add_box(fixtures, f"diffuser_{i}", (1.50,.36,.025),
            (x,0,ROOM_H-.075), (0.95,.94,.87))
scene.include("ceiling_lights", fixtures)

realize(scene)

# World is created explicitly because realize clears Blender's default scene.
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
sc.world.node_tree.links.new(background.outputs["Background"],
                             output.inputs["Surface"])
background.inputs["Color"].default_value = (0.68, .66, .62, 1)
background.inputs["Strength"].default_value = .45

set_view(CAMERA_POSITION, CAMERA_TARGET, lens=CAMERA_LENS, sensor=36)
panorama_camera = sc.camera
panorama_camera.name = "Camera_Panorama"

# A second editable camera aims at the console and yellow panel. The active
# camera remains the panorama for the fixed runner.
bpy.ops.object.camera_add(location=(7.8, -5.3, 3.4))
detail_camera = bpy.context.object
detail_camera.name = "Camera_Console_GRID_Closeup"
detail_target = Vector((2.3, 1.0, 1.35))
detail_camera.rotation_euler = (detail_target-detail_camera.location).to_track_quat("-Z","Y").to_euler()
detail_camera.data.lens = 48
sc.camera = panorama_camera

area_emitter((0,-1.0,3.15), power=1000, size=5.0, target=(0,1,0))
area_emitter((-3,-2.5,3.0), power=550, size=3.0, target=(-1,1,1))
area_emitter((3,1.0,3.0), power=400, size=2.5, target=(2,1,1))

# Small editable German labels on the yellow panel. Text is positioned just in
# front of the panel, facing into the room along negative X.
def grid_label(name, text, y, z, size=.065):
    curve = bpy.data.curves.new(name, type="FONT")
    curve.body = text
    curve.size = size
    curve.extrude = .0005
    obj = bpy.data.objects.new(name, curve)
    sc.collection.objects.link(obj)
    obj.location = (GRID_X-.125, GRID_Y+y, GRID_Z+z)
    # Local text X points toward negative Y; text Y points upward.
    obj.rotation_euler = (math.pi/2, 0, -math.pi/2)
    return obj

grid_label("label_grid", "GRID", -.20, .69, .09)
grid_label("label_fault", "FEHLER-STELLE K", .10, .55, .045)
grid_label("label_switch", "SCHALTER", -.73, -.70, .042)

# Use emissive indicator materials on named lamp meshes while retaining their
# original semantic objects. Material matching is intentionally conservative.
def emission_material(name, color, strength):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        if "Emission Color" in bsdf.inputs:
            bsdf.inputs["Emission Color"].default_value = (*color, 1)
            bsdf.inputs["Emission Strength"].default_value = strength
        elif "Emission" in bsdf.inputs:
            bsdf.inputs["Emission"].default_value = (*color, 1)
    return mat

lamp_red = emission_material("Indicator red illuminated", (.65,.025,.01), 1.3)
lamp_amber = emission_material("Indicator amber illuminated", (1,.35,.015), 1.3)
troffer_mat = emission_material("Fluorescent diffuser", (.95,.91,.78), 1.1)
for obj in bpy.data.objects:
    n = obj.name.lower()
    if obj.type == "MESH":
        mat = None
        if "red_indicator" in n:
            mat = lamp_red
        elif "amber_lamp" in n:
            mat = lamp_amber
        elif "diffuser" in n:
            mat = troffer_mat
        if mat is not None:
            obj.data.materials.clear()
            obj.data.materials.append(mat)

# Organize the Blender objects into named collections based on their semantic
# SceneAct ancestry/name where available.
for cname in ("Architecture", "Wall instruments", "Main console",
              "Independent console", "GRID mimic panel", "Ceiling lights",
              "Cameras and lights"):
    if bpy.data.collections.get(cname) is None:
        col = bpy.data.collections.new(cname)
        sc.collection.children.link(col)

# SceneAct's asset hierarchy is preserved; camera and light objects are grouped.
equipment_col = bpy.data.collections["Cameras and lights"]
for obj in list(sc.objects):
    if obj.type in {"CAMERA", "LIGHT"}:
        for col in list(obj.users_collection):
            col.objects.unlink(obj)
        equipment_col.objects.link(obj)

sc.render.engine = "CYCLES"
sc.cycles.use_denoising = True
sc.render.image_settings.file_format = "PNG"
try:
    sc.view_settings.view_transform = "Filmic"
except Exception:
    pass

# Camera diagnostics: project actual identifiable geometry points at the
# requested aspect. Reference positions are estimates in the landscape crop.
anchors = [
    ("back_wall_left_top", (-4.5,3.34,3.4), (.06,.12)),
    ("back_wall_right_top", (4.5,3.34,3.4), (.86,.12)),
    ("bank_left_lower", (-4.425,2.90,.125), (.04,.62)),
    ("bank_right_upper", (2.325,2.90,2.575), (.70,.25)),
    ("desk_front_left", (-4.285,-1.15,.83), (.05,.91)),
    ("desk_front_right", (2.185,-1.15,.83), (.72,.88)),
    ("grid_upper_corner", (4.37,1.845,2.755), (.83,.27)),
    ("small_console_front", (4.04,1.77,.78), (.89,.65)),
]
bpy.context.view_layer.update()
depsgraph = bpy.context.evaluated_depsgraph_get()
projection = panorama_camera.calc_matrix_camera(
    depsgraph, x=IMAGE_WIDTH, y=IMAGE_HEIGHT, scale_x=1, scale_y=1
)
view = panorama_camera.matrix_world.inverted()
table = []
for name, point, ref in anchors:
    clip = projection @ view @ Vector((*point, 1.0))
    if clip.w <= 0:
        table.append({"anchor":name, "reference":ref, "projection":None,
                      "residual":None, "behind_camera":True})
    else:
        u = .5*(clip.x/clip.w+1)
        v = .5*(1-clip.y/clip.w)
        table.append({"anchor":name, "reference":ref,
                      "projection":[round(u,4),round(v,4)],
                      "residual":[round(u-ref[0],4),round(v-ref[1],4)]})
print("ANCHOR_DIAGNOSTIC " + json.dumps(table, separators=(",",":")))
