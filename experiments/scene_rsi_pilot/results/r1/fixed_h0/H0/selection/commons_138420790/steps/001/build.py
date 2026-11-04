from sceneact import *
import bpy
import math
from mathutils import Vector

scene = Scene("Kitchen")
def B(name, size, center, color):
    n = box(size=size, center=center, color=color)
    scene.include(name, n)
    return n

ivory = (.69,.70,.67)
charcoal = (.045,.049,.046)
black = (.018,.022,.021)
steel = (.34,.36,.35)

# Pale, large-format tiled floor.
B("floor", (18,16,.12), (0,0,-.075), (.66,.65,.61))
for i in range(-7,8):
    B("floor_joint_x_%d"%i, (.009,16,.002), (i*1.20,0,-.013), (.46,.46,.43))
for i in range(-7,8):
    B("floor_joint_y_%d"%i, (18,.009,.002), (0,i*1.20,-.012), (.46,.46,.43))

# Showroom enclosure, with the exposed dark ceiling.
B("rear_wall", (10,.18,4.5), (0,2.65,2.2), (.27,.29,.27))
B("left_wall", (.18,10,4.5), (-3.5,1,2.2), (.36,.37,.34))
B("ceiling", (12,12,.15), (0,0,4.18), (.035,.043,.039))
for x in [-3.2,-1.7,-.2,1.3,2.8,4.3]:
    B("ceiling_joist_"+str(x), (.16,10,.23), (x,0,4.00), (.025,.031,.028))
for y in [-2.3,.1,2.4]:
    B("cross_beam_"+str(y), (11,.25,.36), (0,y,3.96), (.045,.052,.048))
for x in [-2.9,-2.55,-2.2,-1.85,-1.5,-1.15,-.8,-.45,0,.35,.7,1.05,1.4,1.75,2.1,2.45,2.8]:
    B("ceiling_rib_"+str(x), (.025,10,.035), (x,0,4.08), (.075,.081,.075))

# Tall black cabinet on the left.
B("left_tall_cabinet", (.83,.72,2.63), (-2.53,1.94,1.315), charcoal)
B("left_tall_door", (.805,.025,2.56), (-2.53,1.565,1.33), (.065,.071,.066))
B("left_door_vertical_joint", (.009,.008,2.54), (-2.54,1.547,1.33), (.025,.029,.026))
B("left_upper_door_joint", (.80,.008,.009), (-2.53,1.546,2.21), (.03,.033,.03))

# Rear worktop and charcoal tiled backsplash.
B("rear_base", (3.43,.65,.87), (-.55,2.08,.435), (.038,.042,.039))
B("rear_counter", (3.48,.72,.045), (-.55,2.035,.895), (.075,.078,.068))
for x in [-1.9,-1.25,-.60,.05,.70]:
    B("rear_base_seam"+str(x), (.012,.012,.73), (x,1.747,.45), (.012,.015,.013))
B("backsplash", (3.8,.06,1.11), (-.48,2.437,1.49), (.060,.066,.059))
for x in [-2.1,-1.48,-.86,-.24,.38,1.0]:
    B("backsplash_vertical_"+str(x), (.009,.006,1.08), (x,2.402,1.49), (.030,.035,.030))
B("backsplash_horizontal", (3.8,.008,.008), (-.48,2.4,1.46), (.032,.037,.032))
B("upper_black_band", (3.75,.48,.50), (-.5,2.22,2.29), (.032,.038,.034))
B("warm_recess_back", (2.65,.018,.34), (-.64,2.388,1.125), (.31,.265,.228))
B("warm_shelf", (2.70,.39,.035), (-.64,2.19,.951), (.13,.12,.105))
B("under_cabinet_strip", (2.65,.018,.018), (-.64,2.13,1.315), (.83,.71,.55))

# Right-hand appliance tower.
B("oven_tower", (.91,.79,2.60), (1.69,2.13,1.30), (.040,.045,.041))
B("oven_side_panel", (.12,.82,2.64), (2.18,2.12,1.32), (.065,.071,.065))
B("oven_upper_frame", (.70,.035,.52), (1.68,1.717,1.75), steel)
B("microwave_black_face", (.63,.017,.40), (1.68,1.691,1.79), (.025,.033,.032))
B("microwave_glass", (.46,.012,.29), (1.61,1.679,1.80), (.035,.063,.073))
B("microwave_side_control", (.08,.015,.29), (1.957,1.675,1.80), (.095,.105,.101))
B("microwave_bottom_trim", (.67,.018,.045), (1.68,1.672,1.552), (.49,.50,.47))
B("oven_lower_frame", (.71,.04,.68), (1.68,1.714,1.14), (.28,.30,.28))
B("oven_glass", (.62,.018,.48), (1.68,1.684,1.13), (.024,.033,.033))
B("oven_handle", (.56,.055,.036), (1.68,1.63,1.405), (.57,.59,.57))
B("oven_control_band", (.66,.02,.085), (1.68,1.677,1.485), (.40,.42,.40))

# Dark panel to the right and a narrow glimpse into the adjoining display.
B("right_divider", (.14,1.3,2.75), (2.46,1.94,1.375), (.045,.050,.045))
B("right_header", (1.9,.24,.37), (2.17,2.45,2.93), (.30,.32,.29))
B("far_wood_post", (.20,.23,4.05), (2.81,2.22,2.025), (.43,.27,.13))
B("far_white_partition", (.12,1.8,2.55), (3.13,2.6,1.28), (.72,.71,.66))

# Island: plain end panel, three long handleless drawers and recessed plinth.
ix, iy = .05, -.10
length, depth = 2.40, 1.42
B("island_recessed_plinth", (2.26,1.25,.13), (ix,iy,.075), (.21,.23,.21))
B("island_carcass", (length,depth,.81), (ix,iy,.535), ivory)
B("island_left_end", (.045,depth,.89), (ix-length/2-.012,iy,.495), (.56,.58,.56))
B("island_right_end", (.035,depth,.89), (ix+length/2,iy,.495), (.66,.68,.65))
front_y = iy-depth/2-.016
for j,(z,h) in enumerate([(.252,.244),(.507,.244),(.763,.246)]):
    B("drawer_%d"%j, (length-.065,.035,h), (ix+.012,front_y,z), (.70,.72,.69))
    B("drawer_shadow_%d"%j, (length-.07,.012,.014), (ix+.012,front_y-.019,z+h/2+.006), (.29,.32,.29))
B("island_top", (length+.055,depth+.035,.045), (ix,iy,.967), (.79,.80,.75))

# A shallow, pale inset sink and a restrained chrome mixer.
sink_x, sink_y = .38, .14
B("sink_outer_rim", (.64,.48,.006), (sink_x,sink_y,.993), (.70,.72,.68))
B("sink_bowl_shadow", (.57,.405,.007), (sink_x,sink_y,.997), (.48,.53,.50))
B("sink_bowl_bottom", (.48,.32,.009), (sink_x,sink_y,1.000), (.67,.71,.67))
for dx in [-.295,.295]:
    B("sink_side_"+str(dx), (.018,.44,.012), (sink_x+dx,sink_y,1.006), (.84,.85,.80))
for dy in [-.218,.218]:
    B("sink_edge_"+str(dy), (.60,.018,.012), (sink_x,sink_y+dy,1.007), (.84,.85,.80))
# Grooves in the integrated draining area.
for k in range(5):
    B("drain_groove_%d"%k, (.29,.009,.002), (sink_x-.54,sink_y-.13+k*.058,.992), (.69,.72,.67))
chrome=(.59,.64,.62)
faucet_x, faucet_y = sink_x+.10,sink_y+.31
scene.include("tap_base", rod(.032,start=(faucet_x,faucet_y,.99),end=(faucet_x,faucet_y,1.035),color=chrome))
points=[]
for i in range(17):
    t=math.pi*i/16
    points.append((faucet_x, faucet_y-.11+.11*math.cos(t),1.085+.14*math.sin(t)))
points.insert(0,(faucet_x,faucet_y,1.005))
scene.include("arched_tap",sweep_tube(points=points,radius=.012,color=chrome))
scene.include("tap_lever",rod(.009,start=(faucet_x+.048,faucet_y,1.025),end=(faucet_x+.048,faucet_y,1.12),color=chrome))

# Small red kettle on the rear counter.
scene.include("kettle_red",ball(.105,center=(-.74,2.01,1.035),color=(.65,.009,.024)))
B("kettle_black_base", (.18,.15,.035), (-.74,2.01,.947), (.018,.020,.018))
scene.include("kettle_lid",ball(.066,center=(-.74,2.01,1.10),color=(.016,.019,.017)))
handle=[]
for i in range(15):
    a=math.pi*i/14
    handle.append((-.74+.077*math.cos(a),2.025,1.07+.093*math.sin(a)))
scene.include("kettle_handle",sweep_tube(points=handle,radius=.014,color=(.025,.026,.023)))

# Large monolithic plaster-clad extractor suspended above the island.
B("extractor_hood", (1.16,.98,1.94), (-.25,.15,3.015), (.75,.74,.66))
B("extractor_bottom", (1.13,.95,.024), (-.25,.15,2.039), (.58,.58,.52))
B("extractor_bottom_slot", (.73,.23,.008), (-.25,.15,2.022), (.23,.25,.22))
B("extractor_tiny_tab", (.055,.045,.025), (-.67,-.35,2.038), (.48,.48,.42))

# The prominent foreground structural timber.
B("foreground_timber", (.43,.43,4.6), (-2.64,-.60,2.30), (.40,.245,.125))

realize(scene)

# Procedural vertical timber grain; all other finishes retain their simple colors.
wood=bpy.data.materials.new("Natural oak with long grain")
wood.diffuse_color=(.41,.26,.14,1)
wood.use_nodes=True
nodes=wood.node_tree.nodes
links=wood.node_tree.links
bs=nodes.get("Principled BSDF")
bs.inputs["Roughness"].default_value=.68
coord=nodes.new("ShaderNodeTexCoord")
mapping=nodes.new("ShaderNodeVectorMath")
mapping.operation='MULTIPLY'
mapping.inputs[1].default_value=(10,10,.55)
links.new(coord.outputs["Generated"],mapping.inputs[0])
noise=nodes.new("ShaderNodeTexNoise")
noise.inputs["Scale"].default_value=5
noise.inputs["Detail"].default_value=4
noise.inputs["Roughness"].default_value=.72
links.new(mapping.outputs["Vector"],noise.inputs["Vector"])
ramp=nodes.new("ShaderNodeValToRGB")
ramp.color_ramp.elements[0].position=.24
ramp.color_ramp.elements[0].color=(.14,.067,.027,1)
ramp.color_ramp.elements[1].position=.77
ramp.color_ramp.elements[1].color=(.56,.36,.19,1)
links.new(noise.outputs["Fac"],ramp.inputs["Fac"])
links.new(ramp.outputs["Color"],bs.inputs["Base Color"])
bump=nodes.new("ShaderNodeBump")
bump.inputs["Strength"].default_value=.21
bump.inputs["Distance"].default_value=.027
links.new(noise.outputs["Fac"],bump.inputs["Height"])
links.new(bump.outputs["Normal"],bs.inputs["Normal"])
for obj in bpy.context.scene.objects:
    if obj.type!='MESH':
        continue
    if "timber" in obj.name.lower() or "wood_post" in obj.name.lower():
        obj.data.materials.clear()
        obj.data.materials.append(wood)
    else:
        for mat in obj.data.materials:
            if mat and mat.use_nodes:
                p=mat.node_tree.nodes.get("Principled BSDF")
                if p:
                    p.inputs["Roughness"].default_value=.48
                    if any(t in obj.name.lower() for t in ["tap","oven_handle","trim"]):
                        p.inputs["Metallic"].default_value=.75
                        p.inputs["Roughness"].default_value=.24

set_view(position=(-5.35,-3.85,1.68),target=(0,.58,1.68),lens=39,sensor=36,shift=(0,.095))
area_emitter(position=(-3.7,-3.3,4.0),power=1050,size=4.0,target=(0,.1,.6),color=(1.0,.94,.83))
area_emitter(position=(1.0,-.8,3.8),power=650,size=3.0,target=(.1,.2,1),color=(.89,.94,1.0))
area_emitter(position=(-1.4,1.95,1.34),power=35,size=1.8,target=(-1.3,2.4,1.02),color=(1.0,.70,.48))
area_emitter(position=(3.4,2.0,3.3),power=280,size=2.0,target=(1.5,1.0,1.5),color=(1.0,.91,.76))

world=bpy.context.scene.world
world.use_nodes=True
world.node_tree.nodes["Background"].inputs[0].default_value=(.22,.25,.23,1)
world.node_tree.nodes["Background"].inputs[1].default_value=.30
s=bpy.context.scene
s.render.engine='CYCLES'
s.cycles.samples=64
s.cycles.use_denoising=True
s.render.resolution_x=384
s.render.resolution_y=512
s.render.resolution_percentage=100
s.view_settings.view_transform='AgX'
s.view_settings.exposure=.35
