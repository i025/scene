from sceneact import *
import bpy
import math

# Island: image bounds approximately (.33,.55)-(.90,.85).
# Suspended hood: (.42,.05)-(.73,.44), with two large pale faces.
# Foreground timber post: (.16,0)-(.31,.98).
# Rear illuminated niche: (.30,.48)-(.59,.56).
# Oven stack: (.67,.43)-(.79,.58).
# Pale tiled floor fills the bottom quarter; dark exposed ceiling fills the top.

scene = Scene("Modern kitchen showroom")
WHITE = (.71,.72,.69)
BLACK = (.025,.029,.028)
DARK = (.055,.061,.059)
STEEL = (.34,.37,.36)

def add(parent, name, size, center, color):
    parent.include(name, box(size=size, center=center, color=color))

architecture = Asset("Architecture")
add(architecture, "floor", (16,14,.12), (0,0,-.065), (.65,.64,.60))
add(architecture, "rear_wall", (11,.15,4.1), (0,2.2,2.05), (.24,.26,.25))
add(architecture, "left_wall", (.15,8,4.1), (-3.45,1,2.05), (.33,.34,.32))
add(architecture, "dark_ceiling", (13,11,.13), (0,0,3.87), (.028,.034,.033))
# Broad pale band above the dark kitchen cabinetry.
add(architecture, "upper_wall_band", (8,.10,.68), (.2,2.08,2.94), (.37,.39,.37))
for i in range(-4,6):
    add(architecture, f"floor_joint_x_{i}", (.008,12,.002),
        (i*1.15,0,.001), (.44,.44,.41))
for i in range(-4,6):
    add(architecture, f"floor_joint_y_{i}", (14,.008,.002),
        (0,i*1.15,.002), (.44,.44,.41))
# Exposed beams and narrow roof deck ribs.
for i, y in enumerate((-1.5,.2,1.9,3.6)):
    add(architecture, f"ceiling_beam_{i}", (11,.20,.30),
        (0,y,3.66), (.045,.052,.051))
for i in range(10):
    add(architecture, f"deck_rib_{i}", (.035,8,.075),
        (-4+i*.8,.5,3.77), (.075,.083,.080))
add(architecture, "large_overhead_crossbeam", (.30,9,.38),
    (2.25,.2,3.60), (.065,.075,.073))
scene.include("architecture", architecture)

timber = Asset("Timber structural posts")
add(timber, "foreground_oak", (.32,.34,4.1), (-2.04,.02,2.05), (.47,.29,.145))
add(timber, "right_oak", (.18,.23,3.65), (3.48,1.46,1.825), (.54,.36,.21))
scene.include("timber", timber)

rear = Asset("Rear fitted kitchen")
# Full-height dark cabinet at the left.
add(rear, "left_tower_body", (.98,.69,2.45), (-2.45,1.55,1.225), BLACK)
add(rear, "left_tower_door", (.945,.035,2.39), (-2.45,1.185,1.225), (.045,.050,.048))
add(rear, "left_tower_upper_joint", (.96,.012,.008), (-2.45,1.158,2.16), (.015,.019,.018))
# Low rear cupboards and worktop.
add(rear, "base_cabinet", (3.95,.65,.88), (-.02,1.65,.47), (.045,.050,.048))
add(rear, "base_toe", (3.95,.50,.11), (-.02,1.69,.055), (.018,.023,.022))
for i in range(5):
    add(rear, f"rear_door_{i}", (.775,.035,.78),
        (-1.60+i*.79,1.303,.48), (.055,.060,.057))
add(rear, "rear_counter", (4.06,.75,.055), (-.02,1.61,.94), (.16,.17,.15))
# Black wall panels surrounding the warm recessed splashback.
add(rear, "niche_dark_back", (4.12,.06,1.25), (-.06,2.08,1.66), (.035,.040,.037))
add(rear, "niche_warm_panel", (2.94,.035,.40), (-.52,2.025,1.25), (.32,.27,.23))
add(rear, "niche_lower_ledge", (3.05,.24,.035), (-.52,1.93,1.035), (.22,.21,.18))
add(rear, "upper_black_cupboards", (3.95,.42,.56), (-.04,1.88,1.93), (.040,.045,.042))
for i in range(5):
    add(rear, f"upper_panel_joint_{i}", (.009,.016,.55),
        (-1.98+i*.79,1.658,1.93), (.017,.022,.019))
add(rear, "under_cabinet_light", (2.92,.035,.013), (-.53,1.663,1.64), (.95,.73,.46))
# Tall oven housing on the right.
add(rear, "oven_tower", (.94,.77,2.55), (2.47,1.63,1.275), (.037,.043,.041))
add(rear, "oven_lower_door", (.85,.035,.70), (2.47,1.227,.49), (.058,.064,.060))
for i, z in enumerate((1.13,1.66)):
    add(rear, f"oven_frame_{i}", (.81,.055,.49), (2.47,1.213,z), (.27,.29,.28))
    add(rear, f"oven_glass_{i}", (.70,.018,.325), (2.47,1.176,z+.025), (.018,.030,.034))
    add(rear, f"oven_control_{i}", (.76,.022,.072), (2.47,1.169,z+.207), (.16,.18,.18))
    add(rear, f"oven_handle_{i}", (.65,.055,.028), (2.47,1.125,z-.135), (.46,.49,.48))
add(rear, "tower_top_door", (.86,.035,.49), (2.47,1.227,2.22), (.049,.056,.051))
add(rear, "right_dark_wall", (.69,.48,2.76), (3.24,1.79,1.38), (.047,.054,.050))
add(rear, "right_side_reveal", (.07,.76,2.9), (3.61,1.64,1.45), (.12,.14,.13))
scene.include("rear_kitchen", rear)

island = Asset("Island drawers and counter")
add(island, "carcass", (2.34,1.23,.88), (0,-.13,.50), (.53,.55,.53))
add(island, "recessed_plinth", (2.22,1.08,.105), (0,-.10,.075), (.16,.18,.17))
add(island, "left_end_panel", (.075,1.29,.94), (-1.155,-.13,.52), (.60,.62,.60))
add(island, "right_end_panel", (.045,1.25,.91), (1.165,-.13,.51), (.63,.65,.62))
for i, z in enumerate((.252,.537,.817)):
    add(island, f"drawer_front_{i}", (2.26,.045,.267), (.025,-.772,z), (.65,.67,.64))
    add(island, f"drawer_shadow_{i}", (2.26,.025,.015), (.025,-.797,z+.141), (.21,.23,.21))
slab = box((2.43,1.36,.052), center=(0,-.13,1.012), color=(.81,.82,.77))
sink_cut = box((.58,.41,.20), center=(.28,.16,1.015))
island.include("stone_counter", subtract(slab,sink_cut))
add(island, "sink_bottom", (.57,.40,.018), (.28,.16,.925), (.44,.47,.44))
for name, size, center in (
    ("sink_left",(.018,.41,.07),(-.001,.16,.967)),
    ("sink_right",(.018,.41,.07),(.561,.16,.967)),
    ("sink_back",(.58,.018,.07),(.28,.356,.967)),
    ("sink_front",(.58,.018,.07),(.28,-.036,.967))):
    add(island,name,size,center,(.65,.68,.64))
island.include("faucet", sweep_tube(
    points=[(.65,.34,1.04),(.65,.34,1.24),(.64,.32,1.29),
            (.59,.27,1.30),(.48,.25,1.30),(.45,.25,1.26)],
    radius=.013, color=(.53,.57,.55)))
island.include("faucet_base", rod(.032,start=(.65,.34,1.037),end=(.65,.34,1.065),color=STEEL))
scene.include("island", island)

hood = Asset("Large suspended stone extractor")
add(hood, "rectangular_hood", (1.03,.88,1.67), (-.11,.15,2.735), (.72,.72,.65))
add(hood, "underside", (.94,.78,.025), (-.11,.15,1.893), (.44,.45,.40))
add(hood, "underside_filter", (.43,.36,.012), (-.11,.15,1.876), (.21,.23,.21))
add(hood, "small_lower_lip", (.18,.06,.018), (-.35,-.30,1.91), (.52,.54,.49))
scene.include("hood", hood)

accessories = Asset("Counter objects")
# Small red kettle in the rear niche.
accessories.include("kettle_body", ball(.087, center=(-.51,1.68,1.065), color=(.61,.012,.024)))
add(accessories, "kettle_black_foot", (.145,.12,.025), (-.51,1.68,.992), (.02,.024,.023))
accessories.include("kettle_handle", sweep_tube(
    points=[(-.58,1.68,1.08),(-.59,1.68,1.17),(-.54,1.68,1.20),
            (-.46,1.68,1.18),(-.44,1.68,1.09)],
    radius=.014,color=(.025,.028,.025)))
scene.include("accessories", accessories)

realize(scene)

# Materials remain procedural and editable.
def material_for(obj):
    return obj.data.materials[0] if obj.data.materials else None

for obj in bpy.context.scene.objects:
    if obj.type != 'MESH':
        continue
    mat = material_for(obj)
    if mat is None:
        continue
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Roughness"].default_value = .48
    name = obj.name.lower()
    if "oak" in name:
        nt = mat.node_tree
        tex = nt.nodes.new("ShaderNodeTexNoise")
        tex.inputs["Scale"].default_value = 4
        tex.inputs["Detail"].default_value = 3
        coord = nt.nodes.new("ShaderNodeTexCoord")
        mapping = nt.nodes.new("ShaderNodeVectorMath")
        mapping.operation = 'MULTIPLY'
        mapping.inputs[1].default_value = (23,23,.75)
        nt.links.new(coord.outputs["Generated"],mapping.inputs[0])
        nt.links.new(mapping.outputs[0],tex.inputs["Vector"])
        ramp = nt.nodes.new("ShaderNodeValToRGB")
        ramp.color_ramp.elements[0].position=.20
        ramp.color_ramp.elements[0].color=(.18,.085,.032,1)
        ramp.color_ramp.elements[1].position=.80
        ramp.color_ramp.elements[1].color=(.58,.38,.19,1)
        nt.links.new(tex.outputs["Fac"],ramp.inputs[0])
        nt.links.new(ramp.outputs[0],bsdf.inputs["Base Color"])
        bump = nt.nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value=.17
        bump.inputs["Distance"].default_value=.025
        nt.links.new(tex.outputs["Fac"],bump.inputs["Height"])
        nt.links.new(bump.outputs[0],bsdf.inputs["Normal"])
    if "hood" in name or "stone_counter" in name:
        nt=mat.node_tree
        noise=nt.nodes.new("ShaderNodeTexNoise")
        noise.inputs["Scale"].default_value=85
        noise.inputs["Detail"].default_value=2
        bump=nt.nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value=.12
        bump.inputs["Distance"].default_value=.012
        nt.links.new(noise.outputs["Fac"],bump.inputs["Height"])
        nt.links.new(bump.outputs[0],bsdf.inputs["Normal"])
    if "faucet" in name or "oven_handle" in name:
        bsdf.inputs["Metallic"].default_value=.85
        bsdf.inputs["Roughness"].default_value=.22

CAMERA_POSITION = (-6.3,-4.2,2.85)
CAMERA_TARGET = (0,.25,1.92)
set_view(CAMERA_POSITION,CAMERA_TARGET,lens=53)
sc=bpy.context.scene
sc.camera.data.sensor_fit='VERTICAL'
sc.camera.data.sensor_height=32
sc.render.resolution_x=384
sc.render.resolution_y=512
sc.render.resolution_percentage=100
if sc.world is None:
    sc.world=bpy.data.worlds.new("Ambient")
sc.world.use_nodes=True
sc.world.node_tree.nodes["Background"].inputs[0].default_value=(.48,.51,.48,1)
sc.world.node_tree.nodes["Background"].inputs[1].default_value=.23
area_emitter((-3.1,-3.6,3.3),power=1050,size=4.0,target=(0,.2,1.0),color=(1,.94,.83))
area_emitter((1.6,-1.1,3.4),power=650,size=3,target=(0,0,1),color=(.91,.96,1))
area_emitter((-.7,1.60,1.61),power=65,size=1.8,target=(-.7,2.02,1.20),color=(1,.72,.49))
area_emitter((-2.8,1.1,3.1),power=180,size=1.7,target=(-1.7,1.3,1.5),color=(1,.94,.82))
sc.view_settings.view_transform='AgX'
