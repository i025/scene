from sceneact import *
import bpy
import math

# Inventory: pale tiled floor, open dark ceiling and beams; black rear kitchen,
# tall left cupboard, warm recessed worktop, two ovens; pale island, three drawers,
# sink and faucet; suspended rectangular hood; foreground and rear timber posts.
# Near post occludes kitchen; island occludes rear base units; hood occludes wall.
# Dimensions and hidden room extent remain hypotheses in arbitrary metres.
#
# Revision family: camera only.
# Observation (visual estimate): feedback is dominated by a pale foreground wall;
# island and ovens are small and partially obscured, unlike the reference.
# Runtime fact: step 1 completed successfully. No pixel measurements are available.
# Hypothesis: previous camera x=-5.5 lay outside the left wall at x=-3.2.
# Change camera position/target/lens together to view from inside that wall.
# Affected module: camera. Architecture, furniture, fittings, supports and materials
# retain their previous dimensions and positions. Risk: different side-face ratios.
CAMERA = (-2.95, -5.3, 2.55)
TARGET = (0.0, .55, 1.90)
LENS = 38
ISLAND_W, ISLAND_D, COUNTER_Z = 2.35, 1.16, .99
HOOD_BOTTOM, HOOD_TOP = 1.94, 3.93
scene = Scene("Industrial kitchen")

ivory = (.64, .65, .62)
counter = (.77, .78, .73)
black = (.045, .052, .049)
steel = (.29, .31, .30)
wood = (.38, .23, .12)

def slab(parent, key, size, center, color):
    assert all(math.isfinite(v) and v > 0 for v in size)
    return parent.include(key, box(size=size, center=center, color=color))

slab(scene, "floor", (16,15,.12), (0,0,-.06), (.59,.59,.55))
for i in range(-7,8):
    slab(scene, "floor_joint_x_%02d" % (i+7), (.006,15,.0015),
         (i*.95,0,.001), (.36,.36,.33))
for i in range(-6,9):
    slab(scene, "floor_joint_y_%02d" % (i+6), (16,.006,.0015),
         (0,i*.95,.001), (.36,.36,.33))
slab(scene, "rear_plaster", (10,.16,4.4), (0,2.63,2.2), (.36,.38,.35))
slab(scene, "left_plaster", (.16,10,4.4), (-3.2,1,2.2), (.37,.39,.35))
slab(scene, "ceiling_dark_deck", (11,12,.12), (0,0,4.15), (.032,.040,.037))
for i,y in enumerate([-2.2,-.6,1.05,2.7,4.3]):
    slab(scene, "ceiling_crossbeam_%d" % i, (10,.20,.29),
         (0,y,3.94), (.052,.063,.058))
for i,x in enumerate([-3,-1.5,0,1.5,3]):
    slab(scene, "ceiling_joist_%d" % i, (.09,10,.15),
         (x,0,4.025), (.027,.034,.030))
slab(scene, "overhead_main_girder", (.31,11,.38),
     (2,-.5,3.87), (.085,.10,.093))

post = Asset("foreground_timber_post")
slab(post, "solid_post", (.32,.34,4.25), (-2,-1.49,2.125), wood)
scene.include("foreground_timber_post", post)
rearpost = Asset("right_timber_post")
slab(rearpost, "solid_post", (.20,.23,3.9), (2.70,2.20,1.95), (.46,.30,.16))
scene.include("right_timber_post", rearpost)

rear = Asset("rear_work_cabinets")
slab(rear, "base_carcass", (3.35,.66,.88), (-.38,2.10,.48), black)
slab(rear, "worktop", (3.42,.72,.045), (-.38,2.08,.942), (.12,.13,.12))
for i in range(5):
    slab(rear, "base_door_%d" % i, (.655,.025,.79),
         (-1.72+i*.667,1.754,.49), (.058,.067,.060))
slab(rear, "backsplash", (3.47,.055,.40), (-.37,2.43,1.165), (.27,.22,.19))
slab(rear, "upper_black_band", (3.5,.34,.57), (-.37,2.30,1.72), black)
for i in range(5):
    slab(rear, "upper_panel_%d" % i, (.69,.02,.54),
         (-1.76+i*.7,2.117,1.72), (.047,.055,.049))
slab(rear, "niche_light_strip", (3.29,.035,.012),
     (-.40,2.12,1.425), (.92,.74,.52))
scene.include("rear_work_cabinets", rear)

tall = Asset("left_tall_cupboard")
slab(tall, "body", (.78,.76,2.55), (-2.47,2,1.275), (.064,.071,.064))
slab(tall, "front", (.755,.025,2.48), (-2.47,1.608,1.28), (.077,.083,.074))
slab(tall, "upper_door_seam", (.75,.009,.009),
     (-2.47,1.589,2.19), (.024,.028,.024))
scene.include("left_tall_cupboard", tall)

ovens = Asset("oven_tower")
slab(ovens, "surround", (1.05,.74,2.48), (1.73,2.16,1.24), (.043,.048,.044))
slab(ovens, "left_reveal", (.08,.05,2.32), (1.24,1.76,1.25), (.085,.09,.081))
slab(ovens, "right_reveal", (.08,.05,2.32), (2.22,1.76,1.25), (.075,.08,.073))
for i,z in enumerate([.91,1.58]):
    slab(ovens, "oven_frame_%d" % i, (.72,.055,.59), (1.70,1.75,z), steel)
    slab(ovens, "oven_glass_%d" % i, (.63,.018,.39),
         (1.70,1.712,z-.035), (.022,.035,.037))
    slab(ovens, "oven_control_%d" % i, (.67,.018,.085),
         (1.70,1.711,z+.23), (.14,.15,.14))
    slab(ovens, "oven_handle_%d" % i, (.57,.055,.025),
         (1.70,1.666,z+.135), (.45,.47,.44))
slab(ovens, "lower_door", (.89,.03,.55), (1.73,1.77,.30), black)
scene.include("oven_tower", ovens)

kettle = Asset("red_counter_kettle")
kettle.include("red_body", ball(.103, center=(-.65,2.05,1.08), color=(.62,.006,.018)))
slab(kettle, "black_base", (.18,.15,.025), (-.65,2.05,.975), (.014,.018,.016))
slab(kettle, "dark_front", (.115,.025,.09), (-.65,1.958,1.073), (.012,.017,.015))
kettle.include("handle", sweep_tube(
    points=[(-.73,2.08,1.09),(-.74,2.08,1.18),(-.65,2.08,1.205),(-.57,2.08,1.16)],
    radius=.012, color=(.032,.034,.029)))
scene.include("red_counter_kettle", kettle)

island = Asset("island")
slab(island, "recessed_plinth", (ISLAND_W-.12,ISLAND_D-.12,.10),
     (0,-.12,.06), (.20,.21,.19))
slab(island, "cabinet_body", (ISLAND_W,ISLAND_D,.85), (0,-.12,.535), ivory)
slab(island, "left_end_panel", (.035,ISLAND_D,.89),
     (-ISLAND_W/2-.008,-.12,.545), (.57,.59,.56))
for i in range(3):
    slab(island, "drawer_%d" % i, (ISLAND_W-.055,.028,.263),
         (.01,-.12-ISLAND_D/2-.012,.245+i*.277), (.67,.68,.65))
slab(island, "countertop", (ISLAND_W+.025,ISLAND_D+.025,.043),
     (0,-.12,COUNTER_Z-.0215), counter)

sink_x, sink_y = .40, .15
slab(island, "sink_inner_shadow", (.55,.39,.003),
     (sink_x,sink_y,COUNTER_Z+.001), (.40,.43,.40))
slab(island, "sink_bottom", (.49,.33,.005),
     (sink_x,sink_y,COUNTER_Z+.003), (.64,.66,.62))
for key,size,center in [
    ("sink_rim_front",(.58,.018,.009),(sink_x,sink_y-.205,COUNTER_Z+.007)),
    ("sink_rim_back",(.58,.018,.009),(sink_x,sink_y+.205,COUNTER_Z+.007)),
    ("sink_rim_left",(.018,.40,.009),(sink_x-.281,sink_y,COUNTER_Z+.007)),
    ("sink_rim_right",(.018,.40,.009),(sink_x+.281,sink_y,COUNTER_Z+.007))]:
    slab(island, key, size, center, (.70,.72,.68))
island.include("faucet", sweep_tube(
    points=[(.40,.435,.996),(.40,.435,1.16),(.40,.42,1.20),
            (.40,.34,1.215),(.40,.27,1.20),(.40,.26,1.15)],
    radius=.012, color=(.58,.61,.58)))
island.include("tap_lever", rod(radius=.008, start=(.44,.435,1.025),
                              end=(.49,.435,1.09), color=(.56,.59,.56)))
scene.include("island", island)

hood = Asset("suspended_extractor")
slab(hood, "plaster_chimney", (1.26,.94,HOOD_TOP-HOOD_BOTTOM),
     (-.16,.12,(HOOD_TOP+HOOD_BOTTOM)/2), (.75,.75,.69))
slab(hood, "bottom_edge", (1.275,.955,.024),
     (-.16,.12,HOOD_BOTTOM), (.57,.58,.53))
slab(hood, "underside_filter", (.88,.58,.008),
     (-.16,.12,HOOD_BOTTOM-.015), (.22,.24,.21))
scene.include("suspended_extractor", hood)

# Preflight: dimensions checked above; radii positive; curve endpoints distinct.
# Unique child keys preserve repeated panels. All assembly fittings and supports
# belong to their semantic assets. No parent transforms, bindings or cycles.
# Camera is inside the left wall and clear of the foreground post.
realize(scene)

sc = bpy.context.scene
if sc.world is None:
    sc.world = bpy.data.worlds.new("Ambient")
sc.world.use_nodes = True
bg = sc.world.node_tree.nodes.get("Background")
bg.inputs["Color"].default_value = (.40,.43,.40,1)
bg.inputs["Strength"].default_value = .32

woodmat = bpy.data.materials.new("Natural vertical timber grain")
woodmat.use_nodes = True
n = woodmat.node_tree.nodes
l = woodmat.node_tree.links
bs = n.get("Principled BSDF")
bs.inputs["Roughness"].default_value = .69
tex = n.new("ShaderNodeTexNoise")
tex.inputs["Scale"].default_value = 3.5
tex.inputs["Detail"].default_value = 3
coord = n.new("ShaderNodeTexCoord")
mapping = n.new("ShaderNodeVectorMath")
mapping.operation = 'MULTIPLY'
mapping.inputs[1].default_value = (6,6,.24)
l.new(coord.outputs["Generated"], mapping.inputs[0])
l.new(mapping.outputs[0], tex.inputs["Vector"])
ramp = n.new("ShaderNodeValToRGB")
ramp.color_ramp.elements[0].position = .22
ramp.color_ramp.elements[0].color = (.14,.065,.022,1)
ramp.color_ramp.elements[1].position = .80
ramp.color_ramp.elements[1].color = (.55,.34,.17,1)
l.new(tex.outputs["Fac"], ramp.inputs[0])
l.new(ramp.outputs[0], bs.inputs["Base Color"])
bump = n.new("ShaderNodeBump")
bump.inputs["Strength"].default_value = .20
bump.inputs["Distance"].default_value = .018
l.new(tex.outputs["Fac"], bump.inputs["Height"])
l.new(bump.outputs["Normal"], bs.inputs["Normal"])
for obj in bpy.data.objects:
    if obj.type == 'MESH' and ("timber" in obj.name.lower() or "solid_post" in obj.name.lower()):
        obj.data.materials.clear()
        obj.data.materials.append(woodmat)

set_view(CAMERA, TARGET, lens=LENS, sensor=36)
area_emitter((-3.2,-4,3.6), power=1100, size=4.5,
             target=(0,0,1), color=(1,.95,.86))
area_emitter((1.8,-.7,3.6), power=500, size=3,
             target=(0,0,.6), color=(.91,.95,1))
area_emitter((-.5,2.03,1.41), power=45, size=1.9,
             target=(-.5,2.40,1.10), color=(1,.66,.43))
