from sceneact import *
import bpy
import math

# Reference inventory, normalized image coordinates, approximate:
# - Room shell: floor (0, .40)-(1, 1); cream side walls with yellow lower
#   bands, doors and windows on both sides; white ceiling across the top.
# - Desks: dark brown rectangular tops and open-legged frames in rows across
#   (.00, .41)-(.93, .89). Distant desks overlap strongly; exact count uncertain.
# - Stage: far center (.37, .24)-(.68, .43), dark burgundy curtain, pale valance,
#   green side panels, low wooden platform; chalkboard overlaps its lower center.
# - Bags: dark and blue bags on the floor near (.10, .75), (.52, .70),
#   (.67, .77), and (.80, .67); some are partly hidden by desks.
# - Ceiling: several dark three-blade fans, mostly near the upper edge.
# - Side wall details: tall brown doors/shutters, bright window openings,
#   dark wall speakers and small framed pictures. Far details are uncertain.
# - Small books and papers rest on a few desks.
# Estimated expanded primitives: room and stage ~45, desks 24*6=144,
#   fans 5*5=25, doors/windows/pictures ~45, bags/books ~35; total ~294.
# Each box or rod is one mesh; no fillets, Boolean operations, or tube sweeps.

scene = Scene("Classroom")
cream = (0.82, 0.81, 0.65)
ceiling = (0.88, 0.87, 0.80)
yellow = (0.91, 0.67, 0.025)
wood = (0.25, 0.14, 0.075)
wood_light = (0.38, 0.23, 0.12)
wood_edge = (0.15, 0.085, 0.045)
floor_col = (0.62, 0.49, 0.34)
dark = (0.025, 0.035, 0.038)
green = (0.06, 0.25, 0.15)
stage_green = (0.025, 0.29, 0.055)
curtain = (0.105, 0.014, 0.025)
white = (0.91, 0.90, 0.80)

def put(parent, name, size, center, color):
    parent.include(name, box(size=size, center=center, color=color))

# Room axes: camera looks along +Y toward the stage.
room = Asset("architecture")
put(room, "floor", (12, 22, .12), (0, 3, -.07), floor_col)
put(room, "left_cream_wall", (.18, 22, 4.8), (-6, 3, 2.4), cream)
put(room, "right_cream_wall", (.18, 22, 4.8), (6, 3, 2.4), cream)
put(room, "left_yellow_band", (.035, 22, 1.25), (-5.89, 3, .625), yellow)
put(room, "right_yellow_band", (.035, 22, 1.25), (5.89, 3, .625), yellow)
put(room, "ceiling", (12, 22, .12), (0, 3, 4.85), ceiling)
put(room, "far_wall", (12, .16, 4.8), (0, 13.9, 2.4), cream)
# Subtle floor tile seams.
tiles = Asset("floor_tile_lines")
for x in range(-6, 7):
    put(tiles, "lengthwise_%s" % x, (.012, 21.8, .006),
        (x, 3, .001), (0.47, .36, .25))
for y in range(-7, 15):
    put(tiles, "crosswise_%s" % y, (11.9, .012, .006),
        (0, y, .002), (0.50, .39, .28))
room.include("floor_tiles", tiles)
scene.include("room", room)

# Stage opening and curtain assembly.
stage = Asset("stage")
put(stage, "platform", (5.8, 1.45, .32), (0, 12.65, .16), wood_light)
put(stage, "dark_back", (5.65, .10, 2.42), (0, 13.75, 2.15), (0.035, .025, .025))
put(stage, "curtain", (4.45, .08, 2.20), (0, 13.63, 2.25), curtain)
for x in (-2.52, 2.52):
    put(stage, "green_side_%s" % x, (.48, .15, 2.54),
        (x, 13.50, 2.15), stage_green)
put(stage, "valance", (5.0, .18, .31), (0, 13.42, 3.35), (0.78, .75, .61))
for i in range(11):
    put(stage, "valance_fold_%d" % i, (.055, .04, .30),
        (-2.3 + i * .46, 13.31, 3.34), (0.61, .58, .47))
scene.include("stage", stage)

board = Asset("chalkboard")
put(board, "frame", (2.1, .10, 1.15), (0, 12.95, 1.35), (0.68, .69, .60))
put(board, "writing_surface", (1.98, .035, 1.03), (0, 12.88, 1.35), green)
for x in (-.75, .75):
    put(board, "stand_%s" % x, (.045, .045, .7), (x, 12.98, .48), wood_edge)
scene.include("chalkboard", board)

# Tall windows and doors: bright rectangles with wooden frames and open shutters.
walls = Asset("wall_openings")
for side in (-1, 1):
    x = side * 5.86
    inside = x - side * .055
    for j, y in enumerate((-3.6, .1, 3.8, 7.5, 10.8)):
        opening = Asset(("left" if side < 0 else "right") + "_opening_%d" % j)
        put(opening, "bright_opening", (.035, 1.22, 2.85),
            (inside, y, 1.65), (0.91, .90, .73) if side > 0 else (1, .99, .84))
        for dy in (-.64, .64):
            put(opening, "vertical_frame_%s" % dy, (.10, .10, 2.95),
                (inside - side * .04, y + dy, 1.66), wood_light)
        put(opening, "top_frame", (.10, 1.38, .12),
            (inside - side * .04, y, 3.12), wood_light)
        # One brown shutter panel, offset into the room.
        put(opening, "shutter", (.12, .58, 2.45),
            (inside - side * .10, y + .37, 1.40), (0.36, .23, .13))
        walls.include("opening_%s_%d" % (side, j), opening)
    # Wall-mounted dark rectangular speaker.
    speaker = Asset("speaker")
    put(speaker, "cabinet", (.25, .66, .78), (side * 5.70, 5.6, 3.48), dark)
    walls.include("speaker_%s" % side, speaker)
    for j, y in enumerate((1.9, 8.8)):
        picture = Asset("framed_picture")
        put(picture, "frame", (.09, .53, .68), (side * 5.76, y, 3.65), wood_edge)
        put(picture, "picture", (.025, .43, .56),
            (side * 5.70, y, 3.65), (.65, .71, .67))
        walls.include("picture_%s_%d" % (side, j), picture)
scene.include("wall_details", walls)

# Desk dimensions and row spacing are kept explicit for adjustment.
desk_width, desk_depth, desk_height = 1.55, .64, .80
def make_desk(name, x, y):
    d = Asset(name)
    put(d, "top", (desk_width, desk_depth, .10),
        (x, y, desk_height), wood_light)
    for dx in (-.66, .66):
        for dy in (-.23, .23):
            put(d, "leg_%s_%s" % (dx, dy), (.075, .075, .75),
                (x + dx, y + dy, .385), wood)
    put(d, "under_shelf", (1.30, .47, .045),
        (x, y, .47), wood)
    return d

desks = Asset("desk_rows")
for row, y in enumerate((-4.0, -1.7, .6, 2.9, 5.2, 7.5)):
    for col, x in enumerate((-4.35, -1.52, 1.32, 4.15)):
        # The front corners are cropped by the photograph.
        desks.include("desk_%d_%d" % (row, col), make_desk("desk", x, y))
scene.include("desks", desks)

# A few visible papers and books on desks.
books = Asset("books_and_papers")
for i, (x, y, col) in enumerate([
    (-4.40, -1.7, (.68, .47, .27)),
    (-1.55, .6, (.83, .79, .64)),
    (1.30, 5.2, (.60, .29, .28)),
    (4.20, .6, (.73, .42, .38)),
    (-1.50, 5.2, (.80, .79, .72)),
]):
    put(books, "book_%d" % i, (.43, .28, .045), (x, y, .875), col)
scene.include("books", books)

# Backpacks represented by a rounded-looking body, front pocket, and straps.
def backpack(name, x, y, color):
    bag = Asset(name)
    put(bag, "body", (.57, .28, .76), (x, y, .42), color)
    put(bag, "top", (.43, .27, .16), (x, y, .83), color)
    put(bag, "front_pocket", (.40, .08, .35), (x, y - .17, .27),
        tuple(c * .72 for c in color))
    for dx in (-.24, .24):
        put(bag, "strap_%s" % dx, (.045, .05, .59),
            (x + dx, y - .19, .40), dark)
    return bag

bags = Asset("school_bags")
for i, (x, y, color) in enumerate([
    (-3.45, -4.8, (.025, .045, .06)),
    (.95, -2.6, (.025, .035, .045)),
    (2.35, -4.5, (.015, .27, .48)),
    (4.35, -1.2, (.015, .25, .48)),
    (-4.8, -.2, (.16, .23, .075)),
    (-2.2, 1.5, (.015, .20, .34)),
]):
    bags.include("bag_%d" % i, backpack("backpack", x, y, color))
scene.include("bags", bags)

# Three blades per ceiling fan; each blade is a slim rotated box.
fans = Asset("ceiling_fans")
for i, (x, y, scale) in enumerate([
    (-3.5, -3.2, 1.0), (3.4, -2.5, 1.0),
    (-2.5, 4.0, .75), (2.5, 4.6, .75), (0, 10.1, .55)
]):
    fan = Asset("fan")
    fan.include("downrod", rod(.035, start=(x, y, 4.79),
                               end=(x, y, 4.40), color=dark))
    fan.include("hub", ball(.13 * scale, center=(x, y, 4.40), color=wood_edge))
    for j in range(3):
        a = j * 120 + 15
        blade = box((1.28 * scale, .18 * scale, .055),
                    center=(x + .63 * scale, y, 4.40), color=wood_edge)
        blade.turn("+z", a, pivot=(x, y, 4.40))
        fan.include("blade_%d" % j, blade)
    fans.include("fan_%d" % i, fan)
scene.include("fans", fans)

realize(scene)

# The camera is centered in the classroom, slightly above desk height.
set_view((0, -10.4, 2.65), (0, 8.2, 1.75), lens=25, sensor=36)

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
background.inputs["Color"].default_value = (0.82, 0.84, 0.78, 1)
background.inputs["Strength"].default_value = 0.7

area_emitter((0, -1, 4.55), power=1000, size=8, target=(0, 2, 0))
area_emitter((0, 8, 4.55), power=800, size=7, target=(0, 8, 0))
area_emitter((-5.5, 1, 3), power=550, size=5, target=(0, 3, 1))
