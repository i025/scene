from sceneact import *
import bpy
import math
import random

# Observed: convergence and opening x≈.65 agree; cabinet tops remain high, and near panels are too narrow.
# Preserve camera/ceiling; lower shelving tops .13 and restore broader units, moving opening top toward (.65,.08).
# Floor and cabinet faces remain too bright: reduce exposure .7 stop and target only the floor with darker, polished material.

random.seed(9)
scene = Scene("Compact archive aisle")
CAMERA_POSITION = (-.35, -2.0, 1.62)
CAMERA_YAW = math.radians(28)
CAMERA_TARGET = (
    CAMERA_POSITION[0] + 12 * math.sin(CAMERA_YAW),
    CAMERA_POSITION[1] + 12 * math.cos(CAMERA_YAW),
    1.62
)
LENS = 28
CEILING_HEIGHT = 2.85
RIGHT_FACE = 1.20
CABINET_HEIGHT = 2.47
CABINET_DEPTH = 2.50
PANEL_COLOR = (.59, .60, .54)
DARK_METAL = (.045, .058, .047)
SILVER = (.43, .47, .44)

architecture = Asset("Architecture")
architecture.include("archive_floor_surface",
    box((8, 34, .12), center=(1, 12, -.07), color=(.13, .155, .125)))
architecture.include("ceiling",
    box((7, 34, .12), center=(1, 12, CEILING_HEIGHT + .06),
        color=(.69, .70, .66)))
architecture.include("left_wall",
    box((.16, 32, CEILING_HEIGHT),
        center=(-1.36, 12, CEILING_HEIGHT / 2), color=(.66, .67, .60)))
architecture.include("far_wall",
    box((7, .15, CEILING_HEIGHT),
        center=(1, 28, CEILING_HEIGHT / 2), color=(.57, .60, .54)))
for i in range(10):
    architecture.include(f"ceiling_cross_beam_{i}",
        box((5.8, .10, .14), center=(1, -.7 + i * 3.2, CEILING_HEIGHT - .10),
            color=(.60, .62, .57)))
architecture.include("left_ceiling_service",
    box((.12, 32, .15), center=(-1.07, 12, CEILING_HEIGHT - .13),
        color=(.50, .52, .45)))
architecture.include("right_light_raceway",
    box((.10, 31, .07), center=(1.04, 12, CEILING_HEIGHT - .07),
        color=(.73, .74, .67)))
scene.include("architecture", architecture)

def make_closed_unit(index, y0, width):
    a = Asset(f"Mobile archive shelving {index}")
    yc = y0 + width / 2
    a.include(f"unit_{index}_interior",
        box((CABINET_DEPTH, width - .025, CABINET_HEIGHT - .09),
            center=(RIGHT_FACE + CABINET_DEPTH / 2, yc, CABINET_HEIGHT / 2),
            color=(.36, .38, .31)))
    a.include(f"unit_{index}_end_panel",
        box((.065, width, CABINET_HEIGHT),
            center=(RIGHT_FACE, yc, CABINET_HEIGHT / 2 + .035),
            color=PANEL_COLOR))
    a.include(f"unit_{index}_edge",
        box((.025, .016, CABINET_HEIGHT),
            center=(RIGHT_FACE - .040, y0 + .008, CABINET_HEIGHT / 2 + .035),
            color=(.38, .40, .34)))
    a.include(f"unit_{index}_base",
        box((.13, width, .065), center=(RIGHT_FACE - .005, yc, .055),
            color=(.24, .27, .23)))
    a.include(f"unit_{index}_latch_plate",
        box((.018, .040, .095), center=(RIGHT_FACE - .042, yc, 1.12),
            color=SILVER))
    a.include(f"unit_{index}_latch_pull",
        rod(.009, start=(RIGHT_FACE - .064, yc - .012, 1.085),
            end=(RIGHT_FACE - .075, yc - .012, 1.14),
            color=(.24, .28, .26)))
    z = .72
    a.include(f"unit_{index}_wheel",
        rod(.073, start=(RIGHT_FACE - .055, yc, z),
            end=(RIGHT_FACE - .105, yc, z), color=DARK_METAL))
    a.include(f"unit_{index}_hub",
        rod(.023, start=(RIGHT_FACE - .11, yc, z),
            end=(RIGHT_FACE - .14, yc, z), color=SILVER))
    a.include(f"unit_{index}_crank_arm",
        rod(.012, start=(RIGHT_FACE - .145, yc, z),
            end=(RIGHT_FACE - .145, yc - .055, z + .20),
            color=(.19, .22, .19)))
    a.include(f"unit_{index}_crank_grip",
        rod(.018, start=(RIGHT_FACE - .145, yc - .055, z + .20),
            end=(RIGHT_FACE - .145, yc - .20, z + .20), color=DARK_METAL))
    sign_width = min(.32, width * .88)
    a.include(f"unit_{index}_sign_frame",
        box((.028, sign_width, .125),
            center=(RIGHT_FACE - .058, yc, 2.12), color=(.20, .23, .20)))
    a.include(f"unit_{index}_sign_card",
        box((.012, sign_width - .018, .105),
            center=(RIGHT_FACE - .079, yc, 2.12), color=(.80, .81, .76)))
    if index < 12:
        for row in range(2):
            for k in range(4):
                a.include(f"unit_{index}_print_{row}_{k}",
                    box((.006, sign_width * .13, .005),
                        center=(RIGHT_FACE - .088,
                                yc + sign_width * (-.31 + k * .20),
                                2.142 - row * .040),
                        color=(.25, .28, .26)))
    return a

for i, (y, w) in enumerate(((-1.54, .65), (-.86, .66))):
    scene.include(f"near_mobile_{i}", make_closed_unit(i, y, w))

open_y0 = -.20
open_width = .32
exposed = Asset("Exposed book shelving")
exposed.include("exposed_dark_back",
    box((.05, open_width, CABINET_HEIGHT),
        center=(1.83, open_y0 + open_width / 2, CABINET_HEIGHT / 2 + .035),
        color=(.045, .060, .045)))
for side in (0, 1):
    exposed.include(f"exposed_upright_{side}",
        box((.67, .025, CABINET_HEIGHT),
            center=(1.51, open_y0 + side * open_width,
                    CABINET_HEIGHT / 2 + .035),
            color=(.22, .25, .20)))
shelf_heights = (.10, .60, 1.10, 1.60, 2.10, 2.47)
for j, z in enumerate(shelf_heights):
    exposed.include(f"exposed_shelf_{j}",
        box((.68, open_width, .025),
            center=(1.51, open_y0 + open_width / 2, z),
            color=(.32, .34, .28)))
book_colors = [
    (.12, .13, .11), (.31, .105, .035), (.08, .12, .10),
    (.32, .25, .10), (.075, .10, .14), (.38, .29, .16)
]
for level, base in enumerate(shelf_heights[:-1]):
    available_height = shelf_heights[level + 1] - base - .035
    for j in range(4):
        h = min(random.uniform(.33, .46), available_height)
        cy = open_y0 + .045 + j * .071
        exposed.include(f"exposed_book_{level}_{j}",
            box((.39, .059, h), center=(1.44, cy, base + .013 + h / 2),
                color=book_colors[(j + level) % len(book_colors)]))
        if level in (0, 2, 4):
            exposed.include(f"exposed_book_label_{level}_{j}",
                box((.006, .043, .045), center=(1.241, cy, base + .10),
                    color=(.55, .55, .40)))
scene.include("open_book_bay", exposed)

for i in range(27):
    scene.include(f"mobile_{i+2}",
        make_closed_unit(i + 2, .15 + i * .97, .925))

left = Asset("Left wall fixtures")
for i in range(14):
    y = 1.6 + i * 1.77
    left.include(f"left_wall_post_{i}",
        box((.075, .06, CEILING_HEIGHT - .12),
            center=(-1.25, y, CEILING_HEIGHT / 2), color=(.42, .45, .37)))
    left.include(f"left_wall_inset_{i}",
        box((.024, 1.49, 1.57), center=(-1.26, y + .78, 1.52),
            color=(.64, .67, .61)))
for i, y in enumerate((.0, 2.9, 5.8, 10.8, 15.0)):
    left.include(f"left_worktop_{i}",
        box((.58, .74, .065), center=(-1.06, y, .79),
            color=(.25, .27, .20)))
    for k, dy in enumerate((-.27, .27)):
        left.include(f"left_worktop_leg_{i}_{k}",
            box((.045, .045, .75), center=(-.88, y + dy, .39),
                color=(.22, .24, .19)))
for i, y in enumerate((1.3, 4.2, 7.2)):
    left.include(f"left_bin_{i}",
        box((.34, .38, .49), center=(-.95, y, .26),
            color=(.065, .09, .065)))
    left.include(f"left_bin_rim_{i}",
        box((.37, .41, .045), center=(-.95, y, .51),
            color=(.21, .24, .18)))
scene.include("left_furniture", left)

fixtures = Asset("Fluorescent ceiling fixtures")
diffuser_slots = []
for i, y in enumerate((-1.2, 2.0, 5.1, 8.2, 11.3, 14.4, 17.5, 20.6, 23.7)):
    fixtures.include(f"fixture_housing_{i}",
        box((.43, 1.48, .15), center=(-.30, y, CEILING_HEIGHT - .20),
            color=(.65, .68, .65)))
    slot = f"fixture_luminous_diffuser_{i}"
    diffuser_slots.append(slot)
    fixtures.include(slot,
        box((.31, 1.40, .018), center=(-.30, y, CEILING_HEIGHT - .285),
            color=(.94, .97, 1)))
    fixtures.include(f"fixture_end_cap_{i}",
        box((.43, .055, .18), center=(-.30, y - .72, CEILING_HEIGHT - .215),
            color=(.48, .52, .48)))
diffuser_slots.append("right_continuous_light")
fixtures.include("right_continuous_light",
    box((.065, 30, .027), center=(1, 12, CEILING_HEIGHT - .12),
        color=(.94, .97, .91)))
scene.include("ceiling_lighting", fixtures)

exit_sign = Asset("Distant exit sign")
exit_sign.include("exit_back",
    box((.40, .075, .22), center=(-.80, 8.6, 2.27), color=(.78, .79, .68)))
for i in range(4):
    exit_sign.include(f"exit_red_letter_{i}",
        box((.035, .009, .115),
            center=(-.92 + i * .075, 8.556, 2.27), color=(.72, .045, .025)))
scene.include("exit_sign", exit_sign)

realize(scene)
set_view(CAMERA_POSITION, CAMERA_TARGET, lens=LENS, sensor=36)
sc = bpy.context.scene
if sc.world is None:
    sc.world = bpy.data.worlds.new("Ambient")
sc.world.use_nodes = True
sc.world.node_tree.nodes["Background"].inputs["Color"].default_value = (.65, .70, .62, 1)
sc.world.node_tree.nodes["Background"].inputs["Strength"].default_value = .12
for y in (-.9, 2.5, 6, 10, 14, 18, 22):
    area_emitter((-.20, y, CEILING_HEIGHT - .30), power=65, size=1.6,
                 target=(.1, y, 0), color=(.91, .96, 1))
area_emitter((.9, 1, CEILING_HEIGHT - .22), power=35, size=2.5,
             target=(1.2, 3, 1.1), color=(1, .98, .87))

floor_marker = bpy.data.objects.get("archive_floor_surface")
if floor_marker:
    floor_meshes = [o for o in floor_marker.children_recursive if o.type == "MESH"]
    if floor_marker.type == "MESH":
        floor_meshes.append(floor_marker)
    for obj in floor_meshes:
        for slot in obj.material_slots:
            if slot.material:
                mat = slot.material.copy()
                slot.material = mat
                mat.use_nodes = True
                nodes = mat.node_tree.nodes
                links = mat.node_tree.links
                bs = nodes.get("Principled BSDF")
                if bs:
                    bs.inputs["Roughness"].default_value = .23
                    tex = nodes.new("ShaderNodeTexNoise")
                    tex.inputs["Scale"].default_value = 47
                    tex.inputs["Detail"].default_value = 2
                    bump = nodes.new("ShaderNodeBump")
                    bump.inputs["Strength"].default_value = .10
                    bump.inputs["Distance"].default_value = .012
                    links.new(tex.outputs["Fac"], bump.inputs["Height"])
                    links.new(bump.outputs["Normal"], bs.inputs["Normal"])

for marker_name in diffuser_slots:
    marker = bpy.data.objects.get(marker_name)
    if marker:
        meshes = [o for o in marker.children_recursive if o.type == "MESH"]
        if marker.type == "MESH":
            meshes.append(marker)
        for obj in meshes:
            for slot in obj.material_slots:
                if slot.material:
                    mat = slot.material.copy()
                    slot.material = mat
                    mat.use_nodes = True
                    bs = mat.node_tree.nodes.get("Principled BSDF")
                    if bs:
                        bs.inputs["Emission Color"].default_value = (.85, .90, 1, 1)
                        bs.inputs["Emission Strength"].default_value = 3
sc.view_settings.view_transform = "AgX"
sc.view_settings.exposure = -.7
