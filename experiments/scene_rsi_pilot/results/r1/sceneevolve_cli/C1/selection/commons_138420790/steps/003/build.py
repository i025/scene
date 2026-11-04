from sceneact import *
import bpy
from mathutils import Vector

# Comparison with step 2:
# 1. Rear cabinets and ceiling are much too pale. Assign explicit node
#    materials to realized geometry, preserving the intended dark colors.
# 2. The island is slightly small and leftward. Increase the lens from
#    45 to 48 mm and aim farther left.
# 3. The foreground post is too far left and ends too high; bring it
#    closer and rightward. Extend the hood upward and raise its bottom.

CAMERA_POSITION = (4.10, -6.50, 2.30)
CAMERA_TARGET = (-.82, 0, 1.50)
CAMERA_LENS = 48
ROOM_HEIGHT = 4.05
ISLAND_WIDTH = 1.35
ISLAND_LENGTH = 2.50
ISLAND_Y = -.12
COUNTER_HEIGHT = .92
HOOD_BOTTOM = 1.96
HOOD_TOP = 4.03
POST_CENTER = (.45, -3.50)

scene = Scene("Modern kitchen")
cream = (.54, .56, .53)
counter = (.76, .77, .70)
charcoal = (.035, .042, .039)
black = (.012, .017, .015)
steel = (.36, .39, .38)
box_finishes = []

def add_box(parent, name, size, center, color):
    parent.include(name, box(size=size, center=center, color=color))
    box_finishes.append((tuple(center), tuple(size), tuple(color), name))

room = Asset("Room")
add_box(room, "floor", (12,12,.12), (0,0,-.075), (.58,.57,.53))
add_box(room, "back_wall", (7.5,.16,ROOM_HEIGHT),
        (0,2.05,ROOM_HEIGHT/2), (.22,.24,.22))
add_box(room, "left_wall", (.16,6.5,ROOM_HEIGHT),
        (-2.85,.3,ROOM_HEIGHT/2), (.30,.31,.28))
add_box(room, "ceiling", (9,9,.13),
        (0,0,ROOM_HEIGHT+.065), (.018,.023,.021))
scene.include("room", room)

tiles = Asset("Floor tiling")
for i in range(-6,7):
    for j in range(-7,7):
        v = .006*((i+j)%3)
        add_box(tiles, f"tile_{i}_{j}", (.895,.895,.012),
                (i*.90,j*.90,-.009), (.63+v,.62+v,.57+v))
scene.include("tiles", tiles)

kitchen = Asset("Rear kitchen")
add_box(kitchen, "tall_left", (.77,.68,2.28),
        (-1.91,1.58,1.14), charcoal)
add_box(kitchen, "tall_left_front", (.755,.025,2.24),
        (-1.91,1.225,1.14), (.045,.051,.047))
add_box(kitchen, "left_upper_seam", (.75,.008,.009),
        (-1.91,1.208,1.99), black)
add_box(kitchen, "base_run", (2.25,.63,.83),
        (-.41,1.60,.415), (.024,.030,.026))
add_box(kitchen, "back_counter", (2.30,.70,.045),
        (-.41,1.55,.855), (.12,.13,.115))
for i in range(4):
    add_box(kitchen, f"base_door_{i}", (.54,.022,.75),
            (-1.24+.55*i,1.273,.44), (.033,.039,.035))
add_box(kitchen, "backsplash", (2.33,.035,.67),
        (-.39,1.94,1.22), (.047,.055,.046))
for i in range(5):
    add_box(kitchen, f"backsplash_joint_{i}", (.008,.012,.64),
            (-1.52+i*.49,1.914,1.22), (.020,.026,.021))
add_box(kitchen, "upper_cabinets", (2.40,.48,.69),
        (-.45,1.78,1.91), (.027,.034,.028))
for i in range(4):
    add_box(kitchen, f"upper_panel_{i}", (.59,.025,.675),
            (-1.35+i*.60,1.528,1.91), (.039,.047,.038))
add_box(kitchen, "under_cabinet_light", (2.20,.025,.018),
        (-.42,1.53,1.558), (.90,.76,.59))
add_box(kitchen, "oven_tower", (.76,.71,2.11),
        (1.19,1.64,1.055), (.027,.034,.029))
add_box(kitchen, "oven_tower_side", (.045,.76,2.15),
        (1.59,1.64,1.075), (.037,.044,.037))
for n,z in enumerate((.80,1.39)):
    add_box(kitchen, f"oven_frame_{n}", (.625,.035,.52),
            (1.19,1.265,z), (.19,.21,.20))
    add_box(kitchen, f"oven_glass_{n}", (.535,.018,.35),
            (1.19,1.238,z-.015), (.012,.023,.027))
    add_box(kitchen, f"oven_controls_{n}", (.60,.025,.08),
            (1.19,1.232,z+.215), (.24,.26,.24))
    add_box(kitchen, f"oven_handle_{n}", (.48,.045,.024),
            (1.19,1.20,z+.125), (.43,.45,.42))
add_box(kitchen, "right_tall_dark_panel", (.70,.72,2.35),
        (1.97,1.65,1.175), (.022,.029,.024))
add_box(kitchen, "rear_bulkhead", (4.8,.64,.34),
        (-.25,1.76,2.54), (.24,.26,.24))
scene.include("kitchen", kitchen)

island = Asset("Island")
add_box(island, "body", (ISLAND_WIDTH,ISLAND_LENGTH,.805),
        (0,ISLAND_Y,.4775), cream)
add_box(island, "recessed_plinth",
        (ISLAND_WIDTH-.11,ISLAND_LENGTH-.10,.10),
        (-.015,ISLAND_Y,.065), (.17,.18,.16))
add_box(island, "countertop",
        (ISLAND_WIDTH+.045,ISLAND_LENGTH+.05,.045),
        (0,ISLAND_Y,COUNTER_HEIGHT-.0225), counter)
add_box(island, "plain_end", (ISLAND_WIDTH+.005,.025,.825),
        (0,ISLAND_Y-ISLAND_LENGTH/2-.0125,.4675), (.47,.49,.46))
for i,z in enumerate((.235,.488,.735)):
    add_box(island, f"drawer_{i}", (.024,ISLAND_LENGTH-.045,.232),
            (ISLAND_WIDTH/2+.012,ISLAND_Y+.015,z), (.60,.62,.58))
    add_box(island, f"drawer_reveal_{i}",
            (.012,ISLAND_LENGTH-.04,.014),
            (ISLAND_WIDTH/2+.018,ISLAND_Y+.015,z+.122),
            (.20,.22,.20))
scene.include("island", island)

sink = Asset("Sink and faucet")
add_box(sink, "sink_rim", (.49,.48,.008),
        (.025,.53,.924), (.59,.63,.60))
add_box(sink, "sink_basin", (.435,.425,.009),
        (.025,.53,.929), (.43,.48,.45))
add_box(sink, "sink_inner", (.365,.34,.01),
        (.025,.53,.934), (.54,.58,.54))
sink.include("tap", sweep_tube(
    points=[(-.23,.76,.925),(-.23,.76,1.12),
            (-.23,.74,1.17),(-.23,.67,1.19),
            (-.23,.58,1.19),(-.23,.54,1.16),(-.23,.54,1.10)],
    radius=.013, color=(.63,.67,.65)))
sink.include("tap_base", rod(radius=.025,length=.025,
                             center=(-.23,.76,.937),color=steel))
sink.include("lever", rod(radius=.008,start=(-.20,.76,.95),
                          end=(-.16,.76,1.025),color=steel))
scene.include("sink", sink)

hood = Asset("Extractor")
add_box(hood, "housing", (.88,1.22,HOOD_TOP-HOOD_BOTTOM),
        (-.025,-.08,(HOOD_TOP+HOOD_BOTTOM)/2), (.70,.70,.62))
add_box(hood, "underside", (.855,1.195,.018),
        (-.025,-.08,HOOD_BOTTOM-.009), (.45,.46,.40))
add_box(hood, "filter", (.53,.67,.008),
        (-.025,-.08,HOOD_BOTTOM-.022), (.25,.27,.23))
for i,x in enumerate((-.30,.25)):
    add_box(hood, f"lamp_{i}", (.045,.045,.009),
            (x,-.43,HOOD_BOTTOM-.023), (.88,.86,.71))
scene.include("extractor", hood)

kettle = Asset("Red kettle")
kettle.include("red_body", ball(radius=.098,
                                center=(-.58,1.52,.975),
                                color=(.62,.008,.018)))
add_box(kettle, "black_foot", (.15,.14,.028),
        (-.58,1.52,.891), (.012,.015,.013))
kettle.include("handle", sweep_tube(
    points=[(-.65,1.52,.975),(-.68,1.52,1.06),
            (-.65,1.52,1.10),(-.55,1.52,1.10),(-.52,1.52,1.04)],
    radius=.013,color=(.012,.015,.014)))
add_box(kettle, "lid", (.09,.09,.018),
        (-.58,1.52,1.064), (.018,.021,.019))
scene.include("kettle", kettle)

posts = Asset("Timber structure")
add_box(posts, "foreground_post", (.36,.36,4.50),
        (POST_CENTER[0],POST_CENTER[1],2.25), (.38,.235,.12))
add_box(posts, "right_post", (.15,.16,ROOM_HEIGHT),
        (2.52,1.72,ROOM_HEIGHT/2), (.48,.31,.17))
scene.include("posts", posts)

ceiling = Asset("Exposed ceiling")
for i in range(10):
    add_box(ceiling, f"joist_{i}", (.085,7.5,.18),
            (-3.4+i*.66,.1,ROOM_HEIGHT-.13), (.019,.026,.022))
for i,y in enumerate((-2.1,-.2,1.65)):
    add_box(ceiling, f"cross_beam_{i}", (7.7,.20,.29),
            (0,y,ROOM_HEIGHT-.25), (.027,.035,.030))
add_box(ceiling, "large_beam", (.26,7.6,.31),
        (1.60,.2,ROOM_HEIGHT-.30), (.042,.052,.045))
ceiling.include("service_pipe", rod(
    radius=.027,start=(-2.2,1.15,ROOM_HEIGHT-.35),
    end=(2.7,1.15,ROOM_HEIGHT-.35),color=(.08,.10,.085)))
scene.include("ceiling_structure", ceiling)

realize(scene)
bpy.context.view_layer.update()

# Match recorded boxes using world-space bounds, independent of generated
# mesh names or the material state created by SceneAct.
material_cache = {}
wood_meshes = []
def material_for(color):
    key = tuple(color)
    if key not in material_cache:
        mat = bpy.data.materials.new("Explicit finish")
        mat.diffuse_color = (*color,1)
        mat.use_nodes = True
        shader = mat.node_tree.nodes.get("Principled BSDF")
        shader.inputs["Base Color"].default_value = (*color,1)
        shader.inputs["Roughness"].default_value = .55
        material_cache[key] = mat
    return material_cache[key]

for obj in bpy.data.objects:
    if obj.type != "MESH":
        continue
    corners = [obj.matrix_world @ Vector(v) for v in obj.bound_box]
    lo = Vector(tuple(min(v[k] for v in corners) for k in range(3)))
    hi = Vector(tuple(max(v[k] for v in corners) for k in range(3)))
    center = (lo+hi)/2
    size = hi-lo
    best = None
    best_error = 1e9
    for rec in box_finishes:
        c,s,col,name = rec
        error = sum(abs(center[k]-c[k])+abs(size[k]-s[k]) for k in range(3))
        if error < best_error:
            best_error = error
            best = rec
    if best is not None and best_error < .025:
        obj.data.materials.clear()
        obj.data.materials.append(material_for(best[2]))
        if best[3] in ("foreground_post","right_post"):
            wood_meshes.append(obj)

wood = bpy.data.materials.new("Longitudinal timber")
wood.use_nodes = True
nodes = wood.node_tree.nodes
links = wood.node_tree.links
shader = nodes.get("Principled BSDF")
shader.inputs["Roughness"].default_value = .69
coords = nodes.new("ShaderNodeTexCoord")
mapping = nodes.new("ShaderNodeVectorMath")
mapping.operation = "MULTIPLY"
mapping.inputs[1].default_value = (8,8,.32)
noise = nodes.new("ShaderNodeTexNoise")
noise.inputs["Scale"].default_value = 4
noise.inputs["Detail"].default_value = 3
links.new(coords.outputs["Generated"],mapping.inputs[0])
links.new(mapping.outputs[0],noise.inputs["Vector"])
ramp = nodes.new("ShaderNodeValToRGB")
ramp.color_ramp.elements[0].position = .22
ramp.color_ramp.elements[0].color = (.12,.055,.020,1)
ramp.color_ramp.elements[1].position = .79
ramp.color_ramp.elements[1].color = (.46,.28,.135,1)
links.new(noise.outputs["Fac"],ramp.inputs[0])
links.new(ramp.outputs[0],shader.inputs["Base Color"])
bump = nodes.new("ShaderNodeBump")
bump.inputs["Strength"].default_value = .17
bump.inputs["Distance"].default_value = .009
links.new(noise.outputs["Fac"],bump.inputs["Height"])
links.new(bump.outputs[0],shader.inputs["Normal"])
for obj in wood_meshes:
    obj.data.materials.clear()
    obj.data.materials.append(wood)

set_view(position=CAMERA_POSITION,target=CAMERA_TARGET,
         lens=CAMERA_LENS,sensor=36)

area_emitter((.7,-3.5,3.1),power=480,size=4,
             target=(0,0,.5),color=(1,.96,.87))
area_emitter((-2,-.8,2.8),power=240,size=2.4,
             target=(0,.6,1.1),color=(1,.97,.89))
area_emitter((2.8,.7,2.9),power=180,size=2.2,
             target=(0,0,1),color=(.88,.93,1))
area_emitter((-.5,1.45,1.53),power=32,size=1.4,
             target=(-.5,1.45,.85),color=(1,.76,.56))

blender_scene = bpy.context.scene
if blender_scene.world is None:
    blender_scene.world = bpy.data.worlds.new("World")
blender_scene.world.use_nodes = True
background = blender_scene.world.node_tree.nodes.get("Background")
background.inputs["Color"].default_value = (.23,.25,.23,1)
background.inputs["Strength"].default_value = .18
blender_scene.view_settings.view_transform = "AgX"
