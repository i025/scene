from sceneact import *
import bpy
import math

# Reference inventory, approximate normalized image bounds:
# rear slatted walnut wall (0,.11)-(.46,.76), white door (.31,.29)-(.45,.77),
# dark low bench with white drawer (0,.65)-(.20,.81), pale tiled floor below .76.
# Stone counter (.36,.59)-(1,1), dark inset sink (.46,.63)-(.62,.72),
# black four-ring hob (.40,.76)-(.82,1), glossy ivory backsplash (.57,.28)-(1,1).
# Upper walnut cabinets (.46,0)-(1,.44): broad rear end, long wooden fronts,
# silver hood underside, warm narrow light strip. Small switches and sockets.
# Rear cabinet extremities and sink plumbing are occluded and remain unspecified.
#
# Review of first rendering: rear door/bench placement was close. Counter edge
# diverged too far left; overhead cabinetry was excessively deep and filled the
# ceiling region with its underside. Sink was too distant; lighting washed out
# the wood and stone. This revision corrects those supported discrepancies.
#
# Expanded primitive estimate: architecture and tile joints 30; slats 45;
# door 10; bench 7; counter including cutter 7; sink 16; hob 86;
# cabinet and hood 16; electrical 5. Approximately 222 primitive meshes.
# No fillet expansions or dense nested decoration.

scene = Scene("Walnut kitchen revised")
WOOD = (.115,.044,.016)
SLAT = (.285,.118,.042)
STONE = (.62,.58,.49)
WALL = (.76,.75,.69)
DARK = (.012,.015,.014)
METAL = (.32,.33,.30)

def add(parent, name, size, center, color):
    parent.include(name, box(size=size, center=center, color=color))

architecture = Asset("Architecture and tiled floor")
add(architecture,"floor",(8,10,.10),(-.5,0,-.055),(.52,.49,.43))
add(architecture,"rear_wall",(6,.12,3.3),(-1.4,3.08,1.65),(.065,.033,.015))
add(architecture,"right_glossy_wall",(.12,9,3.3),(1.56,-.6,1.65),WALL)
add(architecture,"ceiling",(8,9,.10),(-1.6,-.6,3.03),(.82,.81,.76))
add(architecture,"rear_baseboard",(4,.035,.05),(-1.7,2.995,.025),(.66,.62,.54))
for i in range(12):
    y=-3.6+i*.60
    add(architecture,"horizontal_tile_joint_%02d"%i,(7,.009,.002),(-1.5,y,.001),(.37,.35,.30))
for i in range(5):
    x=-3.2+i*.85
    add(architecture,"long_tile_joint_%02d"%i,(.008,8,.002),(x,-.5,.001),(.39,.37,.32))
scene.include("architecture",architecture)

slats=Asset("Rear walnut slatted wall")
for i in range(45):
    add(slats,"vertical_slat_%02d"%i,(.049,.050,2.86),
        (-3.20+i*.079,2.979,1.45),SLAT)
scene.include("wood_wall",slats)

door=Asset("White framed interior door")
add(door,"opening_shadow",(1.01,.055,2.24),(-.26,2.931,1.12),(.15,.13,.10))
add(door,"white_leaf",(.825,.045,2.085),(-.26,2.878,1.047),(.76,.78,.75))
for label,x in [("left",-.72),("right",.20)]:
    add(door,label+"_jamb",(.058,.074,2.22),(x,2.85,1.11),(.86,.87,.83))
add(door,"top_frame",(.98,.074,.065),(-.26,2.85,2.19),(.86,.87,.83))
add(door,"leaf_reveal",(.009,.009,2.05),(.155,2.85,1.06),(.41,.42,.39))
add(door,"handle_backplate",(.029,.015,.11),(-.57,2.84,1.025),METAL)
door.include("handle_spindle",rod(.016,start=(-.57,2.845,1.055),end=(-.57,2.80,1.055),color=METAL))
door.include("silver_lever",rod(.012,start=(-.57,2.80,1.055),end=(-.46,2.80,1.055),color=METAL))
add(door,"keyhole",(.012,.008,.025),(-.57,2.827,.985),(.08,.08,.07))
scene.include("door",door)

bench=Asset("Low black bench with white drawer")
bx=-2.18
add(bench,"dark_case",(1.43,.48,.44),(bx,2.70,.24),(.019,.022,.020))
add(bench,"white_drawer",(1.30,.024,.285),(bx,2.443,.225),(.80,.82,.79))
for label,x in [("left",bx-.695),("right",bx+.695)]:
    add(bench,label+"_front_edge",(.035,.035,.40),(x,2.425,.24),DARK)
add(bench,"dark_top",(1.45,.50,.045),(bx,2.69,.473),(.065,.043,.022))
add(bench,"drawer_gap",(1.31,.027,.023),(bx,2.426,.389),DARK)
add(bench,"recessed_plinth",(1.30,.39,.045),(bx,2.73,.025),DARK)
scene.include("bench",bench)

counter=Asset("Stone counter and lower cupboards")
add(counter,"lower_cupboard_mass",(1.19,6.4,.83),(.91,-.17,.425),(.36,.30,.22))
add(counter,"cupboard_front",(.025,6.35,.77),(.304,-.17,.44),(.51,.46,.37))
sink_x,sink_y=.82,.85
slab=box((1.24,6.45,.052),center=(.91,-.18,.896),color=STONE)
cut=box((.66,.64,.20),center=(sink_x,sink_y,.89),color=STONE)
counter.include("stone_slab_with_opening",subtract(slab,cut))
add(counter,"front_stone_edge",(.035,6.45,.055),(.289,-.18,.889),STONE)
add(counter,"wall_upstand",(.03,6.4,.035),(1.49,-.17,.925),STONE)
scene.include("counter",counter)

sink=Asset("Dark inset sink with narrow ribbed drainer")
add(sink,"basin_bottom",(.62,.60,.025),(sink_x,sink_y,.757),(.018,.022,.018))
for label,x in [("left",sink_x-.32),("right",sink_x+.32)]:
    add(sink,label+"_interior_wall",(.022,.63,.14),(x,sink_y,.826),(.038,.043,.032))
for label,y in [("near",sink_y-.31),("far",sink_y+.31)]:
    add(sink,label+"_interior_wall",(.66,.022,.14),(sink_x,y,.826),(.038,.043,.032))
for label,x in [("left",sink_x-.35),("right",sink_x+.35)]:
    add(sink,label+"_rim",(.025,.69,.012),(x,sink_y,.929),(.20,.18,.12))
for label,y in [("near",sink_y-.335),("far",sink_y+.335)]:
    add(sink,label+"_rim",(.72,.025,.012),(sink_x,y,.929),(.20,.18,.12))
add(sink,"draining_panel",(.20,.61,.012),(1.26,sink_y,.930),(.050,.055,.039))
for i in range(6):
    add(sink,"drainer_rib_%d"%i,(.14,.012,.008),(1.26,sink_y-.25+i*.10,.940),(.23,.21,.14))
scene.include("sink",sink)

hob=Asset("Black glass four burner induction hob")
add(hob,"thin_metal_border",(.995,1.825,.006),(.865,-1.04,.920),(.14,.15,.13))
add(hob,"glass_surface",(.97,1.80,.018),(.865,-1.04,.932),(.007,.010,.010))
for j,(x,y,r) in enumerate([
    (.61,-.42,.205),(1.12,-.45,.183),
    (.61,-1.30,.205),(1.12,-1.35,.225)
]):
    for k in range(20):
        a=2*math.pi*k/20
        b=2*math.pi*(k+1)/20
        hob.include("burner_%d_segment_%02d"%(j,k),
            rod(.0018,start=(x+r*math.cos(a),y+r*math.sin(a),.943),
                end=(x+r*math.cos(b),y+r*math.sin(b),.943),
                color=(.095,.105,.090)))
for i in range(4):
    add(hob,"touch_control_%d"%i,(.023,.005,.001),(.92+i*.055,-1.77,.944),(.24,.25,.21))
scene.include("hob",hob)

upper=Asset("Walnut overhead cabinets and extractor")
front_x=.88
bottom_z=1.69
add(upper,"cabinet_body",(.63,6.1,1.65),(1.195,-.13,2.525),WOOD)
# The broad rear end is visible to the left of the longitudinal fronts.
add(upper,"broad_rear_end_panel",(1.15,.065,1.65),(.935,2.895,2.525),(.105,.037,.012))
add(upper,"rear_end_vertical_edge",(.045,.11,1.70),(.375,2.86,2.525),(.065,.023,.008))
for i in range(5):
    yy=-2.55+i*1.19
    add(upper,"walnut_front_%d"%i,(.035,1.176,1.60),(front_x,yy,2.525),WOOD)
add(upper,"lower_front_lip",(.055,6.1,.038),(.858,-.13,1.704),(.067,.024,.007))
add(upper,"wood_underside",(.61,6.08,.025),(1.19,-.13,1.686),(.135,.075,.030))
add(upper,"extractor_underside",(.55,1.80,.025),(1.185,-.84,1.666),(.40,.41,.38))
add(upper,"extractor_filter_near",(.39,.62,.008),(1.18,-1.27,1.648),(.24,.26,.24))
add(upper,"extractor_filter_far",(.39,.62,.008),(1.18,-.48,1.648),(.24,.26,.24))
add(upper,"extractor_front_rail",(.032,1.84,.032),(.895,-.84,1.661),(.43,.43,.38))
add(upper,"extractor_control",(.025,.085,.009),(.96,-1.44,1.646),(.035,.038,.032))
add(upper,"warm_light_strip",(.018,6.00,.014),(1.43,-.13,1.661),(1.0,.76,.36))
scene.include("upper_cabinetry",upper)

electrical=Asset("Wall switches and sockets")
for label,x,z in [("switch",-.93,1.10),("socket",-.90,.31)]:
    add(electrical,label+"_plate",(.09,.015,.085),(x,2.94,z),(.84,.84,.78))
    add(electrical,label+"_center",(.045,.009,.047),(x,2.928,z),(.66,.67,.62))
add(electrical,"backsplash_socket",(.012,.14,.11),(1.489,.20,1.15),(.83,.82,.76))
scene.include("electrical",electrical)

realize(scene)

def matching_materials(rgb):
    for mat in bpy.data.materials:
        if mat.use_nodes:
            bs=mat.node_tree.nodes.get("Principled BSDF")
            if bs and max(abs(bs.inputs["Base Color"].default_value[i]-rgb[i]) for i in range(3))<.008:
                yield mat

def texture_finish(rgb,kind):
    for mat in list(matching_materials(rgb)):
        nt=mat.node_tree
        bs=nt.nodes.get("Principled BSDF")
        coord=nt.nodes.new("ShaderNodeTexCoord")
        scale=nt.nodes.new("ShaderNodeVectorMath")
        scale.operation='MULTIPLY'
        nt.links.new(coord.outputs["Generated"],scale.inputs[0])
        noise=nt.nodes.new("ShaderNodeTexNoise")
        nt.links.new(scale.outputs[0],noise.inputs["Vector"])
        ramp=nt.nodes.new("ShaderNodeValToRGB")
        nt.links.new(noise.outputs["Fac"],ramp.inputs[0])
        if kind=="wood":
            scale.inputs[1].default_value=(18,2,1)
            noise.inputs["Scale"].default_value=3
            noise.inputs["Detail"].default_value=2
            ramp.color_ramp.elements[0].color=tuple(c*.57 for c in rgb)+(1,)
            ramp.color_ramp.elements[1].color=tuple(c*1.43 for c in rgb)+(1,)
            bs.inputs["Roughness"].default_value=.34
        elif kind=="stone":
            scale.inputs[1].default_value=(2,9,2)
            noise.inputs["Scale"].default_value=4
            noise.inputs["Detail"].default_value=4
            noise.inputs["Roughness"].default_value=.72
            ramp.color_ramp.elements[0].position=.30
            ramp.color_ramp.elements[0].color=(.12,.10,.075,1)
            ramp.color_ramp.elements[1].position=.40
            ramp.color_ramp.elements[1].color=(.65,.60,.49,1)
            bs.inputs["Roughness"].default_value=.31
        else:
            scale.inputs[1].default_value=(3,16,.5)
            noise.inputs["Scale"].default_value=4
            noise.inputs["Detail"].default_value=2
            ramp.color_ramp.elements[0].color=(.40,.37,.31,1)
            ramp.color_ramp.elements[1].color=(.58,.55,.48,1)
            bs.inputs["Roughness"].default_value=.65
        nt.links.new(ramp.outputs["Color"],bs.inputs["Base Color"])

texture_finish(WOOD,"wood")
texture_finish(SLAT,"wood")
texture_finish((.105,.037,.012),"wood")
texture_finish(STONE,"stone")
texture_finish((.52,.49,.43),"floor")

for mat in bpy.data.materials:
    if not mat.use_nodes:
        continue
    bs=mat.node_tree.nodes.get("Principled BSDF")
    if bs is None:
        continue
    color=bs.inputs["Base Color"].default_value
    if max(color[:3])<.035:
        bs.inputs["Roughness"].default_value=.16
    if max(abs(color[i]-WALL[i]) for i in range(3))<.008:
        bs.inputs["Roughness"].default_value=.19
    if color[0]>.95 and .70<color[1]<.80:
        bs.inputs["Emission Color"].default_value=(1,.69,.32,1)
        bs.inputs["Emission Strength"].default_value=3

sc=bpy.context.scene
if sc.world is None:
    sc.world=bpy.data.worlds.new("SceneWorld")
sc.world.use_nodes=True
background=sc.world.node_tree.nodes.get("Background")
if background is None:
    background=sc.world.node_tree.nodes.new("ShaderNodeBackground")
output=sc.world.node_tree.nodes.get("World Output")
if output is None:
    output=sc.world.node_tree.nodes.new("ShaderNodeOutputWorld")
sc.world.node_tree.links.new(background.outputs["Background"],output.inputs["Surface"])
background.inputs["Color"].default_value=(.78,.80,.82,1)
background.inputs["Strength"].default_value=.24

# Lateral camera correction preserves the rear door while straightening
# the near counter edge and revealing the walnut cabinet fronts.
set_view(position=(.62,-2.50,1.60),target=(.54,3.0,1.24),lens=29.5,sensor=36)
area_emitter(position=(-2.3,-.5,2.7),power=300,size=3.8,
             target=(-.4,2.6,.8),color=(1,.91,.79))
area_emitter(position=(-1.8,-3.5,2.2),power=170,size=3.2,
             target=(.4,1.4,1.2),color=(.92,.95,1))
area_emitter(position=(1.35,1.4,1.62),power=12,size=.6,
             target=(1.46,1.4,1.15),color=(1,.73,.40))
area_emitter(position=(1.35,-1,1.62),power=15,size=.9,
             target=(1.46,-1,1.15),color=(1,.79,.49))
sc.view_settings.view_transform='AgX'
