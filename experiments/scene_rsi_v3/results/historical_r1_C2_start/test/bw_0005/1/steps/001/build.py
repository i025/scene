from sceneact import *
import bpy
import math

# Reference inventory, estimated from the small classroom inset in the image:
# - A rectangular room fills approximately image x=.58–.91, y=.44–.96.
# - Cream back wall, with a long row of daylight windows at x=.61–.83,
#   y=.46–.64; right wall and doorway are partly occluded.
# - Light wooden floor occupies the lower half of the room inset.
# - Low wooden open shelves line the back and left sides and stand through
#   the middle. A prominent freestanding shelf occupies x=.71–.87, y=.72–.94.
# - Child-height tables and chairs are visible behind the foreground shelf.
# - A red oval or round rug lies beneath the foreground furniture.
# - Small trays, boxes and teaching materials sit loosely on the shelves.
# Exact room dimensions, individual materials and far-right furnishings are
# uncertain because the classroom occupies only a small part of the image.
#
# Primitive estimate: architecture and windows ~35; cabinets ~65;
# tables and stools ~35; shelf materials ~35; rug and miscellaneous ~10.
# Total approximately 180 meshes, with no Boolean operations.

scene = Scene("Montessori classroom")

cream = (0.84, 0.82, 0.74)
white = (0.92, 0.92, 0.85)
wood = (0.57, 0.38, 0.20)
wood_light = (0.68, 0.48, 0.27)
wood_edge = (0.48, 0.30, 0.15)
floor_color = (0.67, 0.51, 0.35)
glass = (0.64, 0.79, 0.81)
rug_red = (0.52, 0.13, 0.08)
rug_border = (0.31, 0.12, 0.07)
tray_color = (0.71, 0.56, 0.34)
green = (0.29, 0.43, 0.22)
blue = (0.29, 0.47, 0.55)

room = Asset("room")
room.include("floor", box((9.0, 7.0, 0.12), center=(0, 0, -0.06), color=floor_color))
room.include("back_wall", box((9.0, 0.16, 3.2), center=(0, 3.5, 1.6), color=cream))
room.include("right_wall", box((0.16, 7.0, 3.2), center=(4.5, 0, 1.6), color=cream))
room.include("back_baseboard", box((9.0, 0.04, 0.12), center=(0, 3.39, 0.08), color=white))
room.include("right_baseboard", box((0.04, 7.0, 0.12), center=(4.39, 0, 0.08), color=white))

# Plank joints are restrained and parallel to the room's long axis.
for i in range(19):
    x = -4.28 + i * 0.48
    room.include("floor_joint_%02d" % i,
                 box((0.008, 6.96, 0.003), center=(x, 0, 0.002),
                     color=(0.53, 0.40, 0.28)))

# Windows are mounted just in front of the back wall, with visible deep frames.
windows = Asset("back_window_row")
for i in range(5):
    x = -3.58 + i * 1.26
    windows.include("glass_%d" % i,
                    box((1.12, 0.025, 1.35), center=(x, 3.395, 2.08), color=glass))
    for dx in (-0.58, 0.58):
        windows.include("side_frame_%d_%s" % (i, dx),
                        box((0.055, 0.09, 1.48), center=(x + dx, 3.34, 2.08), color=white))
    for z in (1.36, 2.08, 2.80):
        windows.include("cross_frame_%d_%s" % (i, z),
                        box((1.20, 0.09, 0.055), center=(x, 3.34, z), color=white))
windows.include("continuous_sill", box((6.30, 0.18, 0.08),
                                       center=(-1.06, 3.29, 1.31), color=white))
room.include("windows", windows)

# A simple closed door occupies the far end of the right wall.
door = Asset("right_wall_door")
door.include("leaf", box((0.035, 0.94, 2.13), center=(4.395, 2.68, 1.07),
                         color=(0.72, 0.64, 0.49)))
for y in (2.17, 3.19):
    door.include("jamb_%s" % y, box((0.07, 0.07, 2.20),
                                    center=(4.36, y, 1.10), color=white))
door.include("head", box((0.07, 1.09, 0.08), center=(4.36, 2.68, 2.18), color=white))
door.include("handle", ball(0.035, center=(4.32, 2.35, 1.02), color=wood_edge))
room.include("door", door)
scene.include("architecture", room)

def cabinet(name, x, y, length, depth, height, direction="x", shelves=2):
    """Open child-height shelf; direction specifies its long horizontal axis."""
    a = Asset(name)
    t = 0.055
    def piece(label, along, across, z, la, de, he, color):
        if direction == "x":
            size = (la, de, he)
            center = (x + along, y + across, z)
        else:
            size = (de, la, he)
            center = (x + across, y + along, z)
        a.include(label, box(size, center=center, color=color))
    piece("top", 0, 0, height - t / 2, length, depth, t, wood_light)
    piece("bottom", 0, 0, t / 2 + 0.035, length, depth, t, wood)
    for side in (-1, 1):
        piece("end_%s" % side, side * (length / 2 - t / 2), 0,
              height / 2, t, depth, height, wood_light)
    for j in range(1, shelves):
        z = 0.04 + j * (height - 0.08) / shelves
        piece("shelf_%d" % j, 0, 0, z, length - 2 * t, depth, t, wood_light)
    # Open cubbies retain visible gaps and separate teaching materials.
    for j in range(1, 3):
        along = -length / 2 + j * length / 3
        piece("divider_%d" % j, along, 0, height * 0.27,
              t * 0.75, depth * 0.91, height * 0.42, wood)
    scene.include(name, a)
    return a

cabinet("foreground_island_shelf", 0.25, -1.65, 2.75, 0.60, 0.82)
cabinet("left_wall_shelf", -3.86, 0.35, 3.20, 0.57, 0.78, "y")
cabinet("back_window_shelf", -1.85, 2.75, 2.95, 0.52, 0.72)
cabinet("middle_open_shelf", -1.40, 0.42, 2.15, 0.54, 0.76, "y")
cabinet("right_low_shelf", 3.80, 0.35, 2.20, 0.52, 0.74, "y")

def activity_table(name, x, y, sx, sy):
    a = Asset(name)
    a.include("top", box((sx, sy, 0.065), center=(x, y, 0.59), color=wood_light))
    for dx in (-sx / 2 + 0.09, sx / 2 - 0.09):
        for dy in (-sy / 2 + 0.09, sy / 2 - 0.09):
            a.include("leg_%s_%s" % (dx, dy),
                      box((0.07, 0.07, 0.55), center=(x + dx, y + dy, 0.275), color=wood))
    scene.include(name, a)

def stool(name, x, y):
    a = Asset(name)
    a.include("seat", box((0.40, 0.38, 0.055), center=(x, y, 0.34), color=wood_light))
    for dx in (-0.145, 0.145):
        for dy in (-0.135, 0.135):
            a.include("leg_%s_%s" % (dx, dy),
                      box((0.045, 0.045, 0.32), center=(x + dx, y + dy, 0.16), color=wood))
    scene.include(name, a)

activity_table("central_activity_table", 1.00, 0.65, 1.65, 0.88)
activity_table("back_activity_table", 2.40, 2.10, 1.25, 0.72)
stool("central_stool_left", 0.10, 0.63)
stool("central_stool_right", 1.90, 0.63)
stool("central_stool_front", 1.00, -0.08)
stool("back_stool", 2.35, 1.48)

# Flat, round rug with a subtle darker border.
rug = Asset("round_red_rug")
rug.include("border", rod(1.36, length=0.016, center=(0.20, -1.24, 0.015),
                          axis="+z", color=rug_border))
rug.include("field", rod(1.27, length=0.018, center=(0.20, -1.24, 0.025),
                         axis="+z", color=rug_red))
scene.include("rug", rug)

# Broad, readable shelf materials rather than fine clutter.
materials = Asset("montessori_materials")
for i, x in enumerate((-0.78, -0.20, 0.37, 0.95)):
    materials.include("foreground_tray_%d" % i,
                      box((0.43, 0.30, 0.035), center=(x, -1.65, 0.845), color=tray_color))
    for j in range(2):
        materials.include("foreground_block_%d_%d" % (i, j),
                          box((0.12, 0.11, 0.09 + 0.025 * j),
                              center=(x - 0.09 + j * 0.18, -1.65, 0.91 + 0.0125 * j),
                              color=(wood_edge, green, blue, wood)[i]))
for i, x in enumerate((-2.92, -2.35, -1.78, -1.21, -0.64)):
    materials.include("back_tray_%d" % i,
                      box((0.42, 0.28, 0.04), center=(x, 2.75, 0.755), color=tray_color))
    materials.include("back_box_%d" % i,
                      box((0.21, 0.16, 0.10), center=(x, 2.75, 0.825),
                          color=(wood, blue, wood_edge, green, wood_light)[i]))
for i, y in enumerate((-0.52, 0.12, 0.77, 1.41)):
    materials.include("left_tray_%d" % i,
                      box((0.30, 0.43, 0.035), center=(-3.86, y, 0.815), color=tray_color))
    materials.include("left_box_%d" % i,
                      box((0.15, 0.19, 0.09), center=(-3.86, y, 0.88), color=wood_edge))
materials.include("table_tray", box((0.44, 0.32, 0.035),
                                    center=(0.97, 0.65, 0.64), color=tray_color))
materials.include("table_block", box((0.13, 0.13, 0.12),
                                     center=(0.97, 0.65, 0.715), color=wood))
scene.include("learning_materials", materials)

realize(scene)

# Soft warm daylight enters from the back windows, supported by ambient fill.
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
background.inputs["Color"].default_value = (0.78, 0.83, 0.82, 1)
background.inputs["Strength"].default_value = 0.65

set_view((8.4, -11.4, 7.1), (0, 0.25, 0.75), lens=35, sensor=36)
area_emitter((-1.3, 3.0, 4.5), power=1100, size=5.0,
             target=(0, 0, 0.5), color=(1.0, 0.91, 0.77))
area_emitter((1.5, -3.8, 5.5), power=700, size=5.0,
             target=(0, 0, 0.5), color=(1.0, 0.97, 0.89))
