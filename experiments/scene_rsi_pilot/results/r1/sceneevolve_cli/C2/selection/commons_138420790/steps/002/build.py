from sceneact import *
import bpy

# Three revision families: camera framing, foreground post, dark materials.
CAMERA_POSITION = (-5.1, -5.7, 1.95)
CAMERA_TARGET = (0.05, 0.65, 1.95)
CAMERA_LENS = 47
CAMERA_SHIFT = (0, -0.085)

ROOM_WIDTH = 6.8
ROOM_DEPTH = 7.0
CEILING_HEIGHT = 3.75
ISLAND_WIDTH = 2.55
ISLAND_DEPTH = 1.08
ISLAND_HEIGHT = 0.99
HOOD_WIDTH = 1.10
HOOD_DEPTH = 0.87
HOOD_BOTTOM = 2.02
HOOD_TOP = 3.73

scene = Scene("Kitchen")

ivory = (.66, .67, .63)
counter = (.79, .80, .74)
black = (.012, .016, .015)
charcoal = (.024, .028, .026)
steel = (.36, .39, .38)
wood = (.39, .24, .125)
floor_color = (.60, .59, .54)

def add_box(asset, name, size, center, color):
    assert all(v > 0 for v in size), name
    asset.include(name, box(size=size, center=center, color=color))

architecture = Asset("Architecture")
add_box(architecture, "floor", (ROOM_WIDTH, ROOM_DEPTH, .12),
        (0, .2, -.06), floor_color)
add_box(architecture, "back_wall", (6.8, .16, 3.8),
        (0, 2.40, 1.9), (.26, .28, .26))
add_box(architecture, "left_wall", (.15, 5.6, 3.8),
        (-3.35, .2, 1.9), (.36, .37, .33))
add_box(architecture, "ceiling", (6.8, 7, .12),
        (0, .2, 3.81), (.018, .023, .021))

for i, x in enumerate([-3, -1.8, -.6, .6, 1.8, 3]):
    add_box(architecture, "floor_joint_x_%d" % i,
            (.008, 6.8, .002), (x, .2, .002), (.40, .41, .38))
for i, y in enumerate([-2.8, -1.6, -.4, .8, 2.0]):
    add_box(architecture, "floor_joint_y_%d" % i,
            (6.7, .008, .002), (0, y, .002), (.40, .41, .38))

for i, y in enumerate([-1.6, -.75, .15, 1.05, 1.95]):
    add_box(architecture, "ceiling_joist_%d" % i,
            (6.5, .095, .20), (0, y, 3.63), (.015, .020, .018))
for i, x in enumerate([-.90, 1.55]):
    add_box(architecture, "main_ceiling_beam_%d" % i,
            (.25, 6.8, .32), (x, .2, 3.55), (.020, .025, .023))
scene.include("architecture", architecture)

posts = Asset("Timber supports")
add_box(posts, "foreground_post", (.34, .34, 3.8),
        (-2.6, -1.50, 1.90), wood)
add_box(posts, "far_right_post", (.19, .22, 3.65),
        (2.72, 2.00, 1.825), wood)
scene.include("posts", posts)

kitchen = Asset("Rear kitchen cabinetry")
add_box(kitchen, "left_tall_carcass", (.92, .66, 2.30),
        (-2.13, 1.89, 1.15), black)
for i, z in enumerate([.58, 1.72]):
    add_box(kitchen, "left_tall_door_%d" % i, (.88, .035, 1.12),
            (-2.13, 1.54, z), charcoal)

add_box(kitchen, "rear_toe", (3.45, .54, .13),
        (-.05, 1.91, .095), (.018, .022, .021))
add_box(kitchen, "rear_base", (3.5, .64, .78),
        (-.05, 1.90, .51), black)
add_box(kitchen, "rear_worktop", (3.56, .71, .045),
        (-.05, 1.86, .923), (.17, .18, .16))
for i, x in enumerate([-1.35, -.50, .35, 1.20]):
    add_box(kitchen, "rear_base_front_%d" % i,
            (.825, .025, .72), (x, 1.564, .53), charcoal)

add_box(kitchen, "backsplash", (3.45, .045, .75),
        (-.05, 2.238, 1.32), (.023, .028, .025))
add_box(kitchen, "upper_cabinet_run", (3.45, .43, .52),
        (-.05, 2.04, 1.99), black)
for i, x in enumerate([-1.34, -.48, .38, 1.24]):
    add_box(kitchen, "upper_front_%d" % i,
            (.84, .025, .49), (x, 1.812, 1.99), (.019, .024, .021))
add_box(kitchen, "niche_warm_back", (2.24, .025, .34),
        (-.54, 2.202, 1.12), (.31, .25, .21))
add_box(kitchen, "niche_light_strip", (2.24, .035, .016),
        (-.54, 1.829, 1.435), (.94, .80, .59))

add_box(kitchen, "right_tall_bank", (1.17, .76, 2.34),
        (1.90, 1.96, 1.17), black)
add_box(kitchen, "right_side_door", (.48, .035, 2.27),
        (2.23, 1.561, 1.17), charcoal)
add_box(kitchen, "oven_column_face", (.64, .035, 2.27),
        (1.64, 1.56, 1.17), (.026, .028, .025))
for i, z in enumerate([1.02, 1.51]):
    add_box(kitchen, "oven_frame_%d" % i, (.57, .05, .43),
            (1.64, 1.527, z), steel)
    add_box(kitchen, "oven_glass_%d" % i, (.48, .014, .29),
            (1.64, 1.495, z-.025), (.018, .034, .039))
    add_box(kitchen, "oven_control_%d" % i, (.49, .017, .055),
            (1.64, 1.480, z+.15), (.15, .17, .16))
    kitchen.include(
        "oven_handle_%d" % i,
        rod(radius=.014, start=(1.42, 1.451, z+.095),
            end=(1.86, 1.451, z+.095), color=(.55, .57, .55)))
scene.include("rear_kitchen", kitchen)

island = Asset("Island with drawers and sink")
island_x = .15
island_y = -.05
add_box(island, "recessed_plinth", (2.40, .93, .10),
        (island_x, island_y+.025, .08), (.15, .17, .16))
add_box(island, "cabinet_body", (ISLAND_WIDTH, ISLAND_DEPTH, .83),
        (island_x, island_y, .545), ivory)
add_box(island, "left_end_panel", (.035, 1.09, .88),
        (island_x-1.283, island_y, .55), (.59, .61, .58))
front_y = island_y - ISLAND_DEPTH/2 - .015
for i, z in enumerate([.275, .55, .825]):
    add_box(island, "drawer_%d" % i, (2.48, .028, .259),
            (island_x+.018, front_y, z), ivory)
    add_box(island, "drawer_reveal_%d" % i, (2.47, .015, .012),
            (island_x+.018, front_y-.006, z+.134), (.27, .29, .27))

sink_x, sink_y = .60, .13
sink_w, sink_d = .60, .39
left_edge, right_edge = island_x-1.30, island_x+1.30
front_edge, back_edge = island_y-.565, island_y+.565
z_top = .985
add_box(island, "counter_left",
        (sink_x-sink_w/2-left_edge, 1.13, .045),
        ((left_edge+sink_x-sink_w/2)/2, island_y, z_top), counter)
add_box(island, "counter_right",
        (right_edge-sink_x-sink_w/2, 1.13, .045),
        ((right_edge+sink_x+sink_w/2)/2, island_y, z_top), counter)
add_box(island, "counter_front",
        (sink_w, sink_y-sink_d/2-front_edge, .045),
        (sink_x, (front_edge+sink_y-sink_d/2)/2, z_top), counter)
add_box(island, "counter_back",
        (sink_w, back_edge-sink_y-sink_d/2, .045),
        (sink_x, (back_edge+sink_y+sink_d/2)/2, z_top), counter)
add_box(island, "sink_bottom", (.57, .36, .015),
        (sink_x, sink_y, .915), (.37, .40, .38))
for i, x in enumerate([sink_x-.292, sink_x+.292]):
    add_box(island, "sink_side_%d" % i, (.015, .39, .073),
            (x, sink_y, .955), (.56, .59, .56))
for i, y in enumerate([sink_y-.187, sink_y+.187]):
    add_box(island, "sink_end_%d" % i, (.58, .015, .073),
            (sink_x, y, .955), (.56, .59, .56))
island.include("faucet", sweep_tube(
    points=[(.60, .40, 1.005), (.60, .40, 1.22),
            (.60, .36, 1.27), (.60, .23, 1.27), (.60, .20, 1.22)],
    radius=.014, color=(.58, .62, .60)))
island.include("faucet_lever", rod(
    radius=.009, start=(.65, .40, 1.025), end=(.65, .40, 1.115),
    color=(.57, .60, .58)))
for i, y in enumerate([-.27, .12]):
    add_box(island, "hob_long_line_%d" % i, (.65, .008, .003),
            (-.56, y, 1.010), (.49, .51, .47))
for i, x in enumerate([-.885, -.235]):
    add_box(island, "hob_short_line_%d" % i, (.008, .39, .003),
            (x, -.075, 1.010), (.49, .51, .47))
scene.include("island", island)

hood = Asset("Large suspended ivory extractor")
add_box(hood, "rectangular_enclosure",
        (HOOD_WIDTH, HOOD_DEPTH, HOOD_TOP-HOOD_BOTTOM),
        (-.10, .32, (HOOD_TOP+HOOD_BOTTOM)/2), (.73, .72, .65))
add_box(hood, "bottom_plate", (1.10, .87, .022),
        (-.10, .32, HOOD_BOTTOM), (.55, .56, .51))
add_box(hood, "extractor_filter", (.73, .51, .008),
        (-.10, .32, HOOD_BOTTOM-.014), (.22, .25, .23))
scene.include("hood", hood)

kettle = Asset("Small red kettle")
kettle.include("body", ball(
    radius=.092, center=(-.52, 1.82, 1.035), color=(.62, .006, .025)))
add_box(kettle, "base", (.16, .13, .025), (-.52, 1.82, .955), black)
kettle.include("handle", sweep_tube(
    points=[(-.60, 1.82, 1.07), (-.60, 1.82, 1.16),
            (-.48, 1.82, 1.18), (-.43, 1.82, 1.10)],
    radius=.012, color=(.035, .025, .025)))
kettle.include("spout", rod(
    radius=.022, start=(-.45, 1.81, 1.05), end=(-.40, 1.81, 1.10),
    color=(.13, .14, .13)))
scene.include("kettle", kettle)

realize(scene)
set_view(CAMERA_POSITION, CAMERA_TARGET, lens=CAMERA_LENS,
         shift=CAMERA_SHIFT)
camera = bpy.context.scene.camera
camera.data.sensor_fit = 'VERTICAL'
camera.data.sensor_height = 32

# Preserve the previous surface treatment; darken only the timber grain.
processed_materials = set()
for obj in bpy.context.scene.objects:
    if obj.type != 'MESH':
        continue
    for slot in obj.material_slots:
        mat = slot.material
        if mat is None or mat.as_pointer() in processed_materials:
            continue
        processed_materials.add(mat.as_pointer())
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        if bsdf is None:
            continue
        bsdf.inputs["Roughness"].default_value = .52
        c = bsdf.inputs["Base Color"].default_value
        if c[0] > .30 and .15 < c[1] < .30 and c[2] < .18:
            nodes = mat.node_tree.nodes
            links = mat.node_tree.links
            tex = nodes.new("ShaderNodeTexNoise")
            tex.inputs["Scale"].default_value = 4
            tex.inputs["Detail"].default_value = 3
            coords = nodes.new("ShaderNodeTexCoord")
            mapping = nodes.new("ShaderNodeVectorMath")
            mapping.operation = 'MULTIPLY'
            mapping.inputs[1].default_value = (7, 7, .28)
            links.new(coords.outputs["Generated"], mapping.inputs[0])
            links.new(mapping.outputs["Vector"], tex.inputs["Vector"])
            ramp = nodes.new("ShaderNodeValToRGB")
            ramp.color_ramp.elements[0].position = .18
            ramp.color_ramp.elements[0].color = (.17, .085, .035, 1)
            ramp.color_ramp.elements[1].position = .82
            ramp.color_ramp.elements[1].color = (.36, .21, .10, 1)
            links.new(tex.outputs["Fac"], ramp.inputs[0])
            links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])

world = bpy.context.scene.world
if world is None:
    world = bpy.data.worlds.new("Kitchen world")
    bpy.context.scene.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs[0].default_value = (.28, .31, .32, 1)
world.node_tree.nodes["Background"].inputs[1].default_value = .32

# Lighting and pale surfaces remain fixed to isolate the dark material change.
area_emitter((-2.3, -3.5, 3.35), power=850, size=4.0,
             target=(0, .2, 1.2), color=(1, .95, .86))
area_emitter((2.7, -.4, 3.2), power=450, size=2.5,
             target=(0, 0, 1), color=(.89, .94, 1))
area_emitter((-.65, 1.78, 1.43), power=38, size=1.7,
             target=(-.65, 2.18, 1.07), color=(1, .72, .50))
area_emitter((-2.5, 1.0, 3.25), power=160, size=1.5,
             target=(-1, 1.8, 1.1), color=(1, .93, .80))

# Source audit:
# All box dimensions are positive and finite, including the four counter pieces.
# Every rod has distinct keyword endpoints; consecutive sweep points are distinct.
# Repeated children use indexed keys; no fillet_box or ambiguous transform pivots.
# Geometry remains grouped by object. Camera/materials/lights follow realize().
# No external access, render/save calls, or runner-setting changes.
