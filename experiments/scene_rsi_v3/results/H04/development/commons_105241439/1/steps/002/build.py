import bpy
import math
import random
from mathutils import Vector
from sceneact import *

# Reference inventory and observed comparison, normalized image coordinates:
# Cream wall fills the upper image; blue wall begins at y=.61 in the reference,
# versus approximately .63 in the render. A thin floor strip is visible at .93.
# Board reference x=.11–.895, y=.28–.68; render x=.10–.90, y=.29–.70.
# Its two panels meet at x=.50. The reference is much darker, with dense,
# broad chalk wiping; the render is pale with isolated raised-looking lines.
# Notice reference x=.46–.61, y=.06–.23; render about x=.46–.60, y=.07–.24.
# Rear desk reference x=.19–.60, y=.79–.85; render x=.115–.60, y=.85–.91.
# Its chair back reference x=.29–.38, y=.73–.80; render x=.22–.34, y=.75–.84.
# Foreground desks reference occupy x=.09–.59 and .75–1 at y=.89–.96;
# the render crops almost all of both below the image. Foreground chair backs
# overlap their front edges and are cropped at the bottom. Construction hidden
# by the desks and outside the image remains uncertain.
# Dominant board, wall and desk edges are nearly horizontal; vertical board
# edges and legs are nearly upright. The front desks overlap the rear legs.
#
# Largest corrections: (1) darken and texture the board using procedural
# surface shading; replace conspicuous raised chalk arcs with diffuse streaks.
# (2) Raise the foreground tabletops and chair backs into view, and move those
# desks slightly farther from the camera, producing the reference crops.
# (3) Raise and narrow the rear desktop, and shift its left edge right; move
# its chair right. (4) Raise the blue wall boundary slightly. The board and
# notice already align fairly well, so camera parameters are unchanged.
# These are asset changes, not camera changes: board and notice projections
# should stay fixed, while furniture contours move upward and inward.
#
# Estimated primitive meshes: architecture 4, board 4, notice 17, furniture
# approximately 36, chalk accents 32: about 93 total. Procedural texture
# nodes add no meshes.

random.seed(19)
BOARD_WIDTH = 5.40
BOARD_HEIGHT = 1.80
BOARD_BOTTOM = 1.28
BOARD_Y = -.035
BLUE_HEIGHT = 1.62
CAMERA_POSITION = (0.0, -8.0, 2.13)
CAMERA_TARGET = (0.0, 0.0, 2.13)
CAMERA_LENS = 42.3

scene = Scene("Classroom")
cream = (.79, .78, .72)
blue = (.009, .055, .24)
wood = (.60, .30, .10)
wood_light = (.90, .65, .33)
wood_edge = (.72, .36, .10)
metal = (.42, .44, .42)

architecture = Asset("architecture")
architecture.include("cream_wall", box((9, .10, 5), center=(0, .08, 2.5), color=cream))
architecture.include("blue_lower_wall", box((9, .026, BLUE_HEIGHT),
    center=(0, .012, BLUE_HEIGHT/2), color=blue))
architecture.include("floor", box((9, 8, .08), center=(0, -3.9, -.045),
    color=(.60, .43, .31)))
architecture.include("baseboard", box((9, .045, .055), center=(0, -.025, .035),
    color=(.78, .72, .61)))
scene.include("architecture", architecture)

board = Asset("chalkboard")
board.include("left_green_panel", box((2.7, .075, 1.8),
    center=(-1.35, BOARD_Y, 2.18), color=(.035, .11, .055)))
board.include("right_green_panel", box((2.7, .075, 1.8),
    center=(1.35, BOARD_Y, 2.18), color=(.025, .085, .042)))
board.include("center_joint", box((.022, .025, 1.8),
    center=(0, -.085, 2.18), color=(.12, .15, .10)))
board.include("bottom_edge", box((5.4, .036, .022),
    center=(0, -.083, 1.28), color=(.32, .36, .28)))

# Restrained thin chalk flecks lie flush with the board. Most chalk residue is
# represented in the board's procedural surface rather than raised geometry.
chalk = Asset("chalk_accents")
for i in range(32):
    x = random.uniform(-2.62, 2.62)
    z = random.uniform(1.34, 2.99)
    h = random.uniform(.025, .20)
    chalk.include("fleck_%02d" % i, box(
        (random.uniform(.004, .012), .002, h),
        center=(x, -.074, z), color=random.choice([
            (.18, .27, .18), (.26, .34, .24), (.34, .41, .30)])))
board.include("chalk_accents", chalk)
scene.include("chalkboard", board)

notice = Asset("hanging_notice")
notice.include("sheet", box((.96, .018, .75), center=(.20, -.045, 3.69),
    color=(.83, .81, .75)))
notice.include("top_edge", box((.96, .012, .012), center=(.20, -.060, 4.065),
    color=(.67, .64, .57)))
notice.include("left_string", rod(.004, start=(-.27, -.052, 4.06),
    end=(.20, -.052, 4.42), color=(.60, .58, .51)))
notice.include("right_string", rod(.004, start=(.67, -.052, 4.06),
    end=(.20, -.052, 4.42), color=(.60, .58, .51)))
for i in range(10):
    notice.include("printed_row_%02d" % i, box(
        (random.uniform(.42, .78), .004, .006),
        center=(.20 + random.uniform(-.06, .06), -.058, 3.43+i*.057),
        color=(.50, .49, .45)))
notice.include("wall_hook", ball(.052, center=(-.46, -.055, 3.89),
    color=(.09, .09, .075)))
scene.include("notice", notice)

def add_desk(name, x, y, width, depth, top_z):
    desk = Asset(name)
    desk.include("wooden_top", box((width, depth, .065),
        center=(x, y, top_z), color=wood_light))
    desk.include("front_wood_edge", box((width, .025, .06),
        center=(x, y-depth/2-.012, top_z-.008), color=wood_edge))
    for side in (-1, 1):
        for fore in (-1, 1):
            lx = x + side*(width/2-.13)
            ly = y + fore*(depth/2-.10)
            desk.include("leg_%s_%s" % (side, fore), rod(.026,
                start=(lx, ly, .025), end=(lx, ly, top_z-.04), color=metal))
    desk.include("under_top_bar", rod(.018,
        start=(x-width/2+.10, y, top_z-.13),
        end=(x+width/2-.10, y, top_z-.13), color=metal))
    scene.include(name, desk)

def add_chair(name, x, y, width, back_bottom, back_top):
    chair = Asset(name)
    chair.include("plywood_back", box((width, .055, back_top-back_bottom),
        center=(x, y, (back_bottom+back_top)/2), color=wood))
    chair.include("back_top_edge", box((width, .06, .025),
        center=(x, y, back_top), color=(.84, .59, .31)))
    for side in (-1, 1):
        xx = x + side*(width/2-.05)
        chair.include("back_support_%s" % side, rod(.018,
            start=(xx, y+.025, .18), end=(xx, y+.025, back_top-.03),
            color=metal))
    chair.include("seat", box((width, .42, .045),
        center=(x, y-.16, .47), color=wood_light))
    scene.include(name, chair)

add_chair("rear_chair", -.99, -1.42, .57, 1.00, 1.25)
add_desk("rear_desk", -.65, -1.72, 2.03, .54, 1.06)
add_desk("foreground_left_desk", -.78, -2.85, 2.55, .62, 1.03)
add_chair("foreground_left_chair", -1.48, -3.22, .70, .58, 1.00)
add_desk("foreground_right_desk", 2.45, -2.85, 1.75, .59, 1.03)
add_chair("foreground_right_chair", 2.22, -3.20, .73, .56, .98)

realize(scene)
sc = bpy.context.scene
sc.render.resolution_x = 512
sc.render.resolution_y = 337
sc.render.resolution_percentage = 100
set_view(CAMERA_POSITION, CAMERA_TARGET, lens=CAMERA_LENS, sensor=36)

# Give each board panel an editable procedural material. Generated coordinates
# are scaled anisotropically to create irregular vertical wipe streaks.
def make_board_material(name, left):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    bsdf = nodes.get("Principled BSDF")
    bsdf.inputs["Roughness"].default_value = .92
    tex = nodes.new("ShaderNodeTexCoord")
    mapping = nodes.new("ShaderNodeVectorMath")
    mapping.operation = 'MULTIPLY'
    mapping.inputs[1].default_value = (26.0, 1.0, 1.5 if left else .65)
    links.new(tex.outputs["Generated"], mapping.inputs[0])
    noise = nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 3.0
    noise.inputs["Detail"].default_value = 3.0
    noise.inputs["Roughness"].default_value = .7
    links.new(mapping.outputs[0], noise.inputs["Vector"])
    ramp = nodes.new("ShaderNodeValToRGB")
    if left:
        ramp.color_ramp.elements[0].position = .22
        ramp.color_ramp.elements[0].color = (.012, .052, .023, 1)
        ramp.color_ramp.elements[1].position = .78
        ramp.color_ramp.elements[1].color = (.19, .27, .17, 1)
    else:
        ramp.color_ramp.elements[0].position = .23
        ramp.color_ramp.elements[0].color = (.009, .038, .016, 1)
        ramp.color_ramp.elements[1].position = .80
        ramp.color_ramp.elements[1].color = (.12, .19, .105, 1)
    links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
    links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
    return mat

left_mat = make_board_material("Left board chalk and worn surface", True)
right_mat = make_board_material("Right board vertical wiped surface", False)
for obj in bpy.context.scene.objects:
    if obj.type == 'MESH':
        d = obj.dimensions
        if abs(d.x-2.7) < .03 and abs(d.z-1.8) < .03 and d.y < .12:
            obj.data.materials.clear()
            obj.data.materials.append(left_mat if obj.location.x < 0 else right_mat)

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
background.inputs["Color"].default_value = (.78, .79, .76, 1)
background.inputs["Strength"].default_value = .8
area_emitter((-3, -4, 6), power=850, size=5,
    target=(0, 0, 1.5), color=(1.0, .94, .84))
area_emitter((4, -2, 5), power=350, size=4,
    target=(0, 0, 1.5), color=(.86, .91, 1.0))

# Same camera as the successful first render; no trial camera change is made.
# Reference observations and computed projections are separate quantities.
landmarks = [
    ("board upper left", (-2.70, -.075, 3.08), (.11, .28)),
    ("board lower right", (2.70, -.075, 1.28), (.895, .68)),
    ("rear desk left top", (-1.665, -1.99, 1.0925), (.19, .79)),
    ("foreground left edge", (-2.055, -3.16, 1.0625), (.09, .89)),
]
bpy.context.view_layer.update()
cam = sc.camera
dg = bpy.context.evaluated_depsgraph_get()
projection = cam.calc_matrix_camera(dg, x=sc.render.resolution_x,
    y=sc.render.resolution_y, scale_x=sc.render.pixel_aspect_x,
    scale_y=sc.render.pixel_aspect_y)
print("Landmark                      reference       projected")
for name, point, reference in landmarks:
    clip = projection @ cam.matrix_world.inverted() @ Vector((*point, 1.0))
    uv = None if clip.w <= 1e-8 else (
        .5*(clip.x/clip.w+1), .5*(1-clip.y/clip.w))
    print("%-28s %s %s" % (name, reference,
        None if uv is None else tuple(round(v, 3) for v in uv)))
