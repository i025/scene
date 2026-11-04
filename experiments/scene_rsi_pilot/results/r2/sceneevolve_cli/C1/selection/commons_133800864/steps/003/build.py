from sceneact import *
import bpy, math

# Cabinet cheek is too narrow; widen its visible depth and narrow the front door.
# Towel is too far left, narrow, and low; move it onto the broadened cheek.
# Pitcher needs to move right; restore the counter's dark granular surface.

scene = Scene('Kitchen corner')
ivory=(.70,.64,.49)
trim=(.80,.76,.65)
white=(.88,.84,.73)
steel=(.43,.42,.35)
dark=(.022,.028,.024)
camera_position=(-2.0,-3.0,2.12)
camera_target=(.30,.23,1.745)

def add(parent,name,node):
    parent.include(name,node)

architecture=Asset('Walls and window')
add(architecture,'wall',box((3.5,.10,3.6),center=(.1,.65,1.8),color=(.65,.61,.49)))
add(architecture,'glass',box((.98,.025,2.8),center=(-.60,.56,1.94),color=(.54,.72,.77)))
for i,x in enumerate((-1.10,-.10)):
    add(architecture,'frame_'+str(i),box((.055,.09,2.9),center=(x,.48,1.94),color=trim))
for i,z in enumerate((.52,1.78,3.37)):
    add(architecture,'cross_'+str(i),box((1.04,.07,.055),center=(-.60,.48,z),color=trim))
add(architecture,'mullion',box((.045,.07,2.85),center=(-.65,.48,1.94),color=trim))
for i,(x,z,r) in enumerate([(-.9,2.75,.14),(-.47,2.8,.16),(-.83,2.51,.12),(-.24,2.55,.13),(-.88,1.95,.12)]):
    add(architecture,'foliage_'+str(i),ball(r,center=(x,.545,z),color=(.31,.48,.35)))
for i in range(43):
    slat=box((1.02,.10,.018),center=(-.60,.365,.57+i*.066),color=(.77,.79,.72))
    slat.turn('x',-12)
    add(architecture,'blind_'+str(i),slat)
for i,x in enumerate((-.94,-.27)):
    add(architecture,'tape_'+str(i),box((.012,.009,2.85),center=(x,.294,1.96),color=(.72,.72,.62)))
for i,x in enumerate((-.36,-.32)):
    add(architecture,'cord_'+str(i),rod(.003,start=(x,.26,2.65),end=(x,.26,1.97),color=white))
    add(architecture,'weight_'+str(i),rod(.008,length=.055,center=(x,.26,1.95),color=white))
scene.include('architecture',architecture)

cab=Asset('Cream wall cabinet')
left=.20
right=.97
bottom=1.75
top=3.40
add(cab,'body',box((right-left,.92,top-bottom),center=((left+right)/2,.54,(top+bottom)/2),color=ivory))
add(cab,'side',box((.045,.94,top-bottom),center=(left-.015,.54,(top+bottom)/2),color=(.76,.70,.57)))
add(cab,'door',box((.77,.037,1.60),center=(.585,.085,2.575),color=(.72,.66,.52)))
for i,x in enumerate((.235,.935)):
    add(cab,'stile_'+str(i),box((.055,.027,1.58),center=(x,.052,2.575),color=ivory))
for i,z in enumerate((1.80,3.35)):
    add(cab,'rail_'+str(i),box((.75,.027,.065),center=(.585,.052,z),color=ivory))
add(cab,'panel',box((.595,.013,1.36),center=(.585,.063,2.575),color=(.70,.64,.50)))
add(cab,'bottom',box((.82,.96,.045),center=(.58,.54,1.75),color=(.77,.72,.59)))
add(cab,'knob_stem',rod(.012,start=(.924,.035,1.96),end=(.924,-.007,1.96),color=steel))
add(cab,'knob',ball(.022,center=(.924,-.017,1.96),color=steel))
scene.include('cabinet',cab)

counter=Asset('Granite and sink')
granite=(.31,.29,.23)
add(counter,'slab',box((3.4,1.50,.075),center=(.02,-.10,.872),color=granite))
add(counter,'backsplash',box((3.4,.055,.13),center=(.02,.585,.975),color=granite))
sink_x=-.48
add(counter,'rim',box((.86,.76,.018),center=(sink_x,-.34,.917),color=(.30,.31,.27)))
add(counter,'basin',box((.79,.69,.025),center=(sink_x,-.36,.927),color=(.015,.023,.019)))
for i,x in enumerate((sink_x-.41,sink_x+.41)):
    add(counter,'rim_side_'+str(i),box((.022,.73,.024),center=(x,-.34,.938),color=steel))
add(counter,'faucet_base',rod(.050,length=.024,center=(-.56,.061,.929),color=steel))
add(counter,'faucet',rod(.014,start=(-.56,.061,.94),end=(-.56,.061,1.26),color=steel))
add(counter,'spout',sweep_tube(points=[(-.56,.061,1.26),(-.56,.045,1.30),(-.56,-.035,1.31),(-.56,-.11,1.27)],radius=.013,color=steel))
for i,x in enumerate((-.74,-.38)):
    add(counter,'tap_'+str(i),rod(.033,length=.025,center=(x,.045,.93),color=steel))
    add(counter,'lever_'+str(i),rod(.011,start=(x,.045,.94),end=(x+.035,.045,1.00),color=steel))
scene.include('counter',counter)

towel=Asset('Side mounted towel')
add(towel,'mount',rod(.049,start=(.175,.43,2.08),end=(.12,.43,2.08),color=steel))
add(towel,'neck',rod(.016,start=(.12,.43,2.08),end=(.085,.43,2.08),color=steel))
points=[]
for i in range(25):
    a=2*math.pi*i/24
    points.append((.085,.43+.125*math.sin(a),1.947+.145*math.cos(a)))
add(towel,'ring',sweep_tube(points=points,radius=.006,color=steel))
for i in range(10):
    y=.245+i*.040
    ztop=1.835-.012*abs(i-4)
    zbottom=1.165+.035*math.sin(i*1.5)
    x=.065-.025*math.cos(i*1.8)
    cloth=box((.047,.055,ztop-zbottom),center=(x,y,(ztop+zbottom)/2),color=(.83+.004*i,.79+.004*i,.68+.005*i))
    cloth.turn('x',-8+1.8*i)
    add(towel,'fold_'+str(i),cloth)
add(towel,'fold_over_ring',resized(ball(.125,center=(.062,.43,1.83),color=white),(.42,1.12,.48)))
back=box((.025,.32,.48),center=(.11,.48,1.52),color=(.78,.74,.63))
back.turn('x',-12)
add(towel,'back_layer',back)
scene.include('towel',towel)

paper=Asset('Paper towel dispenser')
add(paper,'roll',rod(.145,length=.66,center=(.55,-.022,2.275),color=(.90,.85,.73)))
add(paper,'spindle',rod(.017,length=.11,center=(.55,-.022,2.655),color=steel))
add(paper,'finial',resized(ball(.031,center=(.55,-.022,2.71),color=steel),(.8,.8,1.2)))
for i,x in enumerate((.43,.67)):
    add(paper,'bracket_'+str(i),ball(.026,center=(x,-.007,1.915),color=(.20,.20,.16)))
add(paper,'arm',rod(.016,start=(.55,.09,1.935),end=(.55,-.06,1.935),color=steel))
scene.include('paper',paper)

appliances=Asset('Blender and accessories')
add(appliances,'blender_base',resized(ball(.105,center=(.205,.31,1.035),color=(.018,.022,.019)),(.9,.9,1.20)))
add(appliances,'collar',rod(.072,length=.045,center=(.205,.31,1.14),color=dark))
cup=rod(.062,length=.29,center=(.19,.31,1.30),color=(.23,.26,.24),opacity=.45)
cup.turn('y',-10)
add(appliances,'clear_blender_cup',cup)
add(appliances,'cup_highlight',rod(.004,start=(.157,.25,1.18),end=(.108,.25,1.44),color=(.59,.61,.55)))
add(appliances,'canister',rod(.063,length=.23,center=(-.035,.265,1.025),color=(.27,.29,.15)))
add(appliances,'canister_rim',rod(.067,length=.018,center=(-.035,.265,1.148),color=steel))
add(appliances,'small_cup',rod(.045,length=.060,center=(-.30,-.01,.944),color=(.22,.20,.14)))
add(appliances,'small_cup_inside',rod(.036,length=.004,center=(-.30,-.01,.975),color=dark))
scene.include('accessories',appliances)

jug=Asset('Gallon water jug')
jugcolor=(.61,.64,.58)
add(jug,'body',fillet_box((.29,.235,.29),radius=.055,center=(.47,-.065,1.06),color=jugcolor))
add(jug,'shoulder',resized(ball(.132,center=(.47,-.065,1.198),color=jugcolor),(1,.85,.94)))
add(jug,'neck',rod(.035,length=.068,center=(.47,-.065,1.31),color=(.70,.72,.64)))
add(jug,'cap',rod(.037,length=.025,center=(.47,-.065,1.347),color=(.79,.79,.69)))
handle=subtract(
    resized(ball(.079,center=(.554,-.059,1.225),color=jugcolor),(.78,.53,1.15)),
    resized(ball(.051,center=(.554,-.059,1.232)),(.75,1.2,1.12)))
add(jug,'handle',handle)
scene.include('jug',jug)

pitcher=Asset('Blue filter pitcher')
add(pitcher,'reservoir',resized(ball(.159,center=(1.00,.245,1.115),color=(.025,.049,.12)),(1,.76,1.47)))
add(pitcher,'base',rod(.121,length=.035,center=(1.00,.245,.938),color=(.047,.070,.12)))
add(pitcher,'upper_body',rod(.139,length=.185,center=(1.00,.245,1.26),color=(.032,.066,.15)))
lid=resized(ball(.16,center=(1.00,.245,1.366),color=(.30,.31,.26)),(1,.82,.22))
lid.turn('y',10)
add(pitcher,'lid',lid)
add(pitcher,'spout',box((.065,.09,.037),center=(.87,.235,1.38),color=(.31,.32,.27)))
add(pitcher,'handle',sweep_tube(points=[(1.123,.245,1.31),(1.193,.245,1.28),(1.223,.245,1.17),(1.197,.245,1.03),(1.129,.245,.995)],radius=.022,color=(.40,.44,.40)))
add(pitcher,'glint',rod(.004,start=(.935,.124,1.01),end=(.925,.124,1.29),color=(.17,.23,.32)))
scene.include('pitcher',pitcher)

realize(scene)
for mat in bpy.data.materials:
    mat.use_nodes=True
    bs=mat.node_tree.nodes.get('Principled BSDF')
    if bs is None:
        continue
    bs.inputs['Roughness'].default_value=.60
    c=bs.inputs['Base Color'].default_value
    if .12<c[0]<.47 and abs(c[0]-c[1])<.035 and c[2]<c[0]:
        bs.inputs['Metallic'].default_value=.35
        bs.inputs['Roughness'].default_value=.32
    if c[2]>.10 and c[0]<.08:
        bs.inputs['Roughness'].default_value=.24

stone=bpy.data.materials.new('Dark finely speckled granite')
stone.use_nodes=True
nt=stone.node_tree
bs=nt.nodes.get('Principled BSDF')
bs.inputs['Roughness'].default_value=.58
noise=nt.nodes.new('ShaderNodeTexNoise')
noise.inputs['Scale'].default_value=240
noise.inputs['Detail'].default_value=2
ramp=nt.nodes.new('ShaderNodeValToRGB')
ramp.color_ramp.elements[0].position=.26
ramp.color_ramp.elements[0].color=(.025,.022,.017,1)
ramp.color_ramp.elements[1].position=.75
ramp.color_ramp.elements[1].color=(.40,.34,.24,1)
for p,col in [(.43,(.095,.081,.057,1)),(.54,(.22,.19,.135,1)),(.63,(.32,.29,.22,1))]:
    e=ramp.color_ramp.elements.new(p)
    e.color=col
nt.links.new(noise.outputs['Fac'],ramp.inputs[0])
nt.links.new(ramp.outputs[0],bs.inputs['Base Color'])
bump=nt.nodes.new('ShaderNodeBump')
bump.inputs['Strength'].default_value=.20
bump.inputs['Distance'].default_value=.002
nt.links.new(noise.outputs['Fac'],bump.inputs['Height'])
nt.links.new(bump.outputs[0],bs.inputs['Normal'])
for obj in bpy.context.scene.objects:
    if obj.type=='MESH' and obj.dimensions.x>3 and obj.dimensions.z<.20:
        obj.data.materials.clear()
        obj.data.materials.append(stone)

set_view(camera_position,camera_target,lens=65,sensor=36)
sc=bpy.context.scene
if sc.world is None:
    sc.world=bpy.data.worlds.new('Ambient')
sc.world.use_nodes=True
sc.world.node_tree.nodes['Background'].inputs[0].default_value=(.65,.67,.69,1)
sc.world.node_tree.nodes['Background'].inputs[1].default_value=.19
area_emitter((-1.5,-.15,2.45),power=135,size=1.65,target=(.35,.2,1.4),color=(.82,.91,1))
area_emitter((.2,-2.5,3.0),power=75,size=2.5,target=(.3,.3,1.7),color=(1,.80,.55))
sc.render.resolution_x=384
sc.render.resolution_y=512
sc.render.resolution_percentage=100
sc.view_settings.view_transform='AgX'
