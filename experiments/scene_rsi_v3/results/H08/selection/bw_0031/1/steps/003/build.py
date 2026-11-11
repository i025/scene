from sceneact import *
import bpy
import math
from mathutils import Vector

# Reference inventory and image anchors, estimated from the lower photograph:
# The photograph occupies x=.03–.94, y=.65–1.00 of the supplied portrait.
# Within that photograph, the rear instrument wall fills about x=0–.68,
# y=0–.55; its top edge falls slightly to the right. Square meters flank
# a dark horizontal vent. The main desk occupies approximately x=0–.70,
# y=.38–1.00; its near left end is cropped, and its long edges rise right.
# A door and smaller console occupy the right background, with dark floor
# visible below. The separate yellow GRID photograph supplies panel detail;
# its location in the room is uncertain.
#
# Review of the second render, using full rendered-frame coordinates:
# 1. The room occupies approximately y=.38–.93, leaving a large gray area
#    above it. The reference room photograph fills its crop. Increase camera
#    lens from 25 to 38 and enclose the view with a taller rear wall; the wall
#    top should move upward and foreground desk contours outward.
# 2. The desk appears roughly x=.18–.83, y=.50–.70, versus the reference
#    photograph's x=0–.70, y=.38–1.00. The longer lens should enlarge it,
#    crop its near left end, and move its lower edge downward. The photograph
#    shows a wider and more detailed inclined surface, so increase its depth.
# 3. The second render's back wall occupies roughly x=.05–.76, y=.38–.61,
#    and the small right desk is largely hidden by the main console. Moving
#    that independent desk farther right should reveal its silhouette.
# 4. The long desk edge rises right in both views, but the rendered edge is
#    shallower. Preserve the left-end viewpoint and bring the camera closer
#    to the foreground desk. Its dark pedestal overlaps the lower wall, as in
#    the photograph. The rendered floor is brighter; a separate dark matte
#    material is assigned, while lighting still determines final brightness.
#
# Projection values below are geometry points, not observed silhouette bounds.
# Camera position, target and lens are independent of asset dimensions.
# Estimated expanded meshes: architecture 6; cabinets, seams and meters 92;
# vent 9; main console and controls about 165; right console 17;
# door 3; GRID panel 35; fixtures 3: about 330 meshes in total.

ROOM_W, ROOM_D, ROOM_H = 11.0, 9.5, 4.3
DESK_L, DESK_R = -4.25, 2.00
CAM_POS = (-5.9, -7.0, 2.85)
CAM_TARGET = (-0.4, 2.0, 1.45)
OLD_LENS, CAM_LENS = 25, 38

scene = Scene("1970s_Dispatch_Control_Room")
wall_col = (.68, .67, .63)
cab_col = (.65, .64, .59)
face_col = (.76, .75, .69)
white = (.84, .83, .77)
dark = (.10, .095, .085)
black = (.025, .025, .022)
floor_col = (.17, .15, .13)
red = (.58, .025, .012)
amber = (.92, .42, .015)
yellow = (.88, .66, .14)

architecture = Asset("Architecture")
architecture.include("floor", box((ROOM_W, ROOM_D, .12),
                                  center=(0, 0, -.06), color=floor_col))
architecture.include("rear_wall", box((ROOM_W, .12, ROOM_H),
                                      center=(0, 3.4, ROOM_H / 2),
                                      color=wall_col))
architecture.include("right_wall", box((.12, ROOM_D, ROOM_H),
                                       center=(5.5, 0, ROOM_H / 2),
                                       color=wall_col))
architecture.include("left_wall", box((.12, ROOM_D, ROOM_H),
                                      center=(-5.5, 0, ROOM_H / 2),
                                      color=wall_col))
architecture.include("ceiling", box((ROOM_W, ROOM_D, .10),
                                    center=(0, 0, ROOM_H + .05),
                                    color=wall_col))
architecture.include("rear_baseboard", box((ROOM_W, .04, .14),
                                           center=(0, 3.31, .07), color=dark))
scene.include("Architecture", architecture)

cabinets = Asset("Rear_Instrument_Wall")
cabinets.include("cabinet_body", box((7.1, .22, 2.72),
                                    center=(-1.2, 3.22, 1.39), color=cab_col))
for i in range(9):
    x = -4.70 + i * .86
    cabinets.include("cabinet_seam_%02d" % i,
                     box((.016, .018, 2.68), center=(x, 3.095, 1.40),
                         color=(.30, .29, .27)))
cabinets.include("upper_panel_line", box((7.05, .018, .016),
                                         center=(-1.2, 3.09, 2.27),
                                         color=(.30, .29, .27)))
cabinets.include("lower_panel_line", box((7.05, .018, .016),
                                         center=(-1.2, 3.09, .39),
                                         color=(.30, .29, .27)))
for col in (0, 1, 2, 3, 7, 8, 9, 10):
    x = -4.52 + col * .60
    for row in range(3):
        z = .76 + row * .45
        k = "%02d_%d" % (col, row)
        cabinets.include("meter_frame_" + k,
                         box((.39, .035, .36), center=(x, 3.065, z),
                             color=dark))
        cabinets.include("meter_face_" + k,
                         box((.32, .018, .29), center=(x, 3.038, z),
                             color=white))
        cabinets.include("meter_needle_" + k,
                         box((.012, .009, .11),
                             center=(x + .025, 3.024, z), color=black))
cabinets.include("vent_frame", box((1.65, .035, .72),
                                   center=(-1.25, 3.06, 1.25), color=dark))
cabinets.include("vent_recess", box((1.52, .018, .59),
                                    center=(-1.25, 3.033, 1.25),
                                    color=cab_col))
for i in range(7):
    cabinets.include("vent_slot_%d" % i,
                     box((1.46, .015, .036),
                         center=(-1.25, 3.018, 1.01 + i * .08), color=dark))
scene.include("Rear_Instrument_Wall", cabinets)

desk = Asset("Main_Operating_Console")
desk.include("dark_pedestal", box((DESK_R - DESK_L, 1.35, .72),
                                  center=((DESK_L + DESK_R) / 2, -.06, .36),
                                  color=(.075, .069, .061)))
desk.include("front_base_panel", box((6.0, .025, .49),
                                     center=(-1.125, -.746, .36),
                                     color=(.13, .12, .10)))
desk.include("writing_ledge", box((6.45, .46, .075),
                                  center=(-1.125, -.91, .80), color=face_col))
desk.include("left_cheek", box((.10, 1.30, .40),
                               center=(-4.22, .02, 1.00), color=cab_col))
desk.include("right_cheek", box((.10, 1.30, .40),
                                center=(1.97, .02, 1.00), color=cab_col))
scene.include("Main_Operating_Console", desk)

small = Asset("Right_Independent_Console")
small.include("pedestal", box((1.45, .82, .74),
                              center=(4.15, 2.38, .37),
                              color=(.16, .15, .13)))
small.include("writing_ledge", box((1.55, .28, .07),
                                   center=(4.15, 1.92, .79), color=face_col))
scene.include("Right_Independent_Console", small)

door = Asset("Right_Wall_Doorway")
door.include("door_frame", box((.90, .055, 2.15),
                               center=(2.72, 3.28, 1.075),
                               color=(.46, .45, .41)))
door.include("door_inset", box((.70, .025, 1.90),
                               center=(2.72, 3.235, 1.12),
                               color=(.20, .19, .17)))
door.include("door_window", box((.47, .018, .83),
                                center=(2.72, 3.215, 1.62),
                                color=(.38, .38, .35)))
scene.include("Right_Wall_Doorway", door)

# The separate panel photograph does not establish its exact position in the room.
grid = Asset("GRID_Mimic_Panel")
grid.include("yellow_board", box((.08, 1.42, 1.92),
                                 center=(5.40, .55, 1.90), color=yellow))

def grid_bar(name, y, z, sy, sz, color=black):
    grid.include(name, box((.025, sy, sz),
                           center=(5.345, y, z), color=color))

grid_bar("main_bus", .40, 1.90, .035, 1.75)
for i, z in enumerate((1.25, 1.66, 2.08, 2.48)):
    grid_bar("horizontal_bus_%d" % i, .40, z, .66, .035)
for i, (y, z) in enumerate(((.10, 1.46), (.70, 1.46),
                             (.10, 1.87), (.70, 1.87),
                             (.10, 2.28), (.70, 2.28))):
    grid_bar("branch_%d" % i, y, z, .035, .38)
for i, (y, z) in enumerate(((.1, 1.66), (.4, 1.66), (.7, 1.66),
                             (.1, 2.08), (.4, 2.08), (.7, 2.08))):
    grid.include("amber_lamp_%d" % i,
                 box((.035, .11, .12), center=(5.315, y, z), color=amber))
for i, z in enumerate((1.10, 2.72)):
    grid.include("red_lamp_%d" % i,
                 ball(.065, center=(5.31, .4, z), color=red))
for i, z in enumerate((1.25, 1.55, 1.85, 2.15, 2.45, 2.72)):
    grid.include("selector_dial_%d" % i,
                 box((.025, .19, .19), center=(5.33, 1.08, z), color=white))
    grid.include("selector_knob_%d" % i,
                 ball(.052, center=(5.29, 1.08, z), color=black))
scene.include("GRID_Mimic_Panel", grid)

fixtures = Asset("Ceiling_Fluorescent_Fixtures")
for i, x in enumerate((-2.6, .4, 3.3)):
    fixtures.include("fluorescent_%d" % i,
                     box((2.0, .40, .035), center=(x, 1.3, 4.22),
                         color=white))
scene.include("Ceiling_Fluorescent_Fixtures", fixtures)

realize(scene)

def get_collection(name):
    c = bpy.data.collections.get(name)
    if c is None:
        c = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(c)
    return c

def material(name, color, rough=.65, metallic=0, emission=0):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    p = m.node_tree.nodes.get("Principled BSDF")
    p.inputs["Base Color"].default_value = (*color, 1)
    p.inputs["Roughness"].default_value = rough
    p.inputs["Metallic"].default_value = metallic
    if emission:
        e = p.inputs.get("Emission Color") or p.inputs.get("Emission")
        if e:
            e.default_value = (*color, 1)
        strength = p.inputs.get("Emission Strength")
        if strength:
            strength.default_value = emission
    return m

surface_mat = material("Console painted metal", (.61, .60, .55), .52, .12)
mark_mat = material("Control markings", (.035, .034, .030), .72)
knob_mat = material("Bakelite knobs", (.035, .033, .030), .34)
red_mat = material("Red indicators emissive", (.65, .025, .012), .38, emission=.8)
amber_mat = material("Amber indicators emissive", (.95, .40, .015), .4, emission=.8)
lamp_mat = material("Fluorescent diffuser", (.95, .93, .82), .5, emission=1.0)
floor_mat = material("Floor matte brown gray", (.17, .15, .13), .86)

def mesh_obj(name, verts, faces, mat, group):
    mesh = bpy.data.meshes.new(name + "_mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    get_collection(group).objects.link(obj)
    obj.data.materials.append(mat)
    return obj

def sloped_face(name, xmin, xmax, yf, yb, zf, zb, group):
    return mesh_obj(name,
                    [(xmin, yf, zf), (xmax, yf, zf),
                     (xmax, yb, zb), (xmin, yb, zb)],
                    [(0, 1, 2, 3)], surface_mat, group)

sloped_face("Main inclined control surface", -4.17, 1.92,
            -.69, .67, .84, 1.34, "Main_Operating_Console_Details")
sloped_face("Small inclined control surface", 3.43, 4.87,
            2.00, 2.74, .83, 1.25, "Right_Independent_Console_Details")

def slope_z(y, yf, yb, zf, zb):
    return zf + (y - yf) * (zb - zf) / (yb - yf)

def disk(name, loc, radius, mat, normal, group):
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=radius,
                                       depth=.025, location=loc)
    obj = bpy.context.object
    obj.name = name
    obj.rotation_euler = Vector(normal).to_track_quat("Z", "Y").to_euler()
    obj.data.materials.append(mat)
    for old in list(obj.users_collection):
        old.objects.unlink(obj)
    get_collection(group).objects.link(obj)

normal = Vector((0, -.50, 1.36)).normalized()
for i in range(11):
    x = -3.90 + i * .55
    for j, y in enumerate((-.48, -.22, .04, .30, .53)):
        z = slope_z(y, -.69, .67, .84, 1.34) + .018
        mat = red_mat if (i * 3 + j) % 17 == 0 else knob_mat
        disk("Main control %02d_%d" % (i, j), (x, y, z), .032,
             mat, normal, "Main_Operating_Console_Details")
    y0, y1 = -.62, .61
    z0 = slope_z(y0, -.69, .67, .84, 1.34) + .012
    z1 = slope_z(y1, -.69, .67, .84, 1.34) + .012
    mesh_obj("Station divider %02d" % i,
             [(x - .23, y0, z0), (x - .215, y0, z0),
              (x - .215, y1, z1), (x - .23, y1, z1)],
             [(0, 1, 2, 3)], mark_mat, "Main_Operating_Console_Details")

small_normal = Vector((0, -.42, .74)).normalized()
for i in range(5):
    for j in range(2):
        y = 2.12 + j * .29
        z = slope_z(y, 2.00, 2.74, .83, 1.25) + .018
        disk("Small control %d_%d" % (i, j), (3.58 + i * .25, y, z),
             .035, red_mat if (i + j) % 6 == 0 else knob_mat,
             small_normal, "Right_Independent_Console_Details")

def label(name, body, pos, size):
    curve = bpy.data.curves.new(name, "FONT")
    curve.body = body
    curve.size = size
    obj = bpy.data.objects.new(name, curve)
    get_collection("GRID_Panel_Labels").objects.link(obj)
    obj.location = pos
    obj.rotation_euler = (math.pi / 2, 0, math.pi / 2)
    obj.data.materials.append(mark_mat)

label("Panel label one", "FERNLEITUNG", (5.30, 1.20, 2.75), .055)
label("Panel label two", "SCHALTER", (5.30, 1.20, 1.05), .055)

def descendants(root):
    result, stack = [], list(root.children)
    while stack:
        obj = stack.pop()
        stack.extend(obj.children)
        if obj.type == "MESH":
            result.append(obj)
    return result

def assign_semantic(fragment, mat):
    selected = []
    for obj in bpy.data.objects:
        if fragment.lower() in obj.name.lower():
            if obj.type == "MESH":
                selected.append(obj)
            selected.extend(descendants(obj))
    seen = set()
    for obj in selected:
        if obj.name in seen:
            continue
        seen.add(obj.name)
        # Replace the finish on this mesh alone; shared source materials are
        # left unchanged for other assets.
        obj.data.materials.clear()
        obj.data.materials.append(mat)
    p = mat.node_tree.nodes.get("Principled BSDF")
    print("Material selection:", fragment, "meshes", len(seen),
          "material", mat.name, "users", mat.users,
          "roughness", p.inputs["Roughness"].default_value,
          "metallic", p.inputs["Metallic"].default_value,
          "emission", p.inputs["Emission Strength"].default_value
          if p.inputs.get("Emission Strength") else "unsupported")

assign_semantic("red_lamp", red_mat)
assign_semantic("amber_lamp", amber_mat)
assign_semantic("fluorescent_", lamp_mat)
assign_semantic("floor", floor_mat)
p = surface_mat.node_tree.nodes["Principled BSDF"]
print("Material selection: Main inclined control surface", surface_mat.name,
      "users", surface_mat.users,
      "roughness", p.inputs["Roughness"].default_value,
      "metallic", p.inputs["Metallic"].default_value)

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
background.inputs["Color"].default_value = (.75, .73, .68, 1)
background.inputs["Strength"].default_value = .35

sc.render.resolution_x = 1920
sc.render.resolution_y = 2628
sc.render.resolution_percentage = 100
sc.render.image_settings.file_format = "PNG"
sc.render.engine = "CYCLES"
sc.cycles.use_denoising = True
try:
    sc.view_settings.view_transform = "Filmic"
except TypeError:
    pass

set_view(CAM_POS, CAM_TARGET, lens=OLD_LENS)
panorama = sc.camera
panorama.name = "Camera_Panorama"
area_emitter((-2, 0, 4.10), power=700, size=4, target=(-1, 1, 0))
area_emitter((2, 1.5, 4.10), power=550, size=3, target=(1, 2, 0))

close_data = bpy.data.cameras.new("Camera_Closeup_Data")
close_cam = bpy.data.objects.new("Camera_Closeup", close_data)
get_collection("Cameras").objects.link(close_cam)
close_cam.location = (2.9, -3.3, 2.2)
close_cam.rotation_euler = (
    Vector((4.6, .8, 1.6)) - close_cam.location
).to_track_quat("-Z", "Y").to_euler()
close_data.lens = 35
sc.camera = panorama

# Reference estimates below refer to the room photograph alone. They are
# distinct from projections in the full portrait camera frame.
landmarks = [
    ("rear wall upper left", (-4.70, 3.09, 2.72), (.03, .08)),
    ("rear wall upper right", (2.30, 3.09, 2.72), (.67, .12)),
    ("console front left", (-4.22, -1.14, .84), (.03, .78)),
    ("console rear right", (1.92, .67, 1.34), (.67, .43)),
    ("small desk rear", (4.87, 2.74, 1.25), (.94, .48)),
]

def project_points():
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    proj = panorama.calc_matrix_camera(
        dg, x=sc.render.resolution_x, y=sc.render.resolution_y,
        scale_x=sc.render.pixel_aspect_x, scale_y=sc.render.pixel_aspect_y)
    out = []
    for _, pt, _ in landmarks:
        clip = proj @ panorama.matrix_world.inverted() @ Vector((*pt, 1))
        out.append(None if clip.w <= 1e-8 else
                   (.5 * (clip.x / clip.w + 1),
                    .5 * (1 - clip.y / clip.w)))
    return out

base = project_points()
panorama.data.lens = CAM_LENS
trial = project_points()
# A larger lens should move the upper cabinet edge upward and the near
# foreground point downward. Restore if this trial moves both incorrectly.
if (base[0] is None or trial[0] is None or
        trial[0][1] >= base[0][1] or
        base[2] is None or trial[2] is None or trial[2][1] <= base[2][1]):
    panorama.data.lens = OLD_LENS
chosen = project_points()
print("Landmark | reference estimate | 25 mm | 38 mm trial | final")
for (name, _, ref), a, b, c in zip(landmarks, base, trial, chosen):
    def fmt(uv):
        return None if uv is None else tuple(round(v, 3) for v in uv)
    print(name, ref, fmt(a), fmt(b), fmt(c))
