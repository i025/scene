# Visual comparison, normalized image coordinates (x, y), estimated:
# Reference rear corner: (.52, .36)-(.52, .59); render: about
# (.60, .40)-(.60, .59). Reference back wall vent: (.15, .44)-(.24, .47);
# render: approximately (.13, .47)-(.20, .49).
# Reference whiteboard: (.59, .25)-(.91, .58); render: approximately
# (.69, .39)-(1.00, .56), cropped on the right.
# Reference foreground panel: approximately (.07, .75)-(.40, .80);
# render: approximately (.07, .87)-(.61, .97). Reference insulation:
# (.56, .68)-(.90, .79); render: (.71, .71)-(1.00, .78), cropped.
# Reference left partition occupies x=0-.12; render shows only a narrow
# strip near the left edge. The reference ceiling grid slopes toward the
# rear and the right baseboard descends toward the image's right edge.
#
# Ranked corrections:
# 1. Increase camera lens from 30 to 35 and aim farther right. The rear
#    corner should move left and upward, and the rear wall should appear
#    taller. Keep the camera height approximately fixed so its floor edge
#    remains near y=.59.
# 2. Move the whiteboard farther along the wall toward the rear and increase
#    its height. Its right edge should leave the crop and its top rise.
# 3. Move the foreground debris farther toward the back and shrink the
#    nearest panel, shifting its silhouette upward and reducing its width.
#    Move the insulation toward the back and left to bring its right edge
#    inside the frame. Widen the visible left partition.
# The exact broken shapes, ceiling openings, and occluded spaces are
# uncertain. Surface brightness also depends on lighting and orientation.
# Estimated expanded primitives: architecture 8, ceiling 31, board 6,
# wall fixtures 8, flag 11, floor debris 10, insulation and strips 7:
# approximately 81 meshes.

from sceneact import *
import bpy

scene = Scene("Classroom reconstruction")

room_width = 6.8
room_depth = 13.0
room_height = 3.2
back_y = 6.5
right_x = room_width / 2
camera_pos = (-2.45, -6.6, 1.65)
camera_target = (2.55, 5.9, 1.70)
camera_lens = 35

wall = (.68, .67, .62)
ceiling_color = (.72, .74, .73)
grid = (.52, .54, .53)
carpet = (.065, .068, .064)
baseboard = (.065, .07, .065)
metal = (.40, .42, .41)

room = Asset("Room architecture")
room.include("carpet floor", box((room_width, room_depth, .12),
    center=(0, 0, -.06), color=carpet))
room.include("back wall", box((room_width, .12, room_height),
    center=(0, back_y, room_height/2), color=wall))
room.include("right wall", box((.12, room_depth, room_height),
    center=(right_x, 0, room_height/2), color=(.72, .71, .67)))
room.include("back baseboard", box((room_width, .035, .14),
    center=(0, back_y-.08, .09), color=baseboard))
room.include("right baseboard", box((.035, room_depth, .14),
    center=(right_x-.08, 0, .09), color=baseboard))
room.include("left partition", box((.10, 4.9, 2.45),
    center=(-3.05, -2.75, 1.23), color=(.84, .86, .85)))
room.include("partition seam", box((.018, .025, 2.36),
    center=(-2.99, -1.8, 1.22), color=(.68, .70, .69)))
scene.include("architecture", room)

roof = Asset("Suspended ceiling")
roof.include("ceiling surface", box((room_width, room_depth, .08),
    center=(0, 0, room_height+.04), color=ceiling_color))
for i in range(8):
    x = -3.35 + i*.95
    roof.include("lengthwise grid %02d" % i,
        box((.025, room_depth, .022),
            center=(x, 0, room_height-.015), color=grid))
for i in range(14):
    y = -6.3 + i*.95
    roof.include("cross grid %02d" % i,
        box((room_width, .025, .022),
            center=(0, y, room_height-.017), color=grid))
for i, y in enumerate((-1.5, .4, 2.3)):
    roof.include("missing tile %d" % i,
        box((.48, .58, .025), center=(-3.08, y, room_height-.025),
            color=(.15, .17, .16)))
for i, y in enumerate((-2.8, .1, 3.0)):
    roof.include("light panel %d" % i,
        box((.83, .83, .018), center=(-1.95, y, room_height-.03),
            color=(.84, .85, .83)))
roof.include("smoke detector",
    ball(.10, center=(-2.0, -4.15, room_height-.055),
         color=(.79, .80, .77)))
scene.include("ceiling", roof)

board = Asset("Wall mounted whiteboard")
board_y = 3.0
board_z = 1.98
board_length = 3.75
board_height = 1.85
board.include("writing surface", box((.035, board_length, board_height),
    center=(right_x-.085, board_y, board_z), color=(.85, .87, .87)))
for z in (board_z-board_height/2, board_z+board_height/2):
    board.include("frame horizontal %.2f" % z,
        box((.045, board_length+.06, .035),
            center=(right_x-.11, board_y, z), color=metal))
for y in (board_y-board_length/2, board_y+board_length/2):
    board.include("frame end %.2f" % y,
        box((.045, .035, board_height),
            center=(right_x-.11, y, board_z), color=metal))
board.include("center seam", box((.046, .012, board_height),
    center=(right_x-.112, board_y, board_z), color=(.68, .71, .71)))
scene.include("whiteboard", board)

fixtures = Asset("Back wall fixtures")
fixtures.include("vent", box((.70, .035, .32),
    center=(-1.92, back_y-.08, 1.97), color=(.28, .31, .31)))
fixtures.include("electrical recess", box((.30, .035, .41),
    center=(-.48, back_y-.08, 1.72), color=(.24, .27, .26)))
fixtures.include("recess inset", box((.17, .04, .31),
    center=(-.48, back_y-.105, 1.72), color=(.51, .54, .51)))
fixtures.include("dark switch", box((.06, .045, .10),
    center=(-.49, back_y-.13, 1.75), color=(.12, .14, .13)))
cover = box((.40, .035, .36), center=(-.30, back_y-.18, 1.46),
            color=(.47, .50, .48))
cover.turn(axis="+y", degrees=-37)
fixtures.include("hanging panel cover", cover)
for i, x in enumerate((.02, .18, .31)):
    fixtures.include("small control %d" % i, box((.09, .025, .15),
        center=(x, back_y-.075, 1.53), color=(.78, .79, .75)))
scene.include("wall fixtures", fixtures)

flag = Asset("Hanging American flag")
flag_x = .72
flag_top = 3.03
flag_w = .32
flag_h = .70
flag.include("cloth", box((flag_w, .025, flag_h),
    center=(flag_x, back_y-.18, flag_top-flag_h/2),
    color=(.83, .82, .77)))
for i in range(7):
    z = flag_top - (i*2+.5)*flag_h/13
    flag.include("red stripe %d" % i, box((flag_w, .012, flag_h/13),
        center=(flag_x, back_y-.198, z), color=(.57, .12, .13)))
flag.include("blue canton", box((flag_w*.45, .015, flag_h*.40),
    center=(flag_x-flag_w*.275, back_y-.209, flag_top-flag_h*.20),
    color=(.12, .18, .31)))
flag.include("flag pole", rod(.018,
    start=(flag_x-.18, back_y-.20, flag_top+.04),
    end=(flag_x+.23, back_y-.20, flag_top-.16),
    color=(.32, .31, .29)))
flag.include("angled support", rod(.012,
    start=(flag_x+.15, back_y-.15, flag_top-.10),
    end=(right_x-.10, 5.25, 2.86), color=(.20, .20, .18)))
scene.include("flag", flag)

debris = Asset("Scattered floor debris")
def piece(name, center, size, angle, color):
    p = box(size, center=center, color=color)
    p.turn(axis="+z", degrees=angle)
    debris.include(name, p)

piece("foreground dark panel", (-1.8, -1.55, .025),
      (1.15, .43, .035), -10, (.13, .14, .13))
piece("foreground light fragment", (-1.77, -1.50, .052),
      (.69, .21, .012), -8, (.28, .29, .26))
piece("foreground black slat", (-1.3, -1.65, .065),
      (.95, .035, .025), 20, (.10, .11, .10))
piece("left dark panel", (-2.5, -.55, .025),
      (1.08, .47, .032), -8, (.15, .16, .15))
piece("left gray inset", (-2.47, -.55, .05),
      (.74, .20, .012), -8, (.30, .31, .28))
piece("back dark panel", (-1.65, 1.25, .025),
      (1.0, .35, .035), 9, (.13, .14, .13))
piece("back light edge", (-1.64, 1.25, .05),
      (.73, .045, .012), 9, (.36, .37, .34))
piece("long white rail", (-1.45, -.65, .045),
      (1.50, .055, .035), -10, (.69, .72, .70))
piece("small black fragment", (.50, 1.4, .025),
      (.42, .19, .025), 18, (.16, .17, .15))
piece("pale small fragment", (1.30, 1.05, .03),
      (.35, .22, .025), -17, (.46, .45, .39))
scene.include("floor debris", debris)

insulation = Asset("Yellow insulation and floor strips")
for i in range(3):
    slab = box((1.65, .65, .055),
        center=(.85, -.85-i*.24, .06+i*.028),
        color=(.72+i*.025, .62+i*.025, .30+i*.02))
    slab.turn(axis="+z", degrees=-8+i*3)
    insulation.include("folded yellow layer %d" % i, slab)
insulation.include("yellow edge", box((1.28, .12, .045),
    center=(.96, -1.41, .09), color=(.80, .69, .35)))
for i in range(3):
    strip = box((.11, 2.8, .025),
        center=(1.60+i*.23, -3.06, .025), color=(.70, .67, .59))
    strip.turn(axis="+z", degrees=22)
    insulation.include("long floor strip %d" % i, strip)
scene.include("insulation and strips", insulation)

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
sc.world.node_tree.links.new(background.outputs["Background"],
                            output.inputs["Surface"])
background.inputs["Color"].default_value = (.65, .68, .69, 1)
background.inputs["Strength"].default_value = .65

set_view(camera_pos, camera_target, lens=camera_lens, sensor=36)
area_emitter((-2.6, -3.3, 3.0), power=420, size=4.0,
    target=(0, 2, 1.2), color=(.90, .94, 1.0))
area_emitter((0, 3.0, 3.0), power=260, size=3.0,
    target=(0, 2, 0), color=(1.0, .96, .88))
