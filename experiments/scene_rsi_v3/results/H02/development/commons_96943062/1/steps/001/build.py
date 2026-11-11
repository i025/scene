# Reference inventory and approximate normalized image anchors:
# - Dark carpeted floor: foreground lower half, rear boundary from (0.11, .61)
#   to (.52, .59), extending to both lower corners.
# - Beige back wall: roughly (.11, .37) to (.52, .61); right wall meets it
#   near (.52, .36)-(.52, .59) and fills the right side.
# - Suspended white ceiling: upper portion, with grid edges converging toward
#   the back-right corner. Several dark missing tiles appear at the left edge.
# - Whiteboard: right wall, approximately (.59, .25)-(.91, .58), with a thin
#   gray perimeter and a vertical center division.
# - American flag: hangs near the upper back-right corner, around
#   (.45, .32)-(.51, .42); its support angles toward the right wall.
# - Back wall: dark vent at (.15, .44)-(.24, .47), electrical panel and
#   dangling gray cover around (.30, .46)-(.38, .54), small wall controls.
# - Yellow folded insulation or mat on floor at (.56, .68)-(.90, .80);
#   pale strips continue diagonally toward the lower-right edge.
# - Scattered dark broken ceiling pieces and thin rails occupy the lower-left
#   and middle foreground. Left foreground has a bright partial partition.
# Occluded space beyond the left partition and the exact shapes of debris are
# uncertain. Dominant edges converge toward the rear corner; the right wall
# base slopes downward to the right, while ceiling grid lines recede rearward.
# Primitive estimate: architecture 9, ceiling grid and panels 38, whiteboard 5,
# flag 18, back-wall equipment 10, debris and insulation 24: about 104 meshes.

from sceneact import *
import bpy
import math

scene = Scene("Abandoned classroom")

# Major dimensions and camera parameters are kept separate for adjustment.
room_width = 6.8
room_depth = 13.0
room_height = 3.2
back_y = 6.5
right_x = room_width / 2
camera_pos = (-2.45, -6.6, 1.65)
camera_target = (0.0, 5.9, 1.70)
camera_lens = 25

wall = (0.68, 0.67, 0.62)
ceiling = (0.72, 0.74, 0.73)
grid = (0.47, 0.49, 0.48)
carpet = (0.105, 0.11, 0.105)
baseboard = (0.085, 0.09, 0.085)
metal = (0.36, 0.38, 0.37)
white = (0.80, 0.82, 0.81)

architecture = Asset("Room architecture")
architecture.include("carpet floor", box((room_width, room_depth, .12),
    center=(0, 0, -.06), color=carpet))
architecture.include("back wall", box((room_width, .12, room_height),
    center=(0, back_y, room_height/2), color=wall))
architecture.include("right wall", box((.12, room_depth, room_height),
    center=(right_x, 0, room_height/2), color=(.72, .71, .67)))
architecture.include("back baseboard", box((room_width, .035, .14),
    center=(0, back_y-.08, .09), color=baseboard))
architecture.include("right baseboard", box((.035, room_depth, .14),
    center=(right_x-.08, 0, .09), color=baseboard))
# Bright partition cropped by the left edge of the photograph.
architecture.include("left partition", box((.10, 4.1, 2.45),
    center=(-3.25, -3.15, 1.23), color=(.84,.86,.85)))
architecture.include("partition vertical seam", box((.018,.025,2.36),
    center=(-3.19,-1.85,1.22), color=(.68,.70,.69)))
scene.include("architecture", architecture)

# Ceiling plane with a regular suspended grid. Dark openings along the left
# edge represent missing tiles.
roof = Asset("Suspended ceiling")
roof.include("ceiling surface", box((room_width, room_depth, .08),
    center=(0, 0, room_height+.04), color=ceiling))
for i in range(8):
    x = -3.35 + i * .95
    roof.include("long grid %02d" % i,
        box((.025, room_depth, .022), center=(x,0,room_height-.015), color=grid))
for i in range(14):
    y = -6.3 + i * .95
    roof.include("cross grid %02d" % i,
        box((room_width,.025,.022), center=(0,y,room_height-.017), color=grid))
for i, y in enumerate((-3.9,-2.0,-.1,1.8)):
    roof.include("missing tile %d" % i,
        box((.55,.65,.025), center=(-3.0,y,room_height-.025), color=(.12,.15,.15)))
# A few light ceiling panels and a smoke detector.
for i, y in enumerate((-2.8, .1, 3.0)):
    roof.include("light panel %d" % i,
        box((.83,.83,.018), center=(-1.95,y,room_height-.03), color=(.86,.87,.84)))
roof.include("smoke detector", ball(.10, center=(-2.0,-4.15,room_height-.055),
                                    color=(.79,.80,.77)))
scene.include("ceiling", roof)

board = Asset("Wall mounted whiteboard")
board_y = 2.85
board_z = 1.91
board_length = 3.35
board_height = 1.38
board.include("white writing surface", box((.035,board_length,board_height),
    center=(right_x-.085,board_y,board_z), color=(.85,.87,.87)))
for z in (board_z-board_height/2, board_z+board_height/2):
    board.include("horizontal frame %.2f" % z,
        box((.045,board_length+.06,.035), center=(right_x-.11,board_y,z), color=metal))
for y in (board_y-board_length/2, board_y+board_length/2):
    board.include("end frame %.2f" % y,
        box((.045,.035,board_height), center=(right_x-.11,y,board_z), color=metal))
board.include("center seam", box((.046,.012,board_height),
    center=(right_x-.112,board_y,board_z), color=(.68,.71,.71)))
scene.include("whiteboard", board)

equipment = Asset("Back wall fixtures")
equipment.include("vent", box((.70,.035,.32), center=(-1.92,back_y-.08,1.97),
    color=(.28,.31,.31)))
equipment.include("electrical recess", box((.30,.035,.41),
    center=(-.48,back_y-.08,1.72), color=(.24,.27,.26)))
equipment.include("recess inset", box((.17,.04,.31),
    center=(-.48,back_y-.105,1.72), color=(.51,.54,.51)))
equipment.include("dark switch", box((.06,.045,.10),
    center=(-.49,back_y-.13,1.75), color=(.12,.14,.13)))
cover = box((.40,.035,.36), center=(-.30,back_y-.18,1.46), color=(.47,.50,.48))
cover.turn(axis="+y", degrees=-37)
equipment.include("hanging panel cover", cover)
for i, x in enumerate((.02,.18,.31)):
    equipment.include("small control %d" % i, box((.09,.025,.15),
        center=(x,back_y-.075,1.53), color=(.78,.79,.75)))
scene.include("back wall fixtures", equipment)

flag = Asset("Hanging American flag")
# Flat cloth on the back wall, with stripes and a blue canton.
flag_x = .72
flag_top = 3.03
flag_w = .32
flag_h = .70
flag.include("cloth", box((flag_w,.025,flag_h),
    center=(flag_x,back_y-.18,flag_top-flag_h/2), color=(.83,.82,.77)))
for i in range(7):
    z = flag_top - (i*2+.5)*flag_h/13
    flag.include("red stripe %d" % i, box((flag_w,.012,flag_h/13),
        center=(flag_x,back_y-.198,z), color=(.57,.12,.13)))
flag.include("blue canton", box((flag_w*.45,.015,flag_h*.40),
    center=(flag_x-flag_w*.275,back_y-.209,flag_top-flag_h*.20),
    color=(.12,.18,.31)))
flag.include("flag pole", rod(.018, start=(flag_x-.18,back_y-.20,flag_top+.04),
    end=(flag_x+.23,back_y-.20,flag_top-.16), color=(.32,.31,.29)))
flag.include("angled support", rod(.012, start=(flag_x+.15,back_y-.15,flag_top-.10),
    end=(right_x-.10,5.25,2.86), color=(.20,.20,.18)))
scene.include("flag", flag)

# Broken panels and metal rails on the carpet. Each is an editable part.
debris = Asset("Scattered floor debris")
def flat_piece(name, center, size, angle, color):
    p = box(size, center=center, color=color)
    p.turn(axis="+z", degrees=angle)
    debris.include(name, p)

flat_piece("foreground dark panel", (-1.45,-3.30,.025), (1.48,.56,.035), -10, (.17,.18,.17))
flat_piece("foreground light fragment", (-1.42,-3.23,.052), (.89,.28,.012), -8, (.33,.34,.31))
flat_piece("foreground black slat", (-.82,-3.45,.065), (1.22,.035,.025), 20, (.13,.14,.13))
flat_piece("left dark panel", (-2.5,-1.95,.025), (1.08,.47,.032), -8, (.19,.20,.19))
flat_piece("left gray inset", (-2.47,-1.95,.05), (.74,.20,.012), -8, (.36,.37,.34))
flat_piece("back dark panel", (-1.65,.02,.025), (1.0,.35,.035), 9, (.16,.17,.16))
flat_piece("back light edge", (-1.64,.02,.05), (.73,.045,.012), 9, (.41,.42,.39))
flat_piece("long white rail", (-1.1,-2.32,.045), (1.68,.055,.035), -10, (.69,.72,.70))
flat_piece("small black fragment", (.50,.45,.025), (.42,.19,.025), 18, (.19,.20,.18))
flat_piece("pale small fragment", (1.30,.05,.03), (.35,.22,.025), -17, (.56,.55,.47))
scene.include("floor debris", debris)

insulation = Asset("Yellow insulation and floor strips")
# The slightly overlapping slabs make the folded, low pile.
flat_piece_dummy = None
for i in range(3):
    slab = box((1.65,.65,.055), center=(1.92, -1.07-i*.24, .06+i*.028),
               color=(.72+i*.025,.62+i*.025,.30+i*.02))
    slab.turn(axis="+z", degrees=-8+i*3)
    insulation.include("folded yellow layer %d" % i, slab)
insulation.include("yellow edge", box((1.28,.12,.045),
    center=(2.03,-1.63,.09), color=(.80,.69,.35)))
for i in range(3):
    strip = box((.11,2.8,.025), center=(2.65+i*.23,-3.28,.025),
                color=(.70,.67,.59))
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
sc.world.node_tree.links.new(background.outputs["Background"], output.inputs["Surface"])
background.inputs["Color"].default_value = (0.65, 0.68, 0.69, 1)
background.inputs["Strength"].default_value = 0.65

set_view(camera_pos, camera_target, lens=camera_lens, sensor=36)
area_emitter((-2.6,-3.3,3.0), power=420, size=4.0,
             target=(0,2,1.2), color=(.90,.94,1.0))
area_emitter((0,3.0,3.0), power=260, size=3.0,
             target=(0,2,0), color=(1.0,.96,.88))
