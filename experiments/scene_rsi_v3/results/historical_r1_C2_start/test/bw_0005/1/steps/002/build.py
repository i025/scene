from sceneact import *
import bpy

# Reference inventory, estimated from the classroom photograph in the right
# part of the supplied graphic:
# - Classroom inset spans approximately x=.58-.96, y=.44-.96. Its irregular
#   border belongs to the graphic, not the room.
# - Cream back wall and a row of tall windows occupy x=.60-.89, y=.45-.68.
#   The right end of the room is partly cropped and obscured.
# - Light plank floor extends across the lower half of the inset.
# - Low open wooden shelves line the back and left, with additional shelves
#   through the middle. A large foreground shelf occupies x=.71-.88, y=.72-.92.
# - Small tables and child-sized chairs sit behind the foreground shelf.
# - A dark red round rug is partly covered by that shelf.
# - Trays, boxes and small materials sit on and inside the shelves. Exact
#   contents and far-right furniture are uncertain.
#
# Review of the previous render: the solid right wall obstructs the room;
# the camera is too elevated, the image too washed out, and the cabinets and
# rug are too small within the frame. This revision opens the near side, lowers
# the viewpoint, strengthens warm wood colors and keeps the main cabinet
# prominent while retaining the surrounding furniture and open circulation.
#
# Expanded primitive estimate: architecture and windows ~65, floor seams 18,
# seven open cabinets ~56, two tables and four chairs ~46, materials ~50,
# rug 2. Total approximately 237 primitives; no Boolean operations.

scene = Scene("Montessori classroom")

cream = (0.82, 0.80, 0.72)
trim = (0.91, 0.89, 0.81)
floor_color = (0.65, 0.49, 0.33)
floor_joint = (0.53, 0.39, 0.27)
wood = (0.56, 0.36, 0.18)
wood_light = (0.69, 0.48, 0.27)
wood_dark = (0.39, 0.25, 0.13)
wood_inside = (0.47, 0.30, 0.15)
glass = (0.64, 0.77, 0.77)
tray = (0.72, 0.58, 0.37)
red = (0.48, 0.105, 0.065)
red_edge = (0.28, 0.09, 0.055)
green = (0.29, 0.39, 0.21)
blue = (0.29, 0.43, 0.45)

room = Asset("architecture")
room.include("floor", box((9.0, 7.0, 0.12),
                          center=(0, 0, -0.06), color=floor_color))
room.include("back_wall", box((9.0, 0.15, 3.0),
                              center=(0, 3.5, 1.5), color=cream))
room.include("back_baseboard", box((9.0, 0.04, 0.12),
                                   center=(0, 3.40, 0.07), color=trim))
# A short far-right wall indicates the return without hiding the room.
room.include("far_right_return", box((0.15, 1.15, 3.0),
                                     center=(4.5, 2.96, 1.5), color=cream))
for i in range(18):
    x = -4.25 + i * 0.5
    room.include("floor_plank_joint_%02d" % i,
                 box((0.009, 6.98, 0.003), center=(x, 0, 0.002),
                     color=floor_joint))

windows = Asset("daylight_windows")
for i in range(5):
    x = -3.68 + i * 1.22
    windows.include("pane_%d" % i,
                    box((1.06, 0.025, 1.35), center=(x, 3.395, 1.98),
                        color=glass))
    for j, dx in enumerate((-0.56, 0.56)):
        windows.include("frame_side_%d_%d" % (i, j),
                        box((0.055, 0.09, 1.46),
                            center=(x + dx, 3.34, 1.98), color=trim))
    for j, z in enumerate((1.27, 1.98, 2.69)):
        windows.include("frame_cross_%d_%d" % (i, j),
                        box((1.17, 0.09, 0.055),
                            center=(x, 3.34, z), color=trim))
windows.include("window_sill", box((6.12, 0.20, 0.08),
                                   center=(-1.24, 3.30, 1.23), color=trim))
room.include("window_row", windows)

# A light-colored door at the distant end is only partly visible.
door = Asset("distant_door")
door.include("leaf", box((0.035, 0.84, 2.10),
                          center=(4.405, 3.0, 1.05), color=(0.70, 0.62, 0.46)))
for j, y in enumerate((2.55, 3.45)):
    door.include("jamb_%d" % j,
                 box((0.07, 0.06, 2.17), center=(4.37, y, 1.085), color=trim))
door.include("head", box((0.07, 0.96, 0.07),
                         center=(4.37, 3.0, 2.17), color=trim))
room.include("door", door)
scene.include("room", room)

def cabinet(name, x, y, length, depth, height, direction="x", divisions=2):
    a = Asset(name)
    thickness = 0.055

    def piece(label, along, across, z, long_size, deep_size, tall_size, color):
        if direction == "x":
            size = (long_size, deep_size, tall_size)
            center = (x + along, y + across, z)
        else:
            size = (deep_size, long_size, tall_size)
            center = (x + across, y + along, z)
        a.include(label, box(size, center=center, color=color))

    piece("top", 0, 0, height - thickness / 2,
          length, depth, thickness, wood_light)
    piece("bottom", 0, 0, 0.07,
          length, depth, thickness, wood)
    piece("middle_shelf", 0, 0, height * 0.49,
          length - 2 * thickness, depth, thickness, wood_light)
    for side in (-1, 1):
        piece("end_%s" % side, side * (length / 2 - thickness / 2), 0,
              height / 2, thickness, depth, height, wood_light)
    # The thin rear board gives the open shelf bays depth while leaving the
    # front fully open toward the camera.
    piece("back", 0, depth / 2 - 0.018, height / 2,
          length - 2 * thickness, 0.036, height - 0.08, wood_inside)
    for j in range(1, divisions + 1):
        along = -length / 2 + j * length / (divisions + 1)
        piece("lower_divider_%d" % j, along, 0, height * 0.265,
              0.045, depth * 0.90, height * 0.39, wood)
    scene.include(name, a)

cabinet("foreground_display_shelf", 0.45, -1.75, 2.8, 0.66, 0.84)
cabinet("left_wall_shelf", -3.85, 0.40, 3.05, 0.57, 0.78, "y")
cabinet("back_window_shelf", -1.80, 2.80, 3.05, 0.55, 0.74)
cabinet("center_island_shelf", -1.55, 0.35, 2.1, 0.58, 0.78, "y")
cabinet("right_rear_shelf", 3.20, 2.65, 1.75, 0.53, 0.76)
cabinet("right_side_shelf", 3.90, 0.42, 1.85, 0.55, 0.76, "y")

def table(name, x, y, sx, sy):
    a = Asset(name)
    a.include("top", box((sx, sy, 0.07),
                          center=(x, y, 0.60), color=wood_light))
    for i, dx in enumerate((-sx / 2 + 0.09, sx / 2 - 0.09)):
        for j, dy in enumerate((-sy / 2 + 0.09, sy / 2 - 0.09)):
            a.include("leg_%d_%d" % (i, j),
                      box((0.065, 0.065, 0.56),
                          center=(x + dx, y + dy, 0.28), color=wood))
    scene.include(name, a)

def child_chair(name, x, y):
    a = Asset(name)
    a.include("seat", box((0.40, 0.38, 0.05),
                           center=(x, y, 0.34), color=wood_light))
    for i, dx in enumerate((-0.15, 0.15)):
        for j, dy in enumerate((-0.14, 0.14)):
            a.include("leg_%d_%d" % (i, j),
                      box((0.045, 0.045, 0.33),
                          center=(x + dx, y + dy, 0.165), color=wood))
    for i, dx in enumerate((-0.15, 0.15)):
        a.include("back_post_%d" % i,
                  box((0.045, 0.045, 0.32),
                      center=(x + dx, y + 0.16, 0.50), color=wood))
    a.include("back_rest", box((0.34, 0.045, 0.12),
                               center=(x, y + 0.16, 0.62), color=wood_light))
    scene.include(name, a)

table("central_activity_table", 1.0, 0.70, 1.55, 0.85)
table("back_activity_table", 2.35, 2.05, 1.15, 0.70)
child_chair("center_chair_left", 0.12, 0.54)
child_chair("center_chair_right", 1.88, 0.54)
child_chair("center_chair_front", 1.05, -0.12)
child_chair("back_chair", 2.30, 1.43)

rug = Asset("round_red_rug")
rug.include("dark_edge", rod(1.30, length=0.014,
                             center=(0.45, -1.49, 0.012),
                             axis="+z", color=red_edge))
rug.include("red_field", rod(1.22, length=0.016,
                             center=(0.45, -1.49, 0.021),
                             axis="+z", color=red))
scene.include("rug", rug)

materials = Asset("montessori_learning_materials")
for i, x in enumerate((-0.58, 0.0, 0.58, 1.16)):
    materials.include("foreground_tray_%d" % i,
                      box((0.44, 0.34, 0.035),
                          center=(x, -1.75, 0.858), color=tray))
    materials.include("foreground_block_%d" % i,
                      box((0.15, 0.15, 0.10),
                          center=(x - 0.06, -1.75, 0.925),
                          color=(wood_dark, green, blue, wood)[i]))
    materials.include("foreground_small_block_%d" % i,
                      box((0.10, 0.10, 0.075),
                          center=(x + 0.10, -1.75, 0.912), color=wood_light))
for i, x in enumerate((-2.93, -2.37, -1.81, -1.25, -0.69)):
    materials.include("back_tray_%d" % i,
                      box((0.40, 0.30, 0.035),
                          center=(x, 2.80, 0.758), color=tray))
    materials.include("back_box_%d" % i,
                      box((0.21, 0.17, 0.11),
                          center=(x, 2.80, 0.83),
                          color=(wood_dark, wood, green, wood_light, blue)[i]))
for i, y in enumerate((-0.55, 0.05, 0.65, 1.25)):
    materials.include("left_tray_%d" % i,
                      box((0.31, 0.42, 0.035),
                          center=(-3.85, y, 0.798), color=tray))
    materials.include("left_block_%d" % i,
                      box((0.14, 0.16, 0.09),
                          center=(-3.85, y, 0.86), color=wood_dark))
for i, x in enumerate((-0.55, 0.30, 1.10)):
    materials.include("shelf_inner_box_%d" % i,
                      box((0.38, 0.32, 0.15),
                          center=(x, -1.80, 0.18), color=tray))
materials.include("table_tray", box((0.42, 0.31, 0.035),
                                     center=(1.0, 0.70, 0.653), color=tray))
materials.include("table_block", box((0.13, 0.13, 0.10),
                                      center=(1.0, 0.70, 0.72), color=wood))
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
sc.world.node_tree.links.new(background.outputs["Background"], output.inputs["Surface"])
background.inputs["Color"].default_value = (0.78, 0.81, 0.79, 1)
background.inputs["Strength"].default_value = 0.45

# Corner view, low enough for the shelves to read as child-height furniture.
set_view((7.8, -13.0, 5.2), (0.0, 0.45, 1.0), lens=38, sensor=36)
area_emitter((-2.0, 2.5, 4.3), power=900, size=4.0,
             target=(0, -0.5, 0.4), color=(1.0, 0.91, 0.78))
area_emitter((0.5, -5.0, 5.0), power=450, size=5.0,
             target=(0, 0.5, 0.5), color=(1.0, 0.96, 0.88))
