from sceneact import *
import bpy

# Reference inventory, estimated from the classroom inset:
# - Rectangular classroom, approximately x=.58-.96 and y=.44-.96 in the
#   supplied graphic. The irregular inset boundary is not room geometry.
# - Cream back wall, with a row of large windows across its left and middle.
#   The far right end and any ceiling details are partially obscured.
# - Light wood floor; low open shelves along the left and back, additional
#   shelves in the middle and right, and a prominent foreground shelf.
# - Small activity tables and child-height seating behind the foreground
#   shelf; a red round rug is partly hidden beneath the foreground shelf.
# - Loosely arranged trays, wooden boxes and blocks on the shelves.
#   Individual contents and the rightmost furniture are uncertain.
#
# Review of the second render: the furniture arrangement reads clearly, but
# the room appears as a small isolated model against a gray background. The
# camera is too distant for a walkthrough view, the surfaces are pale, and
# the windows read as a short horizontal band instead of tall daylight
# windows. This revision moves the camera inside the open corner, enlarges
# the furnishings in frame, extends the windows vertically, and strengthens
# the warm natural wood while maintaining the same shelf and table layout.
#
# Approximate expanded primitive count: room and floor seams 23; windows 31;
# six cabinets 48; tables 10; four stools 20; materials 36; rug 2;
# total about 170 meshes. No Boolean operations.

scene = Scene("Montessori classroom")

cream = (0.82, 0.79, 0.70)
trim = (0.92, 0.90, 0.83)
floor_color = (0.65, 0.49, 0.33)
floor_joint = (0.52, 0.39, 0.27)
wood = (0.54, 0.34, 0.17)
wood_light = (0.70, 0.48, 0.25)
wood_inside = (0.40, 0.25, 0.12)
glass = (0.61, 0.75, 0.75)
tray = (0.73, 0.57, 0.34)
red = (0.48, 0.10, 0.065)
red_edge = (0.26, 0.075, 0.045)
green = (0.28, 0.39, 0.20)
blue = (0.29, 0.43, 0.45)

room = Asset("architecture")
room.include(
    "floor",
    box((9.0, 7.0, 0.12), center=(0, 0, -0.06), color=floor_color)
)
room.include(
    "back_wall",
    box((9.0, 0.15, 3.15), center=(0, 3.5, 1.575), color=cream)
)
room.include(
    "back_baseboard",
    box((9.0, 0.04, 0.12), center=(0, 3.40, 0.07), color=trim)
)
room.include(
    "far_right_return",
    box((0.15, 1.15, 3.15), center=(4.5, 2.96, 1.575), color=cream)
)
for i in range(18):
    x = -4.25 + i * 0.5
    room.include(
        "floor_plank_joint_%02d" % i,
        box((0.008, 6.98, 0.003), center=(x, 0, 0.002),
            color=floor_joint)
    )

windows = Asset("daylight_windows")
for i in range(5):
    x = -3.68 + i * 1.22
    windows.include(
        "pane_%d" % i,
        box((1.06, 0.025, 1.72), center=(x, 3.395, 2.00),
            color=glass)
    )
    for j, dx in enumerate((-0.56, 0.56)):
        windows.include(
            "side_frame_%d_%d" % (i, j),
            box((0.055, 0.09, 1.82),
                center=(x + dx, 3.34, 2.00), color=trim)
        )
    for j, z in enumerate((1.12, 2.00, 2.88)):
        windows.include(
            "cross_frame_%d_%d" % (i, j),
            box((1.17, 0.09, 0.055),
                center=(x, 3.34, z), color=trim)
        )
windows.include(
    "sill",
    box((6.12, 0.20, 0.08), center=(-1.24, 3.30, 1.08),
        color=trim)
)
room.include("windows", windows)

door = Asset("distant_door")
door.include(
    "leaf",
    box((0.035, 0.84, 2.10), center=(4.405, 3.0, 1.05),
        color=(0.70, 0.62, 0.46))
)
for j, y in enumerate((2.55, 3.45)):
    door.include(
        "jamb_%d" % j,
        box((0.07, 0.06, 2.17), center=(4.37, y, 1.085),
            color=trim)
    )
door.include(
    "head",
    box((0.07, 0.96, 0.07), center=(4.37, 3.0, 2.17),
        color=trim)
)
room.include("door", door)
scene.include("room", room)

def cabinet(name, x, y, length, depth, height, direction="x"):
    asset = Asset(name)
    thickness = 0.055

    def piece(label, along, across, z, long_size, deep_size, tall_size, color):
        if direction == "x":
            size = (long_size, deep_size, tall_size)
            center = (x + along, y + across, z)
        else:
            size = (deep_size, long_size, tall_size)
            center = (x + across, y + along, z)
        asset.include(label, box(size, center=center, color=color))

    piece("top", 0, 0, height - thickness / 2,
          length, depth, thickness, wood_light)
    piece("bottom", 0, 0, 0.07, length, depth, thickness, wood)
    piece("middle_shelf", 0, 0, height * 0.49,
          length - 2 * thickness, depth, thickness, wood_light)
    for side in (-1, 1):
        piece("end_%d" % side, side * (length / 2 - thickness / 2),
              0, height / 2, thickness, depth, height, wood_light)
    piece("back", 0, depth / 2 - 0.018, height / 2,
          length - 2 * thickness, 0.036, height - 0.08, wood_inside)
    for j in (1, 2):
        along = -length / 2 + j * length / 3
        piece("lower_divider_%d" % j, along, 0, height * 0.265,
              0.045, depth * 0.90, height * 0.39, wood)
    scene.include(name, asset)

cabinet("foreground_display_shelf", 0.45, -1.75, 2.8, 0.66, 0.84)
cabinet("left_wall_shelf", -3.85, 0.40, 3.05, 0.57, 0.78, "y")
cabinet("back_window_shelf", -1.80, 2.80, 3.05, 0.55, 0.74)
cabinet("center_island_shelf", -1.55, 0.35, 2.1, 0.58, 0.78, "y")
cabinet("right_rear_shelf", 3.20, 2.65, 1.75, 0.53, 0.76)
cabinet("right_side_shelf", 3.90, 0.42, 1.85, 0.55, 0.76, "y")

def table(name, x, y, sx, sy):
    asset = Asset(name)
    asset.include(
        "top",
        box((sx, sy, 0.07), center=(x, y, 0.60), color=wood_light)
    )
    for i, dx in enumerate((-sx / 2 + 0.09, sx / 2 - 0.09)):
        for j, dy in enumerate((-sy / 2 + 0.09, sy / 2 - 0.09)):
            asset.include(
                "leg_%d_%d" % (i, j),
                box((0.065, 0.065, 0.56),
                    center=(x + dx, y + dy, 0.28), color=wood)
            )
    scene.include(name, asset)

def stool(name, x, y):
    asset = Asset(name)
    asset.include(
        "seat",
        box((0.40, 0.38, 0.05), center=(x, y, 0.34),
            color=wood_light)
    )
    for i, dx in enumerate((-0.15, 0.15)):
        for j, dy in enumerate((-0.14, 0.14)):
            asset.include(
                "leg_%d_%d" % (i, j),
                box((0.045, 0.045, 0.33),
                    center=(x + dx, y + dy, 0.165), color=wood)
            )
    scene.include(name, asset)

table("central_activity_table", 1.0, 0.70, 1.55, 0.85)
table("back_activity_table", 2.35, 2.05, 1.15, 0.70)
stool("center_stool_left", 0.12, 0.54)
stool("center_stool_right", 1.88, 0.54)
stool("center_stool_front", 1.05, -0.12)
stool("back_stool", 2.30, 1.43)

rug = Asset("round_red_rug")
rug.include(
    "dark_edge",
    rod(1.30, length=0.014, center=(0.45, -1.49, 0.012),
        axis="+z", color=red_edge)
)
rug.include(
    "red_field",
    rod(1.22, length=0.016, center=(0.45, -1.49, 0.021),
        axis="+z", color=red)
)
scene.include("rug", rug)

materials = Asset("montessori_learning_materials")
for i, x in enumerate((-0.58, 0.0, 0.58, 1.16)):
    materials.include(
        "foreground_tray_%d" % i,
        box((0.44, 0.34, 0.035), center=(x, -1.75, 0.858),
            color=tray)
    )
    materials.include(
        "foreground_block_%d" % i,
        box((0.15, 0.15, 0.10), center=(x - 0.06, -1.75, 0.925),
            color=(wood_inside, green, blue, wood)[i])
    )
    materials.include(
        "foreground_small_block_%d" % i,
        box((0.10, 0.10, 0.075), center=(x + 0.10, -1.75, 0.912),
            color=wood_light)
    )
for i, x in enumerate((-2.93, -2.37, -1.81, -1.25, -0.69)):
    materials.include(
        "back_tray_%d" % i,
        box((0.40, 0.30, 0.035), center=(x, 2.80, 0.758),
            color=tray)
    )
    materials.include(
        "back_box_%d" % i,
        box((0.21, 0.17, 0.11), center=(x, 2.80, 0.83),
            color=(wood_inside, wood, green, wood_light, blue)[i])
    )
for i, y in enumerate((-0.55, 0.05, 0.65, 1.25)):
    materials.include(
        "left_tray_%d" % i,
        box((0.31, 0.42, 0.035), center=(-3.85, y, 0.798),
            color=tray)
    )
    materials.include(
        "left_block_%d" % i,
        box((0.14, 0.16, 0.09), center=(-3.85, y, 0.86),
            color=wood_inside)
    )
for i, x in enumerate((-0.55, 0.30, 1.10)):
    materials.include(
        "shelf_inner_box_%d" % i,
        box((0.38, 0.32, 0.15), center=(x, -1.80, 0.18),
            color=tray)
    )
materials.include(
    "table_tray",
    box((0.42, 0.31, 0.035), center=(1.0, 0.70, 0.653),
        color=tray)
)
materials.include(
    "table_block",
    box((0.13, 0.13, 0.10), center=(1.0, 0.70, 0.72),
        color=wood)
)
scene.include("learning_materials", materials)

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
sc.world.node_tree.links.new(
    background.outputs["Background"], output.inputs["Surface"]
)
background.inputs["Color"].default_value = (0.78, 0.81, 0.79, 1)
background.inputs["Strength"].default_value = 0.45

# Wide corner view, centered on the shelves and activity area.
set_view((5.8, -8.9, 4.0), (-0.25, 0.65, 1.05),
         lens=28, sensor=36)
area_emitter((-2.0, 3.0, 3.6), power=850, size=4.0,
             target=(0, -0.5, 0.4), color=(1.0, 0.91, 0.78))
area_emitter((0.5, -4.0, 4.8), power=350, size=5.0,
             target=(0, 0.5, 0.5), color=(1.0, 0.96, 0.88))
