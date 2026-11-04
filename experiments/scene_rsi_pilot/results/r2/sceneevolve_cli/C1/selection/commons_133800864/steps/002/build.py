from sceneact import *
import bpy, math

# The feedback is too wide: tighten framing and move the view toward the right.
# The towel belongs on the cabinet's left cheek; broaden its hanging silhouette.
# Restore dark speckled granite, rounded paper, and darker countertop appliances.

scene = Scene('Kitchen corner')
ivory = (.70,.64,.49)
trim = (.80,.76,.65)
white = (.88,.84,.73)
steel = (.43,.42,.35)
dark = (.022,.028,.024)
camera_position = (-2.0,-3.0,2.12)
camera_target = (.30,.23,1.77)

def add(parent,name,node):
    parent.include(name,node)

architecture = Asset('Walls and window')
add(architecture,'wall',box((3.5,.10,3.6),center=(.1,.65,1.8),color=(.65,.61,.49)))
add(architecture,'window_glass',box((.98,.025,2.8),center=(-.60,.56,1.94),color=(.54,.72,.77)))
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
add(architecture,'cord',rod(.003,start=(-.31,.26,2.65),end=(-.31,.26,1.97),color=white))
add(architecture,'weight',rod(.008,length=.055,center=(-.31,.26,1.95),color=white))
scene.include('architecture',architecture)

cab = Asset('Cream wall cabinet')
add(cab,'body',box((1.05,.53,1.65),center=(.445,.375,2.465),color=ivory))
add(cab,'side',box((.045,.56,1.67),center=(-.09,.345,2.475),color=(.76,.70,.57)))
add(cab,'door',box((.99,.037,1.60),center=(.455,.085,2.49),color=(.72,.66,.52)))
for i,x in enumerate((.006,.904)):
    add(cab,'stile_'+str(i),box((.060,.027,1.58),center=(x,.052,2.49),color=ivory))
for i,z in enumerate((1.715,3.265)):
    add(cab,'rail_'+str(i),box((.95,.027,.065),center=(.455,.052,z),color=ivory))
add(cab,'panel',box((.76,.013,1.36),center=(.455,.063,2.49),color=(.70,.64,.50)))
add(cab,'bottom',box((1.07,.57,.052),center=(.445,.348,1.66),color=(.77,.72,.59)))
add(cab,'knob_stem',rod(.012,start=(.888,.035,1.925),end=(.888,-.007,1.925),color=steel))
add(cab,'knob',ball(.022,center=(.888,-.017,1.925),color=steel))
scene.include('cabinet',cab)

counter = Asset('Granite and sink')
granite=(.31,.29,.23)
add(counter,'slab',box((3.4,1.50,.075),center=(.02,-.10,.872),color=granite))
add(counter,'backsplash',box((3.4,.055,.16),center=(.02,.585,.99),color=granite))
add(counter,'rim',box((.79,.70,.018),center=(-.69,-.34,.917),color=(.30,.31,.27)))
add(counter,'basin',box((.72,.63,.025),center=(-.69,-.36,.927),color=(.015,.023,.019)))
for i,x in enumerate((-1.06,-.32)):
    add(counter,'rim_side_'+str(i),box((.022,.67,.024),center=(x,-.34,.938),color=steel))
add(counter,'faucet_base',rod(.050,length=.024,center=(-.67,.061,.929),color=steel))
add(counter,'faucet',rod(.014,start=(-.67,.061,.94),end=(-.67,.061,1.26),color=steel))
add(counter,'spout',sweep_tube(points=[(-.67,.061,1.26),(-.67,.045,1.30),(-.67,-.035,1.31),(-.67,-.11,1.27)],radius=.013,color=steel))
for i,x in enumerate((-.85,-.49)):
    add(counter,'tap_'+str(i),rod(.033,length=.025,center=(x,.045,.93),color=steel))
    add(counter,'lever_'+str(i),rod(.011,start=(x,.045,.94),end=(x+.035,.045,1.00),color=steel))
scene.include('counter',counter)

towel=Asset('Side mounted towel')
add(towel,'mount',rod(.049,start=(-.112,.12,1.99),end=(-.166,.12,1.99),color=steel))
add(towel,'neck',rod(.016,start=(-.17,.12,1.99),end=(-.205,.12,1.99),color=steel))
points=[]
for i in range(25):
    a=2*math.pi*i/24
    points.append((-.205,.12+.112*math.sin(a),1.857+.145*math.cos(a)))
add(towel,'ring',sweep_tube(points=points,radius=.006,color=steel))
for i in range(8):
    y=.01+i*.032
    ztop=1.755-.012*abs(i-3)
    zbottom=1.055+.030*math.sin(i*1.5)
    x=-.224-.013*math.cos(i*1.8)
    cloth=box((.035,.045,ztop-zbottom),center=(x,y,(ztop+zbottom)/2),color=(.83+.006*i,.79+.006*i,.68+.007*i))
    cloth.turn('x',-7+2*i)
    add(towel,'fold_'+str(i),cloth)
add(towel,'fold_over_ring',resized(ball(.11,center=(-.223,.12,1.74),color=white),(.38,1.10,.48)))
# A second, shorter layer hangs behind the front folds.
back=box((.025,.23,.48),center=(-.177,.16,1.43),color=(.78,.74,.63))
back.turn('x',-12)
add(towel,'back_layer',back)
scene.include('towel',towel)

paper=Asset('Paper towel dispenser')
add(paper,'roll',rod(.145,length=.66,center=(.55,-.022,2.30),color=(.90,.85,.73)))
add(paper,'spindle',rod(.017,length=.11,center=(.55,-.022,2.68),color=steel))
add(paper,'finial',resized(ball(.031,center=(.55,-.022,2.735),color=steel),(.8,.8,1.2)))
for i,x in enumerate((.43,.67)):
    add(paper,'bracket_'+str(i),ball(.026,center=(x,-.007,1.94),color=(.20,.20,.16)))
add(paper,'arm',rod(.016,start=(.55,.09,1.96),end=(.55,-.06,1.96),color=steel))
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
add(jug,'body',resized(ball(.155,center=(.47,-.065,1.087),color=jugcolor),(1,.80,1.16)))
add(jug,'lower_body',rod(.137,length=.18,center=(.47,-.065,1.015),color=jugcolor))
add(jug,'shoulder',resized(ball(.118,center=(.47,-.065,1.225),color=jugcolor),(1,.85,.90)))
add(jug,'neck',rod(.035,length=.068,center=(.47,-.065,1.31),color=(.70,.72,.64)))
add(jug,'cap',rod(.037,length=.025,center=(.47,-.065,1.347),color=(.79,.79,.69)))
handle=subtract(
    resized(ball(.079,center=(.554,-.059,1.225),color=jugcolor),(.78,.53,1.15)),
    resized(ball(.051,center=(.554,-.059,1.232)),(.75,1.2,1.12)))
add(jug,'handle',handle)
scene.include('jug',jug)

pitcher=Asset('Blue filter pitcher')
add(pitcher,'reservoir',resized(ball(.159,center=(.89,.245,1.115),color=(.025,.049,.12)),(1,.76,1.47)))
add(pitcher,'base',rod(.121,length=.035,center=(.89,.245,.938),color=(.047,.070,.12)))
add(pitcher,'upper_body',rod(.139,length=.185,center=(.89,.245,1.26),color=(.032,.066,.15)))
lid=resized(ball(.16,center=(.89,.245,1.366),color=(.30,.31,.26)),(1,.82,.22))
lid.turn('y',10)
add(pitcher,'lid',lid)
add(pitcher,'spout',box((.065,.09,.037),center=(.76,.235,1.38),color=(.31,.32,.27)))
add(pitcher,'handle',sweep_tube(points=[(1.013,.245,1.31),(1.083,.245,1.28),(1.113,.245,1.17),(1.087,.245,1.03),(1.019,.245,.995)],radius=.022,color=(.40,.44,.40)))
add(pitcher,'glint',rod(.004,start=(.825,.124,1.01),end=(.815,.124,1.29),color=(.17,.23,.32)))
scene.include('pitcher',pitcher)

realize(scene)
for mat in bpy.data.materials:
    mat.use_nodes=True
    nt=mat.node_tree
    bs=nt.nodes.get('Principled BSDF')
    if bs is None:
        continue
    c=bs.inputs['Base Color'].default_value
    bs.inputs['Roughness'].default_value=.60
    if abs(c[0]-granite[0])<.015 and abs(c[1]-granite[1])<.015:
        noise=nt.nodes.new('ShaderNodeTexNoise')
        noise.inputs['Scale'].default_value=210
        noise.inputs['Detail'].default_value=2.5
        ramp=nt.nodes.new('ShaderNodeValToRGB')
        ramp.color_ramp.elements[0].position=.30
        ramp.color_ramp.elements[0].color=(.045,.035,.025,1)
        ramp.color_ramp.elements[1].position=.70
        ramp.color_ramp.elements[1].color=(.43,.37,.27,1)
        nt.links.new(noise.outputs['Fac'],ramp.inputs[0])
        nt.links.new(ramp.outputs[0],bs.inputs['Base Color'])
        bump=nt.nodes.new('ShaderNodeBump')
        bump.inputs['Strength'].default_value=.20
        bump.inputs['Distance'].default_value=.003
        nt.links.new(noise.outputs['Fac'],bump.inputs['Height'])
        nt.links.new(bump.outputs[0],bs.inputs['Normal'])
    if abs(c[0]-steel[0])<.01 and abs(c[1]-steel[1])<.01:
        bs.inputs['Metallic'].default_value=.78
        bs.inputs['Roughness'].default_value=.26
    if c[2]>.10 and c[0]<.08:
        bs.inputs['Roughness'].default_value=.24
    if abs(c[0]-.90)<.01:
        noise=nt.nodes.new('ShaderNodeTexNoise')
        noise.inputs['Scale'].default_value=155
        bump=nt.nodes.new('ShaderNodeBump')
        bump.inputs['Strength'].default_value=.13
        bump.inputs['Distance'].default_value=.0015
        nt.links.new(noise.outputs['Fac'],bump.inputs['Height'])
        nt.links.new(bump.outputs[0],bs.inputs['Normal'])

set_view(camera_position,camera_target,lens=65,sensor=36)
sc=bpy.context.scene
if sc.world is None:
    sc.world=bpy.data.worlds.new('Ambient')
sc.world.use_nodes=True
sc.world.node_tree.nodes['Background'].inputs[0].default_value=(.65,.67,.69,1)
sc.world.node_tree.nodes['Background'].inputs[1].default_value=.23
area_emitter((-1.5,-.15,2.45),power=145,size=1.65,target=(.35,.2,1.4),color=(.82,.91,1))
area_emitter((.2,-2.5,3.0),power=85,size=2.5,target=(.3,.3,1.7),color=(1,.80,.55))
sc.render.resolution_x=384
sc.render.resolution_y=512
sc.render.resolution_percentage=100
sc.view_settings.view_transform='AgX'
